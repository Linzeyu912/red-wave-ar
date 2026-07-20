# S1 建模交付 CHANGELOG

格式：日期 ｜ 任务卡 ｜ 变更内容 ｜ 状态

## 2026-07-20 ｜ M3D-00 ｜ 参考资料与比例审计

- 建立 `modeling_delivery/S1/` 交付目录骨架（runtime / source / preview / references，按 §5.11）。
- 完成参考审计：现有资料仅计划书 v1.2 与立项申报书（背景）；`modeling_input/S1/` 资料包未交付，文物与环境参考图为 0。
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
