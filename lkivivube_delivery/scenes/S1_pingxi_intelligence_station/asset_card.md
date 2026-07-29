# S1 平西情报联络站：Kivicube 资产卡

> 状态：`TWO_MODEL_UNITS / MODEL_V2_PHOTO_PLANE_BUILT / BLENDER_5_1_2_REVIEWED / LOCAL_VALIDATION_PASS / RIGHTS_PENDING / PLATFORM_UPLOAD_PENDING`
> 平台规范：[`../../../docs/KIVICUBE_ASSET_CONSTRAINTS.md`](../../../docs/KIVICUBE_ASSET_CONSTRAINTS.md)

## 模型范围

- 交付目标：两件独立轻量模型，不从旧地下电台白盒、旧虚拟展馆或待审门楼 GLB 推导外形。
- 图片特征约束：[`../../../modeling_input/S1/visual_constraints.md`](../../../modeling_input/S1/visual_constraints.md)。

| 单元 | 对象 | GLB | 不可见面 |
|---|---|---|---|
| S1A | 入口门楼 | `model/S1A_pingxi_gate_v002.glb` | `INFERRED_LOW_DETAIL` |
| S1B | 女报务员雕塑及发报设备 | `model/S1B_radio_operator_statue_v002.glb` | `INFERRED_LOW_DETAIL` |

每个 GLB 目标 ≤5 MB、验收 ≤10 MB。两个 V2 模型均含一个 `photo_emerge` 动画，并已通过本地预算与 Blender 回读检查。

| 单元 | 大小 | 网格 | 三角面 | 材质 | 贴图 | 可编辑源文件 | 预览 |
|---|---:|---:|---:|---:|---:|---|---|
| S1A | 251,232 B | 5 | 1,864 | 5 | 1 | `../../source/blend/S1A_pingxi_gate_v002_source.blend` | `images/S1A_pingxi_gate_preview_v002.png` |
| S1B | 94,612 B | 3 | 1,392 | 3 | 0 | `../../source/blend/S1B_radio_operator_statue_v002_source.blend` | `images/S1B_radio_operator_statue_preview_v002.png` |

## AR 呈现流程

- 当前输入入口：[`../../../modeling_input/S1/00_START_HERE.md`](../../../modeling_input/S1/00_START_HERE.md)。
- 阶段 1：分别识别 S1A、S1B 手绘触发图。
- 阶段 2：在触发图同中心、同尺寸位置分别展示 1:1 真实照片卡；公开展示许可待确认。
- 阶段 3：照片保持可见，门楼或雕塑由照片主体下缘贴地展开；不使用通用厚展台。
- 阶段 4：播放旁白。

## 交付与验收

- S1A 触发图/照片：`images/S1A_pingxi_gate_trigger_v001.jpg`、`images/S1A_pingxi_gate_reference_reveal_v001.jpg`。
- S1B 触发图/照片：`images/S1B_radio_operator_statue_trigger_v001.jpg`、`images/S1B_radio_operator_statue_reference_reveal_v001.jpg`。
- S1B 照片：需缩至 ≤4096、≤5 MB，并处理背景人物；不得直接复制 12 MB 原图。
- 形象与真实配色约束：已用于 V2 建模；不可见面采用 `INFERRED_LOW_DETAIL`，不再索要补图。
- GLB 性能：两个模型均通过 `../../source/validation_report.json`，并经 Blender 5.1.2 实际导入。
- 照片锚点和 Kivicube 位置/缩放：以 `../../source/presentation_handoff_report.json` 为准；S1B 使用裁切参数排除背景人物。
- 旁白文字参考：已收到、待审核；成稿放 `narration/narration_v001.md`。
- 平台预览图：两张 V2 预览已生成，见上表。
- “触发图—真实照片—模型—旁白”流程：网页端与微信小程序端均待验证。
- 上传字段和平台回执：记录到 `upload/`。
