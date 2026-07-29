# 建模场景索引：S1–S7

> 状态：`PLATFORM_INPUT_INDEX / 7_SITES_9_MODEL_UNITS / VISUAL_INPUT_RECEIVED`
> 更新日期：2026-07-29

所有当前建模输入按场景编号归档在 `modeling_input/S1` 至 `modeling_input/S7`，并只服务 Kivicube 平台线。自研 App 的旧 S1 建模口令已移入 `archive/self_built_app/`；现有白盒仍留在 `modeling_delivery/S1/` 以维持构建和追溯。两个输出不得自动互相复用。

## 地点对照表

新增建模约束素材时，**先对照本表确认场景编号、地点、建模单元和输入目录**，再放到对应场景的 `local_reference/source_folder_*/` 下。九个单元的文件级对应见 [`REFERENCE_INVENTORY.md`](REFERENCE_INVENTORY.md)。

| 场景 | 地点（中文） | 建模单元 | 建模输入入口 | 受控文件数 | Kivicube 平台线 |
|---|---|---|---|---:|---|
| S1 | 平西情报联络站 | S1A 入口门楼；S1B 女报务员雕塑 | `S1/00_START_HERE.md` | 14 | 图片与 S1 文字已收到；公开权待确认 |
| S2 | 电报大楼 | S2A 电报大楼 | `S2/00_START_HERE.md` | 11 | 图片已收到；文字与公开权待确认 |
| S3 | 短波通信局 | S3A 通信楼；S3B 天线阵列 | `S3/00_START_HERE.md` | 10 | 图片已收到；文字与公开权待确认 |
| S4 | 居庸关 | S4A 居庸关城楼 | `S4/00_START_HERE.md` | 9 | 图片已收到；文字与公开权待确认 |
| S5 | 西山无名英雄纪念广场 | S5A 纪念雕塑群 | `S5/00_START_HERE.md` | 9 | 图片已收到；文字待补，展示照片需解决水印/权利 |
| S6 | 香山镇芳楼 | S6A 镇芳楼 | `S6/00_START_HERE.md` | 9 | 图片已收到；文字与公开权待确认 |
| S7 | 中国电信博物馆 | S7A 博物馆主体 | `S7/00_START_HERE.md` | 7 | 图片已收到；文字与公开权待确认 |

## 添加建模约束素材

1. 对照上表确认目标场景编号（S1–S7）与地点。
2. 把新素材（参考图、文字资料、测绘约束、比例/材质说明等）放入该场景的 `local_reference/source_folder_20260727/`。
3. 各场景的第一张手绘图按 `trigger_hand_drawn.jpg` 保存；S1、S3 的第二张触发图及对应模型按 [`REFERENCE_INVENTORY.md`](REFERENCE_INVENTORY.md) 登记。每张都必须通过权利审核、识别评分和真实印刷品真机测试。
4. 单独登记绘制手绘图时使用的真实参考照片。只有取得公开展示许可后，才制作 `<scene>_reference_reveal_vNNN.jpg` 并用于识别后的照片展示。
5. 模型采用真实配色，颜色与材质以核验后的真实照片和文字约束为依据，不从红白触发图取色。
6. S1–S7 的图片和 Word 经用户确认使用 Git LFS 上传到公开仓库；PDF、`_source.*` 和其他明确标记的敏感文件仍不入库。
7. 不再要求继续补齐其他角度；缺失视角按低细节保守推断并标记 `INFERRED_LOW_DETAIL`。
8. 每个建模单元开始前，必须先补充权利/来源登记、任务范围、性能预算、输出命名和验收标准。

所有原图和 Word 文件均在各场景的 `local_reference/source_folder_20260727/`，使用 Git LFS 版本化。LFS 入库不改变素材权利状态；未经资产卡审核，仍不得直接进入 App、GLB 纹理或 AR 公开展示。

## 输出分流规则

- **Kivicube 主交付**：每张触发图交付一个目标 ≤5 MB、验收 ≤10 MB 的 `.glb`。七个地点共九套触发图、真实照片展示图、模型与上传元数据；同一地点的多个模型共用其场景目录和资产卡。
- **自研程序线**：`../modeling_delivery/` 只保留既有 Android / Filament 运行时资产、白盒和验证材料；历史建模口令见 `../archive/self_built_app/`。除非另有明确决定，不将平台 GLB 复制或接入 `app/`。
- **共享路线附件**：路线图等跨地点素材登记在 `../modeling_input/_shared/`。原始文件仍受控且不进 Git；其许可未核验时不得充当纹理、平台封面或公开宣传图。
