# ADR-0002：屏幕方向从固定横屏改为跟随传感器

- **状态**：Accepted
- **日期**：2026-07-22
- **决策者**：项目负责人（李雨霏）确认
- **影响范围**：计划书 §2.3、§6.16、AndroidManifest、VR HUD 布局

## 背景

计划书 §2.3 规定「MVP 全应用固定横屏」。实际在主展示机 nubia Z70 Ultra 上发现：
- 曲面屏边缘 + 强制横屏（sensorLandscape）导致 VR HUD 左上角三个按钮（返回/回正/切陀螺仪）被曲面区和状态栏遮挡；
- 竖屏完全不可用，限制了使用姿势（如手持单手操作、桌面支架竖放）。

## 决定

将屏幕方向从 `sensorLandscape`（强制横屏）改为 `fullSensor`（跟随重力传感器，横竖均可）。VR 推荐横屏但不强制。

## 影响

- `AndroidManifest.xml`：`screenOrientation="fullSensor"`，保留 `configChanges`（旋转不重建 Activity）。
- `VrSceneScreen`：HUD 按钮加 `statusBarsPadding` + `displayCutoutPadding` 避开安全区；旋转时重新配置 Filament 视口/投影 + 更新传感器 `screenRotationDeg`（§6.12-2 屏幕方向补偿）。
- `InfoSheet`：底部信息卡加 `navigationBarsPadding` + `displayCutoutPadding`。
- 计划书 §2.3 的「固定横屏」约定调整为「可旋转，VR 推荐横屏但不强制」。

## 不变

- Filament 渲染、传感器 yaw 算法、移动/碰撞/拾取逻辑不受屏幕方向影响（已与方向解耦）。
- 入口边界（scene_id → 释放相机 → 纯虚拟 VR）不变。

## 回滚

改回 `sensorOrientation="sensorLandscape"` 并移除安全区 padding 即可恢复固定横屏。
