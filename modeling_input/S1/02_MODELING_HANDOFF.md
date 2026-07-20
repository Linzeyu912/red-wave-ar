# S1 建模模型对接说明

> 状态：`M3D-01R_READY_FOR_COMPACT_CELLAR_REVIEW`
> 版本：0.2
> 本轮目标：用紧凑地下储洞小室替换旧版 8 m × 8 m 白盒，优化审核级电台并重新制作三张风格图；不进入完整中模、高模和正式材质

> 唯一入口：`modeling_input/S1/00_START_HERE.md`

## 0. 用户修订优先级（必须先读）

`04_COMPACT_CELLAR_REVISION.md` 是本轮空间尺度、布局、电台审核级优化和验收的最高优先级文件。它覆盖本文件中所有“保持旧版 8 m × 8 m 白盒、旧坐标或不改 scene.json”的说法；仍必须保留 `scene_id`、三件文物 ID、JSON schema 和 App 资源契约。

## 1. 当前交接结论

S1 的史实方向、虚拟展馆定位和风格方向已经具备交接条件；现有 `modeling_delivery/S1/` 中的 8 m × 8 m 白盒、三个占位文物、`scene.json` 和预览图只作为对照，不再是本轮基准。

本轮建模模型不能直接开始正式环境。正确顺序是：

```text
旧版白盒留档对照
  -> 按 `04_COMPACT_CELLAR_REVISION.md` 重做紧凑小室
  -> 三张简单材质风格图
  -> 资料与用户联合审核
  -> 才能解锁 M3D-02 核心文物中模和 M3D-03 正式环境
```

## 2. 建模模型必读顺序

1. `红色电波AR产品计划书.md`：§4.3、§4.4、§5、§10、§13、§15；
2. `research/S1_pingxi_intelligence_station/README.md`；
3. `verified_facts.md`、`source_register.md`；
4. `scene_layout_brief.md`；
5. `modeling_brief.md`；
6. `style_reference_board.md`；
7. `visual_reference_register.md`、`rights_and_risks.md`；
8. `modeling_input/S1/03_MATERIALS_GUIDE.md`、`modeling_input/S1/material_manifest.csv`；
9. `modeling_delivery/S1/` 当前白盒、`scene.json`、`asset_report.csv` 和预览。

若 `modeling_delivery/S1/open_questions.md` 与上述研究包冲突，以本研究包的最新用户决策为准，并在交付报告中列出需要同步关闭的旧问题，不能自行选择旧口径。

## 3. 本轮任务边界

### 允许执行

- 检查白盒单位、起点、相机朝向、通道、碰撞和三件文物可见性；
- 在不改变 `scene.json` schema、`scene_id`、文物 ID 和资源路径契约的前提下，更新旧空间坐标、移动边界和碰撞；
- 依 `04_COMPACT_CELLAR_REVISION.md` 把审核级 `p_s1_radio` 从粗略方块升级为可读的原创通用箱式设备；
- 使用简单原创材质和低成本灯光制作三张风格审核图；
- 用程序生成的灰砖、石基、旧木、土色、低饱和军绿和灰蓝信息层验证方向；
- 更新建模交付目录内的预览、报告和变更记录。

### 禁止执行

- 精确复刻当前纪念馆门楼、牌匾、楹联、旗阵、栏杆、浮雕和展墙；
- 把用户图片复制进 Blender、纹理目录、GLB、App 或远程仓库；
- 制作真实人物、肖像、雕塑、地图、可读电文、密码表、印章和电台铭牌；
- 自行确定电台型号、发报键型号和供电设备；
- 进入高模、最终 UV、正式贴图或 P2 动画；
- 修改 `app/`、研究资料包和其他模型负责的代码文件。

## 4. 必须交付的风格图

输出目录：`modeling_delivery/S1/preview/style/`

| 文件 | 固定视角 | 必须表达 |
|---|---|---|
| `STYLE-01_visitor_start.png` | 游客起点，眼高 1.6 m | 第一眼看到暖光电台桌；入口意象与信息层只作辅助 |
| `STYLE-02_operator_45deg.png` | 操作区前左 45° | radio、key、资料包三者互不遮挡，构成可信操作组 |
| `STYLE-03_route_to_entry.png` | 路线区向入口回望 | 灰砖/石基/旧木历史演绎层与灰蓝现代信息层明确分离 |

每张同时输出 1600 × 900 审核版与 1280 × 720 手机阅读版。不得使用外部 HDRI 或无许可材质；如果现有脚本只支持其他尺寸，先在报告中说明，不擅自拉伸图片。

## 5. 报告与停止条件

新增 `modeling_delivery/S1/style_review_report.md`，至少包含：

- 白盒坐标、起点、朝向、通道、碰撞和拾取检查结果；
- 三张风格图的相机参数和灯光说明；
- `USER-VIS-001/002/003` 分别采用的高层特征和主动排除的内容；
- 是否满足红色可见面积约 8–12%、暖光桌面主焦点、暗部可辨；
- 第三方资产清单；若没有，明确写“无”；
- 尚未解决的史实、权利和设备造型问题；
- 本轮变更文件列表。

交付三张图和报告后立即停止，等待用户与资料审核。不得以“风格基本确定”为理由自动进入中模或正式环境。

## 6. 可直接复制给建模模型的提示词

```text
你现在负责 red-wave-ar 项目的 S1 平西情报联络站建模交接阶段。

仓库工作规则：
1. 直接在当前 main 工作，不新建分支；只修改 modeling_delivery/S1/ 下由你负责的文件，不覆盖 app/ 和 research/ 中其他模型的改动。
2. 先完整读取 modeling_input/S1/00_START_HERE.md 和 modeling_input/S1/02_MODELING_HANDOFF.md，并严格按其中“必读顺序”读取全部输入。
3. 当前只做“现有白盒审核 + 三张简单材质风格图”，不进入完整中模、高模、正式 UV、最终贴图或人物/地图制作。
4. modeling_input/S1/local_reference/ 中三张用户图只能屏幕观察：不得导入 Blender、不得打包、不得复制进纹理、GLB、App 或远程仓库；不得临摹牌匾、楹联、旗阵、栏杆、人物、路线、题字、完整浮雕，也不得临摹 `USER-VIS-003` 的设备轮廓、文字、仪表、品牌或展陈布局。
5. 风格必须是“普通山村掩护层 + 紧凑秘密电台行动层 + 克制现代信息层”；第一视觉中心是暖光电台桌，暗朱红面积约 8–12%，暗部可辨，无体积雾、频闪、恐怖化或科幻化表达。
6. 保持 scene.json 的 ID、schema、资源路径和交互契约；按 `04_COMPACT_CELLAR_REVISION.md` 更新游客起点、主要坐标、边界和碰撞，并写入 CHANGELOG。

本轮输出：
- modeling_delivery/S1/preview/style/STYLE-01_visitor_start.png（1600×900）及 720p 版；
- STYLE-02_operator_45deg.png（1600×900）及 720p 版；
- STYLE-03_route_to_entry.png（1600×900）及 720p 版；
- modeling_delivery/S1/style_review_report.md；
- 必要的预览脚本/CHANGELOG/asset_report 更新。

每张图都要说明相机、灯光、采用的高层参考、主动排除的具体内容。完成后三张图和报告后停止并汇报，不自动进入正式资产。提交时只包含你负责的建模文件；遵循项目现行策略直接提交到 main，不做分支合并。
```

## 7. 用户收到建模交付后的对接方式

1. 用户先看 `STYLE-01`：是否第一眼就是电台桌、场景是否过红/过暗；
2. 再看 `STYLE-02`：三件物品是否清楚、尺度是否像可工作的桌面；
3. 再看 `STYLE-03`：是否把历史演绎层与现代信息层分开、有没有像当前纪念馆复制品；
4. 把三张图和 `style_review_report.md` 交给资料审核模型复核史实、版权和已冻结规则；
5. 用户给出“通过 / 指定修改项”；只有明确通过后，资料审核模型再给出 M3D-02/M3D-03 的下一阶段提示词。
