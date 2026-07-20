# S1 建模交付 CHANGELOG

格式：日期 ｜ 任务卡 ｜ 变更内容 ｜ 状态

## 2026-07-20 ｜ M3D-00 ｜ 参考资料与比例审计

- 建立 `modeling_delivery/S1/` 交付目录骨架（runtime / source / preview / references，按 §5.11）。
- 完成当时仓库状态的参考审计：当时仅有计划书 v1.2 与立项申报书（背景），尚无统一建模输入包；该历史结论已被本文件后续“统一建模输入包就位”记录替代。
- 输出 `references/index.md`（参考索引 + 逐资产状态表）、`open_questions.md`（23 条待确认问题，含阻塞分级）、`asset_priority.md`（优先级确认表）。
- 结论：M3D-02/M3D-03 阻塞，等待资料负责人交付并经项目负责人确认的 S1 资料包；M3D-01 白盒待 scene_seed 临时种子确认后启动。
- 状态：✅ M3D-00 审计交付完成（完成标准本身未满足，缺失项已全部登记为阻塞，未虚构任何参考）。

## 2026-07-20 ｜ M3D-01 ｜ S1 白盒场景与占位文物（v0.1，待真机联调）

**依据**：技术负责人 2026-07-20 批准以计划书 §4.4/§5.4 取值 + 资料包 `modeling_brief.md` §8 作为白盒临时种子；资料包状态 `WHITEBOX_ALLOWED / FORMAL_ASSET_BLOCKED`。

**交付物**（`modeling_delivery/S1/`）：

| 文件 | 说明 |
|---|---|
| `runtime/environment_whitebox.glb` | 8.0×8.0×2.6 m 房间（产品白盒尺度，非历史尺寸）：外壳、南墙入口框+关闭门扇、北墙信息面（导览蓝）、电台桌+木凳、木箱×3、吊灯+桌灯占位；552 tris / 2 材质 |
| `runtime/props/radio_station_whitebox.glb` | `p_s1_radio` 占位：主箱体+辅助箱体，无铭文；24 tris |
| `runtime/props/telegraph_key_whitebox.glb` | `p_s1_key` 占位：通用直键；`key_lever` 独立节点位于枢轴 `[0,0.042,0.035]`，供后续 interact 动画；168 tris |
| `runtime/props/code_book_whitebox.glb` | `p_s1_codebook` 无纹理合拢占位（FINAL_MODEL_BLOCKED）；36 tris |
| `runtime/scene.json` | schema_version 1；起点 `[0,1.6,3.0]`；bounds ±3.6 m；7 个 AABB collider；2 个 move point；3 个 prop 配置 |
| `preview/scene_overview.png` | 轴测剖切 + collider 线框 + 起点/move point 标记 + 尺寸标注 |
| `preview/visitor_start.png` | 起点第一人称软件渲染近似 |
| `preview/props_contact_sheet.png` | 三占位文物正面/侧面/背面/线框 |
| `asset_report.csv` | 逐 GLB 统计（含尺寸列） |
| `source/whitebox/*.py` | 参数化生成器（布局唯一事实源 `layout_s1.py`）、校验器、预览渲染器 |

**校验**：
- Khronos glTF-Validator 2.0.0-dev.3.10：4 个 GLB 全部 **0 errors / 0 warnings**。
- 仓库内结构自检 `check_glb.py`：PASS（坐标系/单位/原点/命名/无贴图/单位缩放）。
- `scene.json` 契约交叉检查：PASS（起点与 move point 在 bounds 内、不落入 collider；起点→电台 1.50 m 满足 §4.3 首目标 <2 m；三文物均在 mp_radio 交互半径内）。

**与计划书 §5.4 示例的有意偏差**（详见 open_questions.md 更新）：
1. 电台桌移到起点前方 1.5 m 处（示例坐标首目标距起点 4.1 m，不满足 §4.3 的 2 m 规则）。
2. movement bounds 收紧为 ±3.6 m（8 m 房间内壁 − 0.25 m 游客半径余量；示例 ±5 m 超出房间）。
3. `visitor_start.rotation_deg` 取 `[0,0,0]`（按「-Z 朝前」零旋转即朝电台桌）；§5.4 示例 `[0,180,0]` 与此不一致 → OQ-I-04 待编码联调确认。

**合规**：无任何铭文/徽标/序列号/地图文本/档案内容；无贴图（textures=0）；密码本仅无纹理占位；碰撞只在 scene.json，未进入渲染 GLB；白盒三色区分环境/可交互/导览（资料包 §4.1）。

**已知问题**：
1. 预览图为软件渲染示意，真实材质/光照以 Filament 真机为准。
2. visitor_start 视角中木凳可能被视锥下缘裁切（视角俯仰待联调标定）。
3. 所有坐标为临时值，未通过真机联调前不得冻结；正式 `environment.glb` 须保持同一坐标与碰撞基准（资料包 §7）。

**状态**：⏸ 按资料包 §8 在此停止，等待：① 编码模型真机联调反馈；② 项目负责人对资料包 Q-001/002/003 的审核结论。未通过真机联调，白盒不标记为完成。

## 2026-07-20 ｜ M3D-01 ｜ 白盒 v0.2：对齐冻结风格板

**触发**：资料侧提交 `style_reference_board.md`（`VISUAL_DIRECTION_FROZEN_FOR_NEXT_ASSET_PASS`）与 modeling_brief §6.1 硬约束（commit 305a52d）。

**变更**（仅一处几何，其余不变）：
- 电台桌占位由 1.60×0.70×0.78 m 调整为风格板 §6 ZONE-B 冻结基准 **1.80×0.75×0.78 m**，桌面中心不变；`desk_radio` collider 同步更新为 `[-0.1,0,1.125]–[1.7,0.78,1.875]`；桌腿位置随动。
- 文物摆位、起点、bounds、move points、门/信息面/木箱/灯具均不变（风格板 §9-1：不因风格板重做已验证布局）。

**对齐核对**（风格板白盒相关条款）：
- 三层结构在构图上可读：入口框（地域层）+ 电台桌操作组（行动层）+ 信息面（现代解释层）✓
- 起点中央 40% 可见电台操作组；radio/key/codebook 轮廓互不遮挡 ✓（见重渲 visitor_start.png）
- 主通道净宽 ≥1.2 m（桌旁最窄处 2.3 m）✓ 无台阶/高差 ✓ 无贴脸悬挂物（吊灯底 2.05 m 高于视线）✓
- 拾取射线无遮挡 ✓ 信息中心高度 1.5 m 在 1.2–1.8 m 带内 ✓

**校验**：Khronos glTF-Validator 0 错 0 警（4/4）；check_glb PASS；scene.json 交叉检查 PASS（含文物落桌足迹检查）；visitor→radio 仍 1.50 m。

**下一步（不变）**：真机联调 → 白盒验收 → 按风格板 §10 出 STYLE-01/02/03 三张审核图 → 用户审核后才进入中模。

## 2026-07-20 ｜ M3D-00 同步 ｜ 统一建模输入包就位

- `modeling_input/S1/` 已建立，入口为 `00_START_HERE.md`，并提供全量 `package_manifest.csv`。
- 用户审核、建模交接、素材说明、素材清单和两张本地参考图统一收口；原图由 Git 忽略，不进入远程仓库。
- 重写 `references/index.md`、`open_questions.md` 和 `asset_priority.md`，删除“输入包不存在”“用户决策未确认”等已过期口径。
- 当前正式状态：允许白盒审核和 STYLE-01/02/03；具体电台/发报键、精确建筑、路线、人物和图片发布继续保持阻塞。

## 2026-07-20 ｜ M3D-01 审核轮 ｜ 白盒审核 + STYLE-01/02/03 风格图（按交接闸门停止）

**依据**：`modeling_input/S1/02_MODELING_HANDOFF.md`（状态 READY_FOR_WHITEBOX_REVIEW_AND_STYLE_FRAMES）§3–§5；本轮只做白盒审核与三张简单材质风格图，不改 scene.json 数据契约与运行时 GLB。

**白盒审核**：新增 `source/whitebox/whitebox_selfcheck.py` 数值自检——**25 PASS / 8 WARN / 0 FAIL**（单位比例、起点净空、起点→radio 视线、点击带 1.0–2.5 m、通道 ≥1.2 m、文物落桌、碰撞仅在 scene.json）；Khronos 校验器复核 4 个 GLB 0 错 0 警；`layout_s1.py` 与 scene.json 一致。8 条 WARN 全部列为决策项（见 style_review_report §1.2 W1–W6），其中 W5 桌区位置/W6 门位置与 `scene_layout_brief` PROPOSED 坐标存在差异，按交接 §6 保持现状并上报，不静默处理。

**风格图**：新增 `source/whitebox/render_style_frames.py`（numpy 软件渲染；0.5 m 面细分修正画家算法；自发光信息层最后绘制；程序色板 + 冷暖三层灯光近似），输出 `preview/style/` 六图（1600×900 + 1280×720 各自重渲，未拉伸）：
- `STYLE-01_visitor_start.png`：起点第一眼暖光电台桌 + 背景灰蓝信息层边缘；
- `STYLE-02_operator_45deg.png`：radio/key/资料包轮廓互不遮挡；
- `STYLE-03_route_to_entry.png`：历史层（灰砖/粗石/旧木/暗红门框）与灰蓝信息层分离；含一个**预览候选元素**（导览蓝地点卡，不在运行时 GLB/scene.json，报告中已声明 D-02）。

**测量结论**（style_review_report §4）：红色面积 0.00%/0.00%/0.11%（≤8–12%）；三图最亮格均为桌面格（暖光第一焦点）；暗部 p02 明度 0.109–0.134 无纯黑。第三方资产：无。

**上报决策项**（需用户/项目负责人定夺，详见报告 §1.2/§4/§6）：W1 起点 yaw 基准（OQ-I-04）、W5 桌区位置（现行 vs 布局任务书 PROPOSED，含计划书 §4.3「2 m 首目标」与任务书 3.5–4.5 m 张力）、W6+D-01 门位置导致 STYLE-01 无入口意象、W3/W4 信息面宽度与薄 collider、D-02 地点卡是否补入白盒。

**状态**：⏸ 按交接 §5 停止。三张图 + `style_review_report.md` 已交付，等待用户审核与资料复核；未自动进入中模/正式环境。白盒仍未通过真机联调，不标记为完成。
