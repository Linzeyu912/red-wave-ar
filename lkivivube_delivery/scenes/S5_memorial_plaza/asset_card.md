# S5 西山无名英雄纪念广场：Kivicube 资产卡

> 状态：`VISUAL_INPUT_RECEIVED / VISUAL_CONSTRAINTS_DRAFTED / NARRATION_PENDING / DISPLAY_PHOTO_BLOCKED`
> 平台规范：[`../../../docs/KIVICUBE_ASSET_CONSTRAINTS.md`](../../../docs/KIVICUBE_ASSET_CONSTRAINTS.md)

- 当前输入入口：[`../../../modeling_input/S5/00_START_HERE.md`](../../../modeling_input/S5/00_START_HERE.md)。
- 图片特征约束：[`../../../modeling_input/S5/visual_constraints.md`](../../../modeling_input/S5/visual_constraints.md)。
- 交付目标：S5A 西山无名英雄纪念广场雕塑群轻量模型；现有照片为本轮完整视觉输入。
- 呈现顺序：红白手绘触发图 → 获准的真实参考照片 → 真实配色模型 → 旁白。
- 手绘触发图：`images/S5A_memorial_sculpture_trigger_v001.jpg`，评分与印刷真机测试待完成。
- 真实照片展示图：`images/S5A_memorial_sculpture_reference_reveal_v001.jpg`；当前原图带“百度百科”水印，只能内部参考，公开展示前必须取得许可或更换素材。
- 模型真实配色依据：主要照片已收到，不从红白触发图取色；雕塑背面标记 `INFERRED_LOW_DETAIL`。
- 前置铜牌的语义标题为《家国》，贴图按实物传统右起排列；四尊人物姓名不得在未确认照片方位前绑定到左—右姿态。核验依据：[`../../../modeling_input/SUBJECT_IDENTITY_VERIFICATION.md`](../../../modeling_input/SUBJECT_IDENTITY_VERIFICATION.md)。
- GLB：`model/S5A_memorial_sculpture_v001.glb`，目标 ≤5 MB、验收 ≤10 MB；目标 ≤5 网格、≤30,000 三角面、≤5 材质、≤10 贴图。
- 受控输入：`../../../modeling_input/S5/local_reference/`。
- 旁白文字：待补充后放 `narration/narration_v001.md`。
- 预览图片与上传记录：分别放 `images/`、`upload/`；未经公开展示许可的参考图不得复制进来。
- 网页端与微信小程序端完整流程：待验证。
