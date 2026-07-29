# S7 建模输入包：中国电信博物馆

> 状态：`VISUAL_INPUT_RECEIVED / VISUAL_CONSTRAINTS_DRAFTED / SINGLE_VIEW_ACCEPTED / FACADE_STATE_PENDING / NARRATION_PENDING / RIGHTS_PENDING`
> 导入日期：2026-07-27
> 当前角色：Kivicube 平台 S7 唯一输入入口
> 平台资产卡：`../../lkivivube_delivery/scenes/S7_telecom_museum/asset_card.md`

## 本地素材

当前受控目录共有 7 个文件。S7A 的触发图为 `trigger_hand_drawn.jpg`，主要真实照片为 `d10d05331791c52d672efca4212a9012.png`，计划模型为 `S7A_telecom_museum_v001.glb`。正式文字资料仍待负责同学补充。

## 目标呈现

识别红白手绘触发图后，先展示绘制该图时使用且已获公开许可的真实参考照片，再过渡到按真实建筑颜色和材质制作的 GLB 模型，随后播放旁白。平台统一约束见 [`../../docs/KIVICUBE_ASSET_CONSTRAINTS.md`](../../docs/KIVICUBE_ASSET_CONSTRAINTS.md)。

## 当前边界

- 可在项目内部观察建筑轮廓、材料、比例和环境层级；原图只作参考，不得作为贴图、照片投影或 1:1 复刻依据。
- 现有照片是本轮完整视觉输入，不再等待其他角度；侧后立面和屋顶按 `INFERRED_LOW_DETAIL` 保守处理，不虚构馆名或企业标识。
- 未登记摄影者、来源、拍摄时间、建筑权利或发布许可；在取得真实照片公开展示许可前，不得进入 App、Kivicube、宣传或公开交付。
- 银白体块、弧形立面、入口馆名、高塔标识年代差异和提示词片段见 [`visual_constraints.md`](visual_constraints.md)。
- 高塔竖向企业标识必须作为可替换贴花，最终模型只采用一个年代状态，不与无标识的新状态混合；主体身份核验见 [`../SUBJECT_IDENTITY_VERIFICATION.md`](../SUBJECT_IDENTITY_VERIFICATION.md)。
- 最终 GLB 目标 ≤5 MB、验收 ≤10 MB。文件级对应见 [`../REFERENCE_INVENTORY.md`](../REFERENCE_INVENTORY.md)。
