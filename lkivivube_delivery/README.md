# LKIVIVUBE 平台素材交付

> 状态：`SCAFFOLD_READY / AWAITING_PER_SCENE_CONSTRAINTS`

这是项目的主 AR 素材交付层。它仅包含能上传或支持上传的地点模型、预览图片、旁白文字与元数据；原始参考图、未核验文字和带隐私的申报材料仍留在受控输入层，不直接复制到这里。

## 目录与职责

```text
lkivivube_delivery/
├── asset_manifest.csv                  # 七个地点的一览和状态
├── SCENE_ASSET_CARD_TEMPLATE.md        # 新地点资产卡模板
└── scenes/
    └── S?_slug/
        ├── asset_card.md               # 该地点的唯一交接与验收记录
        ├── model/                      # 最终 <scene>_vNNN.glb
        ├── images/                     # 已获准的预览/封面/图文素材
        ├── narration/                  # 旁白文字、事实来源与审核状态
        └── upload/                     # 上传参数、检查记录与平台回执
```

## 当前平台约束

- 一个地点交付一个独立 `.glb`，**单文件必须为 5–10 MB**；以文件属性的实际字节数为准。
- 模型为“地点轻量建模”，不默认制作可行走的室内展馆、完整电台或 1:1 建筑复刻。
- 所有图片和文字必须在 `asset_card.md` 记录来源与用途。未获公开/纹理许可的参考图只可放受控输入层，不能复制到 `images/` 或嵌入 GLB。
- 平台尚未确认纹理尺寸、动画、坐标、封面尺寸、音频格式或字段名。对应栏位先保留为 `待确认`，收到规则后再填写，不能凭经验臆定。

## 文件命名

| 类型 | 格式 | 示例 |
|---|---|---|
| 模型 | `<scene>_vNNN.glb` | `S2_telegraph_building_v001.glb` |
| 预览图 | `<scene>_cover_vNNN.png` | `S2_telegraph_building_cover_v001.png` |
| 旁白 | `narration_vNNN.md` | `narration_v001.md` |
| 上传检查 | `upload_check_vNNN.md` | `upload_check_v001.md` |

## 开始一个地点的顺序

1. 从 `modeling_input/README.md` 进入对应地点，在 `modeling_input/S?/local_reference/` 放入用户补充的原始图片/文字，并更新来源与约束摘要。
2. 在本目录对应地点的 `asset_card.md` 写清模型范围、不得复制的元素、目标旁白和验收条件。
3. 资产卡状态改为 `MODELING_READY` 后才建模；输出放入该地点的 `model/`、`images/`、`narration/`。
4. 核验 GLB 的文件大小、可打开性、图片/文字来源和命名；记录在 `upload/`。
5. 完成平台实际上传并得到回执后，才将状态改为 `UPLOADED`。

S1 既有地下电台白盒与门楼归档不属于本目录的可上传资产。新平台 S1 必须等新的地点形象约束后独立制作。
