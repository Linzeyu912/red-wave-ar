# S3 “短波通信局”（项目暂定名）：Kivicube 资产卡

> 状态：`TWO_MODEL_UNITS / MODEL_V2_PHOTO_PLANE_BUILT / BLENDER_5_1_2_REVIEWED / LOCAL_VALIDATION_PASS / IDENTITY_PENDING / NARRATION_PENDING / RIGHTS_PENDING / PLATFORM_UPLOAD_PENDING`
> 平台规范：[`../../../docs/KIVICUBE_ASSET_CONSTRAINTS.md`](../../../docs/KIVICUBE_ASSET_CONSTRAINTS.md)

- 当前输入入口：[`../../../modeling_input/S3/00_START_HERE.md`](../../../modeling_input/S3/00_START_HERE.md)。
- 图片特征约束：[`../../../modeling_input/S3/visual_constraints.md`](../../../modeling_input/S3/visual_constraints.md)。
- 交付目标：两件独立轻量模型。
- 呈现顺序：各自的红白手绘触发图 → 同位置 1:1 真实照片卡 → 对应模型从照片主体下缘贴地展开 → 旁白；照片保持可见，不使用通用厚展台。

| 单元 | 对象 | 触发图交付名 | 真实照片交付名 | GLB |
|---|---|---|---|---|
| S3A | 通信楼 | `images/S3A_shortwave_station_building_trigger_v001.jpg` | `images/S3A_shortwave_station_building_reference_reveal_v001.jpg` | `model/S3A_shortwave_station_building_v002.glb` |
| S3B | 天线阵列 | `images/S3B_shortwave_antenna_array_trigger_v001.jpg` | `images/S3B_shortwave_antenna_array_reference_reveal_v001.jpg` | `model/S3B_shortwave_antenna_array_v002.glb` |

- 模型真实配色依据：照片已收到并用于 V2，不从红白触发图取色；公开展示许可待确认。
- S3A：134,244 B、4 网格、2,124 三角面、4 材质、0 贴图、1 个 `photo_emerge` 动画；源文件 `../../source/blend/S3A_shortwave_station_building_v002_source.blend`；预览 `images/S3A_shortwave_station_building_preview_v002.png`。
- S3B：314,084 B、3 网格、4,876 三角面、3 材质、0 贴图、1 个 `photo_emerge` 动画；源文件 `../../source/blend/S3B_shortwave_antenna_array_v002_source.blend`；预览 `images/S3B_shortwave_antenna_array_preview_v002.png`。
- 两个单元的照片主体锚点、模型位置和缩放：`../../source/presentation_handoff_report.json`。
- 两个 GLB 均通过本地预算与 Blender 5.1.2 回读检查。
- S3A 不可见建筑面标记 `INFERRED_LOW_DETAIL`；S3B 次级线缆按性能预算简化。
- “短波通信局”仅为当前项目名；不得把“第三电台”“五六四台”等未证实身份写入模型文字、上传标题或旁白。核验依据：[`../../../modeling_input/SUBJECT_IDENTITY_VERIFICATION.md`](../../../modeling_input/SUBJECT_IDENTITY_VERIFICATION.md)。
- 受控输入：`../../../modeling_input/S3/local_reference/`。
- 旁白文字：待补充后放 `narration/narration_v001.md`。
- 上传记录放 `upload/`；未经公开展示许可的参考图不得复制进来。
- 网页端与微信小程序端完整流程：待验证。
