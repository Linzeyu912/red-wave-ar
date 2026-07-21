package cn.bistu.redwave

import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow

/**
 * CODE-10 应用级页面状态协调器。
 *
 * 这里只保存入口结果和 UI 状态，不持有 Camera、Filament、ExoPlayer 或 SensorManager。
 * 因此从 [Scanning] 进入 [SceneUiState.Loading] 时，跨边界传递的仍然只有
 * [EntryResult.sceneId] 与 [EntryResult.source]。
 */
class SceneCoordinator {

    private val _state = MutableStateFlow<SceneUiState>(SceneUiState.Home)
    val state: StateFlow<SceneUiState> = _state.asStateFlow()

    private var activeEntry: EntryResult? = null

    var lastErrorCode: AppErrorCode? = null
        private set

    fun startScanning(source: EntrySource) {
        require(source == EntrySource.QR || source == EntrySource.IMAGE)
        _state.value = SceneUiState.Scanning(source)
    }

    fun beginLoading(entry: EntryResult) {
        activeEntry = entry
        lastErrorCode = null
        _state.value = SceneUiState.Loading(entry.sceneId, progress = 0f)
    }

    fun updateLoading(sceneId: String, progress: Float) {
        val current = _state.value as? SceneUiState.Loading ?: return
        if (current.sceneId != sceneId) return
        val normalized = progress.coerceIn(0f, 1f)
        if (normalized >= current.progress) {
            _state.value = current.copy(progress = normalized)
        }
    }

    fun markExploring(sceneId: String, sensorMode: SensorMode) {
        val current = _state.value as? SceneUiState.Loading ?: return
        if (current.sceneId != sceneId) return
        _state.value = SceneUiState.Exploring(sceneId, sensorMode)
    }

    fun updateSensorMode(sceneId: String, sensorMode: SensorMode) {
        val current = _state.value as? SceneUiState.Exploring ?: return
        if (current.sceneId != sceneId) return
        _state.value = current.copy(sensorMode = sensorMode)
    }

    fun showError(code: AppErrorCode, recoverable: Boolean = true) {
        lastErrorCode = code
        _state.value = SceneUiState.Error(code, recoverable)
    }

    fun retryActiveScene(): Boolean {
        val entry = activeEntry ?: return false
        lastErrorCode = null
        _state.value = SceneUiState.Loading(entry.sceneId, progress = 0f)
        return true
    }

    fun openDiagnostics() {
        _state.value = SceneUiState.Diagnostics
    }

    fun goHome() {
        activeEntry = null
        _state.value = SceneUiState.Home
    }
}
