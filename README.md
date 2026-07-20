# 红色电波 AR（red-wave-ar）

《永不消逝的红色电波》AR 触发式移动端 VR 研学应用。

**产品形态**：识别入口（二维码 / 触发图 / 手动列表）只负责返回 `scene_id`；识别成功后释放相机与 ARCore Session，进入纯虚拟移动端 VR（Filament 渲染 + 手机姿态环视 + 摇杆/热点移动 + 文物交互 + 音频）。

> 边界（计划书 §1.2）：本项目**不**实现“3D 模型持续锚定在现实空间”。ARCore Pose、Anchor、平面检测、现实相机帧**不会**带入虚拟展馆。

单一事实来源：[`红色电波AR产品计划书.md`](红色电波AR产品计划书.md)。

---

## 技术栈

- Kotlin 2.0.20 + Jetpack Compose（BOM 2024.09.02）
- Android Gradle Plugin 8.5.2 / Gradle 8.9
- 最低 Android 8.0（API 26），AR Optional
- 固定横屏（MVP）
- kotlinx.serialization 1.7.3（数据契约）
- 测试：JUnit 4 + Truth + Robolectric

依赖版本集中在 [`gradle/libs.versions.toml`](gradle/libs.versions.toml)（计划书 §3.5：M1 后固定版本）。

---

## 构建环境

本仓库使用 Gradle Wrapper，无需系统级 Gradle。需要的只是：

1. **JDK 17**（设置 `JAVA_HOME`）
2. **Android SDK**（API 34 + Build-Tools 34.0.0 + platform-tools）

### Windows（本机已配置的路径）

工具链装在 `D:\AndroidDev`：

```
JAVA_HOME        = D:\AndroidDev\jdk-17.0.19+10
ANDROID_HOME     = D:\AndroidDev\sdk
ANDROID_SDK_ROOT = D:\AndroidDev\sdk
GRADLE_USER_HOME = D:\AndroidDev\gradle-home   # 必须是纯 ASCII 路径
```

> **重要**：`GRADLE_USER_HOME` 必须是纯 ASCII 路径。默认的 `C:\Users\<中文名>\.gradle` 在本机会让 Gradle 的 test worker（`GradleWorkerMain`）classloader 加载失败，导致单元测试无法运行。详细诊断见 [`docs/BUILD.md`](docs/BUILD.md)。

在 Git Bash 里设置环境：

```bash
export JAVA_HOME="/d/AndroidDev/jdk-17.0.19+10"
export ANDROID_HOME="/d/AndroidDev/sdk"
export ANDROID_SDK_ROOT="/d/AndroidDev/sdk"
export PATH="$JAVA_HOME/bin:$PATH"
export GRADLE_USER_HOME="D:/AndroidDev/gradle-home"
```

`app/local.properties`（不入库）：

```
sdk.dir=D:/AndroidDev/sdk
```

注意：路径用**正斜杠**。Java Properties 会吞掉反斜杠（`\A`、`\s` 被当转义），导致 AGP `SdkLocator` 报 “文件名、目录名或卷标语法不正确”。

---

## 构建命令

```bash
# 构建 Debug APK
./gradlew assembleDebug

# 运行单元测试
./gradlew testDebugUnitTest

# 构建 Release APK（CODE-11 会启用签名/R8）
./gradlew assembleRelease

# 清理
./gradlew clean
```

产物：`app/build/outputs/apk/debug/app-debug.apk`

---

## 当前进度

### CODE-00：工程与构建基线 ✅

- 单 Activity + Compose 骨架（计划书 §6.5）
- Version Catalog 集中版本管理（§3.5）
- Debug / Release 构建变体，`BuildConfig` 注入诊断与内容校验开关（§6.20、§5.6）
- 固定横屏（§2.3）、AR Optional（§6.4）
- 首页 UI 骨架 + 版本信息页
- 错误码表 `AppErrorCode` 与恢复文案 `AppErrorMessages`（§6.18，覆盖 UT-014）
- 单元测试基础设施就绪

### CODE-01：数据契约与资源仓库 ✅

- 三个 manifest data class（`GlobalManifest` / `SceneManifest` / `ContentManifest`），snake_case↔camelCase（§6.7）
- JSON 解析（kotlinx.serialization，§6.7）
- 路径安全 `ResourcePathSafety`：拒绝绝对路径 / 盘符 / UNC / `..` 穿越与控制字符（§5.6-4）
- `ManifestValidator`：Schema 字段约束（§5.5）+ 7 条跨文件校验（§5.6），Debug 宽松 / Release 严格
- `EntryResolver`：二维码 / 触发图 / 手动三入口映射，重复值判失败（§6.8）
- `ManifestRepository`：读取 + 解析 + 校验 + 资源存在性，错误码稳定为 `MANIFEST_INVALID`
- `AndroidAssetResourceRoot` / `FileResourceRoot`：assets 与已安装场景包的统一抽象
- S1 白盒 assets：`global_manifest.json` + 建模交付的 `scene.json` + `content.json`（文案取自 research/ draft，review_status=draft）+ 占位 thumbnail
- **45 个单元测试全部通过**，覆盖 UT-001~007、014 + 真实资源集成测试

**已知限制（CODE-00/01）**：
- 首页三个入口按钮（二维码/触发图/手动）当前不跳转，逻辑在 CODE-08/09/10 接入。
- 未接入 Filament、ARCore、Media3、ZXing（后续 CODE 任务）。
- Release 变体未启用 minify 与签名（CODE-11）。
- content.json 文案为 draft，音频文件未制作（CODE-07），白盒阶段软检查。
- 目标机型清单待用户提供（计划书 §15.4、§6.4），ABI 暂按通用 arm64-v8a + armeabi-v7a。

---

## 目录结构

```
red-wave-ar/
├── app/
│   ├── build.gradle.kts
│   ├── proguard-rules.pro
│   └── src/
│       ├── main/
│       │   ├── AndroidManifest.xml
│       │   ├── assets/                       # §5.1 运行时资产
│       │   │   ├── global_manifest.json
│       │   │   └── scenes/scene_S1/
│       │   │       ├── scene.json            # 建模白盒交付
│       │   │       ├── content.json          # research/ draft 文案
│       │   │       ├── environment_whitebox.glb
│       │   │       ├── props/*.glb
│       │   │       └── thumbnail.png         # 占位
│       │   ├── java/cn/bistu/redwave/
│       │   │   ├── MainActivity.kt
│       │   │   ├── AppErrorCode.kt           # §6.18 错误码
│       │   │   ├── AppErrorMessages.kt       # §6.18 恢复文案
│       │   │   ├── SceneCoreTypes.kt         # EntrySource / SensorMode / EntryResult
│       │   │   ├── SceneUiState.kt           # §3.4 状态机
│       │   │   ├── data/                     # CODE-01 数据契约
│       │   │   │   ├── ManifestModels.kt     # §5.4/§6.7 三 manifest data class
│       │   │   │   ├── ManifestJson.kt       # JSON 解析
│       │   │   │   ├── ManifestValidator.kt  # §5.5/§5.6 校验
│       │   │   │   ├── ResourcePathSafety.kt # §5.6-4 路径安全
│       │   │   │   ├── EntryResolver.kt      # §6.8 入口映射
│       │   │   │   ├── ManifestRepository.kt # 资源仓库
│       │   │   │   └── AssetResourceRoot.kt  # 资源根抽象
│       │   │   └── ui/
│       │   └── res/
│       └── test/java/cn/bistu/redwave/
│           ├── AppErrorCodeCoverageTest.kt
│           └── data/                         # CODE-01 测试 (UT-001~007,014)
├── gradle/
│   ├── libs.versions.toml
│   └── wrapper/
├── settings.gradle.kts
├── build.gradle.kts
├── gradle.properties
├── gradlew / gradlew.bat
└── 红色电波AR产品计划书.md
```

## 许可

见最终发布的 `THIRD_PARTY_NOTICES.md`（CODE-11 交付）。
