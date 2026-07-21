# 编码侧交接：S1 真机联调前收口

> 交接更新：2026-07-21
> 建模冻结基线：`f816ba9` ｜ S1 资产同步：`37ceb02` ｜ CODE-10：与本交接更新同批提交
> 当前状态：**S1 打包资产同步与 CODE-10 已完成自动化/模拟器验证；建模白盒继续冻结，下一步是真机联调。**

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

## 3. 已解决：Android 包内 S1 资产同步

Android 实际从 `app/src/main/assets/scenes/scene_S1/` 加载资产；该目录现已与冻结源同步：

| 文件 | 建模冻结版 | 当前 App 包内版本 | 结论 |
|---|---:|---:|---|
| `scene.json` | 3485 bytes，`DB82CDAA…` | 3485 bytes，`DB82CDAA…` | 一致 |
| `environment_whitebox.glb` | 49744 bytes，`F9D96CD9…` | 49744 bytes，`F9D96CD9…` | 一致 |
| `props/radio_station_whitebox.glb` | 126352 bytes，`EDF99A72…` | 126352 bytes，`EDF99A72…` | 一致 |
| `props/code_book_whitebox.glb` | 4392 bytes，`AAFFF4BA…` | 4392 bytes，`AAFFF4BA…` | 一致 |
| `props/telegraph_key_whitebox.glb` | 10612 bytes，`F11628A9…` | 10612 bytes，`F11628A9…` | 一致 |

提交 `37ceb02` 已完成“打包资产同步”并添加自动防护：

1. 已将冻结的环境、三件文物 GLB 和 `scene.json` 同步到 APK 的 S1 assets；
2. `verifyS1RuntimeAssets` 已挂到 `preBuild`，逐字节核对冻结源；
3. 建模运行时源未修改；
4. 单元测试和 APK 内 SHA-256 均确认加载紧凑小室，不再是旧 8 m × 8 m 版本。

## 4. 已完成：CODE-10 范围

CODE-00 至 CODE-08 已有基础实现；CODE-09 已由 `docs/decisions/ADR-0001-archive-image-trigger-entry.md` 正式归档。CODE-10 已补齐：

1. `scene_id` 已从二维码/手动列表端到端传入 `VrSceneScreen`，加载器不再硬编码 S1；
2. 首页正式列表来自 `global_manifest.json`，手动入口只输出 `EntryResult(sceneId, MANUAL)`；
3. VR 页已有返回、回正、输入模式切换、Loading 进度和取消；
4. `SceneCoordinator` 已统一驱动 Home / Scanning / Loading / Exploring / Error / Diagnostics；
5. 错误页、诊断页和降级提示已接入 `AppErrorCode` / `AppErrorMessages`；未知二维码可恢复扫描，加载 30 秒超时。

验证结果：108 个单元测试、Debug Lint、Debug APK 构建通过；headless 模拟器已走通手动进入 S1、场景就绪、模式切换、回正和返回首页，未出现致命日志。模拟器结果不等于真机通过。

保持边界：二维码/手动入口只产生 `scene_id`，成功进入 VR 前相机已释放；不得重新引入 ARCore 图像识别、Anchor、Pose 或现实相机画面。

## 5. 真机联调顺序（CODE-10 完成后）

严格按 `modeling_delivery/S1/integration_checklist.md`：

1. 加载 4 个 GLB，确认启动后第一眼看到电台控制面；
2. 确认 `visitor_start.rotation_deg = [0,0,0]` 与真实 Filament yaw 方向，关闭/记录 WR-1；
3. 验证移动 bounds、8 个 collider、门洞、桌体和导览牌；
4. 验证三件文物拾取、距离半径和高亮锚点；
5. 验证二维码成功后相机释放、返回后相机/渲染/音频/传感器生命周期正确；
6. 记录设备型号、Android 版本、帧率、错误码和复现步骤；没有真实设备时不能标记“真机通过”。

## 6. 下一次继续工作的推荐提示词

```text
继续 red-wave-ar 的 S1 真机联调。先完整阅读 docs/CODE_HANDOFF.md 和 modeling_delivery/S1/integration_checklist.md，确认 main 工作区干净并重新运行 testDebugUnitTest、lintDebug、assembleDebug。

在 nubia Z70 Ultra 上安装 Debug APK，按清单逐项验证：二维码成功后相机释放、首帧面向电台控制面、visitor_start/yaw、陀螺仪与触屏切换/回正、bounds 与 8 个 collider、三件文物拾取和高亮、信息卡文字、返回首页后的渲染/音频/传感器释放。至少执行 20 次进入 S1→返回首页循环并记录设备、Android、帧率、错误码和复现步骤。

不得修改 modeling_delivery/S1/runtime/；若坐标或朝向有问题，只记录真机证据并回填 modeling_delivery/S1/open_questions.md，交由建模侧决定。不要重启 ARCore 识图。完成后提交并推送 main。
```
