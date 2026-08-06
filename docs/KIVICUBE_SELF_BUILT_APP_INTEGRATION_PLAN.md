# Kivicube 接入自研 Android App 计划

## 目标与边界

目标是在保留现有 Kotlin / Compose / Filament 导览与虚拟展馆的前提下，新增一个 Kivicube WebAR 页面，由 Kivicube 处理图像 AR 识别、相机与 AR 模型呈现。

最终用户流程：

```text
原生导览首页 / 二维码 / 地点列表
  → Kivicube 场景链接或 scene-id
  → App 内 WebView 的 Kivicube 图像 AR 场景
  → 返回原生导览
```

- 不使用“导出小程序工程”作为 Android App 的接入方式。
- 不在 App 内复刻 Kivicube 的图像识别能力，也不把 Kivicube 的识别结果直接传给 Filament。
- 现有 `VrSceneScreen`、Filament 模型加载、本地二维码扫描和离线导览保留，作为原生展馆/备用体验。
- Kivicube 账号密码、Cookie、密钥或后台令牌不得写入仓库或 App。

## 阶段 0：平西双单元验证（当前由项目方执行）

1. 在项目统一归属的 Kivicube 账号中，分别创建两个“图像 AR”测试场景：S1A 入口门楼、S1B 女报务员。
2. 按 [`../lkivivube_delivery/scenes/S1_pingxi_intelligence_station/KIVICUBE_TEST_HANDOFF.md`](../lkivivube_delivery/scenes/S1_pingxi_intelligence_station/KIVICUBE_TEST_HANDOFF.md) 上传触发图、参考图、地面贴图和 GLB。
3. 对每张手绘触发图完成平台评分和印刷真机识别测试；先验证“识别 → 模型出现”，再添加照片淡入、动画和旁白。
4. 保存场景，记录每个单元的 WebAR 分享链接或 `scene-id`；只向开发交接链接/ID，不提供账号凭据。
5. 真实参考照片当前仅供内部适配测试，取得公开展示许可前不得对外发布。

**阶段 0 产出**：两个可访问的测试链接（S1A、S1B）、触发图评分/真机测试结果、出现的问题与设备型号。

## 阶段 1：Android 接入骨架（由开发执行）

1. 增加独立的 Kivicube 场景配置，维护 `场景编号 → WebAR 链接 / scene-id → 状态`；先登记 S1A、S1B，后续扩至九个单元。
2. 在 `SceneUiState` 与 `SceneCoordinator` 中增加独立的 `KivicubeAr` 状态；不复用假设本地 GLB 的 `Loading` / `Exploring` 状态。
3. 新增 Compose 承载的 Android `WebView` 页面：加载 HTTPS 场景链接、显示加载/网络/返回状态，并处理生命周期。
4. 保持标准 WebView User-Agent；若添加项目标记，仅附加在默认 UA 末尾。
5. 增加 `INTERNET` 权限；沿用已有 `CAMERA` 权限。二维码扫描成功后必须先释放 ZXing 相机，再打开 WebView，避免相机占用冲突。
6. WebView 打开失败、网络不可用或 Kivicube 场景不可访问时，显示原生错误页，并提供“返回导览”和“重试”。

**阶段 1 验收**：S1A、S1B 可从原生首页进入；相机授权正常；Kivicube 中完成识别和模型展示；返回后 App 不崩溃且可再次打开 AR 页面。

## 阶段 2：九单元批量接入与验收

1. 为 S1A、S1B、S2A、S3A、S3B、S4A、S5A、S6A、S7A 分别登记链接/ID、版本、公开状态和最后真机测试时间。
2. 逐单元验证：触发图识别、参考图显示、地面贴图、模型位置、`photo_emerge` 动画、旁白、返回流程。
3. 覆盖至少一台 Android 8+ 设备和目标展示机；记录 WebView 版本、网络状况、加载耗时和失败回退结果。
4. 图片/模型更新后，先更新 Kivicube 场景与测试记录，再更新 App 中的场景链接或版本标记。

## 阶段 3：发布决策

在九个单元通过真机验收后，再确认：

- Kivicube 账户归属、场景数量、体验次数、水印与商用/教育展示权益；
- 真实参考照片的公开展示许可与隐私处理；
- 网络不可用时的原生降级内容；
- Android App 的签名、发布渠道和隐私说明。

Kivicube 提供的是 WebAR 服务接入，不应被视为离线、永久独立的图像识别 SDK。若将来需要完全脱离 Kivicube，再另行立项用 ARCore Augmented Images 等原生方案重建识别、追踪与相机叠加链路。

## 责任分工

| 事项 | 项目方 | 开发 |
|---|---|---|
| Kivicube 账号、场景创建、素材上传 | 负责 | 配合核对素材包 |
| 触发图评分与印刷真机测试 | 负责 | 记录问题、调整配置建议 |
| WebAR 链接 / `scene-id` 交接 | 负责提供 | 安全登记到 App 配置 |
| 原生 App WebView、路由、错误回退 | - | 负责 |
| Kivicube 场景中的识别、模型与交互 | 负责配置 | 配合验收 |
| 账号权益、版权/隐私与正式发布审批 | 负责 | 提供技术清单 |
