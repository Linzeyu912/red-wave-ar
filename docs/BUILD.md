# 构建环境搭建指南

本文记录在本机（Windows 11，无预装 Android 工具链）从零搭建可编译环境的步骤，以及踩过的坑。

## 工具链安装位置

全部装在 `D:\AndroidDev`（纯 ASCII 路径，避免中文用户名问题）：

| 组件 | 路径 | 版本 |
|---|---|---|
| JDK | `D:\AndroidDev\jdk-17.0.19+10` | Temurin 17.0.19 |
| Android SDK | `D:\AndroidDev\sdk` | platform-tools + build-tools 34.0.0 + platforms;android-34 |
| command-line tools | `D:\AndroidDev\sdk\cmdline-tools\latest` | sdkmanager 12.0 |
| Gradle 缓存 | `D:\AndroidDev\gradle-home` | （`GRADLE_USER_HOME`） |

## 安装步骤

### 1. JDK 17（Temurin）

从 Adoptium 下载 Windows x64 zip，解压到 `D:\AndroidDev`：

```powershell
Invoke-WebRequest -Uri "https://api.adoptium.net/v3/binary/latest/17/ga/windows/x64/jdk/hotspot/normal/eclipse?project=jdk" -OutFile jdk17.zip
Expand-Archive jdk17.zip .
```

验证：`D:\AndroidDev\jdk-17.0.19+10\bin\java.exe -version`

### 2. Android command-line tools

```powershell
Invoke-WebRequest -Uri "https://dl.google.com/android/repository/commandlinetools-win-11076708_latest.zip" -OutFile cmdtools.zip
Expand-Archive cmdtools.zip .\sdk
```

**关键**：cmdline-tools 的内容必须放在 `sdk\cmdline-tools\latest\` 下（而不是直接放 `sdk\cmdline-tools\` 根），否则 sdkmanager 会报找不到。解压后手动把 `bin/ lib/ NOTICE.txt source.properties` 移进 `latest\` 子目录。

### 3. 安装 SDK 组件 + 接受许可

```powershell
$env:JAVA_HOME = "D:\AndroidDev\jdk-17.0.19+10"
$env:ANDROID_HOME = "D:\AndroidDev\sdk"
$sdkmgr = "D:\AndroidDev\sdk\cmdline-tools\latest\bin\sdkmanager.bat"
"y`n" * 20 | & $sdkmgr --licenses --sdk_root="$env:ANDROID_HOME"
& $sdkmgr "platform-tools" "platforms;android-34" "build-tools;34.0.0" --sdk_root="$env:ANDROID_HOME"
```

验证：`D:\AndroidDev\sdk\platform-tools\adb.exe version`

### 4. Gradle Wrapper

工程已内置 `gradlew` / `gradlew.bat` + `gradle/wrapper/gradle-wrapper.jar`，首次运行会自动下载 Gradle 8.9 到 `GRADLE_USER_HOME`。

## 踩过的坑（按发生顺序）

### 坑 1：`local.properties` 路径用了反斜杠

**现象**：`assembleDebug` 报
```
java.io.IOException: 文件名、目录名或卷标语法不正确。
at SdkLocator$SdkLocationSource.validateSdkPath
```

**原因**：`local.properties` 写成 `sdk.dir=D:\AndroidDev\sdk`。Java Properties 解析时把 `\A`、`\s` 当转义符吞掉。

**解决**：用正斜杠 `sdk.dir=D:/AndroidDev/sdk`。

### 坑 2：缺少 `android.useAndroidX`

**现象**：`checkDebugAarMetadata FAILED`，提示“contains AndroidX dependencies, but the `android.useAndroidX` property is not enabled”。

**解决**：新建 `gradle.properties`，加 `android.useAndroidX=true`。

### 坑 3：中文用户名导致单元测试 worker 加载失败（最严重）

**现象**：`assembleDebug` 成功，但 `testDebugUnitTest` 报
```
错误: 找不到或无法加载主类 worker.org.gradle.process.internal.worker.GradleWorkerMain
原因: java.lang.ClassNotFoundException: worker.org.gradle.process.internal.worker.GradleWorkerMain
```

**原因**：Windows 用户名是 `林泽羽`（含非 ASCII 字符）。Gradle 默认 `GRADLE_USER_HOME=C:\Users\林泽羽\.gradle`。Gradle 8.9 的 test worker 在 fork 测试 JVM 时，classpath 经过这个含中文的路径加载，classloader 失败。

**解决**：把 `GRADLE_USER_HOME` 设到纯 ASCII 路径 `D:/AndroidDev/gradle-home`，并重新下载依赖（首次 `assembleDebug` 会重下完整依赖树，约几分钟）。

> 注意：每次开新 shell 都要重新 `export GRADLE_USER_HOME="D:/AndroidDev/gradle-home"`，否则 Gradle 会回退到默认中文路径。建议写进 shell profile 或用 IDE 的 Gradle 设置。

## 验证构建

```bash
export JAVA_HOME="/d/AndroidDev/jdk-17.0.19+10"
export ANDROID_HOME="/d/AndroidDev/sdk"
export ANDROID_SDK_ROOT="/d/AndroidDev/sdk"
export PATH="$JAVA_HOME/bin:$PATH"
export GRADLE_USER_HOME="D:/AndroidDev/gradle-home"

./gradlew assembleDebug          # 应输出 BUILD SUCCESSFUL
./gradlew testDebugUnitTest       # 应输出 BUILD SUCCESSFUL，5 个测试通过
```

Debug APK：`app/build/outputs/apk/debug/app-debug.apk`（约 16 MB）。

## 真机安装（待设备清单就绪）

```bash
adb install -r app/build/outputs/apk/debug/app-debug.apk
```

目标机型清单（计划书 §15.4）待项目负责人补充主展示机、备用机、低配机的品牌型号后，再固化 ABI 与 minSdk 实测。
