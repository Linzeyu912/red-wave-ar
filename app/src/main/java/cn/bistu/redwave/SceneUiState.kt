package cn.bistu.redwave

/**
 * 核心状态机（计划书 §3.4、§6.7）。
 *
 * 严格保持“入口只输出 scene_id，成功后释放相机，后续完全是纯虚拟 VR”的边界：
 * - [Scanning] 阶段不携带任何相机帧、ARCore Pose 或 Anchor。
 * - [Loading] 及之后阶段均为纯虚拟体验，不接触现实画面。
 */
sealed interface SceneUiState {

    /**
     * 首页：入口选择与场景列表。
     * 相机与 ARCore Session 尚未创建。
     */
    data object Home : SceneUiState

    /**
     * 扫描中（二维码 / 触发图）。
     * 计划书 §6.8：成功后只携带 scene_id 和入口类型，不携带任何相机数据。
     */
    data class Scanning(val type: EntrySource) : SceneUiState

    /**
     * 场景加载中。相机与 ARCore Session 已释放，Filament 正在加载虚拟场景。
     */
    data class Loading(val sceneId: String, val progress: Float) : SceneUiState

    /**
     * 虚拟展馆探索中：纯 Filament 渲染 + 手机姿态环视 + 摇杆移动 + 文物交互 + 音频。
     */
    data class Exploring(
        val sceneId: String,
        val sensorMode: SensorMode
    ) : SceneUiState

    /**
     * 错误状态（计划书 §6.18）。
     */
    data class Error(
        val code: AppErrorCode,
        val recoverable: Boolean
    ) : SceneUiState
}
