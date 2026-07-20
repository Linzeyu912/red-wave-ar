package cn.bistu.redwave

/**
 * 入口类型（计划书 §1.2、§6.7）。
 * 二维码、触发图、手动列表都只负责返回 scene_id。
 */
enum class EntrySource { QR, IMAGE, MANUAL }

/**
 * 传感器环视模式（计划书 §6.12、§6.16）。
 * 陀螺仪模式使用 TYPE_GAME_ROTATION_VECTOR；触屏模式用拖动 yaw/pitch。
 */
enum class SensorMode { GYROSCOPE, TOUCH }

/**
 * 入口结果（计划书 §6.7、§6.8）。
 * 入口成功事件只携带 scene_id 和入口类型，不携带 Bitmap、Camera Frame、Anchor 或 Pose。
 */
data class EntryResult(
    val sceneId: String,
    val source: EntrySource
)
