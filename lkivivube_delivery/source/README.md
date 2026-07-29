# 九个 Kivicube 轻量模型：可复现源文件

本目录保存七地点、九个独立建模单元的生成、Blender 复核与验收流水线。当前版本是依据 `modeling_input/S1` 至 `S7` 已有照片约束制作的 V1 轻量写实模型，不是 1:1 测绘复刻；照片没有覆盖的侧面、背面和屋顶按 `INFERRED_LOW_DETAIL` 保守闭合。

## 交付内容

- `build_models.py`：生成几何、材质、原创文字贴图和九个嵌入式 GLB。
- `glbkit.py`：本项目的轻量 glTF 2.0/GLB 写出器，使用米制单位、Y 轴向上、正面朝 -Z。
- `blender_review.py`：用 Blender 5.1.2 逐个导入 GLB，保存可编辑 `.blend`，并渲染预览。
- `validate_models.py`：检查 GLB 结构、嵌入资源与 Kivicube 文件/网格/三角面/材质/贴图预算。
- `make_contact_sheet.py`：把九张预览合成总览。
- `build_and_review.ps1`：Windows 一键重建与验收入口。
- `blend/`：从最终 GLB 回读后保存的可继续编辑源文件；这些文件和 GLB 均由 Git LFS 管理。
- `build_report.json`、`blender_review_report.json`、`validation_report.json`：三层机器可读验收证据。
- `model_contact_sheet.png`：九个模型的统一视觉总览。

生成过程中使用的文字图集位于忽略目录 `.build/`，贴图已经嵌入 GLB 和 `.blend`，不需要作为独立上传文件。

## 一键重建

在仓库根目录运行：

```powershell
.\lkivivube_delivery\source\build_and_review.ps1
```

脚本默认使用 `D:\blender-5.1.2-windows-x64\blender.exe`。其他安装位置可显式指定：

```powershell
.\lkivivube_delivery\source\build_and_review.ps1 -BlenderExe 'C:\Tools\Blender\blender.exe'
```

命令必须以 `[PASS]` 输出九个模型且最终报告状态为 `PASS` 才能进入 Kivicube 上传测试。重新生成会覆盖同名 V1 GLB、`.blend`、预览和报告，不会改动受控参考图。

## 人工视觉验收

自动验收通过后仍需打开 `model_contact_sheet.png` 和每个场景 `images/*_preview_v001.png`，按对应 `modeling_input/S?/visual_constraints.md` 检查：

1. 主体剪影、体块关系、标志性构件和真实配色一致；
2. 牌匾文字没有镜像或错序；
3. 参考图未覆盖的面没有虚构高细节；
4. 不含游客、树木、车辆、水印、祭扫物品等排除项；
5. 一个触发图只绑定对应的一个 GLB。

Kivicube 的最终网页端/微信小程序端上传、识别和设备性能测试不由本地脚本替代，平台回执继续记录到各场景的 `upload/`。
