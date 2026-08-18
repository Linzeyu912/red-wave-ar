# 建模参考与触发单元清单

> 状态：`VISUAL_INPUT_RECEIVED / VISUAL_CONSTRAINTS_DRAFTED / PUBLIC_LFS_UPLOAD_CONFIRMED / RIGHTS_PENDING / NARRATION_RESEARCH_DRAFTS_READY`
> 清点日期：2026-07-29
> 原始素材根目录：`modeling_input/S?/local_reference/source_folder_20260727/`

本清单登记受控输入的对应关系。用户已确认将 S1–S7 当前图片和 Word 上传到公开仓库，文件统一通过 Git LFS 存储；这项确认不替代摄影版权、隐私处理或其他公开用途许可。当前共有 7 个地点、9 个独立“触发图—真实照片（内部依据）—地面贴图—模型”单元：平西情报联络站和短波通信局旧址 S3 各有两个触发图，必须分别制作两个模型。

62 张图片已经完成第一轮逐张特征提取。总索引见 [`VISUAL_CONSTRAINTS_INDEX.md`](VISUAL_CONSTRAINTS_INDEX.md)，每个地点的图片覆盖表、主体特征、推断边界和提示词片段见对应的 `S?/visual_constraints.md`。

## 触发图、真实照片与模型对应

| 单元 | 地点与对象 | 手绘触发图原文件 | 真实照片原文件 | 计划 GLB | 内部参考图预处理 |
|---|---|---|---|---|---|
| S1A | 平西情报联络站入口门楼 | `S1/.../trigger_hand_drawn.jpg` | `S1/.../微信图片_20260712203953_1152_5130.jpg` | `S1A_pingxi_gate_v003.glb` | 尺寸可用；公开权待确认 |
| S1B | 平西女报务员雕塑及发报设备 | `S1/.../S1B_radio_operator_trigger_hand_drawn.jpg` | `S1/.../微信图片_20260716203647_1419_5130.jpg` | `S1B_radio_operator_statue_v003.glb` | 触发图 1080×1080，原样复制；真实照片须缩至 ≤2048 长边，背景人物与公开权待处理 |
| S2A | 电报大楼 | `S2/.../trigger_hand_drawn.jpg` | `S2/.../微信图片_20260727183423_918_1.jpg` | `S2A_telegraph_building_v003.glb` | 需压至 ≤5 MB，并裁除车牌等无关信息 |
| S3A | 短波通信局旧址通信楼 | `S3/.../trigger_hand_drawn.jpg` | `S3/.../微信图片_20260727183421_916_1.jpg` | `S3A_shortwave_station_building_v003.glb` | 项目方确认地点；正式史料名称为北京国际电台中央发信台；照片公开权待确认 |
| S3B | 短波通信局旧址天线阵列 | `S3/.../短波通信局2.jpg` | `S3/.../微信图片_20260727183422_917_1.jpg` | `S3B_shortwave_antenna_array_v003.glb` | 项目方确认地点；工信部核心物项包含 360 度旋转式对数周期天线；照片公开权待确认 |
| S4A | 居庸关城楼 | `S4/.../trigger_hand_drawn.jpg` | `S4/.../微信图片_20260727183424_919_1.jpg` | `S4A_juyong_pass_tower_v003.glb` | 需压至 ≤5 MB；公开权待确认 |
| S5A | 西山无名英雄纪念广场雕塑群 | `S5/.../trigger_hand_drawn.jpg` | `S5/.../18b017b5eb0df80ff4c70fc5991203b5.jpg` | `S5A_memorial_sculpture_v003.glb` | 图片带“百度百科”水印，不能直接公开展示 |
| S6A | 香山镇芳楼 | `S6/.../trigger_hand_drawn.jpg` | `S6/.../a4c5a574525a3f829e286f6eea4b9e08.jpg` | `S6A_zhenfang_lou_v003.glb` | 尺寸可用；公开权待确认 |
| S7A | 中国电信博物馆 | `S7/.../trigger_hand_drawn.jpg` | `S7/.../d10d05331791c52d672efca4212a9012.png` | `S7A_telecom_museum_v003.glb` | 尺寸可用；公开权待确认 |

表中 `S?/.../` 均指对应的 `modeling_input/S?/local_reference/source_folder_20260727/`。真实照片可作为内部建模与手绘图对应依据；其派生 `*_reference_reveal_v001.*` 仅保留为内部核对文件，当前不配置为 Kivicube AR 展示图。

九个单元的 Kivicube 正式素材包已经放在各自场景目录的 `kivicube_package/`：原手绘触发图保持 `1080×1080`、不重绘不裁切；绘制参考原图保留画幅比例并仅在长边大于 `2048px` 时下采样；每个模型均有独立 `1024×1024` 地面贴图、`*_model_v003.glb`、`*_narration_v003.m4a` 和对应的 `*_kivicube_setup_v001.json`。所有平台上传文件均带场景唯一前缀。

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
| S1 | `NARRATION_V001_CONTENT_CONFIRMED` | 已选定不含原 Word 高风险具体战例与引语的介绍段落 |
| S2、S4–S7 | `NARRATION_V001_CONTENT_CONFIRMED` | 项目负责人已选定介绍音频正文；来源和禁写边界继续保留在各地点研究稿中 |
| S3 | `IDENTITY_CONFIRMED / OFFICIAL_NAME_MATCHED / NARRATION_V001_CONTENT_CONFIRMED` | 项目方确认为短波通信局旧址；正式史料名称匹配北京国际电台中央发信台 |

最终正文已写入各地点平台交付目录的 `narration/narration_v001.md`，统一索引见 [`../lkivivube_delivery/NARRATION_FINAL_INDEX.md`](../lkivivube_delivery/NARRATION_FINAL_INDEX.md)。用户提供并明确选定的七条源 `narration_v003.m4a` 已完成文件校验，并生成九个场景专属 `*_narration_v003.m4a` 上传副本；`v001.wav` 与 `v002.mp3` 保留为历史版本。
