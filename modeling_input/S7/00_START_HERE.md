# S7 建模输入包：中国电信博物馆

> 状态：`VISUAL_INPUT_RECEIVED / DETAIL_PASS_V2 / SINGLE_VIEW_ACCEPTED / MODEL_V3_BUILT / PRIMARY_SIGNAGE_STATE_SELECTED / NARRATION_REFERENCE_DRAFTED / RIGHTS_PENDING`
> 导入日期：2026-07-27
> 当前角色：Kivicube 平台 S7 唯一输入入口
> 平台资产卡：`../../lkivivube_delivery/scenes/S7_telecom_museum/asset_card.md`

## 本地素材

当前受控目录共有 7 个文件。S7A 的触发图为 `trigger_hand_drawn.jpg`，主要真实照片为 `d10d05331791c52d672efca4212a9012.png`，当前模型为 `S7A_telecom_museum_v003.glb`。已补充基于馆方公开资料的文字素材研究稿，仍需内容审核后才可作为正式旁白。

## 目标呈现

识别红白手绘触发图后，显示与模型底材衔接的 V002 专属地面贴图和静态 GLB，随后播放旁白。真实参考照片只作内部建模与触发图对应核对，不配置为 AR 展示对象。平台统一约束见 [`../../docs/KIVICUBE_ASSET_CONSTRAINTS.md`](../../docs/KIVICUBE_ASSET_CONSTRAINTS.md)。

## 当前边界

- 可在项目内部观察建筑轮廓、材料、比例和环境层级；原图只作参考，不得作为贴图、照片投影或 1:1 复刻依据。
- 现有照片是本轮完整视觉输入，不再等待其他角度；侧后立面和屋顶按 `INFERRED_LOW_DETAIL` 保守处理，不虚构馆名或企业标识。
- 未登记摄影者、来源、拍摄时间、建筑权利或发布许可；真实照片不得进入 Kivicube 场景或用于其他公开用途。
- 银白体块、弧形立面、入口馆名、高塔标识年代差异和提示词片段见 [`visual_constraints.md`](visual_constraints.md)。
- 长短版文字、来源与禁写边界见 [`narration_reference.md`](narration_reference.md)。
- V1 已选择主要真实照片和触发图共同出现的高塔竖向馆名状态；贴花在 `.blend` 中保持可替换，且不与无标识的新状态混合。主体身份核验见 [`../SUBJECT_IDENTITY_VERIFICATION.md`](../SUBJECT_IDENTITY_VERIFICATION.md)。
- 最终 GLB 目标 ≤5 MB、验收 ≤10 MB。文件级对应见 [`../REFERENCE_INVENTORY.md`](../REFERENCE_INVENTORY.md)。
