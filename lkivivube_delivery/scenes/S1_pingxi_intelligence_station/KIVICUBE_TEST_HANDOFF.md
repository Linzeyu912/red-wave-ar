# 平西情报联络站｜Kivicube 测试素材交接

本文件用于在 Kivicube 中先完成 S1A、S1B 两个**独立图像 AR 场景**的内部测试。每个单元分别上传一张手绘触发图、参考图、地面贴图和一个 GLB；不要把两个单元合并为同一个识别目标。

## 测试顺序

1. 新建“图像 AR”场景，先上传“手绘触发图”作为唯一识别图。
2. 先上传 GLB 与地面贴图，验证触发图识别后模型出现并贴地。
3. 再加入“触发图参考原图”作为底层照片平面，并按 `kivicube_setup.json` 设置模型、地面和动画。
4. 旁白放在模型/动画验收后添加。
5. 完成后记录 WebAR 分享链接或 `scene-id`，供自研 Android App 接入。

## S1A｜平西情报联络站：入口门楼

| 用途 | Kivicube 中的用途 | 文件位置 |
|---|---|---|
| 手绘触发图 | 图像 AR 的唯一识别图；原文件，不重绘、不裁切 | [`kivicube_package/S1A_pingxi_gate/S1A_pingxi_gate_trigger_v001.jpg`](kivicube_package/S1A_pingxi_gate/S1A_pingxi_gate_trigger_v001.jpg) |
| 触发图参考原图 | 识别后的底层照片平面；仅内部测试，公开展示前须确认许可 | [`kivicube_package/S1A_pingxi_gate/S1A_pingxi_gate_reference_reveal_v001.jpg`](kivicube_package/S1A_pingxi_gate/S1A_pingxi_gate_reference_reveal_v001.jpg) |
| 地面贴图 | 模型脚下的小范围平面，不覆盖整张照片 | [`kivicube_package/S1A_pingxi_gate/S1A_pingxi_gate_ground_texture_v001.png`](kivicube_package/S1A_pingxi_gate/S1A_pingxi_gate_ground_texture_v001.png) |
| 建模文件 | 上传为一个完整 GLB | [`model/S1A_pingxi_gate_v003.glb`](model/S1A_pingxi_gate_v003.glb) |
| 摆放/动画参数 | 照片、地面、模型的初始位置、缩放与 `photo_emerge` 节奏 | [`kivicube_package/S1A_pingxi_gate/kivicube_setup.json`](kivicube_package/S1A_pingxi_gate/kivicube_setup.json) |

## S1B｜平西情报联络站：女报务员雕塑及发报设备

| 用途 | Kivicube 中的用途 | 文件位置 |
|---|---|---|
| 手绘触发图 | 图像 AR 的唯一识别图；用户提供的原手绘文件，保持原样 | [`kivicube_package/S1B_radio_operator_statue/S1B_radio_operator_statue_trigger_v001.jpg`](kivicube_package/S1B_radio_operator_statue/S1B_radio_operator_statue_trigger_v001.jpg) |
| 触发图参考原图 | 识别后的底层照片平面；仅内部测试，公开展示前须确认许可/隐私 | [`kivicube_package/S1B_radio_operator_statue/S1B_radio_operator_statue_reference_reveal_v001.jpg`](kivicube_package/S1B_radio_operator_statue/S1B_radio_operator_statue_reference_reveal_v001.jpg) |
| 地面贴图 | 模型脚下的小范围平面，不覆盖整张照片 | [`kivicube_package/S1B_radio_operator_statue/S1B_radio_operator_statue_ground_texture_v001.png`](kivicube_package/S1B_radio_operator_statue/S1B_radio_operator_statue_ground_texture_v001.png) |
| 建模文件 | 上传为一个完整 GLB | [`model/S1B_radio_operator_statue_v003.glb`](model/S1B_radio_operator_statue_v003.glb) |
| 摆放/动画参数 | 照片、地面、模型的初始位置、缩放与 `photo_emerge` 节奏 | [`kivicube_package/S1B_radio_operator_statue/kivicube_setup.json`](kivicube_package/S1B_radio_operator_statue/kivicube_setup.json) |

## 使用边界

- 两张“手绘触发图”均为 `1080 × 1080`，应以原文件上传并进行 Kivicube 评分与印刷真机测试。
- 两个 GLB 均为单文件交付；不要在 Kivicube 中拆分人物、设备、门楼或地面为多个模型对象。
- `kivicube_setup.json` 给出的是 Kivicube 自动适配后的初始摆放建议；以实际手机中的识别图尺寸、照片遮挡和模型贴地效果为准微调。
- S1A、S1B 的参考照片均处于内部适配状态。未取得摄影/人物隐私与公开展示许可前，不得公开分享场景链接或用于正式上线。
- 上传后请回填各自的 WebAR 分享链接或 `scene-id`、识别评分、测试手机和问题记录。
