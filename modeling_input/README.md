# 建模与素材输入：统一入口

> 当前状态：`PLATFORM_FIRST / PER_SCENE_CONSTRAINTS_PENDING`

本目录只负责接收和登记当前 Kivicube 地点素材的输入。所有新建模任务先从本文件进入，再进入对应地点的 `00_START_HERE.md`；不得从旧聊天记录、`research/` 或自研白盒归档中直接拼接任务。

| 场景 | 地点 | 当前输入入口 | 平台资产卡 |
|---|---|---|---|
| S1 | 平西情报联络站 | [`S1/00_START_HERE.md`](S1/00_START_HERE.md) | [`S1 asset_card`](../lkivivube_delivery/scenes/S1_pingxi_intelligence_station/asset_card.md) |
| S2 | 电报大楼 | [`S2/00_START_HERE.md`](S2/00_START_HERE.md) | [`S2 asset_card`](../lkivivube_delivery/scenes/S2_telegraph_building/asset_card.md) |
| S3 | 短波通信局 | [`S3/00_START_HERE.md`](S3/00_START_HERE.md) | [`S3 asset_card`](../lkivivube_delivery/scenes/S3_shortwave_station/asset_card.md) |
| S4 | 居庸关 | [`S4/00_START_HERE.md`](S4/00_START_HERE.md) | [`S4 asset_card`](../lkivivube_delivery/scenes/S4_juyong_pass/asset_card.md) |
| S5 | 西山无名英雄纪念广场 | [`S5/00_START_HERE.md`](S5/00_START_HERE.md) | [`S5 asset_card`](../lkivivube_delivery/scenes/S5_memorial_plaza/asset_card.md) |
| S6 | 香山镇芳楼 | [`S6/00_START_HERE.md`](S6/00_START_HERE.md) | [`S6 asset_card`](../lkivivube_delivery/scenes/S6_zhenfang_lou/asset_card.md) |
| S7 | 中国电信博物馆 | [`S7/00_START_HERE.md`](S7/00_START_HERE.md) | [`S7 asset_card`](../lkivivube_delivery/scenes/S7_telecom_museum/asset_card.md) |

## 输入规则

1. 原始图片、Word、测绘记录等只放进对应 `S?/local_reference/`，继续由 `.gitignore` 排除。
2. 可提交到 Git 的内容是约束摘要、来源状态、旁白草稿和资产卡，不是未核验原图。
3. 每个地点必须区分红白手绘触发图、绘图所依据的真实照片和模型；三者的用途与权限分别登记。
4. 真实照片若要在触发后展示，必须取得公开展示许可；只有内部参考权时不得复制到平台交付目录。
5. 单个地点只有在模型范围、形象约束、真实配色依据、旁白参考、使用权边界齐全后才能标为 `MODELING_READY`。
6. 新模型只输出到 `lkivivube_delivery/scenes/`，不写入 `modeling_delivery/` 或 `app/src/main/assets/`。
7. 平台限制与验收目标以 [`../docs/KIVICUBE_ASSET_CONSTRAINTS.md`](../docs/KIVICUBE_ASSET_CONSTRAINTS.md) 为准。

旧地下电台白盒、门楼提示词和 M3D-01R 文件已移至 [`archive/self_built_app/`](../archive/self_built_app/README.md)，仅供自研程序线追溯。
