# S6 建模输入包：香山镇芳楼

> 状态：`VISUAL_INPUT_RECEIVED / DETAIL_PASS_V2 / SINGLE_VIEW_ACCEPTED / MODEL_V3_BUILT / NARRATION_PENDING / RIGHTS_PENDING`
> 导入日期：2026-07-27
> 当前角色：Kivicube 平台 S6 唯一输入入口
> 平台资产卡：`../../lkivivube_delivery/scenes/S6_zhenfang_lou/asset_card.md`

## 本地素材

当前受控目录共有 9 个文件。S6A 的触发图为 `trigger_hand_drawn.jpg`，主要真实照片为 `a4c5a574525a3f829e286f6eea4b9e08.jpg`，当前模型为 `S6A_zhenfang_lou_v003.glb`。正式文字资料仍待负责同学补充。

## 目标呈现

识别红白手绘触发图后，在同一位置展示已获公开许可的 1:1 真实参考照片卡；照片保持可见，GLB 从照片主体下缘贴地展开，随后播放旁白。平台统一约束见 [`../../docs/KIVICUBE_ASSET_CONSTRAINTS.md`](../../docs/KIVICUBE_ASSET_CONSTRAINTS.md)。

## 当前边界

- 可在项目内部观察建筑轮廓、材料、比例和环境层级；原图只作参考，不得作为贴图、照片投影或 1:1 复刻依据。
- 现有照片是本轮完整视觉输入，不再等待其他角度；侧后立面和屋顶不可见结构按 `INFERRED_LOW_DETAIL` 保守处理。
- 未登记摄影者、来源、拍摄时间、建筑权利或发布许可；在取得真实照片公开展示许可前，不得进入 App、Kivicube、宣传或公开交付。
- 灰砖楼体、环廊、山花五角星、门窗与颜色约束及提示词片段见 [`visual_constraints.md`](visual_constraints.md)。
- 最终 GLB 目标 ≤5 MB、验收 ≤10 MB。文件级对应见 [`../REFERENCE_INVENTORY.md`](../REFERENCE_INVENTORY.md)。
