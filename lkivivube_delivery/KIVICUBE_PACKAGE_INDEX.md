# Kivicube 场景素材包索引

所有 7 个地点、9 个模型均按同一流程交付：**原手绘触发图 → 绘制触发图的参考原图 → 模型与局部地面贴图**。

## 触发图与适配预览

![原手绘触发图｜9 个模型](images/kivicube_trigger_images_3x3.png)

![绘制触发图的参考原图｜9 个模型](images/kivicube_trigger_reference_images_3x3.png)

![模型出现时的地面贴图｜9 个模型](images/kivicube_ground_textures_3x3.png)

| 单元 | 中文地点／模型 | 素材包 |
|---|---|---|
| S1A | 平西情报联络站：入口门楼 | `scenes/S1_pingxi_intelligence_station/kivicube_package/S1A_pingxi_gate/` |
| S1B | 平西情报联络站：女报务员雕塑及发报设备 | `scenes/S1_pingxi_intelligence_station/kivicube_package/S1B_radio_operator_statue/` |
| S2A | 电报大楼 | `scenes/S2_telegraph_building/kivicube_package/S2A_telegraph_building/` |
| S3A | 短波通信局：通信楼 | `scenes/S3_shortwave_station/kivicube_package/S3A_shortwave_station_building/` |
| S3B | 短波通信局：天线阵列 | `scenes/S3_shortwave_station/kivicube_package/S3B_shortwave_antenna_array/` |
| S4A | 居庸关城楼 | `scenes/S4_juyong_pass/kivicube_package/S4A_juyong_pass_tower/` |
| S5A | 西山无名英雄纪念广场雕塑群 | `scenes/S5_memorial_plaza/kivicube_package/S5A_memorial_sculpture/` |
| S6A | 香山镇芳楼 | `scenes/S6_zhenfang_lou/kivicube_package/S6A_zhenfang_lou/` |
| S7A | 中国电信博物馆 | `scenes/S7_telecom_museum/kivicube_package/S7A_telecom_museum/` |

## 统一尺寸与摆放规则

- 触发图：直接复制原手绘文件，均为 `1080×1080`，不重绘、不裁切。
- 原图：保持画幅比例；只有原图长边超过 `2048px` 才下采样。
- 地面贴图：每个模型单独一张，均为 `1024×1024`；地面平面根据模型实际占地计算，放置于 `Y=0.004`，模型为 `Y=0.006`。
- 时间线：`0.00s` 识别触发图，`0.15s` 显示原图，`2.20s` 显示模型和地面贴图并播放 `photo_emerge`。

每个单元的精确位置、平面尺寸和模型缩放在其 `kivicube_setup.json` 中。全部原图仍仅可用于内部适配，公开上线前必须按各包 `ASSET_MANIFEST.json` 中的权限状态处理。
