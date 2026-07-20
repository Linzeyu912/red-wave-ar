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

### CODE-02：Filament Host ✅

- Filament 1.56.0（filament-android + gltfio-android + filament-utils-android，固定版本）
- `FilamentHost`：Engine/Renderer/Scene/View/Camera/SwapChain 生命周期，创建销毁顺序固定（§6.10）
- `SceneRenderer`：Choreographer 帧循环，dt 截断（§6.13），Surface 不可用/后台不提交帧（§6.10）
- `FilamentSurfaceView`：专用渲染线程，Surface 生命周期→SwapChain，前后台暂停/恢复
- `MainActivity.onCreate` 显式 `Filament.init()` + `Gltfio.init()` 加载 native lib
- **模拟器验证通过**：Engine 创建成功（OpenGL 后端）、渲染页运行、前后台切换无崩溃

### CODE-03：GLB 场景加载与释放 ✅

- `GltfAssetStore`（render/asset）：AssetLoader + UbershaderProvider + ResourceLoader 生命周期，GLB 字节加载，entity→propId 映射（CODE-06 拾取用），显式释放（§6.10、§6.21）
- `SceneAssetLoader`：单场景加载状态机（Idle→Loading→Ready/Failed），环境致命/P2 文物可降级，进度按 §6.11 权重（配置10%+环境40%+文物35%+资源15%），场景 token 防旧回调（§6.14）
- `TransformMath`：scene.json 的 position/rotation_deg/scale → 4x4 行主序矩阵（§5.2、§5.5）
- 接入渲染页：ManifestRepository 读 scene.json → SceneAssetLoader 加载 S1 白盒（environment + 3 文物）→ attach + transform
- **模拟器验证通过**：状态显示"就绪：资产已加载"，6 次进出渲染页无崩溃、内存无单调增长（§6.21）
- 56 个单元测试通过（含 TransformMath 矩阵转换 7 项）

### CODE-04：姿态与触屏相机 ✅

- `Quaternion` + `slerp` + `smoothingAlpha`：纯四元数运算（单位四元数、逆、乘积、球面插值、与帧率无关平滑系数）
- `OrientationMath`（§6.12 算法规格）：
  - TYPE_GAME_ROTATION_VECTOR → 四元数（§6.12-1）
  - 屏幕方向重映射（§6.12-2，ROTATION_0/90/180/270）
  - 回正 q_relative = inverse(q_reference)*q_screen（§6.12-3/4，UT-008）
  - 默认去 roll，只保留 yaw/pitch（§6.12-5）
  - slerp 平滑 alpha=1-exp(-dt/tau)，tau=0.12（§6.12-6）
  - 触屏 pitch 限幅 ±80°（§6.12，UT-009）
  - yaw/pitch 提取用旋转矩阵 forward 向量法（避免象限歧义）
  - lookAtParams：四元数+眼点 → Filament Camera.lookAt 9 参数
- `OrientationController`：SensorManager 桥接，陀螺仪/触屏双模式，切换不跳变，无传感器降级触屏（§6.18 SENSOR_UNAVAILABLE）
- 渲染页接入：触屏拖动改 yaw/pitch，每帧 onUpdateOrientation 写相机朝向
- **69 个单元测试通过**（+13 姿态算法：四元数、回正、去roll、pitch限幅、slerp、屏幕补偿、平滑收敛）
- 模拟器验证：渲染页运行、App 不崩溃、Filament Engine 正常

### CODE-05：移动、碰撞与热点 ✅

- `MovementMath`（interaction，§6.13 纯数学）：摇杆死区、视线投影、bounds 钳制、AABB 分轴滑动（UT-010/011）
- `MovementController`：visitorPosition 维护，dt 上限防穿墙，热点 0.3s 淡入淡出
- 渲染页接入：相机位置由 MovementController 管理，左半屏摇杆/右半屏环视

### CODE-06：拾取、信息卡和高亮 ✅

- `PickingMath`（§6.14 纯逻辑）：触摸→viewport Y 翻转、距离判定、entity→propId 解析、UI 穿透
- `PickingController`：Scene token 防旧回调（UT-012）、interaction_radius_m 距离限制
- `InfoSheet` Compose 信息卡（§6.16）：标题、正文、来源、音频控制
- 渲染页接入：单击 View.pick，回调核对 token+距离，命中开信息卡

### CODE-07：内容绑定与单实例 Media3 音频 ✅

- Media3 1.4.1（1.7.0 要求 compileSdk 35+AGP 8.6，当前 AGP 8.5.2/SDK 34，用 1.4.1）
- `NarrationController`（§6.15）：全应用单实例 ExoPlayer
  - 打开新文物停止旧讲解从头播新音频（§6.15）
  - stop(reason)：SCENE_CHANGED/ERROR/SWITCHED 清空 MediaItem；CLOSED 暂停；TRANSIENT 焦点/耳机暂停
  - 音频焦点丢失暂停（AudioManager.requestAudioFocus）；耳机拔出暂停（ACTION_AUDIO_BECOMING_NOISY + ExoPlayer 内置）
  - 状态 StateFlow<NarrationState>：itemId/isPlaying/isReady/hasError/positionMs/durationMs
  - 不做后台播放与通知栏（§6.15 MVP）
- `AudioSource` 抽象：Asset（file:///android_asset/）/ File，UI 不关心 URI
- 渲染页接入：选中文物自动播放，信息卡音频控件接实际状态（播放/暂停/进度/时长），音频失败仍展示文字（§6.18）
- **103 个单元测试通过**（+5 音频源/状态契约，Robolectric）

### ADR-0001：归档 F2 触发图入口 ✅

- 主展示机不支持 ARCore → F2 归档，仅保留二维码（F1）+ 手动列表（F3）
- 不触及核心边界（入口仍只返回 scene_id）
- 见 `docs/decisions/ADR-0001-archive-image-trigger-entry.md`

### CODE-08：二维码入口 ✅

- ZXing Android Embedded 4.3.0（DecoratedBarcodeView 嵌入 Compose）
- `QrScannerController`（entry/qr）：decodeContinuous、结果去重（§6.8-3）、识别后冻结、手电筒接口
- `QrScanScreen`（ui/scan，§6.16 二维码页）：
  - CAMERA 权限请求，拒绝返回首页突出手动入口（§6.18 CAMERA_PERMISSION_DENIED，不循环弹框）
  - 扫描 payload → EntryResolver.resolveQr（CODE-01）
  - 未知码"不是本项目卡片，继续扫描"（§6.8-4，不把任意 URL 当 scene_id）
  - 识别成功冻结→释放相机→导航 VR（onResolved 只带 scene_id + EntrySource.QR，§6.8-6）
- 路由接入：首页"扫描二维码"→ QR_SCAN → VR

**已知限制（CODE-00..08）**：
- 首页"手动选择"按钮（Debug）直接进 VR；正式手动列表 CODE-10。
- 真实音频文件未制作；ExoPlayer 实际播放需真机音频资产。
- 二维码实际扫描需真机摄像头验证（模拟器无真实相机预览）。
- 拾取/移动/环视/音频视觉效果在 headless 模拟器无法可靠验证；算法已通过严格单元测试，待真机验收。
- Release 变体未启用 minify 与签名（CODE-11）。
- 目标机型：主展示机 nubia Z70 Ultra（NX736, Android 15）**不支持 ARCore**（F2 已归档）；备用/低配机待补充（见 docs/device_matrix.md）。

---

## 运行验证（模拟器）

本机已配置 Android 模拟器（AVD `redwave_test`，API 34，x86_64，SwiftShader 软件渲染）用于无真机时验证基础运行：

```bash
export ANDROID_HOME="/d/AndroidDev/sdk"
export PATH="/d/AndroidDev/sdk/platform-tools:$PATH"
# 启动模拟器（headless）
"$ANDROID_HOME/emulator/emulator.exe" -avd redwave_test -no-window -no-audio -gpu swiftshader_indirect &
adb wait-for-device && adb shell 'while [[ "$(getprop sys.boot_completed)" != "1" ]]; do sleep 2; done'
# 安装并启动
adb install -r app/build/outputs/apk/debug/app-debug.apk
adb shell am start -n cn.bistu.redwave/.MainActivity
# 查看渲染日志
adb logcat -d | grep -i filament
```

> 模拟器限制：无真实陀螺仪（CODE-04 姿态需真机）、无 ARCore（CODE-09 需真机）、SwiftShader 性能不代表真机帧率。计划书 §6.4 的性能指标以真机 Release 构建为准。

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
