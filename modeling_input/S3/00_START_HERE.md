# S3 建模输入包：“短波通信局”（项目暂定名）

> 状态：`VISUAL_INPUT_RECEIVED / DETAIL_PASS_V2 / TWO_MODEL_UNITS / MODEL_V3_BUILT / IDENTITY_PENDING / NARRATION_REFERENCE_DRAFTED / RIGHTS_PENDING`
> 导入日期：2026-07-27
> 当前角色：Kivicube 平台 S3 唯一输入入口
> 平台资产卡：`../../lkivivube_delivery/scenes/S3_shortwave_station/asset_card.md`

## 本地素材

当前受控目录共有 10 个文件。项目暂称“短波通信局”的 S3 包含两个独立触发与建模单元：

| 单元 | 对象 | 手绘触发图 | 真实照片 | 计划模型 |
|---|---|---|---|---|
| S3A | 通信楼 | `trigger_hand_drawn.jpg` | `微信图片_20260727183421_916_1.jpg` | `S3A_shortwave_station_building_v003.glb` |
| S3B | 天线阵列 | `短波通信局2.jpg` | `微信图片_20260727183422_917_1.jpg` | `S3B_shortwave_antenna_array_v003.glb` |

目录内 `短波通信局文字素材.docx` 不视为已交付成稿。已新增仅限技术与模型说明的研究稿；它不解除地点身份核验限制。

公开资料尚不能把现有照片中的具体楼体和天线与“第三电台”“五六四台”或其他确切台站一一对应。“短波通信局”只作为当前项目名和稳定目录名；正式旁白不得据此扩写具体台站身份。核验记录见 [`../SUBJECT_IDENTITY_VERIFICATION.md`](../SUBJECT_IDENTITY_VERIFICATION.md)。

## 目标呈现

识别红白手绘触发图后，显示与模型底材衔接的 V002 专属地面贴图和静态 GLB，随后播放旁白。真实参考照片只作内部建模与触发图对应核对，不配置为 AR 展示对象。平台统一约束见 [`../../docs/KIVICUBE_ASSET_CONSTRAINTS.md`](../../docs/KIVICUBE_ASSET_CONSTRAINTS.md)。

## 当前边界

- 可在项目内部观察建筑轮廓、材料、比例和环境层级；原图只作参考，不得作为贴图、照片投影或 1:1 复刻依据。
- 现有照片是本轮完整视觉输入，不再等待更多角度。通信楼不可见面按低细节保守闭合；天线模型保留主桅杆、主桁架方向和整体轮廓，次级线缆按移动端预算简化。
- 未登记摄影者、来源、拍摄时间、建筑权利或发布许可；真实照片不得进入 Kivicube 场景或用于其他公开用途。
- 两个单元的逐图形象约束、`INFERRED_LOW_DETAIL` 清单和提示词片段已整理到 [`visual_constraints.md`](visual_constraints.md)。每个 GLB 目标 ≤5 MB、验收 ≤10 MB，只输出到平台资产卡指定目录。
- `IDENTITY_PENDING` 不阻塞按照片进行外形建模，但阻塞具体台站名称、年代和历史归属的旁白定稿。
- 内部测试用的长短版说明、来源和禁写边界见 [`narration_reference.md`](narration_reference.md)。
- 文件级对应与预处理要求见 [`../REFERENCE_INVENTORY.md`](../REFERENCE_INVENTORY.md)。
