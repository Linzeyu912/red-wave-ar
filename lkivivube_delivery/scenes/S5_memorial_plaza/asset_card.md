# S5 西山无名英雄纪念广场：Kivicube 资产卡

> 状态：`MODEL_V3_DETAIL_PHOTO_PLANE_BUILT / BLENDER_5_1_2_REVIEWED / LOCAL_VALIDATION_PASS / NARRATION_PENDING / DISPLAY_PHOTO_BLOCKED / PLATFORM_UPLOAD_PENDING`
> 平台规范：[`../../../docs/KIVICUBE_ASSET_CONSTRAINTS.md`](../../../docs/KIVICUBE_ASSET_CONSTRAINTS.md)

- 当前输入入口：[`../../../modeling_input/S5/00_START_HERE.md`](../../../modeling_input/S5/00_START_HERE.md)。
- 图片特征约束：[`../../../modeling_input/S5/visual_constraints.md`](../../../modeling_input/S5/visual_constraints.md)。
- 交付目标：S5A 西山无名英雄纪念广场雕塑群轻量模型；现有照片为本轮完整视觉输入。
- 呈现顺序：红白手绘触发图 → 同位置 1:1 真实照片卡 → 模型从照片主体下缘贴地展开 → 旁白；照片保持可见，不使用通用厚展台。
- 手绘触发图：`images/S5A_memorial_sculpture_trigger_v001.jpg`，评分与印刷真机测试待完成。
- 真实照片展示图：`images/S5A_memorial_sculpture_reference_reveal_v001.jpg`；当前原图带“百度百科”水印，只能内部参考，公开展示前必须取得许可或更换素材。
- 模型真实配色依据：主要照片已收到，不从红白触发图取色；雕塑背面标记 `INFERRED_LOW_DETAIL`。
- 前置铜牌的语义标题为《家国》，贴图按实物传统右起排列；四尊人物姓名不得在未确认照片方位前绑定到左—右姿态。核验依据：[`../../../modeling_input/SUBJECT_IDENTITY_VERIFICATION.md`](../../../modeling_input/SUBJECT_IDENTITY_VERIFICATION.md)。
- GLB：`model/S5A_memorial_sculpture_v003.glb`，584,488 B、4 网格、8,332 三角面、4 材质、1 贴图、1 个 `photo_emerge` 动画；已细化五折浮雕墙、群像变化、四尊前景人物和《家国》铜牌，本地预算与 Blender 5.1.2 回读检查通过。
- 可编辑源文件：`../../source/blend/S5A_memorial_sculpture_v003_source.blend`。
- V3 预览：`images/S5A_memorial_sculpture_preview_v003.png`。
- 照片主体锚点、模型位置和缩放：`../../source/presentation_handoff_report.json`。
- 受控输入：`../../../modeling_input/S5/local_reference/`。
- 旁白文字：待补充后放 `narration/narration_v001.md`。
- 上传记录放 `upload/`；未经公开展示许可的参考图不得复制进来。
- 网页端与微信小程序端完整流程：待验证。
