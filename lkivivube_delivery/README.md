# Kivicube 平台素材交付

> 状态：`SCAFFOLD_READY / AWAITING_PER_SCENE_CONSTRAINTS`

这是项目的主 AR 素材交付层。它仅包含能上传或支持上传的地点模型、手绘触发图、获准公开的真实参考照片、预览图片、旁白与元数据；原始参考图、未核验文字和带隐私的申报材料仍留在受控输入层，不直接复制到这里。

平台技术约束统一见 [`../docs/KIVICUBE_ASSET_CONSTRAINTS.md`](../docs/KIVICUBE_ASSET_CONSTRAINTS.md)。本目录名 `lkivivube_delivery` 沿用早期拼写以保持路径稳定，正文中的平台正式名称统一为 Kivicube。

## 目录与职责

```text
lkivivube_delivery/
├── asset_manifest.csv                  # 七地点、九建模单元的一览和状态
├── SCENE_ASSET_CARD_TEMPLATE.md        # 新地点资产卡模板
└── scenes/
    └── S?_slug/
        ├── asset_card.md               # 该地点的唯一交接与验收记录
        ├── model/                      # 最终 <asset_id>_<slug>_vNNN.glb
        ├── images/                     # 获准的触发图、真实照片、预览/封面
        ├── narration/                  # 旁白文字、事实来源与审核状态
        └── upload/                     # 上传参数、检查记录与平台回执
```

## 当前平台约束

- 一张触发图对应一个独立 `.glb`；七个地点共九个模型。每个模型目标为 **≤5 MB**，验收上限为 **≤10 MB**，不设大小下限。
- 单模型目标为网格 ≤5、三角面 ≤30,000、材质 ≤5、贴图 ≤10；场景总预算见平台约束文档。
- 贴图使用 JPG/PNG，单边 ≤2048 px；为兼容网页和微信小程序，使用 Kivicube V1 支持的 PBR Metallic-Roughness 或 Unlit 材质。
- 模型采用真实建筑配色。颜色和材质必须引用资产卡登记的真实照片或文字依据，不从红白手绘触发图取色。
- 默认呈现顺序是“识别红白手绘触发图 → 展示对应真实参考照片 → 过渡到真实配色模型 → 旁白”。
- 模型为“地点轻量建模”，不默认制作可行走的室内展馆、完整电台或 1:1 建筑复刻。
- 所有图片和文字必须在 `asset_card.md` 记录来源与用途。真实参考照片必须另行确认公开展示许可；“可用于内部建模参考”不等于“可在 AR 中展示”或“可嵌入纹理”。
- 手绘触发图按图像 AR 识别图规范制作，并完成 Kivicube 评分和真实印刷品真机测试。
- 缺少侧面、背面和细节图不阻塞建模；不可见面采用低细节保守推断，并在资产卡标记 `INFERRED_LOW_DETAIL`。

## 文件命名

| 类型 | 格式 | 示例 |
|---|---|---|
| 模型 | `<asset_id>_<slug>_vNNN.glb` | `S3B_shortwave_antenna_array_v001.glb` |
| 手绘触发图 | `<asset_id>_<slug>_trigger_vNNN.jpg` | `S3B_shortwave_antenna_array_trigger_v001.jpg` |
| 真实照片展示图 | `<asset_id>_<slug>_reference_reveal_vNNN.jpg` | `S3B_shortwave_antenna_array_reference_reveal_v001.jpg` |
| 预览图 | `<asset_id>_<slug>_cover_vNNN.png` | `S3B_shortwave_antenna_array_cover_v001.png` |
| 旁白 | `narration_vNNN.md` | `narration_v001.md` |
| 上传检查 | `upload_check_vNNN.md` | `upload_check_v001.md` |

## 开始一个地点的顺序

1. 从 `modeling_input/README.md` 和 [`../modeling_input/REFERENCE_INVENTORY.md`](../modeling_input/REFERENCE_INVENTORY.md) 进入对应建模单元，登记手绘触发图、对应真实照片及各自权利状态。
2. 在本目录对应地点的 `asset_card.md` 写清模型范围、真实配色依据、不得复制的元素、三段式呈现、目标旁白和验收条件。
3. 资产卡状态改为 `MODELING_READY` 后才建模；输出放入该地点的 `model/`、`images/`、`narration/`。
4. 核验 GLB 性能预算、坐标材质、图片/文字来源和命名；记录在 `upload/`。
5. 在 Kivicube 中验证触发图识别、真实照片展示、模型过渡、旁白以及网页/微信小程序表现。
6. 完成平台实际上传并得到回执后，才将状态改为 `UPLOADED`。

S1 既有地下电台白盒与门楼归档不属于本目录的可上传资产。新的 Kivicube S1 必须等地点形象约束后独立制作。
