# 《永不消逝的红色电波》AR 沉浸式研学应用
## 产品计划书（Project Brief）

> **版本**：v1.0  ｜ **日期**：2026-07-20  ｜ **作者**："红色电波"实践团 · 技术组
> **目标读者**：① 项目负责人（决策与汇报） ② 后续负责 3D 建模的协作者 ③ 后续负责 Android 编码的协作者
> **文档性质**：单一事实来源（Single Source of Truth）。建模与编码均以本文件第 5、6 章为执行标准，凡有冲突以本文件为准。

---

## 1. 项目概述

### 1.1 一句话定位
一款 **Android 原生手机应用**，用户通过 **扫描二维码或识别触发图**进入一个**预先建好 3D 的红色通信历史虚拟场景**，可以在场景中**像云参观博物馆一样自由移动**，用**手机朝向变化（陀螺仪/姿态）环视整个空间**（类 VR 沉浸感），点击场景内的**文物/交互点**触发**文字 + 音频讲解**，完成沉浸式红色研学。

### 1.2 与立项申报书的对接
本产品是申报书《永不消逝的红色电波——首都百年红色通信史》中**板块三「红色数字文创矩阵开发」**的核心数字化成果，对应申报书第（四）节-4 板块三明确写明的交付物：

| 申报书原文交付物 | 本产品对应功能 |
|---|---|
| 「设计 5 款 AR 电台识别卡片」 | 二维码 + 触发图双重入口，5 张主题触发图 |
| 「扫码 3D 设备模型 + 红色历史语音讲解轻量化交互系统」 | 核心功能模块：场景漫游 + 文物点交互 + 音频讲解 |
| 「轻量化线上摩尔斯密码解谜素材」 | 摩尔斯电码彩蛋交互点 |
| 「配套线上云研学长期使用」 | 5 个主题场景对应五大历史阶段，可远程访问 |

### 1.3 为什么要做这个产品（差异化）
申报书中"现实短板"指出基层红色研学**形式同质化、缺互动载体**。本产品的不可替代价值在于：
- **沉浸感**：陀螺仪驱动的 360° 视角变化，比 PPT、平面 AR 卡片更有"在场感"；
- **可远程**：无需亲赴京西各场馆，扫码即进，符合"云研学"长期使用定位；
- **专业辨识度**：由信通学院通信/电子信息专业团队自主研发，区别于文科走访类实践。

---

## 2. 功能定义（Functional Spec）

### 2.1 功能清单（MVP 必须 ✅ / 增强 ⭐）

| ID | 功能 | 优先级 | 说明 |
|---|---|---|---|
| F1 | 二维码扫描入口 | ✅ MVP | 启动 App 默认页，扫二维码跳转到对应场景 |
| F2 | 触发图识别入口 | ✅ MVP | ARCore Augmented Image，扫实物卡片进入对应场景 |
| F3 | 3D 虚拟场景加载 | ✅ MVP | glTF 场景加载与渲染 |
| F4 | 陀螺仪视角控制 | ✅ MVP | 手机朝向 → 相机旋转（DeviceMotion / ARCore Pose） |
| F5 | 场景内移动（云参观式） | ✅ MVP | 屏幕摇杆 / 点击地面热点移动相机位置 |
| F6 | 交互点触发 | ✅ MVP | Raycast 命中文物 → 弹出交互菜单 |
| F7 | 文字介绍展示 | ✅ MVP | 底部抽屉式信息卡 |
| F8 | 音频讲解播放 | ✅ MVP | MediaPlayer / ExoPlayer，支持暂停继续 |
| F9 | 多场景切换 | ✅ MVP | 5 大主题场景（见 §4） |
| F10 | 摩尔斯电码解谜彩蛋 | ⭐ 增强 | 增加趣味性，对接申报书"线上解谜素材" |
| F11 | 收藏/已参观打卡 | ⭐ 增强 | 研学记录留存 |
| F12 | 截图分享 | ⭐ 增强 | 宣传传播 |
| F13 | 离线资源预下载 | ⭐ 增强 | 山区弱网场景（涧沟村宣讲） |

### 2.2 核心用户流程（Happy Path）

```
启动App
  │
  ├─ 首页：扫一扫（二维码/触发图）+ 场景列表入口
  │
  ▼
[扫码/识别] ── 识别成功 ──▶ 加载对应主题场景（loading动画）
  │                                          │
  │  识别失败                                ▼
  └─ 提示重试/手动选择场景          进入虚拟空间（默认相机位）
                                           │
                                  ┌────────┼────────┐
                                  ▼        ▼        ▼
                            摇杆移动   转动手机    点击文物
                            (位置)    (视角)      (交互)
                                  │        │        │
                                  └────────┼────────┘
                                           ▼
                                  弹出信息卡：文字 + 播放音频
                                           │
                                           ▼
                                  继续漫游 / 返回 / 切换场景
```

### 2.3 关键交互细节约定
- **进入场景默认位**：每个场景预设一个"游客起点"相机位置与朝向。
- **移动方式**：屏幕左下虚拟摇杆控制位移（前后左右平移），上下滑动控制俯仰微调；转动手机只改朝向不改位置（避免"走着走着撞墙"）。
- **视角模式切换**：默认"陀螺仪模式"（沉浸）；提供"触屏模式"开关，方便宣讲时不便举着手机操作。
- **交互点视觉**：文物上方悬浮发光指示点（呼吸动画），命中的交互点高亮描边。
- **音频优先级**：同一时刻仅播放一条讲解；切换文物自动停止上一条。

---

## 3. 技术架构与技术选型

### 3.1 平台方案（已确定）
**Android 原生 APP**（Kotlin + Jetpack），渲染层用 **Filament**（Google 开源 PBR 引擎，无需依赖游戏引擎即可加载 glTF），AR 识别层用 **ARCore**（支持 Augmented Image 触发图识别）。

### 3.2 选型理由（写给评审/汇报用）
| 维度 | 选型 | 理由 |
|---|---|---|
| 语言 | Kotlin | Android 官方首选，团队通信/嵌入式背景易上手 |
| 渲染引擎 | **Filament** | 轻量原生，APK 体积可控（远小于 Unity 打包），PBR 渲染质量高，原生支持 glTF |
| AR 识别 | **ARCore** | Android 官方 AR 框架，支持 Augmented Image（触发图）、相机姿态（陀螺仪/SLAM）|
| 相机姿态 | ARCore Pose + SensorManager | Pose 提供高精度 6DoF，退化场景用 SensorManager 陀螺仪兜底 |
| 模型格式 | **glTF 2.0 / .glb** | 业界标准，3D 建模软件全支持，Filament 原生加载 |
| 资源分发 | 本地 assets + 可选远程 OSS | 山区弱网友好，5 场景包可选择性预下载 |
| 音频 | ExoPlayer | AndroidX 官方，支持网络流式播放、后台控制 |
| UI | Jetpack Compose | 现代声明式 UI，与 AR 视图层叠加更简洁 |

> **为什么不选 Unity？** Unity 功能更强但 APK 包体 100MB+、首次启动慢、对弱机型不友好，违背申报书"轻量化"定位；本项目不需要复杂物理/光照，Filament 已足够且包体可控制在 30MB 内。

### 3.3 系统架构图（分层）

```
┌──────────────────────────────────────────────────┐
│  UI 层 (Jetpack Compose)                          │
│  首页 │ 场景列表 │ 信息卡抽屉 │ 设置              │
├──────────────────────────────────────────────────┤
│  业务逻辑层 (ViewModel + UseCase)                 │
│  扫码识别 │ 场景加载 │ 交互命中 │ 音频控制         │
├──────────────────────────────────────────────────┤
│  AR / 渲染层                                      │
│  ┌──────────────┐   ┌──────────────────────┐     │
│  │ ARCore       │   │ Filament Engine      │     │
│  │ - Augmented  │   │ - glTF 资源加载       │     │
│  │   Image 识别  │   │ - 场景图 / 相机控制   │     │
│  │ - Pose 姿态   │   │ - Raycast 拾取       │     │
│  │ - 锚点       │   │ - 光照 / 后处理       │     │
│  └──────────────┘   └──────────────────────┘     │
├──────────────────────────────────────────────────┤
│  数据层                                           │
│  本地 assets（glb/音频/json）+ Room（打卡记录）    │
│  可选远程 OSS（资源热更新）                        │
├──────────────────────────────────────────────────┤
│  Android 平台                                     │
│  Camera2 │ SensorManager │ MediaPlayer/ExoPlayer │
└──────────────────────────────────────────────────┘
```

### 3.4 关键技术实现要点（给编码模型预读）
1. **触发图识别 → 场景加载** 的桥接：ARCore `AugmentedImage` 回调拿到 `index` → 查 `manifest.json` 得到场景资源路径 → 触发 Filament 加载。
2. **陀螺仪控制视角**：在纯虚拟场景（非 AR 锚定）中，读取 `SensorManager.TYPE_GAME_ROTATION_VECTOR`，把四元数映射到 Filament 相机 `setRotation`；当用户进入"AR 锚定模式"时改用 ARCore `Pose`。
3. **云参观式移动**：维护一个虚拟"游客"坐标 `(x, y, z, yaw, pitch)`，摇杆改 `(x, z)` 与 `yaw`，陀螺仪改 `yaw/pitch`，二者冲突时陀螺仪优先。
4. **交互点拾取**：Filament 提供 `Scene.castRay`（或手动 AABB 包围盒检测），命中后读 `hotspots[].id` 触发信息卡。
5. **资源组织**：所有场景用同一套数据 schema（见 §5.4 `scene-manifest.json`），编码层只认 schema，建模层只产 schema。

---

## 4. 内容规划：5 大主题场景

紧扣申报书"抗战、解放、建国、改革开放、新时代"五大历史阶段，每个场景对应一个红色通信点位。

| # | 场景主题 | 对应实物点位 | 核心可交互文物 | 触发图设计元素 |
|---|---|---|---|---|
| S1 | **地下情报电台** | 平西情报联络站 / 涧沟村 | 秘密电台、密码本、发报键 | 暗色窑洞剪影 + 摩尔斯码 |
| S2 | **军事无线电总台** | 西山八大处军委三局 | 大功率无线电台、军用天线阵、作战地图 | 山顶天线塔剪影 |
| S3 | **中央机要电话局** | 香山丽瞩楼 | 磁石电话交换机、专线电话、值班台 | 香山红叶 + 老式电话 |
| S4 | **全国邮电枢纽** | 北京电报大楼 | 电报机、电报纸、报时塔楼 | 钟楼正面剪影 |
| S5 | **5G 新时代** | 中国电信博物馆 | 程控交换机、基站模型、5G 终端、卫星 | 抽象数字波纹 |

每个场景交付内容（详见 §5）：
- 1 个场景级 glb（场馆建筑/环境）
- 3–6 个可交互文物 glb
- 每个文物 1 段文字介绍 + 1 段音频讲解（60–180 秒）
- 1 个 `hotspots` JSON 配置（坐标、朝向、关联资源）

---

## 5. 3D 内容生产规范（给建模协作者）

> 📌 **本章是建模模型的执行依据**。建模完成后必须严格按此规范交付，否则编码无法集成。

### 5.1 资产清单（Deliverables Checklist）
每个场景交付一个独立文件夹 `scene_SX/`，内含：

```
scene_S1/
├── environment.glb          # 场馆/环境模型（必交）
├── props/
│   ├── radio_station.glb    # 文物1
│   ├── code_book.glb        # 文物2
│   └── telegraph_key.glb    # 文物3
├── audio/
│   ├── radio_station.mp3
│   ├── code_book.mp3
│   └── telegraph_key.mp3
├── textures/                # 共享贴图（如复用）
└── meta.json                # 元信息（见 §5.4）
```

### 5.2 建模技术规范

| 项目 | 规范 | 说明 |
|---|---|---|
| **格式** | `.glb`（二进制 glTF 2.0） | 不接受 .fbx/.obj/.blend 直接交付，需导出 glb |
| **坐标系** | glTF 标准：Y-up，右手系，-Z 朝前 | 导出时确认轴向 |
| **单位** | 米（1 unit = 1m） | 文物按真实尺寸 |
| **面数上限（单个 glb）** | 环境 ≤ 80k tris；单个文物 ≤ 15k tris | 中端手机流畅渲染 |
| **贴图** | KTX2 / BasisU 压缩；尺寸 ≤ 2048×2048；文物常用 1024 | Filament 加载 KTX2 性能最佳 |
| **材质** | PBR（metallic-roughness 工作流） | glTF 标准材质，避免 Blender 私有节点 |
| **纹理数（单 glb）** | ≤ 8 张 | 控制内存 |
| **动画** | 可选：文物旋转/开合用 glTF animation | 命名规范：`idle` / `interact` |
| **锚点/原点** | 文物原点放在底面中心，便于程序放置 | 不要把原点放在角落 |
| **命名** | mesh/material/node 用英文小写下划线，见名知义 | 如 `radio_body`、`telegraph_key_arm` |

### 5.3 触发图（识别卡）规范
- 尺寸：**打印输出 A6（105×148mm）**，电子版 PNG **1080×1500 px**；
- ARCore Augmented Image 要求：**图案有足够特征点、避免大量空白、避免高度对称/重复纹理**；
- 每张触发图嵌入：① 场景主视觉 ② 文物剪影 ③ 简短一句话 ④ 一枚二维码（二维码值见 §5.4 manifest 的 `qr_code` 字段）；
- 输出格式：`trigger_S1.png … trigger_S5.png`，并提供 ARCore 训练用的高对比版本。

### 5.4 `meta.json` 数据 Schema（建模 → 编码契约）

```json
{
  "scene_id": "S1",
  "scene_name": "地下情报电台",
  "location_real": "平西情报联络站 / 门头沟涧沟村",
  "qr_code": "REDWAVE-S1",
  "environment_glb": "environment.glb",
  "visitor_start": { "x": 0.0, "y": 1.6, "z": 3.0, "yaw": 0.0, "pitch": 0.0 },
  "movement_bounds": { "x_min": -5.0, "x_max": 5.0, "z_min": -5.0, "z_max": 5.0 },
  "props": [
    {
      "id": "p1_radio",
      "name": "秘密电台",
      "glb": "props/radio_station.glb",
      "position": { "x": 1.2, "y": 0.8, "z": -1.0 },
      "rotation": { "x": 0, "y": 30, "z": 0 },
      "scale": 1.0,
      "interact_radius": 1.5,
      "text": "这是抗战时期平西情报站使用的秘密电台……（约 200 字）",
      "audio": "audio/radio_station.mp3",
      "tags": ["抗战", "隐蔽战线"]
    }
  ]
}
```

> 建模方填好位置/缩放后输出此 json；编码方仅消费此 json，不硬编码任何坐标。

---

## 6. 工程实现指引（给编码协作者）

> 📌 **本章是编码模型的执行依据**。

### 6.1 项目骨架建议
```
red-wave-ar/
├── app/
│   ├── src/main/
│   │   ├── java/cn/bistu/redwave/ar/
│   │   │   ├── ui/              # Compose 页面
│   │   │   ├── ar/              # ARCore 包装
│   │   │   ├── render/          # Filament 渲染封装
│   │   │   ├── scene/           # 场景加载与状态机
│   │   │   ├── interaction/     # 拾取/摇杆/陀螺仪
│   │   │   ├── audio/           # ExoPlayer 封装
│   │   │   └── data/            # manifest 解析、Room
│   │   ├── assets/
│   │   │   ├── scenes/          # 5 个场景文件夹（见 §5.1）
│   │   │   └── global_manifest.json
│   │   └── res/
│   └── build.gradle.kts
├── core/                        # （可选）公共模块
└── docs/
```

### 6.2 核心依赖（建议版本以撰写时最新稳定版为准）
- `com.google.ar:core` — ARCore
- `com.google.android.filament:filament-android` + `gltfio` + `ktx` — Filament 全家桶
- `androidx.media3:media3-exoplayer` — 音频
- `androidx.compose.*` — UI
- `com.airbnb.android:lottie-compose` — Loading/引导动画
- `com.journeyapps:zxing-android-embedded` — 二维码扫描（F1）

### 6.3 关键模块实现要点

**ARCore Augmented Image 识别（F2）**
```kotlin
// 伪代码：从 assets 读取 5 张触发图特征库
val imageDb = session.createAugmentedImageDatabase()
for (scene in scenes) {
    imageDb.addImage(scene.scene_id, loadImageBitmap("triggers/${scene.scene_id}.png"))
}
config.augmentedImageDatabase = imageDb
// 回调：识别到 → loadScene(scene_id)
```

**Filament 场景加载（F3）**
```kotlin
// 用 gltfio 的 ResourceLoader + AssetLoader 异步加载
val asset = assetLoader.createAssetFromBinary(glbByteBuffer)
resourceLoader.asyncBeginLoad(asset)
// 加载完成后 addEntity 到 scene
engine.scene.addEntities(asset.entities)
```

**陀螺仪 → 相机姿态（F4）**
```kotlin
sensorManager.registerListener(
    object : SensorEventListener {
        override fun onSensorChanged(e: SensorEvent) {
            // TYPE_GAME_ROTATION_VECTOR → 四元数
            val q = quaternionFrom(e.values)
            cameraNode.rotation = q   // 仅改朝向，位置另算
        }
    },
    gameRotationSensor, SensorManager.SENSOR_DELAY_GAME
)
```

**Raycast 拾取（F6）**
```kotlin
// 屏幕点击 → NDC 坐标 → 射线 → 与 props AABB 求交 → 取最近的
val ray = camera.screenToWorldRay(touchX, touchY)
val hit = props.filter { it.aabb.intersect(ray) }
                .minByOrNull { distance(it, ray) }
hit?.let { showInfoCard(it.id) }
```

### 6.4 数据流约定
- `assets/global_manifest.json` 列出全部场景索引；
- 进入场景时按 `scene_id` 找到 `scene_SX/meta.json`，统一用 `@Serializable` data class 解析；
- 所有运行时坐标统一用米；UI 层只接收"已解析的领域模型"，不直接接触 glTF 节点名。

### 6.5 性能与兼容性目标
| 指标 | 目标 |
|---|---|
| 冷启动 → 进入场景 | ≤ 5 秒（中端机型）|
| 场景内 FPS | ≥ 30（含 5 文物场景）|
| APK 体积 | ≤ 50 MB（5 场景全量本地资源）|
| 最低 Android 版本 | Android 8.0（API 26），ARCore 支持 |
| 最低机型要求 | 支持 ARCore（Google 维护机型列表），陀螺仪必须 |
| 内存峰值 | ≤ 500 MB |

---

## 7. 里程碑与时间表

> 申报书第二阶段为 7 月上旬实地采集，第三阶段 7 月中-7 月底成果创作。AR 产品应在此窗口内完成。

| 里程碑 | 时间窗 | 建模方交付 | 编码方交付 |
|---|---|---|---|
| **M0 启动** | 7/20–7/22 | — | 工程骨架、依赖接入、空场景跑通 |
| **M1 单场景打通** | 7/23–7/28 | S1 场景白盒 + 1 文物 glb | S1 全流程（扫码→漫游→交互→音频）跑通 |
| **M2 多场景扩展** | 7/29–8/03 | S2–S3 场景完成 | 场景切换、UI 抽屉、音频播放完善 |
| **M3 全量内容** | 8/04–8/10 | S4–S5 完成、触发图定稿 | 5 场景全量集成、性能优化 |
| **M4 增强 + 联调** | 8/11–8/15 | 视觉打磨、贴图优化 | 摩尔斯彩蛋、打卡、截图、离线包 |
| **M5 评优冲刺** | 8/16–8/20 | 宣传海报素材、AR 卡片印刷文件 | Bug 修复、APK 签名打包、演示视频 |

> 关键约束：**M1 必须按期**。一旦 M1 跑通"单场景全链路"，后续就是复制扩展，风险大幅下降。

---

## 8. 分工与协作

### 8.1 角色与职责
| 角色 | 负责人 | 职责 |
|---|---|---|
| 项目负责人 | 李雨霏 | 整体推进、与指导老师/场馆对接、汇报 |
| 技术负责人 | 林泽羽（你） | 架构决策、对接建模与编码、验收 |
| 3D 建模 | 待分配（建模模型/协作者） | 按 §5 规范产出 glb + meta.json + 触发图 |
| Android 编码 | 待分配（编码模型/协作者） | 按 §6 规范实现 APP |
| 内容文案/音频 | 文创组（宋佳麟等） | 每文物 200 字介绍 + 60–180 秒讲解录音 |
| 宣传/测试 | 宣讲组、安全组 | 真机测试、宣讲现场保障 |

### 8.2 协作约定
- **代码/资产仓库**：统一一个 Git 仓库（建议 GitLab/Gitee 私有，支持大文件 LFS）；
- **资产目录约定**：见 §5.1、§6.1，命名不得随意改动；
- **数据契约先行**：建模在产 glb 前，先和技术负责人敲定 `meta.json` 中 `position/interact_radius` 等数值；
- **每周例会**：周一同步进度，周四风险预警，采用 PR / MR 形式评审合并。

---

## 9. 风险与对策

| 风险 | 影响 | 对策 |
|---|---|---|
| 部分安卓机型不支持 ARCore | 用户无法进入 | App 启动检测 `ArCoreApk`，不支持时降级为"触屏漫游模式"（仅用陀螺仪 + 摇杆） |
| 山区宣讲弱网 | 资源加载失败 | 全部资源走本地 assets，离线可用（F13）|
| 建模面数超标导致卡顿 | 体验差 | §5.2 限制 + Profile GPU 检测 + LOD 降级 |
| 触发图识别率低 | 入口失败 | 选用高特征点图案；备份二维码入口（F1）兜底 |
| 团队无 Android 经验 | 工期延误 | Filament/ARCore 官方 sample 充足；M1 仅打通单链路 |
| 音频素材缺失 | 部分功能不可用 | 文创组在 M2 前完成文案与录音；缺音频时 TTS 临时占位 |

---

## 10. 验收标准（Definition of Done）

**MVP 验收（必须在第三阶段结束前达成）**
- ✅ 真机上扫描任一二维码或触发图，能在 5 秒内进入对应场景；
- ✅ 转动手机可见 360° 视角变化；
- ✅ 摇杆可在场景内移动，不穿墙；
- ✅ 点击文物弹出文字 + 播放音频；
- ✅ 5 个场景全部可进入、可漫游、可交互；
- ✅ 中端机型（如骁龙 7 系）≥ 30 FPS，无 crash；
- ✅ 5 张 AR 触发图印刷成品可在现场识别。

**评优加分（增强项）**
- ⭐ 摩尔斯电码解谜彩蛋运行正常；
- ⭐ 打卡/收藏功能可用，研学记录可导出；
- ⭐ 截图分享到微信/抖音链路打通；
- ⭐ 离线资源包可在涧沟村无网环境下运行；
- ⭐ 演示视频（3 分钟）制作完成。

---

## 11. 后续动作（Next Actions）

提交本计划书后，立即并行启动三条线：

1. **建模线**：把本文件 §4、§5 单独抽给建模模型/协作者，要求 M1 前交付 S1 白盒 + 1 文物 + meta.json 草案；
2. **编码线**：把 §2、§3、§6 抽给编码模型/协作者，要求 M1 前跑通"空场景 + 假数据 + 全链路"；
3. **内容线**：文创组按 §4 表格开始撰写 5 场景 ×（3–6 文物）文案，并预约录音；触发图设计稿同步启动。

> 验收门槛：M1 节点（约 7/28）必须能在一个真实手机上"扫码 → 进入白盒房间 → 走动 → 点开一个方块 → 听到一段占位音频"。这是后续一切的地基。

---

*本计划书为活文档，重大架构变更需更新版本号并通知全部协作者。*
