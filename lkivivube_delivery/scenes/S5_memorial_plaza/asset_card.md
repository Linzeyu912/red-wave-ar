# S5 西山无名英雄纪念广场：Kivicube 资产卡

> 状态：`MODEL_V3_DETAIL_STATIC_GROUND_V002_READY / BLENDER_5_1_2_REVIEWED / LOCAL_VALIDATION_PASS / NARRATION_PENDING / REFERENCE_SOURCE_REVIEW_PENDING / PLATFORM_UPLOAD_PENDING`
> 平台规范：[`../../../docs/KIVICUBE_ASSET_CONSTRAINTS.md`](../../../docs/KIVICUBE_ASSET_CONSTRAINTS.md)

- 当前输入入口：[`../../../modeling_input/S5/00_START_HERE.md`](../../../modeling_input/S5/00_START_HERE.md)。
- 图片特征约束：[`../../../modeling_input/S5/visual_constraints.md`](../../../modeling_input/S5/visual_constraints.md)。
- 交付目标：S5A 西山无名英雄纪念广场雕塑群轻量模型；现有照片为本轮完整视觉输入。
- 呈现顺序：红白手绘触发图 → V002 专属地面贴图与静态模型同时出现 → 旁白；参考原图仅作内部核对，不使用通用厚展台。
- 手绘触发图：`images/S5A_memorial_sculpture_trigger_v001.jpg`，评分与印刷真机测试待完成。
- 内部参考原图：`images/S5A_memorial_sculpture_reference_reveal_v001.jpg`；当前原图带“百度百科”水印，只能内部参考，不上传为 AR 展示对象；公开仓库或其他用途前仍须取得许可或更换素材。
- 模型真实配色依据：主要照片已收到，不从红白触发图取色；雕塑背面标记 `INFERRED_LOW_DETAIL`。
- 前置铜牌的语义标题为《家国》，贴图按实物传统右起排列；四尊人物姓名不得在未确认照片方位前绑定到左—右姿态。核验依据：[`../../../modeling_input/SUBJECT_IDENTITY_VERIFICATION.md`](../../../modeling_input/SUBJECT_IDENTITY_VERIFICATION.md)。
- GLB：`model/S5A_memorial_sculpture_v003.glb`，1,327,476 B、5 网格、45,564 三角面、5 材质、1 贴图、保留 1 个历史 `photo_emerge` 动画但 V002 流程不播放；保留五折浮雕墙、群像变化和《家国》铜牌，并把四尊前景人物从球柱体升级为连续头脸、发型、收分肢体、分离手掌/手指与四种差异姿态。本地预算与 Blender 5.1.2 回读检查通过。
- 可编辑源文件：`../../source/blend/S5A_memorial_sculpture_v003_source.blend`。
- V3 预览：`images/S5A_memorial_sculpture_preview_v003.png`。
- 地面与模型的静态位置、缩放和材质衔接：`../../source/presentation_handoff_report.json`。
- 受控输入：`../../../modeling_input/S5/local_reference/`。
- 旁白文字：待补充后放 `narration/narration_v001.md`。
- 上传记录放 `upload/`；参考图仅作内部依据，不得配置为展示对象。
- 网页端与微信小程序端完整流程：待验证。
