# S1 平西情报联络站：平台输入入口

> 状态：`AWAITING_VISUAL_CONSTRAINTS / AWAITING_NARRATION_REFERENCE`

## 当前目标

为 Kivicube 制作一个“平西情报联络站”轻量地点模型，并配套红白手绘触发图、真实参考照片展示、预览图片、旁白和上传记录。模型文件最终为 `S1_pingxi_intelligence_station_v001.glb`，目标不超过 5 MB、验收不超过 10 MB。

默认体验顺序是：识别红白手绘触发图 → 展示绘图所依据且已获公开许可的真实照片 → 展示按真实颜色和材质制作的 GLB 模型 → 旁白。

## 当前不得开始建模

尚未确认地点模型应表现的具体建筑主体、外观轮廓、材质、真实配色、周边范围和禁止复制元素，也未确认真实参考照片的公开展示权。后续用户图片到位后，先形成文字化形象约束和权利记录，再把本文件状态改为 `MODELING_READY`。

旧自研任务中的地下电台小室、发报设备和门楼 GLB 不构成本任务的外形依据，不得直接复制、改名或上传到 Kivicube。

## 素材放置

- 原始图片和文字：`local_reference/`，仅限本地受控使用。
- 手绘触发图：候选文件 `local_reference/**/trigger_hand_drawn.jpg`；经权利和真机识别审核后，才生成平台交付版本。
- 真实照片展示图：必须登记与触发图的对应关系及公开展示许可；未经许可不得复制到平台 `images/`。
- 可追踪形象约束：后续在本目录新增 `visual_constraints.md`。
- 旁白参考与事实来源：后续在本目录新增 `narration_reference.md`。
- 平台交付与验收：[`../../lkivivube_delivery/scenes/S1_pingxi_intelligence_station/asset_card.md`](../../lkivivube_delivery/scenes/S1_pingxi_intelligence_station/asset_card.md)。
- 平台统一规范：[`../../docs/KIVICUBE_ASSET_CONSTRAINTS.md`](../../docs/KIVICUBE_ASSET_CONSTRAINTS.md)。

## 历史资料

旧地下电台白盒、紧凑小室和 GATE-01 建模口令已归档到 [`../../archive/self_built_app/modeling_input/S1/00_START_HERE.md`](../../archive/self_built_app/modeling_input/S1/00_START_HERE.md)。只有明确处理自研程序线历史资产时才可读取该入口。
