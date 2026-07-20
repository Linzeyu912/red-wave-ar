# S1 建模参考资料索引

> 更新日期：2026-07-20
> 状态：`INPUT_PACKAGE_AVAILABLE / STYLE_FRAMES_ALLOWED / FORMAL_ASSETS_PARTIALLY_BLOCKED`
> 唯一输入入口：`modeling_input/S1/00_START_HERE.md`

## 1. 当前结论

`modeling_input/S1/` 已正式交付，不再使用早期“资料包不存在、参考图为 0”的审计结论。建模模型必须从统一入口读取产品、史实、风格、权利、用户图片和当前白盒索引。

当前允许：

- 审核白盒 v0.2；
- 制作 `STYLE-01/02/03` 三张简单材质风格图；
- 使用原创灰砖、石基、旧木、土色、低饱和军绿和灰蓝信息层；
- 观察两张本地用户图片并提取高层材料/空间关系。

当前不允许：

- 复制当前纪念馆门楼、牌匾、楹联、旗阵、栏杆、浮雕和展墙；
- 把用户原图导入 Blender、纹理、GLB、App 或 Git；
- 制作精确型号电台/发报键、真实人物、地图、铭文和档案内容；
- 自动进入完整中模、高模和正式材质。

## 2. 权威输入

| 编号 | 资料 | 路径 | 用途 | 状态 |
|---|---|---|---|---|
| REF-00 | 统一入口与全量清单 | `modeling_input/S1/00_START_HERE.md`、`package_manifest.csv` | 所有人从这里开始 | READY |
| REF-01 | 用户审核 | `modeling_input/S1/01_OWNER_REVIEW.md` | 图片来源、用途、识图和三图闸门 | OWNER REVIEW |
| REF-02 | 建模交接 | `modeling_input/S1/02_MODELING_HANDOFF.md` | 必读顺序、任务、输出、停止条件 | READY |
| REF-03 | 用户图片说明 | `modeling_input/S1/03_MATERIALS_GUIDE.md`、`material_manifest.csv` | 图片哈希、可用/禁用内容 | INTERNAL ONLY |
| REF-04 | 产品计划 | `红色电波AR产品计划书.md` | 产品、数据契约、性能与任务卡 | APPROVED BASELINE |
| REF-05 | 已核史实 | `research/S1_pingxi_intelligence_station/verified_facts.md` | 时间、人物、任务和禁用说法 | VERIFIED WITH CAVEATS |
| REF-06 | 布局规则 | `research/S1_pingxi_intelligence_station/scene_layout_brief.md` | 坐标、分区、通道和碰撞 | WHITEBOX BASELINE |
| REF-07 | 资产规则 | `research/S1_pingxi_intelligence_station/modeling_brief.md` | 资产级造型与导出 | FORMAL PARTIALLY BLOCKED |
| REF-08 | 风格板 | `research/S1_pingxi_intelligence_station/style_reference_board.md` | 材质、色彩、灯光和三张审核图 | FROZEN |
| REF-09 | 视觉/权利 | `visual_reference_register.md`、`rights_and_risks.md` | 图片只可观察及版权边界 | PUBLICATION BLOCKED |
| REF-10 | 当前白盒 | `modeling_delivery/S1/runtime/`、`preview/`、`asset_report.csv` | 风格图和真机联调基础 | v0.2 |

## 3. 逐资产参考状态

| 资产 ID | 当前可做 | 仍然禁止/待补 |
|---|---|---|
| `env_s1_room` | 按三层结构制作风格图；灰砖、石基、旧木、山石/夯土和现代信息层 | 战时原址/当前纪念馆 1:1；精确洞内尺寸 |
| `p_s1_radio` | 无品牌通用箱式设备占位；确定桌面轮廓与灯光 | 具体型号、铭牌、频率、内部结构和“馆藏原件”身份 |
| `p_s1_key` | 通用直键占位；保留 `key_lever` 节点 | 具体制式、厂家、尺寸与最终动画参数 |
| `p_s1_codebook` | 技术 ID 保留；造型与用户名称按无铭文“电文与保密通信资料包” | 密码表、印章、真实电文、具体历史密码本外观 |
| `p_s1_battery` | 只预留空间 | 设备造型和接线 |
| `d_s1_map` | 只做原创抽象信息架构 | 网页/浮雕路线照搬和精确 GIS 声明 |

## 4. 用户图片

- `USER-VIS-001`：补充入口灰砖、瓦檐、石基、暗红木框和门洞纵深；排除旗帜、栏杆、摄像头、牌匾和楹联。
- `USER-VIS-002`：补充灰砖/瓦当/石基质感和现代叙事层级；排除完整浮雕、人物、路线、题字和艺术构图。
- 两张原图只在 `modeling_input/S1/local_reference/` 本地存在并被 Git 忽略。
- 当前允许内部观察，不允许导入工程、发布或识图；详情以 `material_manifest.csv` 为准。

## 5. 下一步

严格执行 `modeling_input/S1/02_MODELING_HANDOFF.md`：白盒审核 → STYLE-01/02/03 → `style_review_report.md` → 停止等待用户审核。正式资产解锁项见 `../open_questions.md`。
