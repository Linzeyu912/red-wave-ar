# 九个 Kivicube 轻量模型：可复现源文件

本目录保存七地点、九个独立建模单元的生成、Blender 复核与验收流水线。当前版本依据 `modeling_input/S1` 至 `S7` 的 62 张现有照片和原位迭代的 [`DETAIL_EXTRACTION_V2.md`](../../modeling_input/DETAIL_EXTRACTION_V2.md) 制作 V3 细节版模型，并生成与底材连续的 V002 专属地面贴图。2026-08-04 的 V2.2 复核保留了已确认体块，统一纠正 S1A、S2A、S3A、S6A、S7A 的入口台阶方向，重点重建 S1B 人物/设备和 S3B 四臂桁架/帘幕线网；未新建交付目录或模型版本。S1B 使用低于 50,000 三角面硬上限的近景人物专项预算，并保持单一 GLB 整体上传。模型不是 1:1 测绘复刻，照片没有覆盖的侧面、背面和屋顶按 `INFERRED_LOW_DETAIL` 保守闭合。

## 交付内容

- `build_models.py`：生成几何、材质、原创文字贴图和九个嵌入式 GLB。
- `glbkit.py`：本项目的轻量 glTF 2.0/GLB 写出器，使用米制单位、Y 轴向上、正面朝 -Z。
- `blender_review.py`：用 Blender 5.1.2 逐个导入 GLB，保存可编辑 `.blend`，并渲染预览。
- `validate_models.py`：检查 GLB 结构、嵌入资源与 Kivicube 文件/网格/三角面/材质/贴图预算。
- `make_contact_sheet.py`：把九张预览合成总览，并同步到 `../images/kivicube_model_previews_3x3.png`，供 Kivicube 素材包索引 README 直接展示。
- `presentation_profiles.json`：九个模型的触发图、内部参考来源、V002 地面材料族、尺寸与静态位置交接参数。
- `make_presentation_handoff.py`：结合最终 GLB 包围盒计算 Kivicube 正方形地面、精确位置与自动适配后的缩放值。
- `presentation_handoff_report.json`：可直接照录到场景编辑器的静态地面与模型布局结果。
- `prepare_all_kivicube_packages.py`：复制原手绘触发图，生成九个 V002 地面贴图与静态 Kivicube 包配置。
- `ground_texture_inputs/`：九张可追踪的 V002 地面材质源；由生成脚本统一归一到 `1024×1024` 并按模型足迹叠加轻微接触阴影。
- `blender_ground_contact_review.py`：按 Kivicube 的静态摆放参数渲染九个“V002 地面＋完整 GLB”贴地预览。
- `make_static_ground_contact_sheet.py`：生成并发布九单元贴地总览 `../images/kivicube_model_ground_contact_3x3.png`。
- `make_reference_detail_sheets.py`：将每个地点全部受控照片生成带文件名的私有细节复核图，不复制到公开交付目录。
- `build_and_review.ps1`：Windows 一键重建与验收入口。
- `blend/`：从最终 GLB 回读后保存的可继续编辑源文件；这些文件和 GLB 均由 Git LFS 管理。
- `build_report.json`、`blender_review_report.json`、`validation_report.json`：三层机器可读验收证据。
- `model_contact_sheet.png`：九个模型的统一视觉总览。

生成过程中使用的文字图集位于忽略目录 `.build/`，贴图已经嵌入 GLB 和 `.blend`，不需要作为独立上传文件。

真实参考照片和细节复核图只用于内部检查；照片不作为当前 Kivicube 场景对象。V002 地面贴图以模型接触材质为色彩桥接，叠加轻微接触阴影，并输出到每个 `kivicube_package/` 目录和 `../images/kivicube_ground_textures_3x3.png`。

## 一键重建

在仓库根目录运行：

```powershell
.\lkivivube_delivery\source\build_and_review.ps1
```

脚本默认使用 `D:\blender-5.1.2-windows-x64\blender.exe`。其他安装位置可显式指定：

```powershell
.\lkivivube_delivery\source\build_and_review.ps1 -BlenderExe 'C:\Tools\Blender\blender.exe'
```

命令必须以 `[PASS]` 输出九个模型且最终报告状态为 `PASS` 才能进入 Kivicube 上传测试。重新生成会覆盖同名 V3 GLB、`.blend`、预览和报告，不会改动受控参考图。

## 人工视觉验收

自动验收通过后仍需打开 `model_contact_sheet.png`、每个场景 `images/*_preview_v003.png`、私有 `.build/reference_detail_sheets/`、`../images/kivicube_ground_textures_3x3.png` 和 `../images/kivicube_model_ground_contact_3x3.png`，按对应 `modeling_input/S?/visual_constraints.md` 及二次细节提取检查：

1. 主体剪影、体块关系、标志性构件和真实配色一致；
2. 牌匾文字没有镜像或错序；
3. 参考图未覆盖的面没有虚构高细节；
4. 不含游客、树木、车辆、水印、祭扫物品等排除项；
5. 一个触发图只绑定对应的一个 GLB；
6. 模型最低点与 V002 专属地面贴图贴合，不带通用厚展台；
7. 地面颜色、材料颗粒和接触阴影与模型底材连续，无突兀色带或厚底座；
8. 参考照片只用于内部主体核对，不配置为 AR 展示图。

Kivicube 的最终网页端/微信小程序端上传、识别和设备性能测试不由本地脚本替代，平台回执继续记录到各场景的 `upload/`。
