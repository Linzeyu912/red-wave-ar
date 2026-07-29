# 建模场景索引：S1–S7

> 状态：`PLATFORM_INPUT_INDEX / AWAITING_PER_SCENE_CONSTRAINTS`
> 更新日期：2026-07-29

所有当前建模输入按场景编号归档在 `modeling_input/S1` 至 `modeling_input/S7`，并只服务 LKIVIVUBE 平台线。自研 App 的旧 S1 建模口令已移入 `archive/self_built_app/`；现有白盒仍留在 `modeling_delivery/S1/` 以维持构建和追溯。两个输出不得自动互相复用。

## 地点对照表

新增建模约束素材时，**先对照本表确认场景编号、地点、英文 slug 和输入目录**，再放到对应场景的 `local_reference/source_folder_*/` 下。英文 slug 只用于 `lkivivube_delivery/scenes/<S?>_<slug>/` 的平台交付命名。

| 场景 | 地点（中文） | 英文 slug（交付目录名） | 建模输入入口 | 本地原始文件 | 自研程序线 | LKIVIVUBE 平台线 |
|---|---|---|---|---:|---|---|
| S1 | 平西情报联络站 | `pingxi_intelligence_station` | `S1/00_START_HERE.md` | 12 项受控素材 + 已归档门楼模型 | 旧版地下电台白盒已接入；新增资料不自动接入 | 等待地点外观约束；不得直接使用旧地下室/门楼 GLB |
| S2 | 电报大楼 | `telegraph_building` | `S2/00_START_HERE.md` | 9 | 未创建 | 等待形象约束与旁白文字 |
| S3 | 短波通信局 | `shortwave_station` | `S3/00_START_HERE.md` | 8 | 未创建 | 等待形象约束与旁白文字 |
| S4 | 居庸关 | `juyong_pass` | `S4/00_START_HERE.md` | 8 | 未创建 | 等待形象约束与旁白文字 |
| S5 | 西山无名英雄纪念广场 | `memorial_plaza` | `S5/00_START_HERE.md` | 8 | 未创建 | 等待形象约束与旁白文字 |
| S6 | 香山镇芳楼 | `zhenfang_lou` | `S6/00_START_HERE.md` | 8 | 未创建 | 等待形象约束与旁白文字 |
| S7 | 中国电信博物馆 | `telecom_museum` | `S7/00_START_HERE.md` | 6 | 未创建 | 等待形象约束与旁白文字 |

## 添加建模约束素材

1. 对照上表确认目标场景编号（S1–S7）与地点。
2. 把新素材（参考图、文字资料、测绘约束、比例/材质说明等）放入该场景的 `local_reference/source_folder_20260727/`。
3. 既有手绘触发图继续按 `trigger_hand_drawn.jpg` 保存；它们目前只作路线/研究参考，不预设为 LKIVIVUBE 的触发或上传素材。
4. 原始文件始终由 `local_reference/.gitignore`（`*` + `!.gitignore`）排除，不进库；如需登记到可追踪清单，写到该场景的 `00_START_HERE.md` 或单独 manifest。
5. 每个场景开始建模前，必须先补充权利/来源登记、任务范围、性能预算、输出命名和验收标准。

所有原图和 Word 文件均在各场景的 `local_reference/source_folder_20260727/`，由 `.gitignore` 排除；不得直接进入 App、GLB、识图、纹理或公开宣传。

## 输出分流规则

- **LKIVIVUBE 主交付**：每个地点最终在 `../lkivivube_delivery/scenes/<S?>_<slug>/` 下交付一个 5–10 MB 的 `.glb`、平台预览图片、可审核旁白文字和上传元数据。建模尚未开始前，只填写该目录中的 `asset_card.md`。
- **自研程序线**：`../modeling_delivery/` 只保留既有 Android / Filament 运行时资产、白盒和验证材料；历史建模口令见 `../archive/self_built_app/`。除非另有明确决定，不将平台 GLB 复制或接入 `app/`。
- **共享路线附件**：路线图等跨地点素材登记在 `../modeling_input/_shared/`。原始文件仍受控且不进 Git；其许可未核验时不得充当纹理、平台封面或公开宣传图。
