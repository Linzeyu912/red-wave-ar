# S4 居庸关：Kivicube 资产卡

> 状态：`MODEL_V3_DETAIL_STATIC_GROUND_V002_READY / BLENDER_5_1_2_REVIEWED / LOCAL_VALIDATION_PASS / NARRATION_PENDING / RIGHTS_PENDING / PLATFORM_UPLOAD_PENDING`
> 平台规范：[`../../../docs/KIVICUBE_ASSET_CONSTRAINTS.md`](../../../docs/KIVICUBE_ASSET_CONSTRAINTS.md)

- 当前输入入口：[`../../../modeling_input/S4/00_START_HERE.md`](../../../modeling_input/S4/00_START_HERE.md)。
- 图片特征约束：[`../../../modeling_input/S4/visual_constraints.md`](../../../modeling_input/S4/visual_constraints.md)。
- 交付目标：S4A 居庸关城楼轻量模型；现有照片为本轮完整视觉输入。
- 呈现顺序：红白手绘触发图 → V002 专属地面贴图与静态模型同时出现 → 旁白；参考原图仅作内部核对，不使用通用厚展台。
- 手绘触发图：`images/S4A_juyong_pass_tower_trigger_v001.jpg`，评分与印刷真机测试待完成。
- 内部参考原图：`images/S4A_juyong_pass_tower_reference_reveal_v001.jpg`；原图已收到，来源与公开边界待确认，但不上传为 AR 展示对象。
- 模型真实配色依据：主要照片已收到，不从红白触发图取色；不可见面标记 `INFERRED_LOW_DETAIL`。
- GLB：`model/S4A_juyong_pass_tower_v003.glb`，758,104 B、6 网格、10,926 三角面、6 材质、1 贴图、保留 1 个历史 `photo_emerge` 动画但 V002 流程不播放；已校正为宽城台、两层木构和三重檐。前侧券门不再用长方体拼弧，而是使用 48 段连续封闭半圆拱圈、连续弧形隧道内拱和贴合外弧的拱上墙，消除折角与孔洞，并补回低频砖缝、双层拱带和径向灰缝；匾额采用支持繁体“關”的楷体原创贴图，正面右起读作“天下第一雄關”。本地预算与 Blender 5.1.2 回读检查通过。
- 可编辑源文件：`../../source/blend/S4A_juyong_pass_tower_v003_source.blend`。
- V3 预览：`images/S4A_juyong_pass_tower_preview_v003.png`。
- 地面与模型的静态位置、缩放和材质衔接：`../../source/presentation_handoff_report.json`。
- 受控输入：`../../../modeling_input/S4/local_reference/`。
- 旁白文字：待补充后放 `narration/narration_v001.md`。
- 上传记录放 `upload/`；参考图仅作内部依据，不得配置为展示对象。
- 网页端与微信小程序端完整流程：待验证。
