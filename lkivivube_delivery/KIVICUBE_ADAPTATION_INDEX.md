# Kivicube 九场景适配素材索引

> 状态：`9_SCENES / ALL_REQUIRED_FILES_PRESENT / USER_AUDIO_V003_SELECTED / LOCAL_VALIDATION_PASS / PLATFORM_IMPORT_PENDING`
> 更新日期：2026-08-18

本页记录 Kivicube 适配文件。项目有 7 个地点、9 个独立触发场景；所有平台上传文件都使用“场景编号 + 场景英文名 + 素材类型 + 版本”的唯一名称。S1A/S1B 的音频内容相同、S3A/S3B 的音频内容相同，但上传文件已按场景分别命名。

## 每个场景的统一装配顺序

1. 上传“触发图”作为图片识别图。
2. 识别成功后约 `0.10s` 显示“地面贴图”和静态 GLB。
3. 地面贴图使用无光照方形平面；模型不自动播放 `photo_emerge` 或其他动画。
4. 约 `0.80s` 播放该场景的 `*_narration_v003.m4a`。
5. “内部参考图”只用于核对触发图与主体，**不要上传为 AR 展示对象**。
6. 精确参数以每个场景的 `*_kivicube_setup_v001.json` 为准；以下位置、尺寸和缩放已从该文件摘出。

所有场景共同参数：地面旋转 `(0, 0, 0)`；模型旋转 `(0, 0, 0)`；正面轴 `-Z`；模型静态显示。

## S1A 平西情报联络站：入口门楼

适配参数：地面尺寸 `1.08 × 1.08`；地面位置 `(0, 0.002, 0.03776)`；模型位置 `(0, 0.004, 0.112671)`；模型缩放 `0.72`。

- [触发图](scenes/S1_pingxi_intelligence_station/kivicube_package/S1A_pingxi_gate/S1A_pingxi_gate_trigger_v001.jpg)
- [地面贴图](scenes/S1_pingxi_intelligence_station/kivicube_package/S1A_pingxi_gate/S1A_pingxi_gate_ground_texture_v002.png)
- [V3 GLB 模型](scenes/S1_pingxi_intelligence_station/kivicube_package/S1A_pingxi_gate/S1A_pingxi_gate_model_v003.glb)
- [当前选定音频 v003](scenes/S1_pingxi_intelligence_station/kivicube_package/S1A_pingxi_gate/S1A_pingxi_gate_narration_v003.m4a)
- [完整参数 JSON](scenes/S1_pingxi_intelligence_station/kivicube_package/S1A_pingxi_gate/S1A_pingxi_gate_kivicube_setup_v001.json)
- [V3 模型预览](scenes/S1_pingxi_intelligence_station/images/S1A_pingxi_gate_preview_v003.png)
- [内部参考图｜不要上传](scenes/S1_pingxi_intelligence_station/kivicube_package/S1A_pingxi_gate/S1A_pingxi_gate_reference_reveal_v001.jpg)
- [音频交付记录](scenes/S1_pingxi_intelligence_station/narration/narration_v003.md)
- [地点资产卡](scenes/S1_pingxi_intelligence_station/asset_card.md)

## S1B 平西情报联络站：女报务员雕塑及发报设备

适配参数：地面尺寸 `0.60 × 0.60`；地面位置 `(-0.12, 0.002, 0.04336)`；模型位置 `(-0.12, 0.004, 0.113032)`；模型缩放 `0.393507`。

- [触发图](scenes/S1_pingxi_intelligence_station/kivicube_package/S1B_radio_operator_statue/S1B_radio_operator_statue_trigger_v001.jpg)
- [地面贴图](scenes/S1_pingxi_intelligence_station/kivicube_package/S1B_radio_operator_statue/S1B_radio_operator_statue_ground_texture_v002.png)
- [V3 GLB 模型](scenes/S1_pingxi_intelligence_station/kivicube_package/S1B_radio_operator_statue/S1B_radio_operator_statue_model_v003.glb)
- [当前选定音频 v003｜内容与 S1A 相同，文件名独立](scenes/S1_pingxi_intelligence_station/kivicube_package/S1B_radio_operator_statue/S1B_radio_operator_statue_narration_v003.m4a)
- [完整参数 JSON](scenes/S1_pingxi_intelligence_station/kivicube_package/S1B_radio_operator_statue/S1B_radio_operator_statue_kivicube_setup_v001.json)
- [V3 模型预览](scenes/S1_pingxi_intelligence_station/images/S1B_radio_operator_statue_preview_v003.png)
- [内部参考图｜不要上传](scenes/S1_pingxi_intelligence_station/kivicube_package/S1B_radio_operator_statue/S1B_radio_operator_statue_reference_reveal_v001.jpg)
- [音频交付记录](scenes/S1_pingxi_intelligence_station/narration/narration_v003.md)
- [地点资产卡](scenes/S1_pingxi_intelligence_station/asset_card.md)

## S2A 电报大楼

适配参数：地面尺寸 `1.06 × 1.06`；地面位置 `(0, 0.002, 0.151313)`；模型位置 `(0, 0.004, 0.191423)`；模型缩放 `0.78`。

- [触发图](scenes/S2_telegraph_building/kivicube_package/S2A_telegraph_building/S2A_telegraph_building_trigger_v001.jpg)
- [地面贴图](scenes/S2_telegraph_building/kivicube_package/S2A_telegraph_building/S2A_telegraph_building_ground_texture_v002.png)
- [V3 GLB 模型](scenes/S2_telegraph_building/kivicube_package/S2A_telegraph_building/S2A_telegraph_building_model_v003.glb)
- [当前选定音频 v003](scenes/S2_telegraph_building/kivicube_package/S2A_telegraph_building/S2A_telegraph_building_narration_v003.m4a)
- [完整参数 JSON](scenes/S2_telegraph_building/kivicube_package/S2A_telegraph_building/S2A_telegraph_building_kivicube_setup_v001.json)
- [V3 模型预览](scenes/S2_telegraph_building/images/S2A_telegraph_building_preview_v003.png)
- [内部参考图｜不要上传](scenes/S2_telegraph_building/kivicube_package/S2A_telegraph_building/S2A_telegraph_building_reference_reveal_v001.jpg)
- [音频交付记录](scenes/S2_telegraph_building/narration/narration_v003.md)
- [地点资产卡](scenes/S2_telegraph_building/asset_card.md)

## S3A 短波通信局旧址：通信楼

适配参数：地面尺寸 `1.04 × 1.04`；地面位置 `(0.04, 0.002, 0.154748)`；模型位置 `(0.043035, 0.004, 0.176836)`；模型缩放 `0.72`。

- [触发图](scenes/S3_shortwave_station/kivicube_package/S3A_shortwave_station_building/S3A_shortwave_station_building_trigger_v001.jpg)
- [地面贴图](scenes/S3_shortwave_station/kivicube_package/S3A_shortwave_station_building/S3A_shortwave_station_building_ground_texture_v002.png)
- [V3 GLB 模型](scenes/S3_shortwave_station/kivicube_package/S3A_shortwave_station_building/S3A_shortwave_station_building_model_v003.glb)
- [当前选定音频 v003](scenes/S3_shortwave_station/kivicube_package/S3A_shortwave_station_building/S3A_shortwave_station_building_narration_v003.m4a)
- [完整参数 JSON](scenes/S3_shortwave_station/kivicube_package/S3A_shortwave_station_building/S3A_shortwave_station_building_kivicube_setup_v001.json)
- [V3 模型预览](scenes/S3_shortwave_station/images/S3A_shortwave_station_building_preview_v003.png)
- [内部参考图｜不要上传](scenes/S3_shortwave_station/kivicube_package/S3A_shortwave_station_building/S3A_shortwave_station_building_reference_reveal_v001.jpg)
- [音频交付记录](scenes/S3_shortwave_station/narration/narration_v003.md)
- [地点资产卡](scenes/S3_shortwave_station/asset_card.md)

## S3B 短波通信局旧址：天线阵列

适配参数：地面尺寸 `0.98 × 0.98`；地面位置 `(0.02, 0.002, 0)`；模型位置 `(0.02, 0.004, 0)`；模型缩放 `0.74`。

- [触发图](scenes/S3_shortwave_station/kivicube_package/S3B_shortwave_antenna_array/S3B_shortwave_antenna_array_trigger_v001.jpg)
- [地面贴图](scenes/S3_shortwave_station/kivicube_package/S3B_shortwave_antenna_array/S3B_shortwave_antenna_array_ground_texture_v002.png)
- [V3 GLB 模型](scenes/S3_shortwave_station/kivicube_package/S3B_shortwave_antenna_array/S3B_shortwave_antenna_array_model_v003.glb)
- [当前选定音频 v003｜内容与 S3A 相同，文件名独立](scenes/S3_shortwave_station/kivicube_package/S3B_shortwave_antenna_array/S3B_shortwave_antenna_array_narration_v003.m4a)
- [完整参数 JSON](scenes/S3_shortwave_station/kivicube_package/S3B_shortwave_antenna_array/S3B_shortwave_antenna_array_kivicube_setup_v001.json)
- [V3 模型预览](scenes/S3_shortwave_station/images/S3B_shortwave_antenna_array_preview_v003.png)
- [内部参考图｜不要上传](scenes/S3_shortwave_station/kivicube_package/S3B_shortwave_antenna_array/S3B_shortwave_antenna_array_reference_reveal_v001.jpg)
- [音频交付记录](scenes/S3_shortwave_station/narration/narration_v003.md)
- [地点资产卡](scenes/S3_shortwave_station/asset_card.md)

## S4A 居庸关城楼

适配参数：地面尺寸 `0.94 × 0.94`；地面位置 `(0, 0.002, 0.202123)`；模型位置 `(0, 0.004, 0.208025)`；模型缩放 `0.70`。

- [触发图](scenes/S4_juyong_pass/kivicube_package/S4A_juyong_pass_tower/S4A_juyong_pass_tower_trigger_v001.jpg)
- [地面贴图](scenes/S4_juyong_pass/kivicube_package/S4A_juyong_pass_tower/S4A_juyong_pass_tower_ground_texture_v002.png)
- [V3 GLB 模型](scenes/S4_juyong_pass/kivicube_package/S4A_juyong_pass_tower/S4A_juyong_pass_tower_model_v003.glb)
- [当前选定音频 v003](scenes/S4_juyong_pass/kivicube_package/S4A_juyong_pass_tower/S4A_juyong_pass_tower_narration_v003.m4a)
- [完整参数 JSON](scenes/S4_juyong_pass/kivicube_package/S4A_juyong_pass_tower/S4A_juyong_pass_tower_kivicube_setup_v001.json)
- [V3 模型预览](scenes/S4_juyong_pass/images/S4A_juyong_pass_tower_preview_v003.png)
- [内部参考图｜不要上传](scenes/S4_juyong_pass/kivicube_package/S4A_juyong_pass_tower/S4A_juyong_pass_tower_reference_reveal_v001.jpg)
- [音频交付记录](scenes/S4_juyong_pass/narration/narration_v003.md)
- [地点资产卡](scenes/S4_juyong_pass/asset_card.md)

## S5A 西山无名英雄纪念广场雕塑群

适配参数：地面尺寸 `1.02 × 1.02`；地面位置 `(-0.0, 0.002, -0.102508)`；模型位置 `(-0.004959, 0.004, -0.002944)`；模型缩放 `0.74`。

- [触发图](scenes/S5_memorial_plaza/kivicube_package/S5A_memorial_sculpture/S5A_memorial_sculpture_trigger_v001.jpg)
- [地面贴图](scenes/S5_memorial_plaza/kivicube_package/S5A_memorial_sculpture/S5A_memorial_sculpture_ground_texture_v002.png)
- [V3 GLB 模型](scenes/S5_memorial_plaza/kivicube_package/S5A_memorial_sculpture/S5A_memorial_sculpture_model_v003.glb)
- [当前选定音频 v003](scenes/S5_memorial_plaza/kivicube_package/S5A_memorial_sculpture/S5A_memorial_sculpture_narration_v003.m4a)
- [完整参数 JSON](scenes/S5_memorial_plaza/kivicube_package/S5A_memorial_sculpture/S5A_memorial_sculpture_kivicube_setup_v001.json)
- [V3 模型预览](scenes/S5_memorial_plaza/images/S5A_memorial_sculpture_preview_v003.png)
- [内部参考图｜不要上传](scenes/S5_memorial_plaza/kivicube_package/S5A_memorial_sculpture/S5A_memorial_sculpture_reference_reveal_v001.jpg)
- [音频交付记录](scenes/S5_memorial_plaza/narration/narration_v003.md)
- [地点资产卡](scenes/S5_memorial_plaza/asset_card.md)

## S6A 香山镇芳楼

适配参数：地面尺寸 `1.00 × 1.00`；地面位置 `(0.02, 0.002, -0.097735)`；模型位置 `(0.02, 0.004, -0.028822)`；模型缩放 `0.68`。

- [触发图](scenes/S6_zhenfang_lou/kivicube_package/S6A_zhenfang_lou/S6A_zhenfang_lou_trigger_v001.jpg)
- [地面贴图](scenes/S6_zhenfang_lou/kivicube_package/S6A_zhenfang_lou/S6A_zhenfang_lou_ground_texture_v002.png)
- [V3 GLB 模型](scenes/S6_zhenfang_lou/kivicube_package/S6A_zhenfang_lou/S6A_zhenfang_lou_model_v003.glb)
- [当前选定音频 v003](scenes/S6_zhenfang_lou/kivicube_package/S6A_zhenfang_lou/S6A_zhenfang_lou_narration_v003.m4a)
- [完整参数 JSON](scenes/S6_zhenfang_lou/kivicube_package/S6A_zhenfang_lou/S6A_zhenfang_lou_kivicube_setup_v001.json)
- [V3 模型预览](scenes/S6_zhenfang_lou/images/S6A_zhenfang_lou_preview_v003.png)
- [内部参考图｜不要上传](scenes/S6_zhenfang_lou/kivicube_package/S6A_zhenfang_lou/S6A_zhenfang_lou_reference_reveal_v001.jpg)
- [音频交付记录](scenes/S6_zhenfang_lou/narration/narration_v003.md)
- [地点资产卡](scenes/S6_zhenfang_lou/asset_card.md)

## S7A 中国电信博物馆

适配参数：地面尺寸 `1.02 × 1.02`；地面位置 `(0.02, 0.002, 0.229623)`；模型位置 `(0.020974, 0.004, 0.210792)`；模型缩放 `0.72`。

- [触发图](scenes/S7_telecom_museum/kivicube_package/S7A_telecom_museum/S7A_telecom_museum_trigger_v001.jpg)
- [地面贴图](scenes/S7_telecom_museum/kivicube_package/S7A_telecom_museum/S7A_telecom_museum_ground_texture_v002.png)
- [V3 GLB 模型](scenes/S7_telecom_museum/kivicube_package/S7A_telecom_museum/S7A_telecom_museum_model_v003.glb)
- [当前选定音频 v003](scenes/S7_telecom_museum/kivicube_package/S7A_telecom_museum/S7A_telecom_museum_narration_v003.m4a)
- [完整参数 JSON](scenes/S7_telecom_museum/kivicube_package/S7A_telecom_museum/S7A_telecom_museum_kivicube_setup_v001.json)
- [V3 模型预览](scenes/S7_telecom_museum/images/S7A_telecom_museum_preview_v003.png)
- [内部参考图｜不要上传](scenes/S7_telecom_museum/kivicube_package/S7A_telecom_museum/S7A_telecom_museum_reference_reveal_v001.jpg)
- [音频交付记录](scenes/S7_telecom_museum/narration/narration_v003.md)
- [地点资产卡](scenes/S7_telecom_museum/asset_card.md)

## 全局核对入口

- [九场景素材包索引](KIVICUBE_PACKAGE_INDEX.md)
- [七地点音频定稿索引](NARRATION_FINAL_INDEX.md)
- [Kivicube 资产技术约束](../docs/KIVICUBE_ASSET_CONSTRAINTS.md)
- [当前素材清单 CSV](asset_manifest.csv)
- [九场景本地校验报告](source/static_ground_validation_report.json)

平台上传完成后，把场景链接、识别评分、真机测试结果和回执记录到各地点的 `upload/` 目录，再将状态从 `PLATFORM_IMPORT_PENDING` 更新为已上传或已验证。
