# S1 平西情报联络站：Kivicube 资产卡

> 状态：`TWO_MODEL_UNITS / MODEL_V3_DETAIL_PHOTO_PLANE_BUILT / BLENDER_5_1_2_REVIEWED / LOCAL_VALIDATION_PASS / RIGHTS_PENDING / PLATFORM_UPLOAD_PENDING`
> 平台规范：[`../../../docs/KIVICUBE_ASSET_CONSTRAINTS.md`](../../../docs/KIVICUBE_ASSET_CONSTRAINTS.md)

## 模型范围

- 交付目标：两件独立轻量模型，不从旧地下电台白盒、旧虚拟展馆或待审门楼 GLB 推导外形。
- 图片特征约束：[`../../../modeling_input/S1/visual_constraints.md`](../../../modeling_input/S1/visual_constraints.md)。

| 单元 | 对象 | GLB | 不可见面 |
|---|---|---|---|
| S1A | 入口门楼 | `model/S1A_pingxi_gate_v003.glb` | `INFERRED_LOW_DETAIL` |
| S1B | 女报务员雕塑及发报设备 | `model/S1B_radio_operator_statue_v003.glb` | `INFERRED_LOW_DETAIL` |

每个 GLB 目标 ≤5 MB、验收 ≤10 MB。两个 V3 模型均含一个 `photo_emerge` 动画，并已通过本地预算与 Blender 回读检查。

| 单元 | 大小 | 网格 | 三角面 | 材质 | 贴图 | 可编辑源文件 | 预览 |
|---|---:|---:|---:|---:|---:|---|---|
| S1A | 298,216 B | 5 | 2,576 | 5 | 1 | `../../source/blend/S1A_pingxi_gate_v003_source.blend` | `images/S1A_pingxi_gate_preview_v003.png` |
| S1B | 1,200,920 B | 4 | 46,316 | 4 | 0 | `../../source/blend/S1B_radio_operator_statue_v003_source.blend` | `images/S1B_radio_operator_statue_preview_v003.png` |

## AR 呈现流程

- 当前输入入口：[`../../../modeling_input/S1/00_START_HERE.md`](../../../modeling_input/S1/00_START_HERE.md)。
- 阶段 1：分别识别 S1A、S1B 手绘触发图。
- 阶段 2：在触发图同中心位置等比例展示对应原图；公开展示许可待确认。
- 阶段 3：原图保持可见，门楼或雕塑与各自脚下地面贴图同时由照片主体下缘贴地展开；不使用通用厚展台。
- 阶段 4：播放旁白。

## 交付与验收

- S1A 触发图／原图／地面贴图：`kivicube_package/S1A_pingxi_gate/`。
- S1B 触发图／原图／地面贴图：`kivicube_package/S1B_radio_operator_statue/`；触发图保持原文件，绘制参考原图保留原画幅比例。
- 每个单元的 Kivicube 时间线、贴图平面与模型摆放参数，见各自 `kivicube_package/*/kivicube_setup.json`。
- 形象与真实配色约束：已按 V2.1 原位复核用于 V3；S1A 六级入口台阶已纠正为外侧最低、靠门最高，并压暗灰砖、灰瓦与酒红木构。
- S1B 已重排为人物在左后、设备在右前的三分之四构图，使用连续法线的雕刻式头脸、收分袖管与分指双手，细化扫发、发辫、圆耳罩、盘扣衣襟、箱式报务机和电键；46,316 三角面属于近景人物专项预算，低于平台 50,000 硬上限。不可见面采用 `INFERRED_LOW_DETAIL`，不生成照片未显示的腿脚姿态。
- 上传策略：S1B 使用一个完整 `S1B_radio_operator_statue_v003.glb`；人物、头发、设备与细节仅在 GLB 内部合并为 4 个材质网格，不拆成多个平台对象。
- GLB 性能：两个模型均通过 `../../source/validation_report.json`，并经 Blender 5.1.2 实际导入。
- 原图锚点和 Kivicube 位置/缩放：以 `../../source/presentation_handoff_report.json` 为准；S1B 的原图包含讲解员，公开展示前需完成隐私与授权审核。
- 旁白文字参考：已收到、待审核；成稿放 `narration/narration_v001.md`。
- 平台预览图：两张 V3 预览已生成，见上表。
- “触发图—真实照片—模型—旁白”流程：网页端与微信小程序端均待验证。
- 上传字段和平台回执：记录到 `upload/`。
