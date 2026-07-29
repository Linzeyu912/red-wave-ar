# S2 电报大楼：Kivicube 资产卡

> 状态：`MODEL_V3_DETAIL_PHOTO_PLANE_BUILT / BLENDER_5_1_2_REVIEWED / LOCAL_VALIDATION_PASS / NARRATION_PENDING / RIGHTS_PENDING / PLATFORM_UPLOAD_PENDING`
> 平台规范：[`../../../docs/KIVICUBE_ASSET_CONSTRAINTS.md`](../../../docs/KIVICUBE_ASSET_CONSTRAINTS.md)

- 当前输入入口：[`../../../modeling_input/S2/00_START_HERE.md`](../../../modeling_input/S2/00_START_HERE.md)。
- 图片特征约束：[`../../../modeling_input/S2/visual_constraints.md`](../../../modeling_input/S2/visual_constraints.md)。
- 交付目标：S2A 电报大楼正立面主轮廓轻量模型；现有照片为本轮完整视觉输入。
- 呈现顺序：红白手绘触发图 → 同位置 1:1 真实照片卡 → 模型从照片主体下缘贴地展开 → 旁白；照片保持可见，不使用通用厚展台。
- 手绘触发图：`images/S2A_telegraph_building_trigger_v001.jpg`，评分与印刷真机测试待完成。
- 真实照片展示图：`images/S2A_telegraph_building_reference_reveal_v001.jpg`；原图已收到，需压至 ≤5 MB、裁除车牌并确认公开展示权。
- 模型真实配色依据：主要照片已收到，不从红白触发图取色；不可见面标记 `INFERRED_LOW_DETAIL`。
- GLB：`model/S2A_telegraph_building_v003.glb`，683,368 B、5 网格、9,836 三角面、5 材质、0 贴图、1 个 `photo_emerge` 动画；已细化上下层窗格、中央入口、横向檐带和钟塔格栅，本地预算与 Blender 5.1.2 回读检查通过。
- 可编辑源文件：`../../source/blend/S2A_telegraph_building_v003_source.blend`。
- V3 预览：`images/S2A_telegraph_building_preview_v003.png`。
- 照片主体锚点、模型位置和缩放：`../../source/presentation_handoff_report.json`。
- 受控输入：`../../../modeling_input/S2/local_reference/`。
- 旁白文字：待补充后放 `narration/narration_v001.md`。
- 上传记录放 `upload/`；未经公开展示许可的参考图不得复制进来。
- 网页端与微信小程序端完整流程：待验证。
