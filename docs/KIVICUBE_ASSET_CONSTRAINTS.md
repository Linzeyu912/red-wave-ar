# Kivicube AR 素材与建模约束

> 状态：`ACTIVE`
> 核对日期：2026-08-10
> 适用范围：`modeling_input/` 与 `lkivivube_delivery/`
> 官方文档入口：<https://www.kivicube.com/docs/zh/manual/>

本文件是 Kivicube 平台线的技术约束单一事实来源。各场景资产卡只记录该地点的实际值和例外，不重复发明平台规则。

仓库目录 `lkivivube_delivery/` 沿用早期拼写以保持已有路径稳定；平台正式名称统一写作 **Kivicube**。

## 1. 项目统一呈现流程

每个触发单元默认采用“**手绘触发图—地面贴图—静态真实配色模型—旁白**”的稳定流程。同一地点可有多个触发单元；当前 S1、S3 各两个，七个地点合计九个模型。

1. 用户扫描以红、白为主色的手绘触发图；
2. 识别稳定后在 `0.10s` 显示该模型专属的 v002 地面贴图；
3. 同时显示静态 GLB，明确关闭 `photo_emerge` 和其他入场动画自动播放；
4. 约 `0.80s` 后播放该地点旁白。

绘制触发图时使用的真实照片仍作为受控建模与对应关系依据，但不再作为识别后的 AR 展示平面。这避免平台动画、照片授权和跨端遮挡问题成为模型测试的阻塞项。此决定见 [`decisions/ADR-0006-static-ground-model-presentation.md`](decisions/ADR-0006-static-ground-model-presentation.md)。

### 1.1 三类视觉资产不得混淆

| 资产 | 作用 | 默认文件名 | 是否进入公开交付 |
|---|---|---|---|
| 手绘触发图 | 图像 AR 识别目标；采用红白主色 | `trigger_hand_drawn.jpg` | 仅在权利和平台识别测试通过后 |
| 绘制参考原图 | 证明手绘触发图与建模主体的对应关系；仅内部核对 | `<scene>_reference_reveal_v001.jpg` | 可随内部素材包保留，但不配置为 Kivicube AR 展示对象 |
| 地面贴图 | 模型脚下的静态环境与材质衔接 | `<scene>_ground_texture_v002.png` | 通过地面素材与模型接缝审核后 |
| GLB 模型 | 最终 AR 主体；采用真实建筑配色和材质 | `<scene>_vNNN.glb` | 通过模型与来源验收后 |

“可供内部建模参考”不等于“可公开展示”。真实照片的摄影者、来源、仓库公开许可和隐私状态仍须登记；无论这些状态如何，当前静态流程都不能把受控原图作为 Kivicube 场景对象或烘焙为 GLB 纹理。若未来另行决定公开使用，应先补拍自有照片、取得授权或换用可公开素材。

### 1.2 推荐的图像 AR 编排

- 触发图只负责识别，不作为模型颜色依据；模型颜色以核验后的真实照片和文字约束为准。
- 地面贴图与 GLB 必须使用相近的底材色系；有台阶、石基、雕塑座或天线脚时，以该接触材质为准。
- AR 内容靠近识别图布置，避免地面或模型离识别图过远或过高，以减轻移动端跟踪抖动。
- 多地点使用不同触发图时，各图必须具有足够明显的特征差异；不得只替换少量文字或编号。
- 每个触发单元必须完成一次手绘图的 Kivicube 星级检查和一次真实印刷品真机识别测试。

### 1.2.1 地面贴图与模型底部衔接

本项目不使用传统独立方形展台，也不以真实照片承担地面。每个模型使用一张专属 v002 地面图：

1. 地面贴图必须为 `1024×1024` 的方形，Kivicube 平面也必须保持方形，避免把石缝、木板或砖缝横纵拉伸。
2. 地面中心必须等于模型转换后实际占地的中心，使模型位于地面图中间上方。边长取模型实际占地长、宽中的较大值，再按每个单元的 `kivicube_setup.json` 预留 `0.12–0.18 × 识别图长边` 的同等四周边界；地面置于 `Y=0.002`。
3. 模型最低顶点必须精确接触本地 `Y=0`；场景中模型整体置于 `Y=0.004`，只留避开深度冲突所需的最小间隔。模型局部原点可因自身建模而不等于地面中心，实际占地中心才是摆放依据。
4. 每张 v002 地面图按模型接触面的材料族制作，并以低对比的底材色桥接和软椭圆接触阴影处理接缝；若预览出现明显色带或“黑底座”效果，可以提高颜色桥接、简化铺装细节或调整模型底材。阴影只能服务于模型实际占地边缘，不得画成厚展台或黑色底座。
5. 建筑自身的城墙、台阶、雕塑底座和天线基座属于主体，必须由 GLB 几何表达；带入口台阶的单元在正面（`-Z`）外侧由地面图提供同材质的平整承接区，但不得用二维贴图伪造立体踏步。禁止额外添加与受控素材无关的厚方台、圆盘展台或大面积不透明地板。
6. 如果模型底部材质、足迹、缩放或朝向改变，必须重新生成或复核其 v002 地面图和 `kivicube_setup.json`，不能只替换 GLB。

九个模型的实际位置、宽度比例、地面尺寸和内部参考来源统一记录在 [`../lkivivube_delivery/source/presentation_profiles.json`](../lkivivube_delivery/source/presentation_profiles.json) 与 [`../lkivivube_delivery/source/presentation_handoff_report.json`](../lkivivube_delivery/source/presentation_handoff_report.json)。这些 JSON 是场景编辑器交接参数，不是 Kivicube 可直接导入的工程文件。

### 1.3 有限视角与推断边界

现有参考照片视为本轮可获得的完整视觉输入，不要求用户继续补齐正、侧、背、屋顶和全部细节。只有单一或有限视角时：

- 可见主轮廓、比例、颜色和标志性构件按照片优先还原；
- 不可见面采用低细节闭合、连续材质和保守体块，并标记 `INFERRED_LOW_DETAIL`；
- 不在不可见面新增牌匾、文字、雕花、人物、门窗样式或历史性构件；
- 只在照片明确支持轴对称且无相反证据时使用对称延展；
- 雕塑背面按姿态体积低细节闭合；天线细线按移动端性能预算保留主结构、简化次级线缆；
- 此类模型定位为轻量 AR 视觉还原，不称为 1:1 复刻、测绘模型或完整数字孪生。

## 2. 会员权益、GLB 文件与场景预算

当前九个触发单元需要九个独立场景。个人版基础包含 4 个场景，因此需要再加购 5 个；如果账号已实际获得邀请好友增加的 1 个场景，则加购 4 个。个人版不包含商用权益，网页、小程序、合辑和自研小程序接入仍带水印。完整购买判断见 [`KIVICUBE_PERSONAL_PLAN_ASSESSMENT.md`](KIVICUBE_PERSONAL_PLAN_ASSESSMENT.md)。

个人版提高的是单文件上传空间和场景/体验额度，不是单独放宽三角面规范。模型精度必须服从 Kivicube 通用模型规范和手机运行预算。

Kivicube 支持 GLB、GLTF、FBX、OBJ，项目统一交付单文件 `.glb`。

| 检查项 | Kivicube 当前规则 | 本项目运行版目标 |
|---|---:|---:|
| 单个模型文件大小 | 基础版 30 MB；个人版 50 MB；高级/企业版 100 MB | **优选 ≤5 MB，验收 ≤10 MB** |
| 单模型三角面数 | 通用模型规范：30 万以内 | 按主体分配 8–18 万上限，见下表 |
| 单模型网格/材质 | 官方强烈建议各不超过 10 | 各 ≤10；优先按材质合并减少 draw call |
| 单模型贴图 | 官方强烈建议不超过 10 | ≤10，且只创建有效贴图 |
| 单张贴图尺寸 | 单边 ≤2048 px | 512/1024/2048 的 2 次幂尺寸 |
| 整个场景资源 | 官网常见问题建议约 10–15 MB | 触发图、地面、GLB 和音频合计尽量 ≤15 MB |

文件大小没有 5 MB 下限，不得为了达到某个体积而增加无效面数、提高无必要的贴图分辨率或填充文件。个人版的 50 MB 是上传资格上限，不是模型质量目标。

| 单元 | 项目三角面验收上限 | 精度优先位置 |
|---|---:|---|
| S1A | 80,000 | 瓦檐、砖檐、门洞、牌匾、正面台阶 |
| S1B | 180,000 | 连续头脸、发辫、耳机、衣褶、分指手、报务设备 |
| S2A | 120,000 | 窗套和分格、钟面、塔冠、入口轴 |
| S3A | 100,000 | 折角玻璃带、水平挑板、旧墙层次、翼楼入口 |
| S3B | 120,000 | 四腿塔、空间桁架、支承节点、帘幕线网和绝缘子 |
| S4A | 120,000 | 券门、垛口、三道檐线、瓦当和彩画层级 |
| S5A | 160,000 | 四尊人物正面、浅浮雕墙和《家国》铜牌 |
| S6A | 100,000 | 五开间、方柱、拱窗、栏杆、孔带和山花 |
| S7A | 100,000 | 弧形板缝、入口玻璃、雨棚、红柱、塔体竖带和浮雕墙 |

上表是项目验收上限，不是必须用满的目标。新增面数只能实现 [`../modeling_input/DETAIL_EVIDENCE_MATRIX.md`](../modeling_input/DETAIL_EVIDENCE_MATRIX.md) 中有来源的细节。S1B 仍作为一个完整 GLB 上传，人物、头发、设备和细节只在文件内部按材质/功能合并为少量网格，不拆成多个需要在 Kivicube 中重新对位的独立模型。

## 3. 建模、坐标与拓扑

- 按真实世界尺寸建模，并在导出前应用/重置位移、旋转和缩放；最终缩放为 `1`。
- 任何模型、骨骼或动画节点的缩放不得为 `0` 或负数。
- 模型放在世界原点；轴心优先设在建筑底部中心，确有旋转展示需求时可设为几何中心。
- 本项目图像 AR 交付不得使用几何中心轴心：模型最低点统一归一到 `Y=0`，以便稳定贴合独立地面平面。
- 法线统一朝外；删除孤立点、重复点、重叠面、隐藏废弃物体和辅助物体。
- 合理合并使用相同材质的网格，减少 draw call；透明与不透明部分拆成不同网格和材质。
- UV 必须展开且位于有效 UV 区间；避免重叠，保持一致的纹素密度，并把接缝放在不显眼处。
- 导出前将曲线和文字转为网格，应用修改器和构造历史。
- 模型、网格、材质、贴图、骨骼、形变和动画名称只能使用英文字母、数字、下划线和连字符；不得使用中文、空格或其他特殊字符，且名称必须唯一。

## 4. 材质、贴图与跨端兼容

- 为同时支持网页和微信小程序，统一使用 Kivicube V1 可用的 PBR Metallic-Roughness 或 Unlit 材质。
- 不把 clearcoat、transmission、iridescence 等 V2 扩展材质作为主效果；V2 扩展材质目前仅支持网页端。
- 贴图使用 JPG 或 PNG，单边不超过 2048 px；优先使用 512、1024、2048 等 2 的幂尺寸。
- 基础通道按需使用 `basecolor`、`normal`、`roughness`、`metallic`、`emissive`、`ao`，不为凑数量创建空贴图。
- 建筑真实配色应记录参考照片编号、色彩判断和不确定项；受光照影响明显的照片不能作为唯一色值依据。
- 可读牌匾和馆名必须先从对应参考图提取字序、繁简、书体、底色和字色，再制作原创文字贴图；不得统一替换为现代无衬线字体，也不得直接裁切受控照片。当前角色映射为：平西/电信馆名用行楷、居庸关繁体匾额用楷体、《家国》铜牌用隶书。
- 默认使用单面材质；只有确需看到背面的薄片结构才开启双面，以兼顾小米等设备的兼容性和性能。
- 透明度小于 100% 的材质必须使用 Blend；不透明材质使用 Opaque。透明与不透明部分不得共用一个材质。
- GLB 不导出灯光，也不依赖 `KHR_lights_punctual`；照明和 HDR 环境在 Kivicube 内容编辑器中设置。

## 5. 动画预算

若地点模型需要淡入、旋转、构件演示或其他动画：

| 检查项 | Kivicube 上限 | 官方建议 |
|---|---:|---:|
| 单模型动画数 | 10 | ≤5 |
| 整个场景动画数 | 40 | ≤10 |
| 单模型骨骼数 | 100 | ≤50 |
| 单模型 Morph 数 | 50 | ≤30 |
| 单顶点骨骼影响数 | 4 | ≤4 |

- 推荐 30 fps。
- 支持变换、骨骼和 Morph 动画，不使用顶点缓存动画。
- 根骨骼不要命名为 `root`，且根骨骼本身不承载动画；如必须承载，应增加一个空父骨骼。
- GLB 可以保留原有动画以兼容历史预览，但 Kivicube 默认不自动播放 `photo_emerge`；首轮场景只使用静态模型。只有平台真机验证明确支持且不破坏贴地效果时，才能另行启用其他动画。

## 6. 触发图、展示图片与旁白

### 6.1 手绘触发图

- 使用 JPG/JPEG、RGB/sRGB。
- 分辨率应在 480–1280 px，建议约 800×800。
- 优先使用 1:1；横图可在 1:1–16:9，竖图可在 9:16–1:1。
- 红白主色可以保留，但必须通过线条密度、建筑轮廓、局部纹理和非对称细节提供足够识别特征。
- 避免大面积纯红/纯白、绝对对称、重复图案、弱对比渐变和过多空白。
- 实物采用哑光、低反光印刷；避免覆膜、亚克力和强反光材质。
- 多图合辑中，各地点触发图还要满足云识别的差异性要求。

### 6.2 真实参考照片与其他图片

- Kivicube 通用图片尺寸不得超过 4096×4096 px。
- 当前定价页列出的图片/识别图上传上限为：基础版 5 MB、个人版 10 MB；高级版图片 15 MB、识别图 10 MB，企业版同为图片 15 MB、识别图 10 MB。项目仍默认按不超过 5 MB 控制，以兼顾加载和版本降级。
- 若未来另行批准公开使用，展示版本应裁去无关人物、车牌、联系方式和其他隐私信息，并保留版权/来源登记；当前流程不上传真实参考照片。
- 真实照片不得直接烘焙为建筑纹理，除非资产卡明确记录了相应许可。

### 6.3 旁白音频

- 建议交付 MP3；Kivicube 也支持 WAV、OGG、M4A、AAC、FLAC 等常见格式。
- 标准音质可用 128 kbit/s；纯人声为减小体积可用单声道 64–96 kbit/s，不建议低于 64 kbit/s。
- 旁白文字必须记录事实来源和审核状态；音频文件与文字版本号保持一致。

## 7. 每个触发与建模单元的验收清单

只有以下项目全部满足，资产卡才能从 `MODELING_READY` 进入 `READY_TO_UPLOAD`：

- [ ] 手绘触发图来源、公开权限和最终文件已登记；
- [ ] 手绘触发图通过 Kivicube 识别评分及真实印刷品真机测试；
- [ ] 真实参考照片与手绘触发图的对应关系明确；
- [ ] 真实参考照片与触发图的对应关系、来源、隐私和仓库公开边界已登记；
- [ ] 模型真实配色有来源，未确认颜色已标记；
- [ ] 缺失视角的推断面已标记 `INFERRED_LOW_DETAIL`，且未虚构标志性细节；
- [ ] GLB 可打开，文件大小、网格、三角面、材质和贴图均在预算内；
- [ ] 坐标、轴心、缩放、法线、UV、透明材质和命名检查通过；
- [ ] 网页端和微信小程序端均以 V1 兼容材质完成真机验证；
- [ ] “触发图—v002 地面贴图—静态模型—旁白”的顺序、贴地接缝和时长通过体验审核；
- [ ] 资产卡、上传记录、事实来源和版本号完整。

## 8. 官方依据

- [Kivicube 图像 AR 场景说明](https://www.kivicube.com/docs/zh/manual/overview/ar-scene-types/image-ar)
- [Kivicube 场景编辑器 3D 画布](https://www.kivicube.com/docs/zh/manual/user-manual/scene-editor/3d-canvas)
- [Kivicube 对象设置面板](https://www.kivicube.com/docs/zh/manual/user-manual/scene-editor/object-settings-panel)
- [Kivicube 交互设置](https://www.kivicube.com/docs/zh/manual/user-manual/scene-editor/interaction-settings)
- [Kivicube 3D 模型规范](https://www.kivicube.com/docs/zh/manual/ar-asset-creation-guide/3d-model/3d-model-specifications)
- [Kivicube 推荐的 GLB 导出流程](https://www.kivicube.com/docs/zh/manual/ar-asset-creation-guide/3d-model/model-export/recommended-glb-export-workflow)
- [Kivicube 模型上传与调整](https://www.kivicube.com/docs/zh/manual/ar-asset-creation-guide/3d-model/3d-model-uploading-and-adjustment)
- [Kivicube 模型常见问题](https://www.kivicube.com/docs/zh/manual/ar-asset-creation-guide/3d-model/model-faq)
- [Kivicube 图像 AR 识别图规范](https://www.kivicube.com/docs/zh/manual/ar-asset-creation-guide/target/image-ar-target)
- [Kivicube 图片规范](https://www.kivicube.com/docs/zh/manual/ar-asset-creation-guide/image)
- [Kivicube 音频规范](https://www.kivicube.com/docs/zh/manual/ar-asset-creation-guide/audio)
- [Kivicube AR 运行环境](https://www.kivicube.com/docs/zh/manual/overview/requirements)
- [Kivicube 定价与版本权益](https://www.kivicube.com/pricing/)
- [Kivicube 定价详情与到期说明](https://www.kivicube.com/docs/zh/manual/overview/kivicube-features)
- [Kivicube 模型基础规范（30 万三角面、2048 贴图）](https://www.kivicube.com/docs/zh/ar-asset-creation-guide/3d-model/legacy-docs/specification)
- [Kivicube 常见性能问题（场景总资源建议 10–15 MB）](https://www.kivicube.com/docs/zh/faq/frequently-asked-questions)
