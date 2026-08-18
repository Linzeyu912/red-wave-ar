# S2 电报大楼：Kivicube 资产卡

> 状态：`MODEL_V3_DETAIL_STATIC_GROUND_V002_READY / NARRATION_USER_AUDIO_V003_SELECTED_READY_FOR_IMPORT / BLENDER_5_1_2_REVIEWED / LOCAL_VALIDATION_PASS / RIGHTS_PENDING / PLATFORM_UPLOAD_PENDING`
> 平台规范：[`../../../docs/KIVICUBE_ASSET_CONSTRAINTS.md`](../../../docs/KIVICUBE_ASSET_CONSTRAINTS.md)

- 当前输入入口：[`../../../modeling_input/S2/00_START_HERE.md`](../../../modeling_input/S2/00_START_HERE.md)。
- 图片特征约束：[`../../../modeling_input/S2/visual_constraints.md`](../../../modeling_input/S2/visual_constraints.md)。
- 交付目标：S2A 电报大楼正立面主轮廓轻量模型；现有照片为本轮完整视觉输入。
- 呈现顺序：红白手绘触发图 → V002 专属地面贴图与静态模型同时出现 → 旁白；参考原图仅作内部核对，不使用通用厚展台。
- 手绘触发图：`images/S2A_telegraph_building_trigger_v001.jpg`，评分与印刷真机测试待完成。
- 内部参考原图：`images/S2A_telegraph_building_reference_reveal_v001.jpg`；原图已收到，车牌、来源和公开边界仍待处理，但不上传为 AR 展示对象。
- 模型真实配色依据：主要照片已收到，不从红白触发图取色；不可见面标记 `INFERRED_LOW_DETAIL`。
- GLB：`model/S2A_telegraph_building_v003.glb`，884,964 B、5 网格、12,716 三角面、5 材质、0 贴图、保留 1 个历史 `photo_emerge` 动画但 V002 流程不播放；已细化上下层窗格、中央入口、横向檐带、钟塔格栅、塔冠及斜角照片共同支持的两翼端墙窗格，并纠正入口台阶为外低内高；本地预算与 Blender 5.1.2 回读检查通过。
- 可编辑源文件：`../../source/blend/S2A_telegraph_building_v003_source.blend`。
- V3 预览：`images/S2A_telegraph_building_preview_v003.png`。
- 地面与模型的静态位置、缩放和材质衔接：`../../source/presentation_handoff_report.json`。
- 受控输入：`../../../modeling_input/S2/local_reference/`。
- 介绍音频：用户明确指定的源音频已校验；Kivicube 上传文件为 `kivicube_package/S2A_telegraph_building/S2A_telegraph_building_narration_v003.m4a`。
- 上传记录放 `upload/`；参考图仅作内部依据，不得配置为展示对象。
- 网页端与微信小程序端完整流程：待验证。
