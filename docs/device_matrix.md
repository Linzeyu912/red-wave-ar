# 目标机型记录（计划书 §6.4、§15.4）

> M0 要求：记录主展示机、备用机、低配机的品牌型号、Android 版本、SoC/RAM、ARCore、陀螺仪、屏幕。
> 每次 Release 必须记录 APK SHA-256、Git commit、版本号、资源版本、设备信息和测试日期。

## 当前已落实机型

| 角色 | 品牌型号 | 型号代码 | Android | SoC/RAM | ARCore | 陀螺仪 | 屏幕 | 状态 |
|---|---|---|---:|---|:---:|:---:|---|---|
| 主展示机 | nubia Z70 Ultra | NX736 | 15 | 骁龙 8 Elite / 12-16GB | ❌ 不支持 | ✅ 支持（待真机核对） | 待核对 | 待真机验收 |
| 备用机 | 待补充 | — | — | — | — | — | — | 待落实 |
| 低配机 | 待补充 | — | — | — | 可不支持 | 可不支持 | — | 待落实 |

## 关键发现：主展示机 ARCore 状态

**nubia Z70 Ultra 不支持 ARCore**（截至 2026-07）：

- 未出现在 Google ARCore 认证设备列表（[developers.google.com/ar/devices](https://developers.google.com/ar/devices)）。
- 第三方实测（Android Police 评测）确认 Google Play Services for AR 不工作。
- nubia 旗舰（Z60/Z70 Ultra）历史上均未通过 ARCore 认证。

### 对项目的影响（符合计划书边界设计）

1. **CODE-09 触发图入口已归档**（ADR-0001）：主展示机不支持 ARCore，触发图入口（F2）暂不实现，仅保留二维码（F1）+ 手动列表（F3）两个入口。后续有 ARCore 认证机型时可重启。
2. 计划书 §1.2、§3.6 的 **"AR Optional"** 设计验证了边界正确性：二维码和手动列表始终可用，无 ARCore 设备不阻塞核心体验。
3. 计划书 §10.1 验收项"无 ARCore 的兼容设备仍能使用二维码/手动入口和触屏模式"——主展示机本身就是这个验收点的实测对象。

### 验证边界（已与项目负责人确认）

- CODE-03 GLB 加载、CODE-04 陀螺仪环视、CODE-05 摇杆移动、CODE-06 拾取、CODE-07 音频：主展示机可真机验收。
- CODE-04 陀螺仪真实姿态：主展示机可验（Z70 Ultra 有陀螺仪）；开发期模拟器只验"不崩溃+触屏降级"。
- 开发阶段无真机时用模拟器（AVD `redwave_test`，x86_64 + SwiftShader）验证基础运行；性能指标以真机 Release 为准。

## 备用机/低配机选型（待项目负责人补充）

- 备用机：任意 Android 8+ 设备即可（不再要求 ARCore，因 F2 已归档）。
- 低配机：建议中端骁龙 6/7 系，用于性能下限验证。

## 入口方案（ADR-0001 已确认）

- F1 二维码：ZXing Android Embedded 4.3.0（计划书原选型）→ CODE-08
- F2 触发图：**归档，可重启**
- F3 手动列表：CODE-10
