# 红色电波（red-wave-ar）

《永不消逝的红色电波》项目工作区。当前采用双线并行：保留并优化已有自研 Android 体验，同时以 Kivicube 为主要 AR 呈现平台，制作“红色电波实践路线”七个地点、九个触发与建模单元的轻量模型、图片和旁白素材。

> 当前项目方向以 [`docs/PROJECT_DIRECTION.md`](docs/PROJECT_DIRECTION.md) 为准。旧地下电台白盒和自研虚拟展馆计划已归档，不再作为新平台建模入口。

## 从这里开始

| 你要做的事 | 唯一入口 |
|---|---|
| 查看当前项目范围与双线边界 | [`docs/PROJECT_DIRECTION.md`](docs/PROJECT_DIRECTION.md) |
| 查看 Kivicube 建模、触发图和素材约束 | [`docs/KIVICUBE_ASSET_CONSTRAINTS.md`](docs/KIVICUBE_ASSET_CONSTRAINTS.md) |
| 补充某个地点的图片、文字或建模约束 | [`modeling_input/README.md`](modeling_input/README.md) |
| 查看 9 个触发图、真实照片与模型对应关系 | [`modeling_input/REFERENCE_INVENTORY.md`](modeling_input/REFERENCE_INVENTORY.md) |
| 查看 62 张图片提取出的主体特征与提示词素材 | [`modeling_input/VISUAL_CONSTRAINTS_INDEX.md`](modeling_input/VISUAL_CONSTRAINTS_INDEX.md) |
| 查看主体身份、同地点一致性与公开资料核验 | [`modeling_input/SUBJECT_IDENTITY_VERIFICATION.md`](modeling_input/SUBJECT_IDENTITY_VERIFICATION.md) |
| 查看或交付 Kivicube 模型、图片与旁白 | [`lkivivube_delivery/README.md`](lkivivube_delivery/README.md) |
| 维护已有 Android / Filament 程序 | [`docs/CODE_HANDOFF.md`](docs/CODE_HANDOFF.md) |
| 构建或测试自研程序 | [`docs/BUILD.md`](docs/BUILD.md) |
| 查阅旧地下电台任务与产品计划 | [`archive/self_built_app/README.md`](archive/self_built_app/README.md) |

## 两条工作线

| 工作线 | 目标 | 活动目录 | 状态 |
|---|---|---|---|
| Kivicube 平台素材 | 七个地点、九个触发单元的 GLB、触发图、真实照片、旁白和上传记录 | `modeling_input/`、`lkivivube_delivery/` | 9 个 V2 GLB 与照片平面衔接已完成本地验收；等待权利确认、后续文字和平台真机验证 |
| 自研程序 | 维护和优化已有 Android / Filament 虚拟研学体验 | `app/`、`modeling_delivery/`、`docs/` | 保留维护，不以真机 AR 连接为当前主阻塞项 |

两条线不得自动混用模型。平台 GLB 不直接复制到 `app/src/main/assets/`；自研 S1 地下电台白盒和门楼也不直接上传到 Kivicube。

## 当前地点

| 场景 | 地点 | 平台状态 |
|---|---|---|
| S1 | 平西情报联络站 | 2 个单元：入口门楼、女报务员雕塑；图片和文字已收到 |
| S2 | 电报大楼 | 1 个单元；图片已收到，文字待补 |
| S3 | “短波通信局”（项目暂定名） | 2 个单元：通信楼、天线阵列；图片已收到，外部身份与文字待核验 |
| S4 | 居庸关 | 1 个单元；图片已收到，文字待补 |
| S5 | 西山无名英雄纪念广场 | 1 个单元；图片已收到，文字待补 |
| S6 | 香山镇芳楼 | 1 个单元；图片已收到，文字待补 |
| S7 | 中国电信博物馆 | 1 个单元；图片已收到，文字待补 |

稳定场景编号、slug 和输入路径见 [`modeling_input/SCENE_INDEX.md`](modeling_input/SCENE_INDEX.md)。

## 目录结构

```text
red-wave-ar/
├── README.md                         # 当前总入口
├── docs/
│   ├── PROJECT_DIRECTION.md          # 项目级单一事实来源
│   ├── KIVICUBE_ASSET_CONSTRAINTS.md # 平台建模与素材技术约束
│   ├── CODE_HANDOFF.md               # 自研程序交接
│   └── BUILD.md                      # 构建与测试
├── modeling_input/
│   ├── README.md                     # 当前建模输入总入口
│   ├── SCENE_INDEX.md                # S1–S7 场景索引
│   ├── REFERENCE_INVENTORY.md         # 9 个触发/照片/模型单元清单
│   ├── VISUAL_CONSTRAINTS_INDEX.md    # 62 张图片的主体特征与提示词索引
│   ├── SUBJECT_IDENTITY_VERIFICATION.md # 主体一致性与公开资料核验
│   └── S1/ ... S7/                   # 逐地点受控输入
├── lkivivube_delivery/
│   ├── README.md                     # Kivicube 平台交付规范（目录名沿用旧拼写）
│   ├── asset_manifest.csv            # 七地点、九建模单元状态总表
│   └── scenes/                       # GLB、图片、旁白、上传记录
├── app/                              # 自研 Android 代码
├── modeling_delivery/                # 自研程序线模型与白盒
├── research/                         # 旧 S1 研究和事实核验档案
└── archive/self_built_app/           # 旧产品计划与地下电台任务
```

## 当前交付规则

- 每张触发图对应一个独立 GLB；七个地点共九个模型。每个 GLB 目标不超过 5 MB、验收上限为 10 MB，不设文件大小下限。
- 统一呈现顺序为“红白手绘触发图识别 → 同位置覆盖获准的 1:1 真实参考照片卡 → 模型从照片主体下缘贴地展开 → 旁白”；照片保留为模型底部环境，不使用传统通用厚展台。
- 缺少其他视角不再阻塞建模；不可见面按低细节保守推断并明确标记，不虚构标志性建筑细节。
- S1–S7 的图片与 Word 参考素材经用户确认上传到公开仓库，并统一使用 Git LFS；PDF 和明确标记的敏感源文件仍不入库。
- Git LFS 只解决大文件存储，不代表照片的版权、隐私或 Kivicube 公开展示许可已经通过；相关状态继续在资产卡中单独审核。
- 平台约束以 [`docs/KIVICUBE_ASSET_CONSTRAINTS.md`](docs/KIVICUBE_ASSET_CONSTRAINTS.md) 为准；场景特有的未确认项保持“待确认”。
- 旁白必须有事实来源和审核状态，不能把未核验参考文字直接作为正式讲解。

## 自研程序快速入口

自研程序使用 Kotlin、Jetpack Compose 与 Filament，最低 Android 8.0（API 26）。本仓库保留 Gradle Wrapper：

```bash
./gradlew testDebugUnitTest
./gradlew assembleDebug
```

构建环境、JDK 17、Android SDK 和 Windows 路径说明统一维护在 [`docs/BUILD.md`](docs/BUILD.md)，不再在根 README 重复。
