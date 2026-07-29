# 红色电波（red-wave-ar）

《永不消逝的红色电波》项目工作区。当前采用双线并行：保留并优化已有自研 Android 体验，同时以 LKIVIVUBE 为主要 AR 呈现平台，制作“红色电波实践路线”七个地点的轻量模型、图片和旁白素材。

> 当前项目方向以 [`docs/PROJECT_DIRECTION.md`](docs/PROJECT_DIRECTION.md) 为准。旧地下电台白盒和自研虚拟展馆计划已归档，不再作为新平台建模入口。

## 从这里开始

| 你要做的事 | 唯一入口 |
|---|---|
| 查看当前项目范围与双线边界 | [`docs/PROJECT_DIRECTION.md`](docs/PROJECT_DIRECTION.md) |
| 补充某个地点的图片、文字或建模约束 | [`modeling_input/README.md`](modeling_input/README.md) |
| 查看或交付 LKIVIVUBE 模型、图片与旁白 | [`lkivivube_delivery/README.md`](lkivivube_delivery/README.md) |
| 维护已有 Android / Filament 程序 | [`docs/CODE_HANDOFF.md`](docs/CODE_HANDOFF.md) |
| 构建或测试自研程序 | [`docs/BUILD.md`](docs/BUILD.md) |
| 查阅旧地下电台任务与产品计划 | [`archive/self_built_app/README.md`](archive/self_built_app/README.md) |

## 两条工作线

| 工作线 | 目标 | 活动目录 | 状态 |
|---|---|---|---|
| LKIVIVUBE 平台素材 | 七个地点的 GLB、预览图片、旁白和上传记录 | `modeling_input/`、`lkivivube_delivery/` | 等待逐地点形象约束 |
| 自研程序 | 维护和优化已有 Android / Filament 虚拟研学体验 | `app/`、`modeling_delivery/`、`docs/` | 保留维护，不以真机 AR 连接为当前主阻塞项 |

两条线不得自动混用模型。平台 GLB 不直接复制到 `app/src/main/assets/`；自研 S1 地下电台白盒和门楼也不直接上传到 LKIVIVUBE。

## 当前地点

| 场景 | 地点 | 平台状态 |
|---|---|---|
| S1 | 平西情报联络站 | 等待新的地点外观与旁白约束 |
| S2 | 电报大楼 | 等待形象约束与旁白文字 |
| S3 | 短波通信局 | 等待形象约束与旁白文字 |
| S4 | 居庸关 | 等待形象约束与旁白文字 |
| S5 | 西山无名英雄纪念广场 | 等待形象约束与旁白文字 |
| S6 | 香山镇芳楼 | 等待形象约束与旁白文字 |
| S7 | 中国电信博物馆 | 等待形象约束与旁白文字 |

稳定场景编号、slug 和输入路径见 [`modeling_input/SCENE_INDEX.md`](modeling_input/SCENE_INDEX.md)。

## 目录结构

```text
red-wave-ar/
├── README.md                         # 当前总入口
├── docs/
│   ├── PROJECT_DIRECTION.md          # 项目级单一事实来源
│   ├── CODE_HANDOFF.md               # 自研程序交接
│   └── BUILD.md                      # 构建与测试
├── modeling_input/
│   ├── README.md                     # 当前建模输入总入口
│   ├── SCENE_INDEX.md                # S1–S7 场景索引
│   └── S1/ ... S7/                   # 逐地点受控输入
├── lkivivube_delivery/
│   ├── README.md                     # 平台交付规范
│   ├── asset_manifest.csv            # 七地点状态总表
│   └── scenes/                       # GLB、图片、旁白、上传记录
├── app/                              # 自研 Android 代码
├── modeling_delivery/                # 自研程序线模型与白盒
├── research/                         # 旧 S1 研究和事实核验档案
└── archive/self_built_app/           # 旧产品计划与地下电台任务
```

## 当前交付规则

- 每个地点最终交付一个独立 GLB，单文件 5–10 MB。
- 未收到地点形象约束前，不生成模型或虚构建筑细节。
- 原始参考图片和含隐私的材料不提交 Git；只提交约束摘要、来源状态和获准的交付素材。
- 平台未确认的动画、纹理、坐标、封面和上传字段保持“待确认”。
- 旁白必须有事实来源和审核状态，不能把未核验参考文字直接作为正式讲解。

## 自研程序快速入口

自研程序使用 Kotlin、Jetpack Compose 与 Filament，最低 Android 8.0（API 26）。本仓库保留 Gradle Wrapper：

```bash
./gradlew testDebugUnitTest
./gradlew assembleDebug
```

构建环境、JDK 17、Android SDK 和 Windows 路径说明统一维护在 [`docs/BUILD.md`](docs/BUILD.md)，不再在根 README 重复。
