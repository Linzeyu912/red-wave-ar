# S5 建模输入包：西山无名英雄纪念广场

> 状态：`VISUAL_INPUT_RECEIVED / DETAIL_PASS_V2 / SINGLE_VIEW_ACCEPTED / MODEL_V3_BUILT / NARRATION_REFERENCE_DRAFTED / DISPLAY_PHOTO_BLOCKED`
> 导入日期：2026-07-27
> 当前角色：Kivicube 平台 S5 唯一输入入口
> 平台资产卡：`../../lkivivube_delivery/scenes/S5_memorial_plaza/asset_card.md`

## 本地素材

当前受控目录共有 9 个文件。S5A 的触发图为 `trigger_hand_drawn.jpg`，本轮补充照片为 `18b017b5eb0df80ff4c70fc5991203b5.jpg`，当前模型为 `S5A_memorial_sculpture_v003.glb`。已补充基于官方来源的文字素材研究稿，仍需内容审核后才可作为正式旁白。

## 目标呈现

识别红白手绘触发图后，显示与模型底材衔接的 V002 专属地面贴图和静态 GLB，随后播放旁白。真实参考照片只作内部建模与触发图对应核对，不配置为 AR 展示对象。平台统一约束见 [`../../docs/KIVICUBE_ASSET_CONSTRAINTS.md`](../../docs/KIVICUBE_ASSET_CONSTRAINTS.md)。

## 当前边界

- 可在项目内部观察建筑轮廓、材料、比例和环境层级；原图只作参考，不得作为贴图、照片投影或 1:1 复刻依据。
- 现有照片是本轮完整视觉输入，不再等待其他角度；雕塑背面和不可见细节按 `INFERRED_LOW_DETAIL` 闭合。
- 未登记摄影者、来源、拍摄时间、建筑权利或发布许可；真实照片不得进入 Kivicube 场景或用于其他公开用途。
- 当前补充照片带“百度百科”水印，可作内部建模参考，但不能作为 AR 展示素材；公开使用前仍需取得许可或更换无水印可公开素材。
- 官方公开资料确认四尊雕像人物为陈宝仓、朱枫、吴石、聂曦，但未给出当前照片视角下的左右姓名顺序；建模阶段只锁定可见姿态，不强行绑定姓名。
- 前置铜牌语义标题统一为《家国》；实物为传统右起排字，正面看从左至右可见“国、家”。四尊人物、浮雕墙、铜牌和提示词片段见 [`visual_constraints.md`](visual_constraints.md)，公开资料核验见 [`../SUBJECT_IDENTITY_VERIFICATION.md`](../SUBJECT_IDENTITY_VERIFICATION.md)。
- 长短版文字、来源与禁写边界见 [`narration_reference.md`](narration_reference.md)。
- 最终 GLB 目标 ≤5 MB、验收 ≤10 MB。文件级对应见 [`../REFERENCE_INVENTORY.md`](../REFERENCE_INVENTORY.md)。
