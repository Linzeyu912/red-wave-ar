# S1 平西情报联络站：Kivicube 资产卡

> 状态：`AWAITING_CONSTRAINTS`
> 平台规范：[`../../../docs/KIVICUBE_ASSET_CONSTRAINTS.md`](../../../docs/KIVICUBE_ASSET_CONSTRAINTS.md)

## 模型范围

- 交付目标：一件轻量地点模型。
- 当前边界：等待用户提供新的地点外观图片与文字约束；不从旧地下电台白盒、旧虚拟展馆或待审门楼 GLB 推导外形。
- GLB：`model/S1_pingxi_intelligence_station_v001.glb`，目标 ≤5 MB、验收 ≤10 MB。

## AR 呈现流程

- 当前输入入口：[`../../../modeling_input/S1/00_START_HERE.md`](../../../modeling_input/S1/00_START_HERE.md)。
- 阶段 1：识别红白手绘触发图；候选原图放 `../../../modeling_input/S1/local_reference/`。
- 阶段 2：展示绘制触发图时使用的真实参考照片；公开展示许可待确认。
- 阶段 3：展示按真实建筑颜色和材质制作的 GLB；配色依据待补充。
- 阶段 4：播放旁白。

## 交付与验收

- 手绘触发图：`images/S1_pingxi_intelligence_station_trigger_hand_drawn_v001.jpg`，评分与印刷真机测试待完成。
- 真实照片展示图：`images/S1_pingxi_intelligence_station_reference_reveal_v001.jpg`，来源、公开展示许可和隐私检查待完成。
- 形象与真实配色约束：待补充；原文件放 `../../../modeling_input/S1/local_reference/`。
- GLB 性能：目标 ≤5 网格、≤30,000 三角面、≤5 材质、≤10 贴图，待检测。
- 旁白文字参考：待补充；成稿放 `narration/narration_v001.md`。
- 平台预览图：待补充，放 `images/`。
- “触发图—真实照片—模型—旁白”流程：网页端与微信小程序端均待验证。
- 上传字段和平台回执：记录到 `upload/`。
