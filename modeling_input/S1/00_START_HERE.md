# S1 平西情报联络站：平台输入入口

> 状态：`VISUAL_INPUT_RECEIVED / DETAIL_PASS_V2 / MODEL_V3_BUILT / NARRATION_REFERENCE_DRAFTED / RIGHTS_PENDING`

## 当前目标

平西情报联络站包含两个独立触发与建模单元：

| 单元 | 对象 | 手绘触发图 | 真实照片 | 当前模型 |
|---|---|---|---|---|
| S1A | 入口门楼 | `trigger_hand_drawn.jpg` | `微信图片_20260712203953_1152_5130.jpg` | `S1A_pingxi_gate_v003.glb` |
| S1B | 女报务员雕塑及发报设备 | `S1B_radio_operator_trigger_hand_drawn.jpg` | `微信图片_20260716203647_1419_5130.jpg` | `S1B_radio_operator_statue_v003.glb` |

默认体验顺序是：识别红白黑手绘触发图 → V002 专属地面贴图与静态 GLB 同时出现 → 旁白。原图仅作内部对应核对，不配置为 AR 展示平面；不使用通用厚展台。

## 当前建模边界

- 现有照片是本轮完整视觉输入，不再等待侧面、背面、屋顶或更多细节照片。
- 可见面按照片还原；门楼和雕塑的不可见面按低细节保守闭合并标记 `INFERRED_LOW_DETAIL`。
- S1B 的绘制参考原图包含讲解员；它仅作内部依据，仍须完成隐私与来源审核，不能上传为展示平面。
- 两张真实照片当前只作内部建模和触发图对应依据。
- `平西情报联络站文字素材.docx` 已收到；其整理稿、公开来源和待核验项见 [`narration_reference.md`](narration_reference.md)。

旧自研任务中的地下电台小室、发报设备和门楼 GLB 不构成本任务的外形依据，不得直接复制、改名或上传到 Kivicube。

## 素材放置

- 原始图片和文字：`local_reference/`，仅限本地受控使用。
- 手绘触发图：S1A 原图为 `local_reference/**/trigger_hand_drawn.jpg`，S1B 原图为 `local_reference/**/S1B_radio_operator_trigger_hand_drawn.jpg`；Kivicube 包内仅复制原文件，不重绘、不裁切。两者均须经真机识别审核后再公开发布。
- 内部参考原图：必须登记与触发图的对应关系、来源和隐私状态；不得配置为 Kivicube AR 展示对象。
- 文件级对应关系：[`../REFERENCE_INVENTORY.md`](../REFERENCE_INVENTORY.md)。
- 可追踪形象约束：[`visual_constraints.md`](visual_constraints.md)，已分别记录 S1A、S1B 的逐图依据、主体特征、推断边界和提示词片段。
- 旁白参考与事实来源：从已收到的 Word 整理到 `narration_reference.md`，原文件保持受控。
- 平台交付与验收：[`../../lkivivube_delivery/scenes/S1_pingxi_intelligence_station/asset_card.md`](../../lkivivube_delivery/scenes/S1_pingxi_intelligence_station/asset_card.md)。
- 平台统一规范：[`../../docs/KIVICUBE_ASSET_CONSTRAINTS.md`](../../docs/KIVICUBE_ASSET_CONSTRAINTS.md)。

## 历史资料

旧地下电台白盒、紧凑小室和 GATE-01 建模口令已归档到 [`../../archive/self_built_app/modeling_input/S1/00_START_HERE.md`](../../archive/self_built_app/modeling_input/S1/00_START_HERE.md)。只有明确处理自研程序线历史资产时才可读取该入口。
