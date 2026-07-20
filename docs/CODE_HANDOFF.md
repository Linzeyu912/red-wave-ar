# 编码侧交接：S1 真机联调前收口

> 交接日期：2026-07-20
> 当前主分支基线：`f816ba9`（交接提交前的冻结状态）
> 当前状态：**暂停开发；建模白盒已冻结，等待编码侧完成打包资产同步、CODE-10 和真机联调。**

## 1. 本次会话已完成的只读核对

- 已完整阅读 S1 真机联调清单：`modeling_delivery/S1/integration_checklist.md`；
- 已阅读 Android 入口、渲染、GLB 加载、姿态、移动、拾取、音频、二维码及状态机代码；
- 已运行基线测试：

  ```powershell
  $env:JAVA_HOME='D:\AndroidDev\jdk-17.0.19+10'
  $env:ANDROID_HOME='D:\AndroidDev\sdk'
  $env:ANDROID_SDK_ROOT='D:\AndroidDev\sdk'
  $env:GRADLE_USER_HOME='D:\AndroidDev\gradle-home'
  .\gradlew.bat testDebugUnitTest
  ```

  结果：`BUILD SUCCESSFUL`，本次会话未修改任何 Kotlin、GLB、JSON 或 App 资产。

## 2. 已冻结、不得直接修改的建模基准

建模侧最终白盒/风格审核冻结提交：

- `8062c0c`：紧凑地下储洞小室 + 审核级 radio；
- `d0341c1`：全画幅无烧字 STYLE 图；
- `f816ba9`：记录用户审核通过，等待真机联调。

当前 S1 基准是原创地下储洞门内小室：约 `5.3 × 4.7 × 2.25 m`；首个目标是面向游客的 `p_s1_radio`。运行时坐标唯一事实源是：

`modeling_delivery/S1/runtime/scene.json`

除非真机联调给出明确复现证据，否则不得改动该目录下的 GLB、坐标、碰撞、相机构图或文物 ID。任何建议修改必须先记录为联调结论，再交回建模侧处理。

## 3. 第一优先级阻塞：Android 包内 S1 资产仍是旧版

Android 实际从 `app/src/main/assets/scenes/scene_S1/` 加载资产，但该目录仍是旧的 8 m × 8 m 版本：

| 文件 | 建模冻结版 | 当前 App 包内版本 | 结论 |
|---|---:|---:|---|
| `scene.json` | 3485 bytes，SHA-256 `DB82CDAA…` | 3270 bytes，SHA-256 `374F867D…` | 不一致 |
| `environment_whitebox.glb` | 49744 bytes | 47768 bytes | 不一致 |
| `props/radio_station_whitebox.glb` | 126352 bytes | 3032 bytes | 不一致 |
| `props/code_book_whitebox.glb` | 4392 bytes | 4392 bytes | 当前一致 |
| `props/telegraph_key_whitebox.glb` | 10612 bytes | 10612 bytes | 当前一致 |

下一位编码模型必须先完成“打包资产同步”并添加自动防护：

1. 以 `modeling_delivery/S1/runtime/` 为源，将冻结的环境、文物 GLB 和 `scene.json` 同步到 APK 的 S1 assets；
2. 在 Gradle 构建前增加校验任务，确保包内运行时文件与建模冻结源逐字节一致；
3. 不修改 `modeling_delivery/S1/runtime/` 中的任何内容；
4. 用资产集成测试和 Debug APK 验证实际加载的是紧凑小室，不是旧 8 m × 8 m 版本。

## 4. 紧随其后的 CODE-10 范围

CODE-00 至 CODE-08 已有基础实现；CODE-09 已由 `docs/decisions/ADR-0001-archive-image-trigger-entry.md` 正式归档。下一步是 CODE-10（完整 UI 与错误恢复），优先补齐以下缺口：

1. `RedWaveApp` 已保存二维码解析出的 `resolvedSceneId`，但没有传入 `VrPlaceholderScreen`；`loadSceneS1Whitebox()` 仍把 `"S1"` 写死；必须改为传递已解析的 `scene_id`。
2. 首页“手动选择场景”目前只在 Debug 中直接进入 S1；要改为基于 `global_manifest.json` 的正式场景列表，并只输出 `EntryResult(sceneId, EntrySource.MANUAL)`。
3. VR 页需要可见的返回首页、视角回正、陀螺仪/触屏切换和 Loading 取消入口；不能让用户困在渲染页。
4. `SceneUiState` 已定义 `Home / Scanning / Loading / Exploring / Error`，但尚未成为统一协调器；实现时用它避免 UI 直接耦合 QR、Filament、音频和传感器生命周期。
5. 所有错误继续经 `AppErrorCode` 和 `AppErrorMessages` 映射；相机拒绝、资源无效、GLB 加载失败和音频失败都必须有可执行的返回/重试/手动入口。

保持边界：二维码/手动入口只产生 `scene_id`，成功进入 VR 前相机已释放；不得重新引入 ARCore 图像识别、Anchor、Pose 或现实相机画面。

## 5. 真机联调顺序（CODE-10 完成后）

严格按 `modeling_delivery/S1/integration_checklist.md`：

1. 加载 4 个 GLB，确认启动后第一眼看到电台控制面；
2. 确认 `visitor_start.rotation_deg = [0,0,0]` 与真实 Filament yaw 方向，关闭/记录 WR-1；
3. 验证移动 bounds、8 个 collider、门洞、桌体和导览牌；
4. 验证三件文物拾取、距离半径和高亮锚点；
5. 验证二维码成功后相机释放、返回后相机/渲染/音频/传感器生命周期正确；
6. 记录设备型号、Android 版本、帧率、错误码和复现步骤；没有真实设备时不能标记“真机通过”。

## 6. 明日继续工作的推荐提示词

```text
继续 red-wave-ar 的编码工作。先完整阅读 docs/CODE_HANDOFF.md、modeling_delivery/S1/integration_checklist.md、modeling_delivery/S1/runtime/scene.json、红色电波AR产品计划书.md 的 CODE-10 和真机验收部分。

先完成“Android S1 打包资产同步与构建前一致性校验”：以 modeling_delivery/S1/runtime/ 为唯一模型源，确保 app 包内实际加载紧凑地下储洞小室的 scene.json、environment_whitebox.glb 与 radio_station_whitebox.glb；不得修改建模源文件。写自动测试/Gradle 校验，并运行构建和单元测试。

资产同步验证通过后，再实现 CODE-10：scene_id 端到端传递、正式手动场景列表、VR 返回/回正/输入模式切换、Loading 取消和错误恢复。不要重启 ARCore 识图；二维码与手动入口只输出 scene_id。每一步先说明准备修改的文件，完成后构建、测试、提交并推送 main。
```
