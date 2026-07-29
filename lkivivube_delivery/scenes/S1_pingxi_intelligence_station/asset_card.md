# S1 平西情报联络站：Kivicube 资产卡

> 状态：`VISUAL_INPUT_RECEIVED / VISUAL_CONSTRAINTS_DRAFTED / TWO_MODEL_UNITS / RIGHTS_PENDING`
> 平台规范：[`../../../docs/KIVICUBE_ASSET_CONSTRAINTS.md`](../../../docs/KIVICUBE_ASSET_CONSTRAINTS.md)

## 模型范围

- 交付目标：两件独立轻量模型，不从旧地下电台白盒、旧虚拟展馆或待审门楼 GLB 推导外形。
- 图片特征约束：[`../../../modeling_input/S1/visual_constraints.md`](../../../modeling_input/S1/visual_constraints.md)。

| 单元 | 对象 | GLB | 不可见面 |
|---|---|---|---|
| S1A | 入口门楼 | `model/S1A_pingxi_gate_v001.glb` | `INFERRED_LOW_DETAIL` |
| S1B | 女报务员雕塑及发报设备 | `model/S1B_radio_operator_statue_v001.glb` | `INFERRED_LOW_DETAIL` |

每个 GLB 目标 ≤5 MB、验收 ≤10 MB。

## AR 呈现流程

- 当前输入入口：[`../../../modeling_input/S1/00_START_HERE.md`](../../../modeling_input/S1/00_START_HERE.md)。
- 阶段 1：分别识别 S1A、S1B 手绘触发图。
- 阶段 2：分别展示与其对应的真实照片；公开展示许可待确认。
- 阶段 3：分别展示按真实颜色和材质制作的门楼模型或雕塑模型。
- 阶段 4：播放旁白。

## 交付与验收

- S1A 触发图/照片：`images/S1A_pingxi_gate_trigger_v001.jpg`、`images/S1A_pingxi_gate_reference_reveal_v001.jpg`。
- S1B 触发图/照片：`images/S1B_radio_operator_statue_trigger_v001.jpg`、`images/S1B_radio_operator_statue_reference_reveal_v001.jpg`。
- S1B 照片：需缩至 ≤4096、≤5 MB，并处理背景人物；不得直接复制 12 MB 原图。
- 形象与真实配色约束：参考图已收到，下一步整理；不可见面不再索要补图。
- GLB 性能：目标 ≤5 网格、≤30,000 三角面、≤5 材质、≤10 贴图，待检测。
- 旁白文字参考：已收到、待审核；成稿放 `narration/narration_v001.md`。
- 平台预览图：待补充，放 `images/`。
- “触发图—真实照片—模型—旁白”流程：网页端与微信小程序端均待验证。
- 上传字段和平台回执：记录到 `upload/`。
