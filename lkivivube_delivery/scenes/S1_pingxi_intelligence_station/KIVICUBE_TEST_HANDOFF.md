# 平西情报联络站｜Kivicube 测试素材交接

本文件用于在 Kivicube 中先完成 S1A、S1B 两个**独立图像 AR 场景**的内部测试。每个单元分别上传一张手绘触发图、一张 V002 地面贴图和一个 GLB；绘制触发图的参考原图仅用于内部核对，不能配置为 AR 展示对象。不要把两个单元合并为同一个识别目标。

## 测试顺序

1. 新建“图像 AR”场景，先上传“手绘触发图”作为唯一识别图。
2. 上传 V002 地面贴图和 GLB，按该场景的 `*_kivicube_setup_v001.json` 设置无光照地面与静态模型；验证它们在识别后同时出现并贴地。
3. 不添加“触发图参考原图”展示平面，也不启用 `photo_emerge`。
4. 旁白放在模型与地面衔接验收后添加。
5. 完成后记录 WebAR 分享链接或 `scene-id`，供自研 Android App 接入。

## S1A｜平西情报联络站：入口门楼

| 用途 | Kivicube 中的用途 | 文件位置 |
|---|---|---|
| 手绘触发图 | 图像 AR 的唯一识别图；原文件，不重绘、不裁切 | [`kivicube_package/S1A_pingxi_gate/S1A_pingxi_gate_trigger_v001.jpg`](kivicube_package/S1A_pingxi_gate/S1A_pingxi_gate_trigger_v001.jpg) |
| 触发图参考原图 | 内部确认手绘图与模型主体的依据；不上传为展示对象 | [`kivicube_package/S1A_pingxi_gate/S1A_pingxi_gate_reference_reveal_v001.jpg`](kivicube_package/S1A_pingxi_gate/S1A_pingxi_gate_reference_reveal_v001.jpg) |
| 地面贴图 | V002 无光照正方形地面；石材色与门楼底材衔接 | [`kivicube_package/S1A_pingxi_gate/S1A_pingxi_gate_ground_texture_v002.png`](kivicube_package/S1A_pingxi_gate/S1A_pingxi_gate_ground_texture_v002.png) |
| 建模文件 | 上传为一个完整 GLB | [`kivicube_package/S1A_pingxi_gate/S1A_pingxi_gate_model_v003.glb`](kivicube_package/S1A_pingxi_gate/S1A_pingxi_gate_model_v003.glb) |
| 介绍音频 | 场景专属文件名；识别后约 0.80 秒播放 | [`kivicube_package/S1A_pingxi_gate/S1A_pingxi_gate_narration_v003.m4a`](kivicube_package/S1A_pingxi_gate/S1A_pingxi_gate_narration_v003.m4a) |
| 摆放参数 | 地面、模型的静态初始位置、缩放与底材衔接说明 | [`kivicube_package/S1A_pingxi_gate/S1A_pingxi_gate_kivicube_setup_v001.json`](kivicube_package/S1A_pingxi_gate/S1A_pingxi_gate_kivicube_setup_v001.json) |

## S1B｜平西情报联络站：女报务员雕塑及发报设备

| 用途 | Kivicube 中的用途 | 文件位置 |
|---|---|---|
| 手绘触发图 | 图像 AR 的唯一识别图；用户提供的原手绘文件，保持原样 | [`kivicube_package/S1B_radio_operator_statue/S1B_radio_operator_statue_trigger_v001.jpg`](kivicube_package/S1B_radio_operator_statue/S1B_radio_operator_statue_trigger_v001.jpg) |
| 触发图参考原图 | 内部确认手绘图与模型主体的依据；不上传为展示对象 | [`kivicube_package/S1B_radio_operator_statue/S1B_radio_operator_statue_reference_reveal_v001.jpg`](kivicube_package/S1B_radio_operator_statue/S1B_radio_operator_statue_reference_reveal_v001.jpg) |
| 地面贴图 | V002 无光照正方形地面；深色木材色与报务员/设备底材衔接 | [`kivicube_package/S1B_radio_operator_statue/S1B_radio_operator_statue_ground_texture_v002.png`](kivicube_package/S1B_radio_operator_statue/S1B_radio_operator_statue_ground_texture_v002.png) |
| 建模文件 | 上传为一个完整 GLB | [`kivicube_package/S1B_radio_operator_statue/S1B_radio_operator_statue_model_v003.glb`](kivicube_package/S1B_radio_operator_statue/S1B_radio_operator_statue_model_v003.glb) |
| 介绍音频 | 内容与 S1A 相同，上传文件名独立 | [`kivicube_package/S1B_radio_operator_statue/S1B_radio_operator_statue_narration_v003.m4a`](kivicube_package/S1B_radio_operator_statue/S1B_radio_operator_statue_narration_v003.m4a) |
| 摆放参数 | 地面、模型的静态初始位置、缩放与底材衔接说明 | [`kivicube_package/S1B_radio_operator_statue/S1B_radio_operator_statue_kivicube_setup_v001.json`](kivicube_package/S1B_radio_operator_statue/S1B_radio_operator_statue_kivicube_setup_v001.json) |

## 使用边界

- 两张“手绘触发图”均为 `1080 × 1080`，应以原文件上传并进行 Kivicube 评分与印刷真机测试。
- 两个 GLB 均为单文件交付；不要在 Kivicube 中拆分人物、设备、门楼或地面为多个模型对象。
- `*_kivicube_setup_v001.json` 给出的是 Kivicube 自动适配后的初始摆放建议；以实际手机中的识别图尺寸、地面与模型的贴地/材质连续效果为准微调。
- S1A、S1B 的参考照片均只作内部依据。未取得摄影/人物隐私与仓库公开许可前，不得将其另作公开素材或配置到场景中。
- 上传后请回填各自的 WebAR 分享链接或 `scene-id`、识别评分、测试手机和问题记录。
