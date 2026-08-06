# Kivicube 平台素材交付

> 状态：`NINE_MODELS_V3_DETAIL_STATIC_GROUND_V002_READY / BLENDER_5_1_2_REVIEWED / LOCAL_VALIDATION_PASS / PLATFORM_UPLOAD_PENDING`

这是项目的主 AR 素材交付层。它包含可上传的地点模型、原手绘触发图、专属地面贴图、旁白与元数据；真实参考照片仅作为触发图和主体的内部核对副本，不配置为 AR 展示对象。原始参考图、未核验文字和带隐私的申报材料仍按受控输入与资产卡规则处理。

平台技术约束统一见 [`../docs/KIVICUBE_ASSET_CONSTRAINTS.md`](../docs/KIVICUBE_ASSET_CONSTRAINTS.md)。本目录名 `lkivivube_delivery` 沿用早期拼写以保持路径稳定，正文中的平台正式名称统一为 Kivicube。

平西 S1A/S1B 的 Kivicube 内部测试文件和上传顺序见 [`scenes/S1_pingxi_intelligence_station/KIVICUBE_TEST_HANDOFF.md`](scenes/S1_pingxi_intelligence_station/KIVICUBE_TEST_HANDOFF.md)；后续自研 Android App 的接入计划见 [`../docs/KIVICUBE_SELF_BUILT_APP_INTEGRATION_PLAN.md`](../docs/KIVICUBE_SELF_BUILT_APP_INTEGRATION_PLAN.md)。

## 目录与职责

```text
lkivivube_delivery/
├── asset_manifest.csv                  # 七地点、九建模单元的一览和状态
├── SCENE_ASSET_CARD_TEMPLATE.md        # 新地点资产卡模板
├── source/                             # 可复现生成脚本、Blender 源文件、预览与验收报告
└── scenes/
    └── S?_slug/
        ├── asset_card.md               # 该地点的唯一交接与验收记录
        ├── model/                      # 最终 <asset_id>_<slug>_vNNN.glb
        ├── images/                     # 触发图、内部参考原图、预览/封面
        ├── narration/                  # 旁白文字、事实来源与审核状态
        └── upload/                     # 上传参数、检查记录与平台回执
```

## 当前平台约束

- 一张触发图对应一个独立 `.glb`；七个地点共九个模型。每个模型目标为 **≤5 MB**，验收上限为 **≤10 MB**，不设大小下限。
- 单模型通常目标为网格 ≤5、三角面 ≤30,000、材质 ≤5、贴图 ≤10；S1B 近景人物专项允许三角面突破建议值但必须低于平台 50,000 硬上限。场景总预算见平台约束文档。
- 每个触发单元上传一个完整 GLB；材质或功能零件只在 GLB 内部分网格，不拆成多个需要在场景中重新对位的上传对象。
- 贴图使用 JPG/PNG，单边 ≤2048 px；为兼容网页和微信小程序，使用 Kivicube V1 支持的 PBR Metallic-Roughness 或 Unlit 材质。
- 模型采用真实建筑配色。颜色和材质必须引用资产卡登记的真实照片或文字依据，不从红白手绘触发图取色。
- 默认呈现顺序是“识别红白手绘触发图 → 专属地面贴图与静态真实配色 GLB 同时出现 → 旁白”。地面为无光照平面，以模型实际占地加边距计算；其颜色、材质和轻微接触阴影须与模型底材连续，不使用传统通用厚展台。
- 模型为“地点轻量建模”，不默认制作可行走的室内展馆、完整电台或 1:1 建筑复刻。
- 所有图片和文字必须在 `asset_card.md` 记录来源与用途。真实参考照片不得因本流程而被配置为 AR 展示图；“可用于内部建模参考”也不等于“可嵌入纹理”或“可对外发布”。
- 手绘触发图按图像 AR 识别图规范制作，并完成 Kivicube 评分和真实印刷品真机测试。
- 缺少侧面、背面和细节图不阻塞建模；不可见面采用低细节保守推断，并在资产卡标记 `INFERRED_LOW_DETAIL`。

## V3 细节模型交付

九个模型均已根据 62 张现有素材重新提取建筑层级、门窗分格、屋檐瓦垄、天线桁架、雕塑衣饰和设备构件，并生成 V3 GLB。2026-08-04 在原 V1/V2 流程和原文件位置完成 V2.1 迭代：保留确认准确的元素，纠正五个建筑模型的入口台阶方向，重点细化 S1B 女报务员与设备、S3B 四臂桁架夹角和帘幕线网。各文件经 Blender 5.1.2 实际导入、保存可编辑 `.blend` 并渲染预览；GLB 结构和 Kivicube 本地预算检查全部通过。GLB 可以保留历史 `photo_emerge` 动画，但静态地面 V002 流程明确不自动播放。生成方法、总览图、摆放参数和机器可读报告见 [`source/README.md`](source/README.md)，逐单元细节依据见 [`../modeling_input/DETAIL_EXTRACTION_V2.md`](../modeling_input/DETAIL_EXTRACTION_V2.md)。

| 单元 | 模型 | 大小 | 网格 | 三角面 | 材质 | 贴图 | 动画 |
|---|---|---:|---:|---:|---:|---:|---:|
| S1A | 平西情报联络站入口门楼 | 298,216 B | 5 | 2,576 | 5 | 1 | 1 |
| S1B | 女报务员雕塑及发报设备 | 1,200,920 B | 4 | 46,316 | 4 | 0 | 1 |
| S2A | 电报大楼 | 683,368 B | 5 | 9,836 | 5 | 0 | 1 |
| S3A | 通信楼 | 317,896 B | 4 | 4,492 | 4 | 0 | 1 |
| S3B | 天线阵列 | 1,462,740 B | 3 | 22,448 | 3 | 0 | 1 |
| S4A | 居庸关城楼 | 517,464 B | 5 | 7,348 | 5 | 1 | 1 |
| S5A | 西山无名英雄纪念广场雕塑群 | 584,488 B | 4 | 8,332 | 4 | 1 | 1 |
| S6A | 香山镇芳楼 | 515,552 B | 5 | 7,658 | 5 | 0 | 1 |
| S7A | 中国电信博物馆 | 390,380 B | 5 | 5,024 | 5 | 1 | 1 |

以上是本地模型交付通过状态，不等同于 Kivicube 平台已上传。手绘触发图评分、静态地面与模型的网页端/微信小程序真机衔接、旁白和参考照片的来源/公开边界仍按资产卡继续办理。

## 文件命名

| 类型 | 格式 | 示例 |
|---|---|---|
| 模型 | `<asset_id>_<slug>_vNNN.glb` | `S3B_shortwave_antenna_array_v001.glb` |
| 手绘触发图 | `<asset_id>_<slug>_trigger_vNNN.jpg` | `S3B_shortwave_antenna_array_trigger_v001.jpg` |
| 内部绘制参考图 | `<asset_id>_<slug>_reference_reveal_vNNN.jpg` | `S3B_shortwave_antenna_array_reference_reveal_v001.jpg` |
| 专属地面贴图 | `<asset_id>_<slug>_ground_texture_vNNN.png` | `S3B_shortwave_antenna_array_ground_texture_v002.png` |
| 预览图 | `<asset_id>_<slug>_cover_vNNN.png` | `S3B_shortwave_antenna_array_cover_v001.png` |
| 旁白 | `narration_vNNN.md` | `narration_v001.md` |
| 上传检查 | `upload_check_vNNN.md` | `upload_check_v001.md` |

## 开始一个地点的顺序

1. 从 `modeling_input/README.md` 和 [`../modeling_input/REFERENCE_INVENTORY.md`](../modeling_input/REFERENCE_INVENTORY.md) 进入对应建模单元，登记手绘触发图、对应真实照片（内部依据）及各自权利状态。
2. 在本目录对应地点的 `asset_card.md` 写清模型范围、真实配色依据、地面与底材衔接、不得复制的元素、静态呈现、目标旁白和验收条件。
3. 资产卡状态改为 `MODELING_READY` 后才建模；输出放入该地点的 `model/`、`images/`、`narration/`。
4. 核验 GLB 性能预算、坐标材质、图片/文字来源和命名；记录在 `upload/`。
5. 在 Kivicube 中验证触发图识别、V002 地面贴图、静态模型贴地、旁白以及网页/微信小程序表现。
6. 完成平台实际上传并得到回执后，才将状态改为 `UPLOADED`。

S1 既有地下电台白盒与门楼归档不属于本目录的可上传资产；当前 S1A/S1B 已依据新的地点照片约束独立生成。
