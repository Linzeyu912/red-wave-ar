# 平西情报联络站｜Kivicube 触发图、原图与地面贴图包

本目录用于平西场景（S1）的内部 Kivicube 适配。文件名保持英文；下方使用中文说明。

## 内容与对应关系

| 地点建模 | 触发图（红白黑手绘） | 触发图参考原图 | 地面贴图 | GLB |
|---|---|---|---|---|
| 平西情报联络站：入口门楼（S1A） | `S1A_pingxi_gate/S1A_pingxi_gate_trigger_v001.jpg` | `S1A_pingxi_gate/S1A_pingxi_gate_reference_reveal_v001.jpg` | `S1A_pingxi_gate/S1A_pingxi_gate_ground_texture_v001.png` | `../model/S1A_pingxi_gate_v003.glb` |
| 平西情报联络站：女报务员雕塑及发报设备（S1B） | `S1B_radio_operator_statue/S1B_radio_operator_statue_trigger_v001.png` | `S1B_radio_operator_statue/S1B_radio_operator_statue_reference_reveal_v001.jpg` | `S1B_radio_operator_statue/S1B_radio_operator_statue_ground_texture_v001.png` | `../model/S1B_radio_operator_statue_v003.glb` |

S1B 的旧“触发图”实际上是白底雕塑照片，并非红白黑手绘图。本包已将它作为触发图的参考原图，并补出对应的红白黑手绘触发图；不再使用含讲解员的室内照片作为 AR 首帧。

## Kivicube 装配顺序

1. 将每个目录中的 `*_trigger_*` 上传为对应模型的图片识别图。
2. 识别成功后，在 0.15 秒显示 `*_reference_reveal_*`；该文件是保留画幅比例的原图副本。
3. 到 2.20 秒再显示 `*_ground_texture_*` 和同目录 `kivicube_setup.json` 指定的 GLB，自动播放 `photo_emerge`。
4. 地面贴图放在 `Y=0.004`、模型放在 `Y=0.006`。地面仅铺在模型脚下矩形，不应覆盖整张原图；精确坐标、尺寸、模型缩放见各自 `kivicube_setup.json`。

## 使用边界

- 这是“图片识别图 → 原图 → 模型＋地面贴图”的展示包，不包含新的厚展台模型。
- `ASSET_MANIFEST.json` 记录了每对触发图／参考原图的受控来源、尺寸与文件大小。
- 所有原图的公开展示授权仍为 `RIGHTS_PENDING`。可用于当前内部 Kivicube 调试；上线公开前须确认授权。
