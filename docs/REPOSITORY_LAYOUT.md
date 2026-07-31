# 仓库目录与维护边界

本说明用于帮助维护者判断文件应放在哪里、哪些目录可以清理，以及哪些路径不能随意调整。项目有两条并行工作线：Kivicube 平台素材线和自研 Android 程序线；两条线的交付物不得互相替代。

项目范围与优先级以 [`PROJECT_DIRECTION.md`](PROJECT_DIRECTION.md) 为准；平台素材的技术限制以 [`KIVICUBE_ASSET_CONSTRAINTS.md`](KIVICUBE_ASSET_CONSTRAINTS.md) 为准。

## 顶层目录

| 路径 | 职责 | 写入规则 |
|---|---|---|
| `app/` | Kotlin、Compose、Filament 自研 Android 程序及其运行时 assets | 仅放自研程序代码和已验收的自研运行时资源 |
| `docs/` | 项目规则、构建说明、交接说明和架构决策记录 | 项目级文档的唯一位置；决策记录放入 `docs/decisions/` |
| `modeling_input/` | Kivicube 建模输入：按 S1–S7 分组的参考图、文字与视觉约束 | 新地点素材先登记在对应 `S?/`，不要从旧资料直接拷入交付目录 |
| `lkivivube_delivery/` | Kivicube 交付：GLB、预览图、资产卡和可复现的生成脚本 | 仅放平台交付物及其生成源码；目录名沿用历史拼写，禁止重命名 |
| `modeling_delivery/` | 自研 Android 线的白盒模型、运行时资源和验收材料 | 不作为 Kivicube 上传素材来源 |
| `research/` | 历史研究、事实核验与来源登记 | 仅作资料追溯；新增正式约束应回写到当前输入或项目文档 |
| `archive/` | 已停止的自研方案和历史任务 | 只读归档；不作为新任务入口 |
| `发票留存/` | 与项目相关的受控票据 | 仅保留经确认可入库的清单与票据；不要混入技术素材 |
| `gradle/`、根目录 Gradle 文件 | Android 构建配置与 Wrapper | 按 Gradle/Android 升级流程维护 |

## Kivicube 素材流

```text
modeling_input/S?/local_reference/
        ↓ 受控输入、事实与视觉约束
modeling_input/S?/00_START_HERE.md
        ↓ 建模与验收依据
lkivivube_delivery/scenes/S?_*/
        ↓ 平台交付（GLB、预览图、资产卡）
Kivicube 平台上传与真机验证
```

- 新任务从 `modeling_input/README.md` 进入，再进入对应地点的 `00_START_HERE.md`。
- 交付状态以 `lkivivube_delivery/asset_manifest.csv` 和各场景 `asset_card.md` 为准。
- `lkivivube_delivery/source/` 保存生成和验收脚本；脚本产出的 `.build/` 内容是本地临时文件，不提交。
- `lkivivube_delivery/` 的拼写是稳定路径的一部分，已被脚本、报告和文档引用，不能改为其他名称。

## 自研程序素材流

```text
research/ 与 modeling_delivery/
        ↓ 经过自研线验收的资源
app/src/main/assets/
        ↓
app/（Android 程序）
```

- 自研程序构建、测试和环境说明见 [`BUILD.md`](BUILD.md)。
- Kivicube GLB 不直接复制到 `app/src/main/assets/`；反向亦然。
- 运行时资源如需更新，应同时检查对应的应用清单、测试和 `modeling_delivery/` 验收材料。

## 本地文件与清理规则

下列内容均为本地生成物或敏感资料，已由 `.gitignore` 排除，可在确认没有正在运行的构建、建模或资料处理任务后自行清理：

- `.gradle/`、`.kotlin/`、`app/build/`：Gradle/Kotlin 构建缓存和产物；
- `.venv/`、`__pycache__/`、`lkivivube_delivery/source/.build/`：建模脚本虚拟环境与生成缓存；
- `tmp/`、`.zcode/`：临时工作文件；
- `_source.*` 和一般 PDF：源资料或敏感资料。`发票留存/*.pdf` 是经明确允许保留的例外，不能按普通临时文件处理。

清理前不要删除 Git LFS 已跟踪的 `.glb`、`.blend`、图片或 Word 参考资料；这些是仓库可复现交付的一部分。可用 `git status --ignored` 区分受忽略的本地文件与受版本控制的交付物。

## 变更前检查

1. 新增或更新 Kivicube 素材时，确认其落在对应场景的输入或交付目录，并同步资产卡/清单。
2. 修改路径、场景 slug 或文件名之前，先检索 `README`、JSON 报告、脚本和 Android assets 中的引用。
3. 提交前确认 `git status` 只包含预期文件；不要提交构建缓存、未确认资料或临时渲染产物。
