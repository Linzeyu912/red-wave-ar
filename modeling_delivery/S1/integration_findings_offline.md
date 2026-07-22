# S1 白盒联调离线结论（编码侧）

> 日期：2026-07-22 ｜ 编码侧：林泽羽 ｜ 适用提交：`6897a2f`
> 真机联调因网络隔离阻塞（见下），以下为**可离线确认的项**；需真机的项标注为待验。

## WR-1 / OQ-I-04：yaw 基准（可离线确认 ✅）

**结论：yaw 基准正确，无需修正。**

链路验证（纯向量计算，不依赖真机）：

1. `visitor_start.rotation_deg = [0,0,0]` → 初始姿态四元数 = IDENTITY
2. `OrientationMath.forwardVector(IDENTITY)` = (0, 0, **-1**) → 朝 -Z
3. Filament `Camera.lookAt(eye, eye+forward, up)`：eye=[0,1.55,1.65], forward=(0,0,-1) → center=[0,1.55,0.65] → 朝 -Z
4. scene.json：游客 z=1.65，电台 z=0.04 → 电台在游客 -Z 方向 → **游客正面面向电台** ✅
5. radio `rotation_deg=[0,180,0]`：电台 yaw 180°，控制面（表窗+旋钮）朝 +Z → **朝向游客** ✅

约定一致性：
- 建模约定「零旋转 = -Z 朝前」（integration_checklist §1）
- 编码 `forwardVector` 取 R(q)·(0,0,-1)，yaw 正方向绕 +Y 逆时针（右手系）
- 两者一致，WR-1 **关闭**。

## 游客起点不落入 collider（可离线确认 ✅）

起点 [0, 1.55, 1.65]，圆形代理半径 0.25m：
- bounds x∈[-2.25,2.25] z∈[-1.95,1.95]：起点 x=0∈bounds, z=1.65∈bounds ✅
- 8 个 collider 逐一检查：起点 (0,1.65) 不落入任一 AABB（最近的 desk_radio z∈[-0.275,0.475]，起点 z=1.65 远在其外）✅

## move_points 不落入 collider（可离线确认 ✅）

- mp_radio [0.75, 0.95]：desk_radio z∈[-0.275,0.475]，mp z=0.95 在其外 ✅
- mp_guide [-1.5, 1.15]：wall_west x∈[-2.9,-2.65]，mp x=-1.5 在其外 ✅

## 待真机验证的项（阻塞：网络隔离）

| 项 | 原因 |
|---|---|
| 4 个 GLB 实际渲染（朝向/比例/材质） | 需真机 Filament 实测 |
| 陀螺仪 yaw 手感（真机传感器数据） | 需真机 TYPE_GAME_ROTATION_VECTOR |
| 触屏/陀螺仪切换无跳变 | 需真机操作 |
| 8 个 collider 实际碰撞手感 | 需真机走动 |
| 三文物拾取 + 高亮锚点位置 | 需真机 View.pick |
| QR 入口后相机释放 | 需真机摄像头 |
| 帧率（计划书 §6.4 ≥30FPS） | 需真机 Release 构建 |
| 进入/退出 20 次内存不增长 | 需真机循环 |

## 真机连接阻塞说明

- 主展示机 nubia Z70 Ultra (NX736J, Android 15) USB ADB：Windows 识别到 ADB Interface（VID_19D2 PID_0306 MI_01, SubClass_42 Prot_01 = ADB 协议），但 adb 在 USB/libusb 两种后端下均枚举不到（驱动绑定问题）。
- 无线调试：电脑(10.153.203.x)与手机(10.153.191.x)被网关 AP isolation 隔离，无法互通。
- 解除阻塞需：手机与电脑连同一不隔离子网（如手机热点），或解决 USB 驱动。
