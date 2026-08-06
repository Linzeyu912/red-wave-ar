# S3 “短波通信局”（项目暂定名）：Kivicube 资产卡

> 状态：`TWO_MODEL_UNITS / MODEL_V3_DETAIL_STATIC_GROUND_V002_READY / BLENDER_5_1_2_REVIEWED / LOCAL_VALIDATION_PASS / IDENTITY_PENDING / NARRATION_PENDING / RIGHTS_PENDING / PLATFORM_UPLOAD_PENDING`
> 平台规范：[`../../../docs/KIVICUBE_ASSET_CONSTRAINTS.md`](../../../docs/KIVICUBE_ASSET_CONSTRAINTS.md)

- 当前输入入口：[`../../../modeling_input/S3/00_START_HERE.md`](../../../modeling_input/S3/00_START_HERE.md)。
- 图片特征约束：[`../../../modeling_input/S3/visual_constraints.md`](../../../modeling_input/S3/visual_constraints.md)。
- 交付目标：两件独立轻量模型。
- 呈现顺序：各自的红白手绘触发图 → 对应 V002 专属地面贴图与静态模型同时出现 → 旁白；真实照片仅作内部核对，不使用通用厚展台。

| 单元 | 对象 | 触发图交付名 | 内部参考原图 | GLB |
|---|---|---|---|---|
| S3A | 通信楼 | `images/S3A_shortwave_station_building_trigger_v001.jpg` | `images/S3A_shortwave_station_building_reference_reveal_v001.jpg` | `model/S3A_shortwave_station_building_v003.glb` |
| S3B | 天线阵列 | `images/S3B_shortwave_antenna_array_trigger_v001.jpg` | `images/S3B_shortwave_antenna_array_reference_reveal_v001.jpg` | `model/S3B_shortwave_antenna_array_v003.glb` |

- 模型真实配色依据：照片已收到并用于 V3，不从红白触发图取色；照片不配置为 AR 展示对象，来源边界待确认。
- S3A：317,892 B、4 网格、4,492 三角面、4 材质、0 贴图、保留 1 个历史 `photo_emerge` 动画但 V002 流程不播放；保留七层弧形玻璃带、挑板、盲墙和低翼，入口台阶纠正为外低内高；源文件 `../../source/blend/S3A_shortwave_station_building_v003_source.blend`；预览 `images/S3A_shortwave_station_building_preview_v003.png`。
- S3B：1,462,740 B、3 网格、22,448 三角面、3 材质、0 贴图、保留 1 个历史 `photo_emerge` 动画但 V002 流程不播放；两组对向共线桁架轴按近正交关系建模，细化十节四腿塔架、共同支承节点、空间三角臂、端部封头、主拉索、四扇区帘幕线网和代表性绝缘子；源文件 `../../source/blend/S3B_shortwave_antenna_array_v003_source.blend`；预览 `images/S3B_shortwave_antenna_array_preview_v003.png`。
- 两个单元的地面/模型静态位置、缩放和材质衔接：`../../source/presentation_handoff_report.json`。
- 两个 GLB 均通过本地预算与 Blender 5.1.2 回读检查。
- S3A 不可见建筑面标记 `INFERRED_LOW_DETAIL`；S3B 次级线缆按性能预算简化。
- “短波通信局”仅为当前项目名；不得把“第三电台”“五六四台”等未证实身份写入模型文字、上传标题或旁白。核验依据：[`../../../modeling_input/SUBJECT_IDENTITY_VERIFICATION.md`](../../../modeling_input/SUBJECT_IDENTITY_VERIFICATION.md)。
- 受控输入：`../../../modeling_input/S3/local_reference/`。
- 旁白文字：待补充后放 `narration/narration_v001.md`。
- 上传记录放 `upload/`；参考图仅作内部依据，不得配置为展示对象。
- 网页端与微信小程序端完整流程：待验证。
