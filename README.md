# 红色电波（red-wave-ar）

《永不消逝的红色电波》项目工作区。当前采用双线并行：保留并优化已有自研 Android 体验，同时以 Kivicube 为主要 AR 呈现平台，制作“红色电波实践路线”七个地点、九个触发与建模单元的轻量模型、图片和旁白素材。

> 当前项目方向以 [`docs/PROJECT_DIRECTION.md`](docs/PROJECT_DIRECTION.md) 为准。旧地下电台白盒和自研虚拟展馆计划已归档，不再作为新平台建模入口。

## 项目逻辑（已确认）

项目保留两条相互独立的实现路线：

1. **Kivicube 第三方平台版（当前主线）**：本项目负责制作并上传手绘触发图、专属地面贴图、三维模型和介绍音频；图像识别、AR 调用与终端呈现由 Kivicube 平台完成。
2. **自研软件版（长期路线）**：继续维护和扩展 Android / Filament 软件，并在后续进行手机相机、显示设备或投影仪等真机适配。目标是不依赖第三方平台持续订阅，但仍需承担设备、开发和维护成本。

Kivicube 当前统一体验流程为：

```text
扫描同学手绘触发图
  → 识别成功
  → 专属地面贴图与静态三维模型出现
  → 播放该地点的介绍音频
```

触发图只用于图像识别；绘制触发图时参考的真实照片只作内部核对，不在识别后展示。七个地点对应九个独立 Kivicube 触发单元：S1A/S1B 共用一份平西介绍文字，S3A/S3B 共用一份短波通信局旧址介绍文字，其余单元各使用一份。

## 当前素材完成度

| 素材 | 应有数量 | 当前数量 | 状态 |
|---|---:|---:|---|
| 最终三维模型 `*_v003.glb` | 9 | 9 | 已存在并通过本地校验，尚未完成平台上传与真机验证 |
| 手绘触发图 `*_trigger_v001.jpg` | 9 | 9 | 已存在，仍需在 Kivicube 完成识别评分和印刷真机测试 |
| 专属地面贴图 `*_ground_texture_v002.png` | 9 | 9 | 已存在，均为 1024×1024 |
| 介绍音频文字 `narration_v001.md` | 7 | 7 | 已从长版、短版研究稿中审核选定，可用于录音或语音合成 |
| 实际音频文件 `.mp3/.wav` | 7 | 0 | 尚未录制或生成，后续补入并映射到九个触发单元 |

七份已选定文字的统一入口为 [`lkivivube_delivery/NARRATION_FINAL_INDEX.md`](lkivivube_delivery/NARRATION_FINAL_INDEX.md)。这里的“文字已定稿”只表示朗读内容已经选定，不表示实际音频已经生成。

## Kivicube 九宫格预览

以下图片会随建模与素材打包流程自动更新；完整的文件定位、Kivicube 上传参数和逐单元素材包见 [`lkivivube_delivery/KIVICUBE_PACKAGE_INDEX.md`](lkivivube_delivery/KIVICUBE_PACKAGE_INDEX.md)。

![九个模型预览](lkivivube_delivery/images/kivicube_model_previews_3x3.png)

![九张原手绘触发图](lkivivube_delivery/images/kivicube_trigger_images_3x3.png)

![九张触发图参考原图](lkivivube_delivery/images/kivicube_trigger_reference_images_3x3.png)

![九张模型地面贴图](lkivivube_delivery/images/kivicube_ground_textures_3x3.png)

![九个模型与地面贴图的静态贴地预览](lkivivube_delivery/images/kivicube_model_ground_contact_3x3.png)

## 从这里开始

| 你要做的事 | 唯一入口 |
|---|---|
| 查看当前项目范围与双线边界 | [`docs/PROJECT_DIRECTION.md`](docs/PROJECT_DIRECTION.md) |
| 了解目录职责、资料流向与可安全清理的本地文件 | [`docs/REPOSITORY_LAYOUT.md`](docs/REPOSITORY_LAYOUT.md) |
| 查看 Kivicube 建模、触发图和素材约束 | [`docs/KIVICUBE_ASSET_CONSTRAINTS.md`](docs/KIVICUBE_ASSET_CONSTRAINTS.md) |
| 补充某个地点的图片、文字或建模约束 | [`modeling_input/README.md`](modeling_input/README.md) |
| 查看 9 个触发图、真实照片与模型对应关系 | [`modeling_input/REFERENCE_INVENTORY.md`](modeling_input/REFERENCE_INVENTORY.md) |
| 查看七个地点的旁白文字研究稿、来源与审核边界 | [`modeling_input/NARRATION_REFERENCE_INDEX.md`](modeling_input/NARRATION_REFERENCE_INDEX.md) |
| 查看七个地点已经确定的介绍音频正文 | [`lkivivube_delivery/NARRATION_FINAL_INDEX.md`](lkivivube_delivery/NARRATION_FINAL_INDEX.md) |
| 查看 62 张图片提取出的主体特征与提示词素材 | [`modeling_input/VISUAL_CONSTRAINTS_INDEX.md`](modeling_input/VISUAL_CONSTRAINTS_INDEX.md) |
| 查看针对模型真实度的二次细节提取 | [`modeling_input/DETAIL_EXTRACTION_V2.md`](modeling_input/DETAIL_EXTRACTION_V2.md) |
| 查看主体身份、同地点一致性与公开资料核验 | [`modeling_input/SUBJECT_IDENTITY_VERIFICATION.md`](modeling_input/SUBJECT_IDENTITY_VERIFICATION.md) |
| 查看或交付 Kivicube 模型、图片与旁白 | [`lkivivube_delivery/README.md`](lkivivube_delivery/README.md) |
| 查看 Kivicube 与自研 Android App 的接入计划 | [`docs/KIVICUBE_SELF_BUILT_APP_INTEGRATION_PLAN.md`](docs/KIVICUBE_SELF_BUILT_APP_INTEGRATION_PLAN.md) |
| 维护已有 Android / Filament 程序 | [`docs/CODE_HANDOFF.md`](docs/CODE_HANDOFF.md) |
| 构建或测试自研程序 | [`docs/BUILD.md`](docs/BUILD.md) |
| 查阅旧地下电台任务与产品计划 | [`archive/self_built_app/README.md`](archive/self_built_app/README.md) |

## 两条工作线

| 工作线 | 目标 | 活动目录 | 状态 |
|---|---|---|---|
| Kivicube 平台素材 | 七个地点、九个触发单元的 GLB、触发图、专属地面贴图、内部参考原图、旁白和上传记录 | `modeling_input/`、`lkivivube_delivery/` | 9 个 V3 细节版 GLB 与 V002 地面贴图衔接已完成本地验收；七个地点介绍音频文字已定稿，等待录音、图片权利确认和平台真机验证 |
| 自研程序 | 维护和优化已有 Android / Filament 虚拟研学体验 | `app/`、`modeling_delivery/`、`docs/` | 保留维护，不以真机 AR 连接为当前主阻塞项 |

两条线不得自动混用模型。平台 GLB 不直接复制到 `app/src/main/assets/`；自研 S1 地下电台白盒和门楼也不直接上传到 Kivicube。

## 当前地点

| 场景 | 地点 | 平台状态 |
|---|---|---|
| S1 | 平西情报联络站 | 2 个单元：入口门楼、女报务员雕塑；介绍音频文字已定稿 |
| S2 | 电报大楼 | 1 个单元；介绍音频文字已定稿 |
| S3 | 短波通信局旧址（北京国际电台中央发信台） | 2 个单元：通信楼、天线阵列；身份与介绍音频文字已确认 |
| S4 | 居庸关 | 1 个单元；介绍音频文字已定稿 |
| S5 | 西山无名英雄纪念广场 | 1 个单元；介绍音频文字已定稿 |
| S6 | 香山镇芳楼 | 1 个单元；介绍音频文字已定稿 |
| S7 | 中国电信博物馆 | 1 个单元；介绍音频文字已定稿 |

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
│   ├── NARRATION_FINAL_INDEX.md       # 七个地点已经选定的介绍音频文字
│   ├── asset_manifest.csv            # 七地点、九建模单元状态总表
│   └── scenes/                       # GLB、触发图、地面贴图、旁白文字和上传记录
├── app/                              # 自研 Android 代码
├── modeling_delivery/                # 自研程序线模型与白盒
├── research/                         # 旧 S1 研究和事实核验档案
└── archive/self_built_app/           # 旧产品计划与地下电台任务
```

## 当前交付规则

- 每张触发图对应一个独立 GLB；七个地点共九个模型。每个 GLB 目标不超过 5 MB、验收上限为 10 MB，不设文件大小下限。
- 统一呈现顺序为“红白手绘触发图识别 → 专属地面贴图与静态 GLB 同时出现 → 旁白”；真实参考照片仅用于内部确认触发图与主体的对应关系，不上传为 AR 展示平面。
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
