# 建模参考与触发单元清单

> 状态：`VISUAL_INPUT_RECEIVED / VISUAL_CONSTRAINTS_DRAFTED / PUBLIC_LFS_UPLOAD_CONFIRMED / RIGHTS_PENDING / TEXT_PARTIAL`
> 清点日期：2026-07-29
> 原始素材根目录：`modeling_input/S?/local_reference/source_folder_20260727/`

本清单登记受控输入的对应关系。用户已确认将 S1–S7 当前图片和 Word 上传到公开仓库，文件统一通过 Git LFS 存储；这项确认不替代摄影版权、隐私处理或 Kivicube 公开展示许可。当前共有 7 个地点、9 个独立“触发图—真实照片—模型”单元：平西情报联络站和项目暂称“短波通信局”的 S3 各有两个触发图，必须分别制作两个模型。

62 张图片已经完成第一轮逐张特征提取。总索引见 [`VISUAL_CONSTRAINTS_INDEX.md`](VISUAL_CONSTRAINTS_INDEX.md)，每个地点的图片覆盖表、主体特征、推断边界和提示词片段见对应的 `S?/visual_constraints.md`。

## 触发图、真实照片与模型对应

| 单元 | 地点与对象 | 手绘触发图原文件 | 真实照片原文件 | 计划 GLB | 展示图预处理 |
|---|---|---|---|---|---|
| S1A | 平西情报联络站入口门楼 | `S1/.../trigger_hand_drawn.jpg` | `S1/.../微信图片_20260712203953_1152_5130.jpg` | `S1A_pingxi_gate_v003.glb` | 尺寸可用；公开权待确认 |
| S1B | 平西女报务员雕塑及发报设备 | `lkivivube_delivery/.../kivicube_package/S1B_radio_operator_statue/S1B_radio_operator_statue_trigger_v001.png` | `S1/.../平西情报联络站2.jpg` | `S1B_radio_operator_statue_v003.glb` | 白底原图可作首帧；公开权待确认 |
| S2A | 电报大楼 | `S2/.../trigger_hand_drawn.jpg` | `S2/.../微信图片_20260727183423_918_1.jpg` | `S2A_telegraph_building_v003.glb` | 需压至 ≤5 MB，并裁除车牌等无关信息 |
| S3A | S3 参考素材所示通信楼 | `S3/.../trigger_hand_drawn.jpg` | `S3/.../微信图片_20260727183421_916_1.jpg` | `S3A_shortwave_station_building_v003.glb` | 尺寸与体积可用；具体台站身份与公开权待确认 |
| S3B | S3 参考素材所示天线阵列 | `S3/.../短波通信局2.jpg` | `S3/.../微信图片_20260727183422_917_1.jpg` | `S3B_shortwave_antenna_array_v003.glb` | 尺寸与体积可用；具体台站身份与公开权待确认 |
| S4A | 居庸关城楼 | `S4/.../trigger_hand_drawn.jpg` | `S4/.../微信图片_20260727183424_919_1.jpg` | `S4A_juyong_pass_tower_v003.glb` | 需压至 ≤5 MB；公开权待确认 |
| S5A | 西山无名英雄纪念广场雕塑群 | `S5/.../trigger_hand_drawn.jpg` | `S5/.../18b017b5eb0df80ff4c70fc5991203b5.jpg` | `S5A_memorial_sculpture_v003.glb` | 图片带“百度百科”水印，不能直接公开展示 |
| S6A | 香山镇芳楼 | `S6/.../trigger_hand_drawn.jpg` | `S6/.../a4c5a574525a3f829e286f6eea4b9e08.jpg` | `S6A_zhenfang_lou_v003.glb` | 尺寸可用；公开权待确认 |
| S7A | 中国电信博物馆 | `S7/.../trigger_hand_drawn.jpg` | `S7/.../d10d05331791c52d672efca4212a9012.png` | `S7A_telecom_museum_v003.glb` | 尺寸可用；公开权待确认 |

表中 `S?/.../` 均指对应的 `modeling_input/S?/local_reference/source_folder_20260727/`。真实照片均可先作为内部建模依据；只有公开展示权确认且预处理合格后，才能生成 `lkivivube_delivery/scenes/.../images/*_reference_reveal_v001.*`。

S2 的 `e7014ebbe8b936c91c629951317c1fa2.jpg` 是补充的展陈参考，不替代 S2A 的主要真实照片。

## 单视角建模约定

现有照片是本轮可获得的完整视觉输入。缺少侧面、背面、屋顶和细节近照不再阻塞建模，统一按以下规则处理：

1. 触发图和真实照片中可见的主轮廓、比例关系、主要颜色与标志性构件优先还原；
2. 不可见的侧面、背面采用低细节、连续材质和保守体块，不新增牌匾、文字、雕花或历史性装饰；
3. 只有正面明确呈轴对称且其他资料不矛盾时，才允许把可见结构对称延展到另一侧；
4. 屋顶只还原照片可确认的高度、坡向或檐口，不臆造内部结构；
5. 门窗等重复构件按可见节奏简化，不承诺不可见面的数量与现实完全一致；
6. 雕塑不可见背面按整体体积和姿态做低细节闭合，不虚构服饰纹样或设备结构；
7. 天线阵列以主桅杆、桁架方向和整体轮廓为重点，细线数量按移动端性能预算简化；
8. 所有推断区域在资产卡标记为 `INFERRED_LOW_DETAIL`，不得表述为测绘复原或 1:1 数字复刻。

## 文字资料状态

| 场景 | 状态 | 说明 |
|---|---|---|
| S1 | `RECEIVED / NOT_REVIEWED` | `平西情报联络站文字素材.docx` 已收到，后续提取并做事实与旁白审核 |
| S2–S7 | `AWAITING_AUTHOR` | 以用户最新说明为准，正式文字资料仍由负责同学编写；目录内旧文件不视为已交付成稿 |

文字未到不阻塞形象约束整理和建模准备，但在旁白成稿、事实核验与场景正式发布前必须补齐。
