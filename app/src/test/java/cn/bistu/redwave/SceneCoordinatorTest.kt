package cn.bistu.redwave

import com.google.common.truth.Truth.assertThat
import org.junit.Test

class SceneCoordinatorTest {

    @Test
    fun entryResult_drivesLoadingAndExploringWithoutCameraState() {
        val coordinator = SceneCoordinator()
        coordinator.startScanning(EntrySource.QR)
        assertThat(coordinator.state.value)
            .isEqualTo(SceneUiState.Scanning(EntrySource.QR))

        coordinator.beginLoading(EntryResult("S1", EntrySource.QR))
        coordinator.updateLoading("S1", 0.55f)
        assertThat(coordinator.state.value)
            .isEqualTo(SceneUiState.Loading("S1", 0.55f))

        coordinator.markExploring("S1", SensorMode.GYROSCOPE)
        assertThat(coordinator.state.value)
            .isEqualTo(SceneUiState.Exploring("S1", SensorMode.GYROSCOPE))
    }

    @Test
    fun staleSceneCallbacks_doNotChangeCurrentState() {
        val coordinator = SceneCoordinator()
        coordinator.beginLoading(EntryResult("S1", EntrySource.MANUAL))

        coordinator.updateLoading("S2", 0.8f)
        coordinator.markExploring("S2", SensorMode.TOUCH)

        assertThat(coordinator.state.value)
            .isEqualTo(SceneUiState.Loading("S1", 0f))
    }

    @Test
    fun loadError_canRetryLastEntryOrReturnHome() {
        val coordinator = SceneCoordinator()
        coordinator.beginLoading(EntryResult("S1", EntrySource.MANUAL))
        coordinator.showError(AppErrorCode.GLB_LOAD_FAILED)

        assertThat(coordinator.lastErrorCode).isEqualTo(AppErrorCode.GLB_LOAD_FAILED)
        assertThat(coordinator.retryActiveScene()).isTrue()
        assertThat(coordinator.state.value).isEqualTo(SceneUiState.Loading("S1", 0f))

        coordinator.goHome()
        assertThat(coordinator.state.value).isEqualTo(SceneUiState.Home)
        assertThat(coordinator.retryActiveScene()).isFalse()
    }
}
