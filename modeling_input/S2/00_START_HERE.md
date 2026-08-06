# S2 建模输入包：电报大楼

> 状态：`VISUAL_INPUT_RECEIVED / DETAIL_PASS_V2 / SINGLE_VIEW_ACCEPTED / MODEL_V3_BUILT / NARRATION_REFERENCE_DRAFTED / RIGHTS_PENDING`
> 导入日期：2026-07-27
> 当前角色：Kivicube 平台 S2 唯一输入入口
> 平台资产卡：`../../lkivivube_delivery/scenes/S2_telegraph_building/asset_card.md`

## 本地素材

当前受控目录共有 11 个文件。S2A 的触发图为 `trigger_hand_drawn.jpg`，主要真实照片为 `微信图片_20260727183423_918_1.jpg`，当前模型为 `S2A_telegraph_building_v003.glb`。`e7014ebbe8b936c91c629951317c1fa2.jpg` 只作补充展陈参考。已补充基于官方来源的文字素材研究稿，仍需内容审核后才可作为正式旁白。

## 目标呈现

识别红白手绘触发图后，显示与模型底材衔接的 V002 专属地面贴图和静态 GLB，随后播放旁白。真实参考照片只作内部建模与触发图对应核对，不配置为 AR 展示对象。平台统一约束见 [`../../docs/KIVICUBE_ASSET_CONSTRAINTS.md`](../../docs/KIVICUBE_ASSET_CONSTRAINTS.md)。

## 当前边界

- 可在项目内部观察建筑轮廓、材料、比例和环境层级；原图只作参考，不得作为贴图、照片投影或 1:1 复刻依据。
- 现有照片是本轮完整视觉输入，不再等待侧面、背面或更多细节照片；不可见面按 `INFERRED_LOW_DETAIL` 保守闭合。
- 未登记摄影者、来源、拍摄时间、建筑权利或发布许可；真实照片不得进入 Kivicube 场景或用于其他公开用途。
- 主要照片约 5.16 MB，展示副本需压至 ≤5 MB，并裁除车牌等无关信息。最终 GLB 目标 ≤5 MB、验收 ≤10 MB。
- 图片特征、主体边界、年代差异和提示词片段见 [`visual_constraints.md`](visual_constraints.md)。
- 长短版文字、来源与禁写边界见 [`narration_reference.md`](narration_reference.md)。
- 文件级对应见 [`../REFERENCE_INVENTORY.md`](../REFERENCE_INVENTORY.md)。
