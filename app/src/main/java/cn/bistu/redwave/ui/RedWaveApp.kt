package cn.bistu.redwave.ui

import androidx.activity.compose.BackHandler
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.LocalContext
import cn.bistu.redwave.AppErrorCode
import cn.bistu.redwave.AppInfo
import cn.bistu.redwave.EntryResult
import cn.bistu.redwave.EntrySource
import cn.bistu.redwave.SceneCoordinator
import cn.bistu.redwave.SceneUiState
import cn.bistu.redwave.data.AndroidAssetResourceRoot
import cn.bistu.redwave.data.GlobalManifest
import cn.bistu.redwave.data.ManifestLoadException
import cn.bistu.redwave.data.ManifestRepository
import cn.bistu.redwave.ui.diagnostics.DiagnosticsScreen
import cn.bistu.redwave.ui.error.ErrorScreen
import cn.bistu.redwave.ui.home.HomeScreen
import cn.bistu.redwave.ui.scan.QrScanScreen
import cn.bistu.redwave.ui.vr.VrSceneScreen
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext

/**
 * CODE-10 应用根页面。所有页面只响应 [SceneCoordinator]，入口结果仅携带 scene_id/source。
 */
@Composable
fun RedWaveApp() {
    val context = LocalContext.current
    val coordinator = remember { SceneCoordinator() }
    val uiState by coordinator.state.collectAsState()
    val repository = remember(context.applicationContext) {
        ManifestRepository(
            AndroidAssetResourceRoot.fromContext(context.applicationContext),
            strict = AppInfo.strictReleaseValidation
        )
    }
    var globalManifest by remember { mutableStateOf<GlobalManifest?>(null) }

    LaunchedEffect(repository) {
        val result = withContext(Dispatchers.IO) { repository.loadGlobalManifest() }
        result.fold(
            onSuccess = { globalManifest = it },
            onFailure = { coordinator.showError(it.toAppErrorCode(), recoverable = false) }
        )
    }

    BackHandler(enabled = uiState != SceneUiState.Home) {
        coordinator.goHome()
    }

    when (val state = uiState) {
        SceneUiState.Home -> HomeScreen(
            scenes = globalManifest?.scenes.orEmpty(),
            isIndexReady = globalManifest != null,
            onScanQr = { coordinator.startScanning(EntrySource.QR) },
            onManualSelect = { sceneId ->
                repository.buildEntryResolver()
                    .mapCatching { it.resolveManual(sceneId).getOrThrow() }
                    .fold(
                        onSuccess = coordinator::beginLoading,
                        onFailure = { coordinator.showError(it.toAppErrorCode()) }
                    )
            },
            onDiagnostics = coordinator::openDiagnostics,
            modifier = Modifier.fillMaxSize()
        )

        SceneUiState.Diagnostics -> DiagnosticsScreen(
            sceneCount = globalManifest?.scenes?.size ?: 0,
            lastErrorCode = coordinator.lastErrorCode,
            onBack = coordinator::goHome,
            modifier = Modifier.fillMaxSize()
        )

        is SceneUiState.Scanning -> {
            if (state.type == EntrySource.QR) {
                QrScanScreen(
                    onResolved = coordinator::beginLoading,
                    onError = { coordinator.showError(it) },
                    onManualSelect = coordinator::goHome,
                    onBack = coordinator::goHome,
                    modifier = Modifier.fillMaxSize()
                )
            } else {
                ErrorScreen(
                    code = AppErrorCode.ARCORE_UNSUPPORTED,
                    recoverable = true,
                    onRecovery = coordinator::goHome,
                    onDiagnostics = coordinator::openDiagnostics,
                    onHome = coordinator::goHome
                )
            }
        }

        is SceneUiState.Loading,
        is SceneUiState.Exploring -> {
            val sceneId = when (state) {
                is SceneUiState.Loading -> state.sceneId
                is SceneUiState.Exploring -> state.sceneId
                else -> error("unreachable")
            }
            VrSceneScreen(
                sceneId = sceneId,
                uiState = state,
                onLoadingProgress = { coordinator.updateLoading(sceneId, it) },
                onReady = { coordinator.markExploring(sceneId, it) },
                onSensorModeChanged = { coordinator.updateSensorMode(sceneId, it) },
                onFatalError = { coordinator.showError(it) },
                onExit = coordinator::goHome,
                modifier = Modifier.fillMaxSize()
            )
        }

        is SceneUiState.Error -> ErrorScreen(
            code = state.code,
            recoverable = state.recoverable,
            onRecovery = {
                when (state.code) {
                    AppErrorCode.GLB_LOAD_FAILED,
                    AppErrorCode.SCENE_PACKAGE_MISSING,
                    AppErrorCode.OUT_OF_MEMORY_RISK -> {
                        if (!coordinator.retryActiveScene()) coordinator.goHome()
                    }
                    AppErrorCode.MANIFEST_INVALID -> coordinator.openDiagnostics()
                    else -> coordinator.goHome()
                }
            },
            onDiagnostics = coordinator::openDiagnostics,
            onHome = coordinator::goHome,
            modifier = Modifier.fillMaxSize()
        )
    }
}

private fun Throwable.toAppErrorCode(): AppErrorCode = when (this) {
    is ManifestLoadException -> code
    is cn.bistu.redwave.data.EntryResolver.EntryResolutionException -> code
    else -> AppErrorCode.MANIFEST_INVALID
}
