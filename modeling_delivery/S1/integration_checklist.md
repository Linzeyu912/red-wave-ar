# S1 白盒真机联调核对清单（integration_checklist）

> 适用提交：`8062c0c` 及之后的 M3D-01R-P 呈现修订提交 ｜ scene_id：`S1` ｜ 阶段：白盒 + 风格审核（未进入 M3D-02/03）
> **`modeling_delivery/S1/runtime/scene.json` 是运行时坐标唯一事实源**；本清单只是其联调摘要，如有出入以 scene.json 为准。
> 坐标系：Y-up、右手系、-Z 朝前；单位：米；文物原点在底面中心；碰撞体只在 scene.json，不在渲染 GLB 内。

## 1. 起点与移动

- `visitor_start.position_m = [0.0, 1.55, 1.65]`（眼高 1.55 m）
- `visitor_start.rotation_deg = [0.0, 0.0, 0.0]`（零旋转，按 -Z 朝前即面向电台桌）
- `movement`：type=bounds，speed 1.2 m/s，x ∈ [-2.25, 2.25]，z ∈ [-1.95, 1.95]

## 2. 碰撞体（8 个 AABB，min_m → max_m）

| id | min_m | max_m |
|---|---|---|
| wall_north | [-2.9, 0.0, -2.6] | [2.9, 2.25, -2.35] |
| wall_south | [-2.9, 0.0, 2.35] | [2.9, 2.25, 2.6] |
| wall_east | [2.65, 0.0, -2.35] | [2.9, 2.25, 2.35] |
| wall_west | [-2.9, 0.0, -2.35] | [-2.65, 2.25, 2.35] |
| desk_radio | [-0.9, 0.0, -0.275] | [0.9, 0.78, 0.475] |
| stool | [0.09, 0.0, -0.91] | [0.51, 0.45, -0.49] |
| crate | [1.65, 0.0, -2.1] | [2.25, 0.42, -1.6] |
| guide_plate | [-2.66, 1.1, 1.5] | [-2.6, 1.75, 2.2] |

## 3. 文物（props）

| id | glb（runtime/ 下） | position_m | rotation_deg | interaction_radius_m | highlight_anchor_m（局部） |
|---|---|---|---|---|---|
| p_s1_radio | props/radio_station_whitebox.glb | [0.32, 0.78, 0.04] | [0, 180, 0] | 1.8 | [0.0, 0.15, -0.1] |
| p_s1_key | props/telegraph_key_whitebox.glb | [-0.34, 0.78, 0.34] | [0, 0, 0] | 1.6 | [0.0, 0.12, 0.0] |
| p_s1_codebook | props/code_book_whitebox.glb | [-0.58, 0.78, -0.1] | [0, 0, 0] | 1.9 | [0.0, 0.1, 0.0] |

- 环境：`environment_glb = environment_whitebox.glb`（原点即场景原点，无需额外变换）。
- radio yaw 180° 使倾斜控制面（表窗+旋钮）朝 +Z 即朝游客；highlight_anchor 为局部坐标，随 yaw 变换。

## 4. 移动观察点（move_points）

| id | position_m | look_at_m | 用途 |
|---|---|---|---|
| mp_radio | [0.75, 1.55, 0.95] | [0.32, 1.0, 0.04] | 电台近看检查点（距 radio 1.01 m） |
| mp_guide | [-1.5, 1.55, 1.15] | [-2.63, 1.42, 1.85] | 西墙导览牌观察点 |

## 5. 推荐真机测试顺序

1. 加载 environment_whitebox.glb + 三个 props GLB，核对 4 个 GLB 单位/朝向/原点（Filament 目视 + Khronos 已 0 错 0 警）。
2. 放置 visitor_start，第一眼应看到暖光电台桌与电台控制面（首目标水平距 1.64 m < 2 m）。
3. 启用 bounds 行走：x/z 四向触界应被拦停；起点与两个 move point 均不落入任何 collider。
4. 逐一撞测 8 个 collider（重点：desk_radio 四周、门洞两侧 wall_south 段、guide_plate 薄板）。
5. 在 visitor_start 与 mp_radio 分别对三件文物做拾取（点击带 1.0–2.5 m、各 interaction_radius 内），核对高亮锚点落在文物本体上。
6. 走 mp_radio → mp_guide → 门洞回望路线，确认视线无穿模、无碰撞卡死。
7. 记录帧率与手感，回填联调结论到 open_questions.md（OQ-I-03）。

## 6. 唯一待确认项

- **WR-1（OQ-I-04）**：`visitor_start.rotation_deg = [0,0,0]` 约定零旋转即朝 -Z；radio 首次实际使用 yaw 180°。请编码侧确认真机引擎 yaw 正方向与本约定一致，若相反需统一口径后由建模侧调整（scene.json 会同步更新并保持唯一事实源）。

> 本清单对应白盒资产；真机联调通过前，白盒与电台均不标记为完成。
