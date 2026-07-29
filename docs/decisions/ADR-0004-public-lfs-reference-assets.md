# ADR-0004：参考素材通过 Git LFS 进入公开仓库

> 日期：2026-07-29
> 状态：`ACCEPTED`

## 背景

S1–S7 的建模输入包含 JPG、JPEG、PNG、WEBP 和 Word 文件，部分原图体积较大。此前各 `local_reference/` 使用 `.gitignore` 排除所有原始素材，导致远程仓库无法保存建模依据。

远程仓库 `Linzeyu912/red-wave-ar` 为公开仓库。2026-07-29，用户在知悉 Git LFS 不提供隐私保护、文件仍会公开的情况下，确认将 S1–S7 当前图片和 Word 参考素材上传。

## 决策

- S1–S7 的图片与 Word 参考素材使用 Git LFS 版本化。
- GLB、GLTF、FBX、Blend、无损音频和视频等后续大体积交付也使用 Git LFS。
- PDF、`_source.*` 和其他明确标记的敏感源文件继续由根 `.gitignore` 排除。
- Git LFS 入库只解决版本管理和传输，不代表素材已经获得纹理使用权、宣传权或 Kivicube AR 公开展示许可。
- 公开展示许可、隐私处理、水印和来源风险继续在 `asset_manifest.csv` 与逐场景资产卡中单独跟踪。

## 结果

- 克隆仓库并需要完整素材时，开发者必须安装 Git LFS 并执行 `git lfs pull`。
- 不得用普通 Git 提交绕过 `.gitattributes` 中的 LFS 规则。
- 新增素材前仍需排查身份证号、手机号、未公开申报材料等敏感信息；用户本次确认不自动覆盖未来新增文件。
- S5 当前带“百度百科”水印的照片可以作为公开仓库中的建模参考记录，但仍不能直接作为 AR 展示图。
