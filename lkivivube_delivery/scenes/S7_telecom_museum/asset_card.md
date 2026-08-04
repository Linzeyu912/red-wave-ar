# S7 中国电信博物馆：Kivicube 资产卡

> 状态：`MODEL_V3_DETAIL_PHOTO_PLANE_BUILT / BLENDER_5_1_2_REVIEWED / LOCAL_VALIDATION_PASS / PRIMARY_SIGNAGE_STATE_SELECTED / NARRATION_PENDING / RIGHTS_PENDING / PLATFORM_UPLOAD_PENDING`
> 平台规范：[`../../../docs/KIVICUBE_ASSET_CONSTRAINTS.md`](../../../docs/KIVICUBE_ASSET_CONSTRAINTS.md)

- 当前输入入口：[`../../../modeling_input/S7/00_START_HERE.md`](../../../modeling_input/S7/00_START_HERE.md)。
- 图片特征约束：[`../../../modeling_input/S7/visual_constraints.md`](../../../modeling_input/S7/visual_constraints.md)。
- 交付目标：S7A 中国电信博物馆主体轻量模型；现有照片为本轮完整视觉输入。
- 呈现顺序：红白手绘触发图 → 同位置 1:1 真实照片卡 → 模型从照片主体下缘贴地展开 → 旁白；照片保持可见，不使用通用厚展台。
- 手绘触发图：`images/S7A_telecom_museum_trigger_v001.jpg`，评分与印刷真机测试待完成。
- 真实照片展示图：`images/S7A_telecom_museum_reference_reveal_v001.jpg`；原图已收到，公开展示权待确认。
- 模型真实配色依据：主要照片已收到，不从红白触发图取色；不可见面标记 `INFERRED_LOW_DETAIL`，不虚构馆名或企业标识。
- V3 沿用主要照片和手绘触发图共同出现的“高塔带竖向中国电信博物馆馆名”状态；没有混入无标识状态的冲突细节。该贴花在 `.blend` 中仍可替换。核验依据：[`../../../modeling_input/SUBJECT_IDENTITY_VERIFICATION.md`](../../../modeling_input/SUBJECT_IDENTITY_VERIFICATION.md)。
- GLB：`model/S7A_telecom_museum_v003.glb`，390,380 B、5 网格、5,024 三角面、5 材质、1 贴图、1 个 `photo_emerge` 动画；已将弧形主体改为前半曲面并细化幕墙分格、金属板缝、入口、塔楼和后翼，同时纠正入口台阶为外低内高；本地预算与 Blender 5.1.2 回读检查通过。
- 可编辑源文件：`../../source/blend/S7A_telecom_museum_v003_source.blend`。
- V3 预览：`images/S7A_telecom_museum_preview_v003.png`。
- 照片主体锚点、模型位置和缩放：`../../source/presentation_handoff_report.json`。
- 受控输入：`../../../modeling_input/S7/local_reference/`。
- 旁白文字：待补充后放 `narration/narration_v001.md`。
- 上传记录放 `upload/`；未经公开展示许可的参考图不得复制进来。
- 网页端与微信小程序端完整流程：待验证。
