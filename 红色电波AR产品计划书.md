# 《永不消逝的红色电波》AR 触发式移动端 VR 研学应用
## 产品计划书（Project Brief）

> **版本**：v1.3  ｜ **日期**：2026-07-20  ｜ **作者**：“红色电波”实践团 · 技术组
> **目标读者**：① 项目负责人 ② 3D 建模协作者 ③ Android 编码协作者 ④ 内容文案与测试人员
> **文档性质**：本文件是当前实现阶段的单一事实来源。项目附件和成果表述在最终验收后按实际实现效果回写，不用早期附件限制最终产品形态，也不得在附件中声称尚未通过验收的功能。

---

## 0. v1.3 核心决策

1. **产品形态统一为“识别入口 + 纯虚拟展馆”**：二维码扫描或触发图识别只负责确定 `scene_id`；识别成功后关闭相机与识别会话，进入完全独立的虚拟 3D 空间。
2. **后续体验属于移动端类 VR，不是现实画面上的 AR 叠加**：手机姿态负责环视，屏幕摇杆或移动热点负责虚拟位移，文物热点负责文字与音频交互。
3. **先验证单场景全链路，再扩展五场景**：S1 是技术 MVP 和旗舰场景；S2–S5 先按轻量模板生产，通过技术闸门后再决定是否升级为完整场景。
4. **所有技术指标以真机 Release 构建实测为准**：未经过技术验证的 API、APK 体积和性能数字只作为目标，不作为既成事实。
5. **S1 采用有史料依据的虚拟主题展馆，不宣称原址 1:1 复原**：1943 年冬涧沟村秘密电台作为物理空间核心，1947 年清风店战役作为结果层；保留技术 ID `p_s1_codebook`，但用户可见语义改为无铭文的“电文与保密通信资料包”。

---

## 1. 项目概述

### 1.1 一句话定位

一款 **Android 原生移动端沉浸式虚拟研学应用**。用户通过**二维码、触发图识别或场景列表**进入对应的红色通信历史虚拟展馆；二维码与图像识别仅作为场景触发入口，进入后不再显示现实相机画面。用户通过**手机姿态环视虚拟空间**，通过**屏幕摇杆或移动热点改变位置**，点击文物获取**文字介绍和音频讲解**。

### 1.2 AR 与 VR 边界

| 阶段 | 技术 | 作用 | 是否显示现实画面 |
|---|---|---|---|
| 二维码入口 | ZXing | 将二维码解析为 `scene_id` | 是，仅扫描时 |
| 触发图入口 | ARCore Augmented Images | 将识别图解析为 `scene_id` | 是，仅识别时 |
| 手动入口 | Compose 场景列表 | 无相机权限时的稳定兜底 | 否 |
| 虚拟展馆 | Filament + SensorManager | 加载虚拟场景、环视、移动、交互 | 否 |

> 本项目不实现“3D 模型持续锚定在识别卡片或现实空间中”。ARCore Pose、平面检测、锚点和现实遮挡不属于当前范围。

### 1.3 与立项材料的关系

早期立项材料只作为主题、内容范围和成果表达参考。最终附件以实际通过验收的功能为准，建议按以下方式回写：

| 立项材料参考方向 | 当前实现目标 |
|---|---|
| 5 款 AR 电台识别卡片 | 5 张二维码 + 触发图双入口卡片 |
| 扫码调取 3D 模型与语音讲解 | 扫码或识图进入对应虚拟展馆，观看 3D 文物并播放讲解 |
| 轻量化摩尔斯密码解谜 | 作为增强功能，基础体验稳定后实现 |
| 线上云研学长期使用 | 输出可安装 APK、标准化资源包和交接文档 |

### 1.4 产品价值

- **沉浸感**：手机姿态驱动 360° 环视，比平面图文更有“在场感”。
- **专业辨识度**：通信史内容与 3D、传感器、移动端渲染结合，体现信通专业特色。
- **可复用**：场景、文案和音频由统一数据契约驱动，可持续新增内容。
- **可演示**：二维码、识图和手动入口并存，现场条件不理想时仍能完成展示。

---

## 2. 功能定义

### 2.1 功能清单

| ID | 功能 | 层级 | 说明 |
|---|---|---|---|
| F1 | 二维码扫描入口 | ✅ MVP | 扫描二维码并解析为 `scene_id` |
| F2 | 触发图识别入口 | ✅ MVP | ARCore Augmented Images 识别卡片；只负责选场景 |
| F3 | 场景列表入口 | ✅ MVP | 无相机权限、识别失败或设备不支持 ARCore 时兜底 |
| F4 | 纯虚拟 3D 场景加载 | ✅ MVP | 识别完成后关闭相机，加载 glTF / GLB 场景 |
| F5 | 陀螺仪环视 | ✅ MVP | `TYPE_GAME_ROTATION_VECTOR` 驱动视角，支持回正 |
| F6 | 触屏环视 | ✅ MVP | 无陀螺仪或不便举机时使用 |
| F7 | 虚拟移动 | ✅ MVP | S1 使用摇杆和可行走边界；轻量场景可使用移动热点 |
| F8 | 文物交互 | ✅ MVP | 点击文物或热点，弹出信息卡 |
| F9 | 文字与音频讲解 | ✅ MVP | 同时只播放一条音频，支持暂停和继续 |
| F10 | S1 完整旗舰场景 | ✅ MVP | 单场景全链路与真机验收基线 |
| F11 | S2–S5 轻量模板场景 | ◇ P1 | 复用统一展馆模板，逐步替换为专属环境 |
| F12 | 离线场景包 | ◇ P1 | 基础包内置 S1，其余场景可预下载或活动前安装 |
| F13 | 摩尔斯电码解谜 | ⭐ P2 | 评优增强功能 |
| F14 | 收藏、打卡与截图分享 | ⭐ P2 | 不阻塞核心体验交付 |

> **范围闸门**：M1 未通过前，不同时启动 S2–S5 的高精度完整场景。先证明“识别 → 退出相机 → 加载虚拟场景 → 环视 → 移动 → 交互 → 音频”稳定可用。

### 2.2 核心用户流程

```text
启动 App
  │
  ├─ 扫二维码 ──────┐
  ├─ 识别触发图 ────┼─▶ EntryResolver 解析 scene_id
  └─ 手动选择场景 ──┘                │
                                    ▼
                          停止相机 / 关闭 ARCore Session
                                    │
                                    ▼
                         加载对应纯虚拟 3D 展馆
                                    │
                    ┌───────────────┼───────────────┐
                    ▼               ▼               ▼
                手机姿态环视     触屏环视/回正      摇杆或热点移动
                    └───────────────┼───────────────┘
                                    ▼
                         点击文物：文字 + 音频讲解
                                    │
                                    ▼
                       继续参观 / 返回首页 / 切换场景
```

### 2.3 关键交互约定

- **识别结束即退出相机**：入口模块只返回 `scene_id`，不把 ARCore Pose 带入虚拟场景。
- **游客起点**：每个场景预设位置、朝向和安全可行走区域。
- **陀螺仪模式**：进入场景时记录当前姿态为基准；提供“视角回正”，并进行四元数平滑和屏幕旋转补偿。
- **触屏模式**：拖动控制 yaw/pitch；与陀螺仪模式互斥，避免输入冲突。
- **屏幕方向**：MVP 全应用固定横屏，扫描页、Loading 和 VR 不在运行中切换方向；若后续支持竖屏，必须重新验收相机取景、传感器坐标和 UI 布局。
- **移动方式**：摇杆只改变虚拟位置，不修改手机姿态；复杂碰撞未就绪时，使用热点移动或简单碰撞盒。
- **交互反馈**：可交互文物有悬浮标记或描边，点击后打开底部信息卡。
- **音频规则**：同一时刻只播放一条讲解；切换文物、场景或退出时停止上一条音频。
- **眩晕控制**：限制移动速度，不加入视角晃动；默认提供触屏模式和固定移动热点。

---

## 3. 技术架构与选型

### 3.1 平台方案

采用 **Android 原生 App（Kotlin + Jetpack Compose）**。Filament 负责纯虚拟场景渲染，ARCore 只负责触发图识别，ZXing 负责二维码扫描，SensorManager 负责虚拟展馆中的手机姿态输入。

### 3.2 技术选型

| 模块 | 选型 | 说明 |
|---|---|---|
| 语言与 UI | Kotlin + Jetpack Compose | 页面、权限提示、信息卡和设置 |
| 二维码入口 | ZXing Android Embedded | 输出统一的 `scene_id` |
| 图片入口 | ARCore Augmented Images | 只识别图片名称或索引，不做现实锚定 |
| 渲染引擎 | Filament + gltfio | 加载 glTF / GLB，渲染纯虚拟展馆 |
| 姿态输入 | SensorManager | 使用 `TYPE_GAME_ROTATION_VECTOR`，支持校准和平滑 |
| 模型格式 | glTF 2.0 / GLB | 运行时统一格式 |
| 音频 | AndroidX Media3 ExoPlayer | 本地或预下载音频播放 |
| 本地记录 | DataStore；需要结构化记录时再引入 Room | 避免 MVP 过早增加依赖 |
| 资源策略 | 基础 APK + 可选场景包 | S1 内置，其余资源按实测体积决定 |

### 3.3 系统架构

```text
┌─────────────────────────────────────────────────────────┐
│ UI 层：Compose                                           │
│ 首页 │ 扫描页 │ Loading │ 虚拟展馆 HUD │ 信息卡 │ 设置   │
├─────────────────────────────────────────────────────────┤
│ 入口层                                                   │
│ QR Scanner │ Image Recognizer │ Manual Scene Picker      │
│                   └────▶ EntryResolver(scene_id)         │
├─────────────────────────────────────────────────────────┤
│ 场景业务层                                               │
│ Scene State Machine │ Manifest Loader │ Audio Controller │
├─────────────────────────────────────────────────────────┤
│ 纯虚拟体验层                                             │
│ Filament Renderer │ Sensor Controller │ Movement/Picking │
├─────────────────────────────────────────────────────────┤
│ 数据与资源层                                             │
│ global_manifest.json │ scene.json │ content.json │ GLB   │
└─────────────────────────────────────────────────────────┘
```

### 3.4 核心状态机

```text
HOME
  ├─▶ QR_SCANNING
  ├─▶ IMAGE_RECOGNIZING
  └─▶ SCENE_SELECTING
             │
             ▼
      ENTRY_RESOLVED(scene_id)
             │
      releaseCameraAndArSession()
             ▼
         SCENE_LOADING
       ├─▶ VR_EXPLORING
       └─▶ LOAD_ERROR ─▶ SCENE_SELECTING
```

相机和 ARCore Session 必须在进入 `SCENE_LOADING` 前停止，避免相机占用、功耗和生命周期冲突。

### 3.5 关键实现约定

1. **ARCore 图像库**：使用 `AugmentedImageDatabase(session)` 或预生成 `.imgdb`；识别到有效图片后读取名称或索引并映射为 `scene_id`。
2. **二维码映射**：二维码只承载稳定入口值，例如 `REDWAVE-S1`；解析失败时提示重试或转手动选择。
3. **姿态计算**：读取游戏旋转向量，转换为四元数；用进入场景时的逆基准姿态完成“回正”，再映射到 Filament 相机。
4. **虚拟移动**：维护 `visitorPosition`；摇杆在水平面改变位置，姿态传感器只改变视线方向。
5. **文物拾取**：优先使用 Filament `View.pick(...)` 的异步结果映射实体；若固定版本验证不通过，则使用应用侧交互碰撞盒，不使用不存在的 `Scene.castRay`。
6. **资源版本**：所有 JSON 必须包含 `schema_version`；应用拒绝加载不兼容版本并显示可理解的错误提示。
7. **依赖固定**：M1 技术验证通过后，把 ARCore、Filament、Media3、Compose 和 ZXing 版本固定到 Version Catalog，不使用“构建时最新版本”。

### 3.6 发布与使用方式

- MVP 以签名 APK 交付，提前安装到演示和宣讲设备，不依赖现场应用商店下载。
- 应用配置为 **AR Optional**：不支持 ARCore 的设备仍可通过二维码和手动列表进入虚拟展馆。
- 最终至少保留一台已验证的主展示机和一台备用机。
- 若后续需要让外部微信扫码直接安装或打开 App，再单独设计 HTTPS 落地页与 Android App Link；该能力不属于当前 MVP。

---

## 4. 内容规划：五大主题场景

五个主题场景都属于纯虚拟展馆。S1 作为旗舰场景完整制作；S2–S5 先复用轻量展馆模板，是否升级为专属完整环境由 M2 资源与性能评估决定。

| 场景 | 主题 | 对应点位 | 核心文物 | 首轮交付级别 |
|---|---|---|---|---|
| S1 | 隐蔽通信主题展馆 | 平西情报联络站 / 涧沟村 | 秘密电台、发报键、电文与保密通信资料包 | 旗舰完整场景 |
| S2 | 军事无线电总台 | 西山八大处军委三局 | 无线电台、军用天线、作战地图 | 轻量模板场景 |
| S3 | 中央机要电话局 | 香山丽瞩楼 | 磁石交换机、专线电话、值班台 | 轻量模板场景 |
| S4 | 全国邮电枢纽 | 北京电报大楼 | 电报机、电报纸、报时塔楼 | 轻量模板场景 |
| S5 | 5G 新时代 | 中国电信博物馆 | 程控交换机、基站、5G 终端、卫星 | 轻量模板场景 |

### 4.1 内容交付量

- S1：1 个专属环境、3–5 个可交互文物、3–5 段文字和音频。
- S2–S5 首轮：每场景 1 个统一模板环境、1–3 个代表性文物及对应讲解。
- 只有在 M2 前资产、人力和性能均达标时，才把 S2–S5 升级为专属环境和 3–6 个文物。

### 4.2 内容质量要求

- 每段文案必须记录史料来源、撰稿人、审核人和版本。
- 场馆照片、文物纹理、人物录音和背景音乐必须记录授权或使用依据。
- 文字和音频保持一致；修改内容时同步更新 `content.json` 的版本。
- 历史表述在集成前由项目负责人或指定内容审核人确认。

### 4.3 场景共同空间规则

所有场景都必须满足以下共同约束，使编码层能够复用同一套相机、移动和拾取逻辑：

- 默认游客眼高为 **1.6 m**，主要展品交互中心建议位于地面以上 **0.8–1.8 m**。
- 默认场景可活动范围建议控制在 **6 m × 6 m 至 12 m × 12 m**；超出范围必须说明原因。
- 游客起点前方 2 m 内必须有一个明显的首个交互目标，避免进入场景后不知道做什么。
- 主通道净宽不少于 1.2 m；不在狭窄区域放置必须靠近才能触发的热点。
- 环境、文物、交互提示和 UI 的视觉层级必须可区分，发光提示不能与环境灯光混为一体。
- 场景根节点保持单位缩放和零旋转；所有运行时位移、旋转和缩放由 `scene.json` 控制。
- 不把大段文字烘焙进纹理。铭牌、编号或历史标语必须由内容组确认后才能进入模型。
- 每个场景至少设置一个返回入口、一个视角回正入口和一个触屏/陀螺仪切换入口；这些由程序 UI 实现，不建模成场景物体。

### 4.4 S1：平西情报联络站隐蔽通信主题展馆（旗舰场景）

**空间目标**：营造隐蔽、克制、紧张但可清晰参观的虚拟通信展馆。以 1943 年冬涧沟村山洞秘密电台与农家掩护关系为物理叙事核心，以小型信息卡呈现 1945 年交通线和 1947 年清风店战役结果。S1 采用地下储洞门内侧的原创紧凑小室，体验净尺寸约 **5.3 m × 4.7 m × 2.25 m**；该尺寸是产品体验尺度，不是历史测绘尺寸或原址复原。桌面和电台区域必须是明确的暖光引导焦点，不使用过强烟雾、全屏暗角或大型展馆式信息墙。

**史料与空间边界**：

- 1941 年 2 月是平西情报交通联络站体系成立时间；公开权威资料记载初址在涞水计鹿村，不能写成“1941 年涧沟村山洞电台建成”。
- 1943 年冬涧沟村秘密电台有多源支持，作为 S1 的主场景时间锚点。
- 现纪念馆由关帝庙改建，另有政府资料称战时相关原址位于村西两个农家小院；现馆、农家院和山洞电台不得合并宣称为同一原址建筑。
- 当前政府照片和媒体视频只能用于观察，未取得书面许可前不得进入纹理、展板、触发卡或宣传素材。
- 详细来源、事实等级、视觉限制和待补材料见 `research/S1_pingxi_intelligence_station/`。

| 资产 ID | 中文名称 | 级别 | 建模与摆放要求 | 交互要求 |
|---|---|---|---|---|
| `env_s1_room` | 隐蔽通信主题环境 | MVP | 原创地下储洞小室：夯土/粗石/局部灰砖修补、低矮旧木门、紧凑木桌和小型导览牌；不复制现纪念馆，不宣称 1:1 | 提供外边界和主要障碍物碰撞盒 |
| `p_s1_radio` | 秘密电台（场景化复原） | MVP | 独立 GLB；无品牌、无编号的通用箱式设备，必须具有可读的倾斜面板、无文字表窗、旋钮、接线端和单根线缆；馆方确认型号前禁止补真实铭文和精确制式 | 点击打开介绍并播放讲解 |
| `p_s1_key` | 发报键 | MVP | 独立 GLB，按键臂可选骨骼或节点动画 | 点击可播放短摩尔斯音效；正式解谜为 P2 |
| `p_s1_codebook` | 电文与保密通信资料包 | MVP | 技术 ID 保持不变；造型改为无铭文纸束/资料夹的通用复原，不制作密码表、印章、真实电文或“馆藏原件”外观 | 点击说明保密通信与资料传递；明确为场景化载体 |
| `p_s1_battery` | 电池/供电设备 | P1 | 结构可信，避免过度细碎线路 | 点击显示供电背景 |
| `d_s1_map` | 历史路线示意面 | P1 | 按已核地名原创重绘并标“路线示意”；不得使用网页截图或现馆地图照片，避免 4K 贴图 | 点击放大为 UI 图片，不在 3D 内塞入全文 |

**游客起点建议**：`[0.0, 1.55, 1.65]`，朝向电台桌；首个目标为 `p_s1_radio`，第一眼水平距离建议 1.4–1.9 m。
**MVP 完成条件**：环境、`p_s1_radio`、`p_s1_key`、`p_s1_codebook` 均可加载、拾取、展示文字和播放音频；信息卡必须区分史实、通用复原和路线示意。

### 4.5 S2：军事无线电总台

**空间目标**：突出军事通信的组织性、规模感和指挥氛围。首轮使用 8 m × 8 m 的轻量指挥室模板，后续可扩展天线观察区。

| 资产 ID | 中文名称 | 级别 | 建模与摆放要求 | 交互要求 |
|---|---|---|---|---|
| `env_s2_command_room` | 无线电指挥室 | P1 | 指挥桌、设备架、墙面图板，整体材质数量受控 | 提供矩形可行走区和设备架碰撞盒 |
| `p_s2_radio` | 大功率无线电台 | P1 必交 | 作为首轮代表文物，面板细节要在手机屏幕可辨 | 点击打开设备用途讲解 |
| `p_s2_antenna` | 军用天线模型 | P1 | 可做缩比陈列，不要求搭建室外大场景 | 点击展示天线与通信距离说明 |
| `p_s2_map` | 作战通信地图 | P2 | 使用经审核的示意内容 | 点击后以 UI 大图展示 |
| `p_s2_headset` | 通信耳机 | P2 | 独立小道具，避免面数浪费 | 点击播放通信岗位说明 |

**首轮完成条件**：模板环境 + `p_s2_radio` + 一段经审核讲解；其余资产不阻塞五入口交付。

### 4.6 S3：中央机要电话局

**空间目标**：突出机要电话接续、值班和人工交换流程。首轮使用 8 m × 6 m 的值班室模板，灯光比 S1 更明亮、秩序感更强。

| 资产 ID | 中文名称 | 级别 | 建模与摆放要求 | 交互要求 |
|---|---|---|---|---|
| `env_s3_switch_room` | 机要电话值班室 | P1 | 墙面、值班台、座椅和设备区 | 提供可行走边界和设备碰撞盒 |
| `p_s3_switchboard` | 磁石电话交换机 | P1 必交 | 插孔、线缆和操作区可辨；线缆不使用过高分段 | 点击说明人工交换流程 |
| `p_s3_phone` | 专线电话 | P1 | 听筒独立节点，拿起动画为 P2 | 点击播放机要通信讲解 |
| `p_s3_console` | 值班台 | P2 | 可与环境合并，但交互区域需独立实体 | 点击展示值班制度简介 |
| `p_s3_logbook` | 值班记录本 | P2 | 不使用未经确认的真实姓名和号码 | 点击显示审核后的摘录 |

**首轮完成条件**：模板环境 + `p_s3_switchboard` + 一段经审核讲解。

### 4.7 S4：全国邮电枢纽

**空间目标**：体现电报业务、信息流转和公共通信基础设施。首轮使用展陈大厅模板，视觉重心为电报机及其纸带。

| 资产 ID | 中文名称 | 级别 | 建模与摆放要求 | 交互要求 |
|---|---|---|---|---|
| `env_s4_telegraph_hall` | 电报展陈厅 | P1 | 统一展台、墙面时间轴、设备工作台 | 提供展台碰撞盒和热点移动点 |
| `p_s4_telegraph` | 电报机 | P1 必交 | 键盘、走纸机构和机身比例可信 | 点击介绍收发流程 |
| `p_s4_tape` | 电报纸带/电报纸 | P1 | 使用审核后的示例内容，不使用真实隐私信息 | 点击以 UI 展示放大图 |
| `p_s4_clock_model` | 电报大楼报时塔模型 | P2 | 作为缩比建筑模型，不要求完整外景 | 点击介绍枢纽与报时功能 |
| `p_s4_document` | 业务单据 | P2 | 文字内容由内容组提供 | 点击展示历史业务流程 |

**首轮完成条件**：模板环境 + `p_s4_telegraph` + 一段经审核讲解。

### 4.8 S5：5G 新时代

**空间目标**：形成与前四个历史场景明显不同的现代数字展厅，体现从程控交换到移动通信、5G 和卫星通信的演进。

| 资产 ID | 中文名称 | 级别 | 建模与摆放要求 | 交互要求 |
|---|---|---|---|---|
| `env_s5_digital_gallery` | 现代数字展厅 | P1 | 明亮冷色、简洁展台和抽象波纹，控制透明材质 | 提供热点移动点，首轮可不做自由碰撞 |
| `p_s5_switch` | 程控交换机 | P1 必交 | 设备机柜和模块结构可辨 | 点击讲解程控交换意义 |
| `p_s5_base_station` | 基站模型 | P1 | 采用缩比展示，避免完整城市外景 | 点击介绍移动通信网络 |
| `p_s5_terminal` | 5G 终端 | P2 | 屏幕内容使用程序 UI 或低成本贴图 | 点击介绍 5G 应用 |
| `p_s5_satellite` | 通信卫星模型 | P2 | 太阳翼和天线结构简化但比例协调 | 点击介绍天地一体通信 |

**首轮完成条件**：模板环境 + `p_s5_switch` + 一段经审核讲解。

### 4.9 场景内容表模板

内容组为每个文物填写下表，缺少任一必填项时不得进入 Release 包：

| 字段 | 必填 | 规则 |
|---|---|---|
| `id` | 是 | 必须与 `scene.json` 中的资产 ID 完全一致 |
| 中文标题 | 是 | 建议 4–16 字 |
| 简介正文 | 是 | 建议 150–300 字，避免无法证实的绝对化表述 |
| 音频脚本 | 是 | 建议 60–120 秒，与正文事实一致 |
| 音频文件 | 是 | MP3/AAC，响度统一，无明显底噪 |
| 史料来源 | 是 | 书目、馆藏说明、采访编号或官方页面 |
| 撰稿人/审核人 | 是 | 可追溯到具体人员 |
| 素材授权 | 是 | 自有、获授权、公共领域或合理使用依据 |
| 扩展图片 | 否 | 用于 UI 放大，不直接堆入 3D 贴图 |

---

## 5. 3D 内容生产规范

### 5.1 运行时资产结构

```text
assets/
├── global_manifest.json
└── scenes/
    └── scene_S1/
        ├── environment.glb
        ├── props/
        │   ├── radio_station.glb
        │   ├── code_book.glb
        │   └── telegraph_key.glb
        ├── audio/
        │   ├── radio_station.mp3
        │   ├── code_book.mp3
        │   └── telegraph_key.mp3
        ├── scene.json
        └── content.json
```

Blender 工程、原始高分辨率贴图和未压缩音频属于源资产，放入独立 `source_assets/` 或 LFS，不进入 APK。

### 5.2 建模规范

| 项目 | 初始规范 | 说明 |
|---|---|---|
| 格式 | GLB（glTF 2.0） | 运行时不直接接收 FBX、OBJ、BLEND |
| 坐标系 | Y-up、右手系、-Z 朝前 | 导出后真机验证 |
| 单位 | 1 unit = 1 米 | 文物按真实尺寸 |
| 面数 | 环境建议 ≤ 80k tris；单文物建议 ≤ 15k tris | 不是唯一性能指标 |
| 贴图 | KTX2 / BasisU；通常 ≤ 2048×2048 | 优先嵌入运行时 GLB |
| 材质 | PBR metallic-roughness | 避免 Blender 私有节点 |
| Draw Call | 每场景按真机 Profile 控制 | 材质数量和透明物体必须受控 |
| 原点 | 文物底面中心 | 便于程序放置 |
| 命名 | 英文小写下划线 | 如 `radio_body` |
| 动画 | 可选 `idle` / `interact` | 不阻塞 MVP |

上述数值是初始预算。M1 使用真实 S1 资产完成 GPU、内存、包体测量后，技术负责人可以收紧或放宽，但必须记录变更。

### 5.3 触发图规范

- 打印尺寸 A6（105×148 mm），电子版建议 1080×1500 px。
- 图案需要丰富且不对称，避免大面积纯色、重复纹理和严重压缩。
- 使用 `arcoreimg eval-img` 评估，目标分数不低于 75；低于目标必须重新设计。
- 每张卡同时包含触发图和二维码，确保识图失败时仍能进入。
- 输出 `trigger_S1.png … trigger_S5.png`，并记录对应 `scene_id`。

### 5.4 统一数据契约

#### `global_manifest.json`

```json
{
  "schema_version": 1,
  "content_version": "2026.07.20.1",
  "scenes": [
    {
      "scene_id": "S1",
      "scene_name": "平西隐蔽通信主题展馆",
      "qr_payload": "REDWAVE-S1",
      "image_name": "trigger_S1",
      "scene_manifest": "scenes/scene_S1/scene.json",
      "content_manifest": "scenes/scene_S1/content.json",
      "thumbnail": "scenes/scene_S1/thumbnail.webp",
      "package_version": 1,
      "bundled": true
    }
  ]
}
```

#### `scene.json`

```json
{
  "schema_version": 1,
  "scene_id": "S1",
  "environment_glb": "environment.glb",
  "visitor_start": {
    "position_m": [0.0, 1.6, 3.0],
    "rotation_deg": [0.0, 180.0, 0.0]
  },
  "movement": {
    "type": "bounds",
    "speed_mps": 1.2,
    "x_min_m": -5.0,
    "x_max_m": 5.0,
    "z_min_m": -5.0,
    "z_max_m": 5.0
  },
  "colliders": [
    {
      "id": "wall_north",
      "min_m": [-5.0, 0.0, -5.2],
      "max_m": [5.0, 3.0, -4.8]
    }
  ],
  "move_points": [
    {
      "id": "mp_radio",
      "position_m": [0.0, 1.6, 1.5],
      "look_at_m": [1.2, 1.0, -1.0]
    }
  ],
  "props": [
    {
      "id": "p_s1_radio",
      "glb": "props/radio_station.glb",
      "position_m": [1.2, 0.8, -1.0],
      "rotation_deg": [0.0, 30.0, 0.0],
      "scale": 1.0,
      "interaction_radius_m": 1.5,
      "highlight_anchor_m": [0.0, 0.6, 0.0]
    }
  ]
}
```

#### `content.json`

```json
{
  "schema_version": 1,
  "scene_id": "S1",
  "items": [
    {
      "id": "p_s1_radio",
      "title": "秘密电台",
      "text": "经内容审核后的介绍文本。",
      "audio": "audio/radio_station.mp3",
      "audio_duration_sec": 90,
      "sources": [
        {
          "title": "来源名称或档案编号",
          "type": "museum_label",
          "locator": "展柜或档案位置"
        }
      ],
      "author": "内容组",
      "reviewer": "项目负责人",
      "review_status": "approved"
    }
  ]
}
```

建模方负责 `scene.json` 中的资产与空间数据；内容组负责 `content.json`；编码方负责 `global_manifest.json`、Schema 校验和最终集成。

### 5.5 数据字段约束

#### `global_manifest.json` 字段

| 字段 | 类型 | 必填 | 约束 |
|---|---|---|---|
| `schema_version` | integer | 是 | 当前为 `1`，不兼容变更时递增 |
| `content_version` | string | 是 | 建议 `YYYY.MM.DD.N`，用于缓存失效 |
| `scenes` | array | 是 | `scene_id` 不得重复 |
| `scene_id` | string | 是 | 正则 `^S[1-9][0-9]*$` |
| `qr_payload` | string | 是 | 全局唯一；解析前去除首尾空白但区分大小写 |
| `image_name` | string | 是 | 与 ARCore 图片库中的名称一致 |
| `scene_manifest` | string | 是 | 相对 assets 或场景包根目录，不允许 `..` |
| `content_manifest` | string | 是 | 同上 |
| `thumbnail` | string | 是 | WebP/PNG，用于首页卡片 |
| `package_version` | integer | 是 | 场景包更新时递增 |
| `bundled` | boolean | 是 | `true` 表示随 APK 安装 |

#### `scene.json` 字段

| 字段 | 类型 | 必填 | 约束 |
|---|---|---|---|
| `scene_id` | string | 是 | 必须与全局索引一致 |
| `environment_glb` | string | 是 | 路径存在且扩展名为 `.glb` |
| `visitor_start.position_m` | float[3] | 是 | 位于可行走区内，Y 通常为 1.6 |
| `visitor_start.rotation_deg` | float[3] | 是 | 顺序固定为 X/Y/Z，角度单位为度 |
| `movement.type` | enum | 是 | `bounds`、`hotspots` 或未来版本定义的值 |
| `movement.speed_mps` | float | 是 | MVP 建议 0.6–1.8 |
| `colliders` | array | 否 | AABB；`min_m` 每一维必须小于 `max_m` |
| `move_points` | array | 否 | 热点模式必填；位置必须位于安全区域 |
| `props` | array | 是 | 至少 1 项；`id` 全场景唯一 |
| `props[].position_m` | float[3] | 是 | 世界坐标，单位米 |
| `props[].rotation_deg` | float[3] | 是 | 世界欧拉角，仅用于配置；加载时转四元数 |
| `props[].scale` | float | 是 | 大于 0；非 1 值必须由技术负责人确认 |
| `interaction_radius_m` | float | 是 | 建议 0.3–2.0 |
| `highlight_anchor_m` | float[3] | 是 | 相对文物局部坐标，用于悬浮提示 |

#### `content.json` 字段

| 字段 | 类型 | 必填 | 约束 |
|---|---|---|---|
| `items[].id` | string | 是 | 必须能在 `scene.json.props[].id` 中找到 |
| `title` | string | 是 | 不能为空，建议不超过 24 个汉字 |
| `text` | string | 是 | 不能为空；Release 禁止占位文本 |
| `audio` | string | 是 | 文件存在，格式在 Media3 支持范围内 |
| `audio_duration_sec` | integer | 是 | 与实际音频误差不超过 2 秒 |
| `sources` | array | 是 | 至少 1 项；包含标题、类型和定位信息 |
| `author` / `reviewer` | string | 是 | Release 禁止 `待填写` |
| `review_status` | enum | 是 | 仅 `draft`、`reviewing`、`approved`；Release 只接收 `approved` |

### 5.6 Schema 级校验规则

编码方除 JSON 语法校验外，还必须实现以下跨文件检查：

1. 全局索引中的每个场景文件都存在，且三个文件内的 `scene_id` 一致。
2. `qr_payload`、`image_name`、文物 ID、碰撞盒 ID 和移动点 ID 在各自作用域内唯一。
3. 每个 `content.items[].id` 都对应一个文物；每个 MVP 文物都有已批准内容。
4. GLB、音频和缩略图路径必须解析在允许的资源根目录内，拒绝绝对路径和路径穿越。
5. 游客起点和移动点必须在 movement bounds 内，并且不得落入 collider。
6. 文物缩放必须为有限正数；所有坐标和角度必须是有限数，拒绝 `NaN` 和无穷值。
7. Release 构建发现占位文字、缺失来源、缺失音频或未批准内容时直接失败，不静默跳过。

### 5.7 建模输入包

建模模型开始任何资产前，技术负责人必须提供以下输入。缺失项应先列为阻塞，不得凭空补全历史细节：

```text
modeling_input/SX/
├── brief.md                  # 场景主题、空间尺寸、资产 ID、优先级
├── references/
│   ├── index.md              # 每张参考图的来源、授权和用途
│   ├── environment/          # 建筑/空间参考
│   └── props/                # 文物多角度参考
├── content_outline.md        # 文物名称与已确认历史要点
├── scale_reference.png       # 人体或标准物比例尺
└── scene_seed.json           # 预分配 ID、起点和初始位置
```

参考图不足时，建模模型可以完成白盒比例和结构，但不得自行生成带有具体历史铭文、徽标、序列号或档案内容的最终贴图。

### 5.8 建模生产流程

1. **参考审计**：确认正面、侧面、背面、尺寸和材质信息；把未知部分列入 `open_questions.md`。
2. **白盒阶段**：只做空间比例、游客起点、主通道、文物位置和相机视线；输出灰模 GLB。
3. **白盒联调**：编码方加载灰模，验证坐标轴、比例、移动边界、碰撞盒和热点位置。
4. **中模阶段**：完成轮廓、主要机械结构、UV 和材质分组；不提前雕刻手机端不可见细节。
5. **贴图阶段**：完成 PBR 贴图、必要烘焙和 KTX2 压缩；检查在中端手机上的可辨识度。
6. **交互准备**：文物根节点、动画节点和交互提示锚点命名固定；不随最终导出自动重命名。
7. **运行时优化**：清理隐藏面、重复材质、未使用贴图和不可见小物件；必要时提供 LOD。
8. **导出验证**：用 glTF Validator 检查；在独立 glTF 查看器和项目真机各验证一次。
9. **交付报告**：输出资产统计、已知问题、来源清单、预览图和 `scene.json` 建议值。

### 5.9 Blender / DCC 文件约定

- Collection 建议按 `ENV`、`PROPS`、`COLLISION_GUIDE`、`LIGHT_GUIDE` 分组。
- 所有应用到运行时的对象必须执行合理的 Rotation/Scale Apply；根节点缩放保持 1。
- 环境和文物分文件交付，避免修改一个小文物时重新导出整个场景。
- 碰撞参考几何不导入正式渲染 GLB；由 `scene.json.colliders` 表达，或在导出前剔除。
- 不使用依赖 Blender 插件才能还原的私有材质节点；最终材质必须能映射到 glTF PBR。
- 透明材质只用于确有必要的玻璃、屏幕或灯罩，并单独统计；能用遮罩就不用半透明混合。
- 法线、切线、UV、贴图色彩空间必须正确：Base Color/Emissive 为 sRGB，法线/粗糙度/金属度为线性数据。
- 文物原点位于底面中心，正面朝 -Z；环境原点位于世界设计原点。
- 动画只使用 glTF 支持的节点、骨骼或形变动画；每段动画名称唯一且可循环属性明确。

### 5.10 资产性能报告模板

每个 GLB 随交付提供一行统计，汇总到 `asset_report.csv`：

| 字段 | 示例 | 验收用途 |
|---|---|---|
| `asset_id` | `p_s1_radio` | 与配置关联 |
| `file` | `props/radio_station.glb` | 路径检查 |
| `size_bytes` | `7340032` | 包体预算 |
| `triangles` | `12450` | 几何预算 |
| `vertices` | `7800` | 内存参考 |
| `materials` | `3` | Draw Call 参考 |
| `textures` | `5` | 纹理数量 |
| `max_texture_px` | `2048` | 纹理预算 |
| `animations` | `idle;interact` | 程序绑定 |
| `validator_errors` | `0` | 必须为 0 |
| `validator_warnings` | `1` | 需解释或消除 |

### 5.11 建模交付目录

```text
modeling_delivery/SX/
├── runtime/
│   ├── environment.glb
│   ├── props/*.glb
│   ├── thumbnail.webp
│   └── scene.json
├── source/
│   ├── scene_SX.blend
│   ├── props/*.blend
│   └── textures_source/
├── preview/
│   ├── scene_overview.png
│   ├── visitor_start.png
│   └── props_contact_sheet.png
├── asset_report.csv
├── references/index.md
├── open_questions.md
└── CHANGELOG.md
```

### 5.12 建模验收清单

- [ ] 文件名、节点名、材质名和资产 ID 符合约定。
- [ ] Y-up、右手系、-Z 朝前、米制单位、根节点单位缩放均正确。
- [ ] 游客起点看得到首个交互文物，主通道无遮挡。
- [ ] 环境和文物没有明显穿插、漂浮、反面或法线错误。
- [ ] GLB 在独立查看器中无丢贴图、粉色材质或动画断裂。
- [ ] Validator error 为 0；warning 已消除或记录理由。
- [ ] 真机画面中铭牌和关键结构可辨，暗部不过黑，高光不过曝。
- [ ] 单资产和整场景达到 M1 后冻结的包体、面数、材质和纹理预算。
- [ ] `scene.json` 坐标、碰撞盒、移动点和交互锚点已在真机核对。
- [ ] 源文件、运行时文件、预览、统计和参考来源全部齐全。

---

## 6. 工程实现指引

### 6.1 项目骨架

```text
red-wave-ar/
├── app/src/main/
│   ├── java/cn/bistu/redwave/
│   │   ├── ui/
│   │   ├── entry/
│   │   │   ├── qr/
│   │   │   ├── image/
│   │   │   └── resolver/
│   │   ├── vr/
│   │   ├── render/
│   │   ├── scene/
│   │   ├── sensor/
│   │   ├── interaction/
│   │   ├── audio/
│   │   └── data/
│   └── assets/
├── source_assets/
├── docs/
└── gradle/libs.versions.toml
```

### 6.2 技术验证顺序

1. 建立 Compose + Filament 空场景并稳定运行。
2. 加载一个真实 GLB，验证材质、尺寸、灯光和内存。
3. 接入 SensorManager，实现回正、平滑和触屏切换。
4. 接入 `View.pick(...)` 或交互碰撞盒，完成一个文物信息卡。
5. 接入 Media3 音频。
6. 接入二维码并解析 `scene_id`。
7. 最后接入 ARCore 图片识别，验证识别后释放相机再进入虚拟场景。

这样可以把 ARCore 生命周期问题与虚拟展馆渲染问题分开定位。

### 6.3 资源与数据流

- 启动时读取 `global_manifest.json` 并校验 Schema。
- 入口模块只输出 `scene_id`，不得直接调用 Filament。
- SceneCoordinator 根据 `scene_id` 加载 `scene.json` 与 `content.json`。
- GLB 加载、实体映射、音频和内容绑定由统一 ID 关联，不在代码中硬编码坐标或文案。
- 场景切换时必须销毁旧实体、纹理、音频和传感器监听，避免内存泄漏。

### 6.4 性能与兼容性目标

| 指标 | v1.3 目标 | 测量条件 |
|---|---|---|
| 已安装场景加载 | ≤ 5 秒 | 不含首次权限和 AR 服务安装 |
| 帧率 | ≥ 30 FPS | 指定中端主展示机，S1 Release 构建 |
| 连续稳定运行 | ≥ 30 分钟无 crash | 完整参观与多次切换 |
| 内存峰值 | 初始目标 ≤ 500 MB | Android Studio Profiler / 系统统计 |
| 基础 APK | 初始目标 ≤ 50 MB | 仅内置应用与 S1，实测后冻结 |
| 触发图识别 | 10 次至少成功 9 次 | 指定光照、距离和打印卡 |
| 最低系统 | Android 8.0（API 26） | ARCore 为可选能力 |
| 降级路径 | 二维码 + 手动列表 + 触屏环视 | ARCore 或陀螺仪不可用时 |

M0 前必须把“主展示机、备用机、低配测试机”的具体品牌、型号、Android 版本和 ARCore 支持状态填入测试记录，不再用“骁龙 7 系”等模糊描述代替。

### 6.5 Android 工程原则

- MVP 使用**单 app module + 清晰 package 分层**，不为形式上的“整洁架构”提前拆分大量 Gradle module。
- UI 使用单 Activity 和 Compose Navigation；Filament 渲染表面通过 `AndroidView` 或明确封装的 View 容器接入。
- `ViewModel` 只保存可序列化的 UI/业务状态，不持有 Activity、ARCore Session、Filament Engine、Surface 或 ExoPlayer。
- Camera、ARCore、Filament、Sensor 和 Audio 都由独立 owner 管理生命周期，并由 SceneCoordinator 编排。
- 所有 IO、JSON 解析和校验离开主线程；所有 Filament Engine 变更在统一渲染线程/主线程策略下串行执行。
- 不允许入口层直接操作场景，也不允许 GLB 节点名直接泄漏到 Compose UI。
- Release 关闭调试菜单和冗余日志，但保留错误码、版本号、设备信息与资产版本的诊断页。

### 6.6 推荐 package 与职责

| Package | 主要类/接口 | 职责边界 |
|---|---|---|
| `ui.home` | `HomeScreen`, `HomeViewModel` | 首页、场景列表、入口选择 |
| `ui.scan` | `QrScanScreen`, `ImageScanScreen` | 权限提示和扫描 UI，不直接加载场景 |
| `ui.vr` | `VrScreen`, `VrHud`, `InfoSheet` | 渲染容器上层 UI、模式开关、信息卡 |
| `entry` | `EntryResolver`, `EntryResult` | 把二维码值/图片名称统一映射为 `scene_id` |
| `entry.qr` | `QrScannerController` | ZXing 生命周期、结果去重和超时 |
| `entry.image` | `ImageRecognizerController` | ARCore Session、图片库、识别状态 |
| `scene` | `SceneCoordinator`, `SceneStateMachine` | 状态跳转、加载、切换、退出和错误恢复 |
| `render` | `FilamentHost`, `SceneRenderer` | Engine/View/Scene/Camera/SwapChain 和帧循环 |
| `render.asset` | `GltfAssetStore` | AssetLoader、ResourceLoader、实体释放 |
| `sensor` | `OrientationController` | 旋转向量、回正、屏幕方向补偿、平滑 |
| `interaction` | `MovementController`, `PickingController` | 摇杆、碰撞、热点移动、实体拾取 |
| `audio` | `NarrationController` | 单实例 ExoPlayer、播放状态、切换停止 |
| `data` | `ManifestRepository`, `SceneRepository` | JSON 读取、Schema 校验、路径解析、缓存 |
| `diagnostics` | `DiagnosticsCollector` | FPS、加载耗时、错误码、设备与资源版本 |

### 6.7 核心领域模型

以下代码用于约束字段与职责；实现时可以拆文件，但字段语义不得擅自改变：

```kotlin
@Serializable
data class GlobalManifest(
    val schemaVersion: Int,
    val contentVersion: String,
    val scenes: List<SceneIndexItem>
)

@Serializable
data class SceneIndexItem(
    val sceneId: String,
    val sceneName: String,
    val qrPayload: String,
    val imageName: String,
    val sceneManifest: String,
    val contentManifest: String,
    val thumbnail: String,
    val packageVersion: Int,
    val bundled: Boolean
)

data class EntryResult(
    val sceneId: String,
    val source: EntrySource
)

enum class EntrySource { QR, IMAGE, MANUAL }

sealed interface SceneUiState {
    data object Home : SceneUiState
    data class Scanning(val type: EntrySource) : SceneUiState
    data class Loading(val sceneId: String, val progress: Float) : SceneUiState
    data class Exploring(val sceneId: String, val sensorMode: SensorMode) : SceneUiState
    data class Error(val code: AppErrorCode, val recoverable: Boolean) : SceneUiState
}

enum class SensorMode { GYROSCOPE, TOUCH }
```

JSON 使用 `snake_case`，Kotlin 使用 `camelCase`；通过 `@SerialName` 或统一命名策略映射。禁止为省事把所有字段做成 nullable；只有契约明确可选的字段才允许空值。

### 6.8 入口解析与去重

`EntryResolver` 是三种入口与场景系统之间的唯一桥梁：

```kotlin
interface EntryResolver {
    fun resolveQr(payload: String): Result<EntryResult>
    fun resolveImage(imageName: String): Result<EntryResult>
    fun resolveManual(sceneId: String): Result<EntryResult>
}
```

规则：

1. 启动时从 `global_manifest.json` 建立二维码、图片名和场景 ID 三张不可变索引。
2. 重复值视为清单错误，应用进入诊断错误页，不按“第一个匹配”继续。
3. 扫描控制器收到连续相同结果时，只处理第一次；在导航完成前忽略后续帧。
4. 无法识别的二维码显示“不是本项目卡片”，不能把任意 URL 当场景 ID。
5. 识图状态需达到 ARCore `TRACKING`；记录图片名称后立即冻结结果，开始释放 Session。
6. 入口成功事件只携带 `scene_id` 和入口类型，不携带 Bitmap、Camera Frame、Anchor 或 Pose。

### 6.9 Camera 与 ARCore 生命周期

二维码和触发图页面互斥，不同时占用摄像头。建议生命周期如下：

```text
进入扫描页
  ├─检查 CAMERA 权限
  ├─检查对应能力（QR / ARCore）
  ├─创建并 resume 扫描控制器
  └─收到唯一 EntryResult
         ├─停止分析帧
         ├─pause / close Session 或 scanner
         ├─释放 Surface、Camera 和回调
         └─确认释放完成后导航到 Loading
```

- `onPause` 必须暂停二维码扫描或 ARCore Session；`onDestroy` 必须关闭并清空引用。
- 用户拒绝 Camera 权限后仍应返回首页并使用手动列表；不循环弹权限框。
- ARCore 未安装、需要更新或设备不兼容时显示具体原因，并提供“改用二维码/手动选择”。
- 从 VR 返回扫描页时创建新的扫描会话，不复用已关闭的旧 Session。
- 应编写生命周期测试覆盖：切后台、锁屏、旋转屏幕、拒绝权限、扫描成功瞬间按返回键。

### 6.10 Filament 对象所有权与渲染循环

`FilamentHost` 负责以下对象，创建和销毁顺序固定：

| 对象 | 创建时机 | 销毁要求 |
|---|---|---|
| `Engine` | 进入第一个 VR 页面前懒加载 | App 结束或明确释放 Host 时最后销毁 |
| `Renderer` | Engine 创建后 | 在 Engine 前销毁 |
| `Scene` | 每个虚拟场景一个 | 切场景时先移除并销毁实体 |
| `View` | VR 渲染容器建立时 | 先解除 Scene/Camera 再销毁 |
| `Camera` + entity | View 建立时 | 从 View 解绑后销毁 |
| `SwapChain` | Surface available 时 | Surface destroyed 时立即销毁 |
| `AssetLoader` | Host 初始化时 | 所有 asset 已释放后销毁 |
| `ResourceLoader` | Host 初始化时 | 取消异步加载后销毁 |

每帧流程：

1. `Choreographer` 提供帧时间并计算 `dt`，异常大间隔需截断。
2. 更新 ResourceLoader 异步加载进度。
3. 更新传感器目标姿态与平滑后的相机旋转。
4. 更新摇杆位移、碰撞和热点动画。
5. 更新 glTF Animator（如有）。
6. `renderer.beginFrame(swapChain)` 成功后渲染 View，再 `endFrame()`。
7. Surface 不可用、页面后台或对象已释放时不得继续提交帧。

### 6.11 场景加载管线

```text
scene_id
  → 查全局索引
  → 定位 bundled assets 或已安装场景包
  → 并行读取 scene.json / content.json
  → Schema + 跨文件校验
  → 创建空 Scene、Camera、IBL 与主光源
  → 加载 environment.glb
  → 分批加载 props/*.glb
  → 建立 entity ↔ prop_id 映射
  → 绑定 content 与 audio 路径
  → 设置 visitor_start、movement、colliders
  → 首帧成功后进入 Exploring
```

建议进度权重：配置校验 10%、环境 40%、文物 35%、纹理/资源完成 10%、首帧 5%。不能只按文件数计算，否则大环境加载时进度会长时间不动。

加载行为：

- 支持取消：退出 Loading 或切换场景时取消未完成加载，不再回调旧页面。
- 环境加载失败视为致命；P2 文物失败可降级隐藏，但必须记录错误和显示“部分展品暂不可用”。
- 首帧前先显示 Loading，不把未完成材质和跳动物体直接展示给用户。
- 切场景时先停音频和传感器监听，再移除实体、销毁资源，最后创建新 Scene。
- 同一场景重复进入可缓存已解析 JSON；是否缓存 GPU 资源由内存实测决定，默认不跨场景常驻。

### 6.12 姿态算法规格

陀螺仪模式使用 `TYPE_GAME_ROTATION_VECTOR`，不使用 ARCore Pose。算法步骤：

1. 把 SensorEvent 的 rotation vector 转为单位四元数 `q_device`。
2. 根据屏幕 `ROTATION_0/90/180/270` 重映射设备坐标，得到 `q_screen`。
3. 首次有效采样或点击“回正”时保存基准 `q_reference`。
4. 计算相对姿态 `q_relative = inverse(q_reference) * q_screen`。
5. 为减少眩晕，默认去除 roll，只保留 yaw/pitch；如后续需要完整 roll，放入高级设置。
6. 对目标姿态使用与帧率无关的 slerp：`alpha = 1 - exp(-dt / tau)`，`tau` 初始建议 0.08–0.15 s。
7. 把相对姿态应用到相机朝向；相机位置由 MovementController 独立维护。

触屏模式：

- 水平拖动改变 yaw，垂直拖动改变 pitch。
- pitch 限制在约 `[-80°, 80°]`，避免翻转。
- 切换模式时，以当前画面姿态初始化新模式，禁止瞬间跳回零角度。
- 页面进入后台时暂停传感器监听；恢复后重新建立参考姿态并提示用户回正。

### 6.13 虚拟移动与碰撞

摇杆输入为二维向量 `(x, y)`，长度先限制到 1，再应用死区。移动方向基于当前视角投影到水平面：

```text
forward = normalize(projectToXZ(cameraForward))
right   = normalize(cross(forward, worldUp))
delta   = (right * joystick.x + forward * joystick.y) * speed * dt
```

规则：

- `dt` 上限建议 50 ms，防止恢复前台时一步穿墙。
- 游客使用半径约 0.25 m 的二维圆形代理，不把相机当无体积点。
- 先检查 movement bounds，再用圆形代理与 AABB collider 做分轴滑动；碰到墙时允许沿墙移动。
- 不实现重力、跳跃、台阶和复杂物理；所有可行走地面视为同一高度。
- 热点移动模式点击后使用 200–400 ms 淡出/淡入切换位置，避免高速相机飞行导致眩晕。
- 模型坐标变化后，建模方必须重新核对 colliders 和 move_points，不能只替换 GLB。

### 6.14 文物拾取与高亮

- Android 触摸坐标原点在左上，Filament Viewport 坐标需要按当前 Surface 尺寸转换 Y 轴。
- 使用 `View.pick(x, y, handler, callback)` 获取异步结果；回调可能晚于页面退出，必须核对 Scene token。
- 通过加载时建立的 `entityId → propId` 映射找到文物；环境实体、提示点和不可交互装饰不进入映射。
- 同一文物由多个 mesh/entity 构成时，全部映射到同一 `propId`。
- 点击空白区域关闭信息卡或取消选中；点击 UI 时不得穿透到 3D。
- 高亮优先使用独立提示图标、轮廓替代材质或轻量 emissive 变化；不得每次点击重新创建大量 MaterialInstance。
- `interaction_radius_m` 用于限制过远点击：即使屏幕拾取命中，游客距离过远也只提示靠近，不直接打开内容。

### 6.15 音频控制

`NarrationController` 全应用只维护一个 ExoPlayer：

```kotlin
interface NarrationController {
    fun play(itemId: String, source: AudioSource)
    fun pause()
    fun resume()
    fun stop(reason: StopReason)
    val state: StateFlow<NarrationState>
}
```

- 打开新文物自动停止旧讲解并从头播放新音频。
- 关闭信息卡时默认暂停；切场景、返回首页或资源错误时停止并清空 MediaItem。
- 本地 assets 和下载场景包通过统一 `AudioSource` 抽象，UI 不关心实际 URI。
- UI 显示标题、播放/暂停、进度、总时长和文字稿；拖动进度条为 P1。
- 音频焦点丢失时暂停；耳机拔出时暂停；不在 MVP 中做后台播放和通知栏控制。
- 所有正式音频统一响度、采样率策略和开头/结尾静音，具体参数由音频负责人冻结后记录。

### 6.16 UI 页面规格

| 页面 | 必须元素 | 主要状态 | 失败/空状态 |
|---|---|---|---|
| 启动页 | Logo、版本号、初始化进度 | 读取索引、检查资源 | 清单无效时进入诊断页 |
| 首页 | 扫二维码、识别卡片、场景列表 | 正常、资源更新中 | Camera 不可用仍可手动进入 |
| 二维码页 | 取景框、手电筒、返回、帮助 | 扫描、已识别 | 非项目码、权限拒绝、超时 |
| 图片识别页 | 取景框、卡片轮廓提示、返回 | 初始化、搜索、已识别 | ARCore 缺失/不兼容/更新失败 |
| Loading | 场景名、进度、取消 | 校验、环境、文物、首帧 | 缺文件、版本不兼容、内存不足 |
| VR 展馆 | 渲染区、摇杆/热点、回正、模式切换、返回 | 探索、选中文物、音频播放 | 部分文物缺失提示 |
| 信息卡 | 标题、正文、来源摘要、音频控制 | 展开/收起、播放/暂停 | 音频失败时仍展示文字 |
| 设置/诊断 | 传感器模式、灵敏度、版本、设备、资产版本 | 正常 | 提供复制诊断摘要 |

UI 叠加规则：MVP 固定横屏；VR 页面渲染区铺满屏幕，所有触控区域满足可点击尺寸；摇杆与信息卡不重叠；信息卡展开时暂停摇杆输入，避免阅读时继续移动。

### 6.17 权限与能力矩阵

| 能力 | Camera 权限 | ARCore | 陀螺仪 | 网络 |
|---|---:|---:|---:|---:|
| 二维码入口 | 需要 | 不需要 | 不需要 | 不需要 |
| 触发图入口 | 需要 | 需要且设备兼容 | ARCore 自行使用传感器 | 不需要，服务安装/更新除外 |
| 手动入口 | 不需要 | 不需要 | 不需要 | 不需要 |
| 陀螺仪 VR | 不需要 | 不需要 | 需要 | 不需要 |
| 触屏 VR | 不需要 | 不需要 | 不需要 | 不需要 |
| 可选场景下载 | 不需要 | 不需要 | 不需要 | 需要 |

### 6.18 错误码与恢复动作

| 错误码 | 场景 | 用户提示 | 恢复动作 |
|---|---|---|---|
| `CAMERA_PERMISSION_DENIED` | 相机权限拒绝 | 无法使用扫描入口 | 返回首页并突出手动入口 |
| `ARCORE_UNSUPPORTED` | 设备不支持 ARCore | 当前设备不能识别卡片 | 改用二维码或手动选择 |
| `ARCORE_INSTALL_REQUIRED` | 缺少服务 | 需要安装/更新 AR 服务 | 引导安装；失败后降级 |
| `ENTRY_UNKNOWN` | 未知二维码/图片 | 未识别为项目卡片 | 继续扫描或手动选择 |
| `MANIFEST_INVALID` | JSON/跨文件校验失败 | 资源配置损坏 | 显示诊断编号，不进入场景 |
| `SCENE_PACKAGE_MISSING` | 场景未安装 | 该场景资源尚未安装 | 下载、重新安装或返回 |
| `GLB_LOAD_FAILED` | GLB 无法解析 | 场景加载失败 | 重试一次；仍失败则返回 |
| `PARTIAL_PROP_FAILED` | 非核心文物失败 | 部分展品暂不可用 | 隐藏该文物并继续参观 |
| `AUDIO_LOAD_FAILED` | 音频缺失/损坏 | 音频暂不可用 | 保留文字内容 |
| `SENSOR_UNAVAILABLE` | 无旋转向量 | 已切换触屏模式 | 自动启用 Touch |
| `RENDER_SURFACE_LOST` | Surface 丢失 | 正在恢复画面 | 重建 SwapChain；超时返回 |
| `OUT_OF_MEMORY_RISK` | 内存压力 | 场景过大，无法稳定加载 | 清理资源并返回首页 |

所有错误日志至少包含：错误码、App 版本、设备型号、Android 版本、场景 ID、包版本和最近状态；不记录相机画面、用户姓名或其他无关个人信息。

### 6.19 场景包与离线策略

MVP 的 S1 位于 APK assets。P1 场景包建议结构：

```text
files/scenes/S2/3/
├── package_manifest.json
├── scene.json
├── content.json
├── environment.glb
├── props/*.glb
├── audio/*
└── thumbnail.webp
```

- 下载到临时目录，校验文件清单、大小和 SHA-256 后再原子切换到正式版本目录。
- 只在新版本完整可用后删除旧版本；安装失败继续使用旧版本。
- `package_manifest.json` 记录 `scene_id`、`package_version`、`schema_version`、文件哈希和总大小。
- 清理缓存时不能删除当前正在使用的场景包。
- 若项目周期内不实现下载，采用活动前把全部场景随专用 APK 打包的方式，文档中明确构建变体，不假装已支持在线更新。

### 6.20 可观测性与性能采样

Debug/内部测试构建显示诊断浮层：

- 当前 FPS、帧时间 P50/P95。
- 当前场景、状态机状态、SensorMode。
- 加载总耗时及配置/环境/文物/首帧分段耗时。
- GLB 数量、实体数量、材质数量、纹理估算、内存峰值。
- 当前姿态采样率、渲染分辨率和 Surface 尺寸。
- 最近 10 条错误码和场景切换记录。

Release 默认关闭浮层，但在设置页连续点击版本号 5 次可打开内部诊断模式，便于现场排错。

### 6.21 安全释放顺序

退出 VR 或切场景时按以下顺序执行，禁止依赖 GC：

1. 禁止新输入事件和拾取回调。
2. 停止 NarrationController。
3. 注销 SensorEventListener 和 Choreographer callback。
4. 取消异步资源加载，等待或忽略带旧 Scene token 的回调。
5. 从 Filament Scene 移除所有实体。
6. 逐个释放 glTF asset、纹理和相关实体。
7. 解绑 View 的 Scene 和 Camera。
8. Surface 销毁时释放 SwapChain。
9. 场景级对象清空后回到 Home；Engine 是否保留由 Host 策略决定。

至少进行 20 次“进入 S1 → 返回首页”循环测试，确认内存不会持续增长。

---

## 7. 里程碑与技术闸门

| 里程碑 | 时间窗 | 关键交付 | 通过条件 |
|---|---|---|---|
| M0 范围冻结 | 7/20–7/22 | 确定负责人、目标机型、S1 资产清单、固定入口规则 | 编码与建模负责人已落实；主测试机可用 |
| M1 技术闸门 | 7/23–7/27 | 触发图/二维码 → S1 白盒 → 环视 → 移动 → 点击 → 音频 | Release 真机连续运行 20 分钟；核心链路无阻塞 |
| M2 S1 MVP | 7/28–8/02 | S1 正式环境、3 个文物、完整文案和音频 | 达到 §10 MVP 验收 |
| M3 五场景扩展 | 8/03–8/09 | S2–S5 轻量模板场景 | 五入口可用；每场景至少 1 个有效文物 |
| M4 联调与优化 | 8/10–8/15 | 性能优化、识别卡定稿、离线验证 | 三台目标机完成测试；高优先级问题关闭 |
| M5 发布与评优 | 8/16–8/20 | 签名 APK、演示视频、交接文档、实际成果清单 | 发布包可复现安装；附件表述与实测一致 |

### 7.1 闸门降级规则

- 触发图识别不稳定：保留二维码与手动入口，不阻塞虚拟展馆。
- 陀螺仪体验不稳定：默认触屏环视，陀螺仪作为可选设置。
- 摇杆碰撞无法按期完成：改为移动热点或有限可行走区域。
- S2–S5 专属环境来不及：继续使用统一轻量模板，不复制未经验证的高精度场景。
- APK 体积超标：基础包只保留 S1，其余场景改为预下载包。

---

## 8. 分工与协作

### 8.1 角色与职责

| 角色 | 负责人 | 职责 |
|---|---|---|
| 项目负责人 | 李雨霏 | 总体推进、场馆与指导老师对接、最终内容与成果表述确认 |
| 技术负责人 | 林泽羽 | 架构、技术闸门、数据契约、代码与资产验收 |
| Android 编码 | **M0 前落实** | 入口、虚拟展馆、传感器、交互、音频与发布 |
| 3D 建模 | **M0 前落实** | S1 白盒与正式资产、S2–S5 模板资产、`scene.json` |
| 内容文案/音频 | 文创组（宋佳麟等） | `content.json`、来源记录、讲解录音与审核流转 |
| 宣传/测试 | 宣讲组、安全组 | 目标用户测试、真机回归、现场保障与佐证材料 |

> Android 编码和 3D 建模负责人未落实时，M1 之后的日期只能视为目标，不能视为已承诺排期。

### 8.2 协作约定

- 代码和运行时配置进入 Git；大型源资产使用 Git LFS 或独立资产库。
- 所有合并通过 PR / MR，禁止直接覆盖已验收的 Schema 和资产。
- `scene.json` 与 `content.json` 在提交前运行 JSON Schema 校验。
- 模型先交白盒，再交材质版本；编码不得等待全部美术资源才开始。
- 内容必须经过来源和审核状态检查后才能进入 Release 包。
- M1 前采用每日短同步；M1 后每周一同步进度、周四预警风险。

---

## 9. 风险与对策

| 风险 | 影响 | 对策 |
|---|---|---|
| 五场景范围膨胀 | 延期、质量下降 | S1 旗舰 + S2–S5 轻量模板；通过闸门再扩展 |
| ARCore 设备不兼容 | 无法识图 | AR Optional；二维码和手动列表始终可用 |
| 触发图识别率低 | 入口失败 | `arcoreimg` 评分、实物测试、二维码兜底 |
| 相机未正确释放 | 黑屏、耗电、冲突 | 状态机统一管理权限与 Session 生命周期 |
| 陀螺仪漂移或眩晕 | 体验差 | 回正、平滑、限速、触屏模式和移动热点 |
| 摇杆穿墙 | 破坏体验 | 简单碰撞盒；来不及时使用安全区域或热点移动 |
| 模型过重 | 低帧率、内存高 | 真机 Profile、KTX2、减少材质和透明物体、必要时 LOD |
| APK 体积过大 | 分发困难 | 基础包内置 S1，其余场景预下载 |
| Android/建模负责人未落实 | 计划失真 | M0 前落实，否则缩小交付范围 |
| API 或依赖变化 | 伪代码无法实现 | M1 后固定依赖版本；示例代码必须通过编译 |
| 历史内容或版权问题 | 影响成果可信度 | 来源、审核、授权记录随内容一同交付 |
| 现场弱网 | 场景不可用 | 演示设备提前安装全部需要的场景包 |

---

## 10. 验收标准

### 10.1 技术 MVP：S1

- [ ] 二维码、触发图和手动列表均能解析到 S1；其中任一识别入口失败时可以切换兜底入口。
- [ ] 识别成功后相机画面停止，进入纯虚拟展馆，不存在现实画面叠加。
- [ ] 陀螺仪环视、视角回正和触屏环视均可用，输入模式切换不会跳变失控。
- [ ] 用户可以在限定区域移动，或通过移动热点到达所有可交互文物。
- [ ] 至少 3 个文物可以打开经审核的文字并播放对应音频。
- [ ] 指定主展示机达到 30 FPS、5 秒内加载和连续 30 分钟无 crash。
- [ ] 打印触发图在规定测试条件下 10 次至少成功识别 9 次。
- [ ] 无 ARCore 的兼容设备仍能使用二维码/手动入口和触屏模式。

### 10.2 最终交付

- [ ] S1 完整场景通过 MVP 验收。
- [ ] S2–S5 至少以轻量模板场景交付；升级为完整场景的数量按最终实测记录。
- [ ] 输出签名 APK、版本号、安装说明、设备兼容记录和资源清单。
- [ ] 输出 5 张触发卡印刷文件、演示视频和现场备用入口。
- [ ] `global_manifest.json`、`scene.json`、`content.json` 通过校验。
- [ ] 历史来源、审核记录和素材授权清单完成归档。
- [ ] 最终申报附件、总结报告和宣传文案只描述已经通过验收的功能。

### 10.3 增强验收

- [ ] 摩尔斯电码解谜流程完整。
- [ ] 打卡、收藏或截图分享至少完成一项。
- [ ] S2–S5 中至少一个升级为专属完整环境。
- [ ] 场景包可在活动前预下载并离线运行。

---

## 11. 立即执行事项

1. **负责人和设备**：在 M0 前确定 Android 编码、3D 建模负责人及三台目标测试机。
2. **S1 最小资产**：交付一张真实触发图、一个白盒房间、一个真实 GLB 文物和一段占位音频。
3. **技术闸门**：先跑通“识别 → 释放相机 → 进入虚拟场景 → 环视 → 移动 → 点击 → 音频”。
4. **依赖与 Schema 冻结**：M1 通过后固定依赖版本，并为三个 JSON 文件补充可执行 Schema。
5. **内容清单**：列出五场景首轮文物、来源、文案负责人、录音负责人和审核状态。
6. **基于实测回写附件**：M5 统计最终完整场景数、性能和可用入口，再形成对外成果表述。

> **当前唯一不可跳过的门槛**：在一台真实手机上完成“扫描或识图 → 退出相机 → 进入 S1 白盒虚拟展馆 → 手机环视 → 移动 → 点开一个文物 → 听到音频”。在此之前，不以五场景、美术打磨或增强功能代替核心链路验证。

---

## 12. 技术参考基线

- ARCore Augmented Images Android Guide：<https://developers.google.com/ar/develop/java/augmented-images/guide>
- ARCore Supported Devices：<https://developers.google.com/ar/devices>
- Filament Android Source / API：<https://github.com/google/filament>

---

## 13. 建模模型任务卡

后续建模模型必须按任务卡领取工作。一次只处理一个可独立验收的任务，不在没有参考和审核的情况下批量生成五场景最终资产。

### M3D-00：参考资料与比例审计

**输入**：§4 场景清单、`modeling_input/SX/`；S1 还必须读取 `research/S1_pingxi_intelligence_station/` 全部文件。

**动作**：为所有计划资产建立参考索引，标出尺寸、材质、可见面、未知区域、授权状态和历史内容风险。

**输出**：`references/index.md`、`open_questions.md`、资产优先级确认表。
**完成标准**：MVP 资产至少有正面、侧面或结构替代参考；未知铭文不被自行补画。

### M3D-01：S1 白盒场景

**依赖**：M3D-00、S1 `scene_seed.json`。

**动作**：制作约 5.3 m × 4.7 m × 2.25 m 的紧凑地下储洞小室白盒，放置起点、桌面、审核级通用电台、发报键、无铭文“电文与保密通信资料包”占位、低矮门洞、墙体和碰撞参考。该尺度是体验尺度，不作历史尺寸或原址复原声明。

**输出**：`environment_whitebox.glb`、三个占位文物 GLB、初版 `scene.json`、游客视角预览。
**完成标准**：真机比例正确，起点看得到电台，移动不出边界，热点可点击。

### M3D-02：S1 核心文物

**依赖**：M3D-01 白盒通过。

**动作**：按 `p_s1_radio`、`p_s1_key`、`p_s1_codebook` 顺序制作中模、UV、PBR 材质和运行时 GLB。`p_s1_codebook` 保留技术 ID，但只制作无铭文纸束/资料夹；电台型号、密码、电文、印章和馆藏身份在没有馆方资料时不得自行补全。

**输出**：源文件、运行时文件、预览、统计、节点说明。
**完成标准**：独立查看器与真机无材质错误，资产 ID/原点/朝向符合 §5，单资产预算合格。

### M3D-03：S1 正式环境

**依赖**：M3D-01、内容组确认环境参考。

**动作**：在不改变已验收空间尺度的前提下替换白盒墙体、桌椅、灯具和装饰；补碰撞盒。

**输出**：`environment.glb`、预览、资产报告、更新后的 `scene.json`。
**完成标准**：主通道和游客起点不变，暗部可辨，S1 整场达到性能目标。

### M3D-04：通用轻量展馆模板

**依赖**：S1 加载管线和性能闸门通过。

**动作**：制作可换主题色、展板和展台布局的轻量环境，用于 S2–S5 首轮交付。

**输出**：模板源文件、四个场景变体 GLB、每场景缩略图和起点。
**完成标准**：四场景视觉可区分但复用材质和结构，任何一个都能在目标机达到 30 FPS。

### M3D-05：S2–S5 首轮代表文物

**依赖**：M3D-00、M3D-04。

**顺序**：`p_s2_radio` → `p_s3_switchboard` → `p_s4_telegraph` → `p_s5_switch`。

**输出**：四个代表文物及对应 `scene.json` 位置、交互锚点和统计。
**完成标准**：五入口均能进入纯虚拟场景并看到至少一个正式文物。

### M3D-06：扩展文物与动画

**依赖**：最终交付基线已完成。

**动作**：按 P1/P2 优先级补资产和 `interact` 动画。
**限制**：不得为了动画改变文物 ID、根节点和已绑定内容；新增动画必须有无动画降级路径。

### M3D-07：五张触发卡

**输入**：五场景主视觉、二维码 payload、打印模板。

**动作**：设计高特征度触发图，执行 `arcoreimg` 评分和 A6 打印测试。

**输出**：印刷 PNG/PDF、高对比训练图、评分记录、二维码核对表。
**完成标准**：每张卡 10 次至少识别 9 次，二维码内容与全局索引完全一致。

### 建模模型执行提示

交给建模模型时附带以下要求：

> 先完整阅读本计划书第 4、5、10、13 章。只执行指定任务卡，不改资产 ID、坐标系、目录或优先级。开始前列出缺失参考和需要确认的历史细节；可以用灰模处理未知部分，但不得虚构铭文、徽标、序列号和史料。每次交付必须同时包含源文件、运行时 GLB、预览图、资产统计、参考来源、已知问题和更新后的 `scene.json`。

---

## 14. 编码模型任务卡

编码模型按依赖顺序推进。每个任务完成后必须提交可运行代码、测试或真机证据，不把大段未经编译的伪代码当作交付。

### CODE-00：工程与构建基线

**动作**：创建 Android 工程、包名、Compose、Version Catalog、Debug/Release 构建、基础 CI。

**输出**：可安装空壳 APK、版本信息页、README 构建命令。
**完成标准**：命令行和 Android Studio 均能构建；主展示机安装启动成功。

### CODE-01：数据契约与资源仓库

**动作**：实现三个 manifest data class、JSON 解析、Schema 与跨文件校验、路径安全、EntryResolver。

**测试**：有效样例、重复 ID、缺文件、路径穿越、未批准内容、非法数值。
**完成标准**：错误配置返回明确错误码，不发生崩溃或静默忽略。

### CODE-02：Filament Host

**依赖**：CODE-00。

**动作**：封装 Engine、Renderer、Scene、View、Camera、SwapChain、帧循环和 Surface 生命周期。

**输出**：纯色背景 + 测试三角形或内置 GLB 的稳定渲染页。
**完成标准**：前后台和 Surface 重建无黑屏、无重复帧回调、无崩溃。

### CODE-03：GLB 场景加载与释放

**依赖**：CODE-01、CODE-02、M3D-01。

**动作**：实现环境/文物分批加载、进度、实体映射、取消、场景切换和显式释放。
**完成标准**：S1 白盒进入/退出 20 次，内存不持续增长；缺少 P2 文物可降级。

### CODE-04：姿态与触屏相机

**依赖**：CODE-02。

**动作**：实现 `TYPE_GAME_ROTATION_VECTOR`、屏幕方向补偿、基准回正、slerp、去 roll、触屏 yaw/pitch 和无传感器降级。
**完成标准**：四个持机方向测试正确；模式切换画面无明显跳变；后台恢复可重新回正。

### CODE-05：移动、碰撞与热点

**依赖**：CODE-03、CODE-04。

**动作**：实现摇杆死区、视线水平投影、限速、bounds、AABB 滑动、热点淡入淡出。
**完成标准**：不能越过外边界或穿过 S1 主要墙体；低帧恢复时不瞬移。

### CODE-06：拾取、信息卡和高亮

**依赖**：CODE-03。

**动作**：实现 View.pick、坐标转换、Scene token、实体映射、距离限制、选中状态和 Compose 信息卡。
**完成标准**：多个 mesh 映射到同一文物；点击 UI 不穿透；退出页面后旧回调不生效。

### CODE-07：内容与音频

**依赖**：CODE-01、CODE-06。

**动作**：绑定 `content.json`，实现单实例 Media3、焦点处理、进度状态和文本降级。
**完成标准**：切换文物停止旧音频；音频失败仍能阅读文字；切场景彻底停止。

### CODE-08：二维码入口

**依赖**：CODE-01、状态机基础。

**动作**：实现权限、扫描、去重、未知码提示、EntryResult 导航和相机释放。
**完成标准**：扫描 `REDWAVE-S1` 后进入 S1；拒绝权限可手动进入。

### CODE-09：触发图入口

**依赖**：CODE-01、CODE-08 的入口状态机。

**动作**：实现 AR Optional 检查、图片库、识别状态、服务安装/更新提示、Session 释放。
**完成标准**：识图后相机完全退出再加载 VR；不支持 ARCore 的设备正常降级。

### CODE-10：完整 UI 与错误恢复

**依赖**：CODE-03 至 CODE-09。

**动作**：完成 §6.16 页面、诊断页、错误码映射、Loading 取消和返回导航。
**完成标准**：所有错误都有用户可执行的下一步，不出现死页或无限 Loading。

### CODE-11：性能、场景包与发布

**依赖**：S1 MVP。

**动作**：Profile、资源预算冻结、可选场景包或专用全量 APK、签名、混淆验证、安装说明和 Release 回归。
**完成标准**：达到 §6.4、§10、§15 的目标，输出可复现构建和签名 APK。

### 编码模型执行提示

交给编码模型时附带以下要求：

> 先完整阅读本计划书第 0–3、5.4–5.6、6、10、14、15 章。严格保持“入口只输出 scene_id，成功后释放相机，后续完全是纯虚拟 VR”的边界。按任务卡顺序实现，先给出将修改的文件和依赖，再编码并运行构建/测试。不要硬编码文物坐标、文案和资源路径；不要把 ARCore Pose、Anchor 或现实相机帧带入 VR。示例 API 必须以固定依赖版本实际编译结果为准。

---

## 15. 测试计划与用例矩阵

### 15.1 自动化测试

| ID | 层级 | 场景 | 预期 |
|---|---|---|---|
| UT-001 | Unit | 二维码值映射 | 正确返回唯一 `scene_id` |
| UT-002 | Unit | 重复 `qr_payload`/`image_name` | Manifest 校验失败 |
| UT-003 | Unit | `../`、绝对路径或空路径 | 拒绝并返回 `MANIFEST_INVALID` |
| UT-004 | Unit | content ID 找不到 prop | Release 校验失败 |
| UT-005 | Unit | `review_status=draft` | Debug 可警告，Release 拒绝 |
| UT-006 | Unit | 起点落入 collider | 校验失败 |
| UT-007 | Unit | 入口重复帧 | 只产生一个 EntryResult |
| UT-008 | Unit | 传感器回正 | 当前姿态变为视觉零点 |
| UT-009 | Unit | 触屏 pitch 超界 | 被限制在允许范围 |
| UT-010 | Unit | 摇杆死区 | 小输入不产生位移 |
| UT-011 | Unit | 撞墙斜向移动 | 被阻挡轴停止，另一轴继续滑动 |
| UT-012 | Unit | 场景 token 变化 | 旧拾取/加载回调被忽略 |
| UT-013 | Unit | 新音频替换旧音频 | 旧 MediaItem 停止并清理 |
| UT-014 | Unit | 错误码映射 | 每个错误有稳定用户文案与恢复动作 |

### 15.2 集成与生命周期测试

| ID | 场景 | 操作 | 通过条件 |
|---|---|---|---|
| IT-001 | QR 全链路 | 扫 S1 → Loading → VR | 相机释放，5 秒目标内首帧 |
| IT-002 | 图片全链路 | 识别 S1 卡 → VR | 无现实画面残留，无 AR Session 占用 |
| IT-003 | 权限拒绝 | 拒绝 Camera | 返回首页，可手动进入 |
| IT-004 | ARCore 不兼容 | 在不支持设备打开识图 | 给出降级按钮，不崩溃 |
| IT-005 | 后台恢复 | VR 中切后台 30 秒再返回 | Surface、音频和传感器恢复正确 |
| IT-006 | 扫描后台恢复 | 扫描页切后台再返回 | 相机不重复占用，可继续扫描 |
| IT-007 | 快速返回 | 识别成功瞬间按返回 | 不进入幽灵场景，不泄漏相机 |
| IT-008 | 加载取消 | Loading 中取消 | 加载回调停止，资源释放 |
| IT-009 | 场景切换 | S1/S2 往返 10 次 | 不串内容、不持续涨内存 |
| IT-010 | 音频中断 | 来电/音频焦点丢失/拔耳机 | 讲解暂停，不外放突响 |

### 15.3 手工体验与性能测试

| ID | 场景 | 条件 | 目标 |
|---|---|---|---|
| MT-001 | 触发图识别率 | 每张卡、规定光照和距离、10 次 | 每张至少成功 9 次 |
| MT-002 | 二维码识别 | 五张打印卡、不同角度 | 五张均正确进入对应场景 |
| MT-003 | 首次引导 | 未看说明的测试用户 | 30 秒内能进入一个场景 |
| MT-004 | 姿态舒适度 | 连续环视 5 分钟 | 无明显漂移、抖动和频繁眩晕反馈 |
| MT-005 | 文物可达性 | S1 全路线 | 所有 MVP 文物可到达、可点击 |
| MT-006 | 文字可读性 | 主展示机和低配机 | 无裁切，字号和对比度合格 |
| MT-007 | 音频一致性 | 对照脚本逐项播放 | 文件、标题、正文和文物 ID 一致 |
| PT-001 | S1 帧率 | Release、主展示机、完整 S1 | 平均 ≥30 FPS，P95 帧时间记录归档 |
| PT-002 | 加载时间 | 冷进入 S1，重复 5 次 | 中位数和最差值均记录，目标 ≤5 秒 |
| PT-003 | 稳定性 | 连续参观/切换 30 分钟 | 无 crash、ANR、黑屏和音频失控 |
| PT-004 | 内存循环 | 进入/退出 S1 共 20 次 | 回落到稳定区间，无单调增长 |
| PT-005 | 弱网/无网 | 飞行模式启动 | 所有已安装场景可用 |

### 15.4 目标设备记录模板

| 角色 | 品牌型号 | Android | SoC/RAM | ARCore | 陀螺仪 | 屏幕 | 结果 |
|---|---|---:|---|---|---|---|---|
| 主展示机 | 待填写 | 待填写 | 待填写 | 待核对 | 待核对 | 待填写 | 待测试 |
| 备用机 | 待填写 | 待填写 | 待填写 | 待核对 | 待核对 | 待填写 | 待测试 |
| 低配机 | 待填写 | 待填写 | 待填写 | 可不支持 | 可不支持 | 待填写 | 待测试 |

每次 Release 必须记录 APK SHA-256、Git commit、版本号、资源版本、设备信息和测试日期，使演示问题可以复现。

---

## 16. 发布包与交接材料

### 16.1 编码交付

```text
release_delivery/
├── apk/red-wave-ar-vX.Y.Z.apk
├── checksums/SHA256SUMS.txt
├── build/BUILD.md
├── install/INSTALL.md
├── compatibility/device_matrix.md
├── diagnostics/performance_report.md
├── tests/test_report.md
├── licenses/THIRD_PARTY_NOTICES.md
├── assets/runtime_asset_manifest.csv
└── source_commit.txt
```

### 16.2 内容与建模交付

- 五场景运行时目录和源资产目录。
- `asset_report.csv`、参考来源、授权和内容审核记录。
- 五张触发卡印刷文件、训练图和识别率测试记录。
- 正式音频、脚本、文字稿和内容版本号。
- 一套可用于宣传的场景截图和文物透明底预览图。

### 16.3 Release 检查

- [ ] `versionCode`、`versionName`、Git commit 和内容版本已记录。
- [ ] Release 使用正式签名；密钥不进入仓库或交付公开目录。
- [ ] 目标 ABI 与设备矩阵匹配；没有误删 Filament/ARCore 必需类或 native library。
- [ ] 混淆、资源压缩和签名后的 APK 已重新安装测试，不只测试 Debug。
- [ ] Camera 权限用途说明、隐私说明和第三方开源许可齐全。
- [ ] 所有占位文案、测试音频、调试按钮和内部地址已清理。
- [ ] 飞行模式、拒绝权限、无 ARCore 和传感器缺失的降级路径已复测。
- [ ] APK、触发卡和演示视频使用同一版场景映射。
- [ ] 主展示机、备用机均预装并完成现场彩排。
- [ ] 最终成果表只填写这一个 Release 实际通过的功能和场景数量。

---

## 17. 决策记录与变更规则

任何影响建模或编码契约的决定都追加到 `docs/decisions/ADR-XXXX.md`，至少包含：背景、选项、决定、影响、回滚方案和负责人。以下变化必须写 ADR：

- 从摇杆自由移动改为热点移动，或反向切换。
- 改变坐标系、单位、资产 ID、JSON 字段或 Schema 版本。
- 更换 Filament、ARCore、二维码或音频方案。
- 改变基础 APK 与场景包的资源分发策略。
- 把 S2–S5 从模板场景升级为专属环境，或削减场景。
- 改变最低 Android、目标 ABI、屏幕方向或设备范围。

变更执行顺序：

1. 提交 ADR 草案并标出受影响任务、文件和验收项。
2. 技术负责人确认后更新本计划书版本和 Schema。
3. 建模、编码、内容三方更新各自交付物。
4. 重新执行受影响测试，不沿用旧验收结论。
5. 最终成果附件只采用最新 Release 与最新 ADR 的结论。

*本计划书为活文档。重大范围、Schema、依赖或验收标准变化必须更新版本号，并在提交记录中说明。*
