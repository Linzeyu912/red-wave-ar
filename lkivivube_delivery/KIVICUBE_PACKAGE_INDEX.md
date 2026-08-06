# Kivicube 场景素材包索引

所有 7 个地点、9 个模型均按同一流程交付：**原手绘触发图 → 专属地面贴图与静态模型**。绘制触发图的参考原图保留在包内，仅供内部核对，不作为 AR 展示对象。

## 当前 3D 建模预览

![九个模型预览｜会随构建流程自动更新](images/kivicube_model_previews_3x3.png)

## 触发图与适配预览

![原手绘触发图｜9 个模型](images/kivicube_trigger_images_3x3.png)

![绘制触发图的参考原图｜9 个模型](images/kivicube_trigger_reference_images_3x3.png)

![模型出现时的地面贴图｜9 个模型](images/kivicube_ground_textures_3x3.png)

![静态模型与地面贴图的贴地预览｜9 个模型](images/kivicube_model_ground_contact_3x3.png)

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
- 地面贴图：每个模型单独一张 V002、均为 `1024×1024`；使用无光照正方形平面，模型转换后占地中心与地面中心重合，四周按单元留 `0.12–0.18`，地面为 `Y=0.002`，模型为 `Y=0.004`。入口台阶由 GLB 几何表达，正面仅以同材质地面承接。
- 时间线：`0.00s` 识别触发图，`0.10s` 同时显示地面贴图与静态 GLB，`0.80s` 播放旁白；不自动播放 `photo_emerge`。

每个单元的精确位置、正方形地面尺寸、颜色衔接说明和模型缩放在其 `kivicube_setup.json` 中。全部原图仍仅可用于内部核对；涉及来源、人物隐私或仓库公开时，仍必须按各包 `ASSET_MANIFEST.json` 中的权限状态处理。

贴地预览由 Blender 按同一静态位置和缩放参数生成，用于检查地面与模型底部的连续感；Kivicube 真机中的环境光会不同，但不得出现明显色带、厚展台或黑色底座效果。
