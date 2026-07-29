# 建模与素材输入：统一入口

> 当前状态：`PLATFORM_FIRST / VISUAL_INPUT_RECEIVED / VISUAL_CONSTRAINTS_DRAFTED / TEXT_PARTIAL`

本目录只负责接收和登记当前 Kivicube 地点素材的输入。所有新建模任务先从本文件进入，再进入对应地点的 `00_START_HERE.md`；不得从旧聊天记录、`research/` 或自研白盒归档中直接拼接任务。

| 场景 | 地点 | 当前输入入口 | 图片特征约束 | 平台资产卡 |
|---|---|---|---|---|
| S1 | 平西情报联络站 | [`S1/00_START_HERE.md`](S1/00_START_HERE.md) | [`S1/visual_constraints.md`](S1/visual_constraints.md) | [`S1 asset_card`](../lkivivube_delivery/scenes/S1_pingxi_intelligence_station/asset_card.md) |
| S2 | 电报大楼 | [`S2/00_START_HERE.md`](S2/00_START_HERE.md) | [`S2/visual_constraints.md`](S2/visual_constraints.md) | [`S2 asset_card`](../lkivivube_delivery/scenes/S2_telegraph_building/asset_card.md) |
| S3 | “短波通信局”（项目暂定名） | [`S3/00_START_HERE.md`](S3/00_START_HERE.md) | [`S3/visual_constraints.md`](S3/visual_constraints.md) | [`S3 asset_card`](../lkivivube_delivery/scenes/S3_shortwave_station/asset_card.md) |
| S4 | 居庸关 | [`S4/00_START_HERE.md`](S4/00_START_HERE.md) | [`S4/visual_constraints.md`](S4/visual_constraints.md) | [`S4 asset_card`](../lkivivube_delivery/scenes/S4_juyong_pass/asset_card.md) |
| S5 | 西山无名英雄纪念广场 | [`S5/00_START_HERE.md`](S5/00_START_HERE.md) | [`S5/visual_constraints.md`](S5/visual_constraints.md) | [`S5 asset_card`](../lkivivube_delivery/scenes/S5_memorial_plaza/asset_card.md) |
| S6 | 香山镇芳楼 | [`S6/00_START_HERE.md`](S6/00_START_HERE.md) | [`S6/visual_constraints.md`](S6/visual_constraints.md) | [`S6 asset_card`](../lkivivube_delivery/scenes/S6_zhenfang_lou/asset_card.md) |
| S7 | 中国电信博物馆 | [`S7/00_START_HERE.md`](S7/00_START_HERE.md) | [`S7/visual_constraints.md`](S7/visual_constraints.md) | [`S7 asset_card`](../lkivivube_delivery/scenes/S7_telecom_museum/asset_card.md) |

九个触发与建模单元的文件对应、预处理要求和文字状态见 [`REFERENCE_INVENTORY.md`](REFERENCE_INVENTORY.md)；图片提取结论和提示词组装顺序见 [`VISUAL_CONSTRAINTS_INDEX.md`](VISUAL_CONSTRAINTS_INDEX.md)；同地点主体一致性、公开资料出处和身份边界见 [`SUBJECT_IDENTITY_VERIFICATION.md`](SUBJECT_IDENTITY_VERIFICATION.md)。

## 输入规则

1. 原始图片和 Word 放进对应 `S?/local_reference/`，由 `.gitattributes` 统一通过 Git LFS 版本化。
2. 仓库为公开仓库；用户已确认 S1–S7 当前参考图片和 Word 可进入 Git LFS。PDF、`_source.*` 和其他明确标记的敏感文件仍由根 `.gitignore` 排除。
3. 每个地点必须区分红白手绘触发图、绘图所依据的真实照片和模型；三者的用途与权限分别登记。
4. Git LFS 入库不等于取得 AR 展示许可。真实照片若要在触发后展示，仍必须取得公开展示许可；只有内部参考权时不得复制到平台交付目录。
5. 单个触发单元在模型范围、形象约束、真实配色依据和推断边界明确后即可进入建模准备；旁白可后补，但正式发布前必须完成。
6. 新模型只输出到 `lkivivube_delivery/scenes/`，不写入 `modeling_delivery/` 或 `app/src/main/assets/`。
7. 平台限制与验收目标以 [`../docs/KIVICUBE_ASSET_CONSTRAINTS.md`](../docs/KIVICUBE_ASSET_CONSTRAINTS.md) 为准。
8. 不再要求用户补齐正、侧、背和全部细节图；缺失视角按 [`REFERENCE_INVENTORY.md`](REFERENCE_INVENTORY.md) 的单视角约定做低细节保守推断。

旧地下电台白盒、门楼提示词和 M3D-01R 文件已移至 [`archive/self_built_app/`](../archive/self_built_app/README.md)，仅供自研程序线追溯。
