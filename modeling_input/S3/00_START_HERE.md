# S3 建模输入包：短波通信局

> 状态：`VISUAL_INPUT_RECEIVED / TWO_MODEL_UNITS / NARRATION_PENDING / RIGHTS_PENDING`
> 导入日期：2026-07-27
> 当前角色：Kivicube 平台 S3 唯一输入入口
> 平台资产卡：`../../lkivivube_delivery/scenes/S3_shortwave_station/asset_card.md`

## 本地素材

当前受控目录共有 10 个文件。短波通信局包含两个独立触发与建模单元：

| 单元 | 对象 | 手绘触发图 | 真实照片 | 计划模型 |
|---|---|---|---|---|
| S3A | 通信楼 | `trigger_hand_drawn.jpg` | `微信图片_20260727183421_916_1.jpg` | `S3A_shortwave_station_building_v001.glb` |
| S3B | 天线阵列 | `短波通信局2.jpg` | `微信图片_20260727183422_917_1.jpg` | `S3B_shortwave_antenna_array_v001.glb` |

正式文字资料仍由负责同学编写；目录内 `短波通信局文字素材.docx` 不视为已交付成稿。

## 目标呈现

识别红白手绘触发图后，先展示绘制该图时使用且已获公开许可的真实参考照片，再过渡到按真实建筑颜色和材质制作的 GLB 模型，随后播放旁白。平台统一约束见 [`../../docs/KIVICUBE_ASSET_CONSTRAINTS.md`](../../docs/KIVICUBE_ASSET_CONSTRAINTS.md)。

## 当前边界

- 可在项目内部观察建筑轮廓、材料、比例和环境层级；原图只作参考，不得作为贴图、照片投影或 1:1 复刻依据。
- 现有照片是本轮完整视觉输入，不再等待更多角度。通信楼不可见面按低细节保守闭合；天线模型保留主桅杆、主桁架方向和整体轮廓，次级线缆按移动端预算简化。
- 未登记摄影者、来源、拍摄时间、建筑权利或发布许可；在取得真实照片公开展示许可前，不得进入 App、Kivicube、宣传或公开交付。
- 两个单元的基础视觉范围已明确；下一步分别形成形象约束和 `INFERRED_LOW_DETAIL` 清单。每个 GLB 目标 ≤5 MB、验收 ≤10 MB，只输出到平台资产卡指定目录。
- 文件级对应与预处理要求见 [`../REFERENCE_INVENTORY.md`](../REFERENCE_INVENTORY.md)。
