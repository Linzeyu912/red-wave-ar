# 建模参考地点资料库

> 状态：`LOCAL_REFERENCE_ONLY / NOT_RUNTIME_INTEGRATED`
> 导入日期：2026-07-27
> 原始资料包：`red-wave-ar素材约束与要求`

本目录收纳尚未分配正式场景 ID 的建模输入。原始图片和 Word 文件均保留在各地点的 `local_reference/source_folder_20260727/`，文件名及层级与用户提供的资料包一致；它们由 `.gitignore` 排除，不进入 Git、App、GLB、识图库或宣传素材。

| 原始地点目录 | 仓库位置 | 文件数 | 当前处理 |
|---|---|---:|---|
| 电报大楼 | `telegraph_building/` | 9 | 待建立场景任务书 |
| 短波通信局 | `shortwave_communication_bureau/` | 8 | 待建立场景任务书 |
| 居庸关 | `juyongguan/` | 8 | 待建立场景任务书 |
| 西山无名英雄纪念广场 | `xishan_unknown_heroes_memorial_plaza/` | 8 | 待建立场景任务书 |
| 香山镇芳楼 | `xiangshan_fanglou/` | 8 | 待建立场景任务书 |
| 中国电信博物馆 | `telecom_museum/` | 6 | 待建立场景任务书 |
| 平西情报联络站 | `../S1/local_reference/source_folder_20260727/` | 7 | 已并入现有 S1 输入包，见 `S1/05_SOURCE_FOLDER_IMPORT.md` |

共导入 54 个原始文件：47 张图片和 7 个 Word 文件。除“平西情报联络站文字素材.docx”含可读正文外，其余 5 个地点的 Word 文件为 0 字节；“西山无名英雄纪念广场文字素材.docx”虽然非空，但未包含可提取的正文。两种情况均不构成可执行建模要求。

## 使用边界

- 原图只用于内部观察、比例和材质层级研究；未经来源、版权及发布用途确认，不得作为照片纹理、图片投射、App 内容、识图目标或宣传素材。
- 本资料库没有创建新的 `scene_id`，也没有修改 `global_manifest.json`、`scene.json` 或运行时资源。
- 每个新地点在进入建模前，必须先建立单独的场景任务书、权利登记、性能预算和验收条件；不能仅凭参考图推断历史原貌、尺寸、题字、设备型号或人物信息。
- 需要公开、进 App 或精确复刻时，必须新增来源/授权记录并获得用户确认。
