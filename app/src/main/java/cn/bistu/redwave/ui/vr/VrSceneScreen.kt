package cn.bistu.redwave.ui.vr

import android.app.Activity
import android.content.Context
import android.view.GestureDetector
import android.view.MotionEvent
import android.view.Surface
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.material3.Button
import androidx.compose.material3.LinearProgressIndicator
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Surface as ComposeSurface
import androidx.compose.material3.Text
import androidx.compose.material3.TextButton
import androidx.compose.runtime.Composable
import androidx.compose.runtime.DisposableEffect
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.unit.dp
import androidx.compose.ui.viewinterop.AndroidView
import androidx.lifecycle.Lifecycle
import androidx.lifecycle.LifecycleEventObserver
import androidx.lifecycle.compose.LocalLifecycleOwner
import cn.bistu.redwave.AppErrorCode
import cn.bistu.redwave.AppErrorMessages
import cn.bistu.redwave.SceneUiState
import cn.bistu.redwave.SensorMode
import cn.bistu.redwave.audio.AudioSource
import cn.bistu.redwave.audio.NarrationController
import cn.bistu.redwave.audio.StopReason
import cn.bistu.redwave.data.AndroidAssetResourceRoot
import cn.bistu.redwave.data.ContentManifest
import cn.bistu.redwave.data.ManifestLoadException
import cn.bistu.redwave.data.ManifestRepository
import cn.bistu.redwave.data.SceneManifest
import cn.bistu.redwave.interaction.MovementController
import cn.bistu.redwave.interaction.PickingController
import cn.bistu.redwave.interaction.PickingMath
import cn.bistu.redwave.render.FilamentSceneConfig
import cn.bistu.redwave.render.FilamentSurfaceView
import cn.bistu.redwave.render.SceneRenderer
import cn.bistu.redwave.render.asset.GltfAssetStore
import cn.bistu.redwave.render.asset.SceneAssetLoader
import cn.bistu.redwave.sensor.OrientationController
import cn.bistu.redwave.sensor.OrientationMath
import kotlinx.coroutines.delay

/**
 * CODE-10 正式 VR 场景页。入口相机已在进入本页前释放，本页只加载纯虚拟资产。
 */
@Composable
fun VrSceneScreen(
    sceneId: String,
    uiState: SceneUiState,
    onLoadingProgress: (Float) -> Unit,
    onReady: (SensorMode) -> Unit,
    onSensorModeChanged: (SensorMode) -> Unit,
    onFatalError: (AppErrorCode) -> Unit,
    onExit: () -> Unit,
    modifier: Modifier = Modifier
) {
    val context = LocalContext.current
    val lifecycleOwner = LocalLifecycleOwner.current
    val surfaceViewRef = remember(sceneId) { mutableStateOf<FilamentSurfaceView?>(null) }
    val cleanupRef = remember(sceneId) { mutableStateOf<SceneCleanup?>(null) }
    val narration = remember(sceneId) { NarrationController(context.applicationContext) }
    val narrationState by narration.state.collectAsState()
    var status by remember(sceneId) { mutableStateOf("正在读取场景配置…") }
    var selectedPropId by remember(sceneId) { mutableStateOf<String?>(null) }
    val exploring = uiState as? SceneUiState.Exploring

    LaunchedEffect(selectedPropId) {
        val cleanup = cleanupRef.value
        val propId = selectedPropId
        if (propId == null || cleanup == null) {
            narration.stop(StopReason.CLOSED)
        } else {
            val item = cleanup.contentManifest.items.firstOrNull { it.id == propId }
            if (item != null) {
                val path = "${cleanup.assetBaseDir}/${item.audio}".replace("//", "/")
                narration.play(propId, AudioSource.Asset(path))
            }
        }
    }

    LaunchedEffect(narration) {
        while (true) {
            narration.pollPosition()
            delay(500)
        }
    }

    LaunchedEffect(narrationState.hasError) {
        if (narrationState.hasError) {
            status = AppErrorMessages.recoveryFor(AppErrorCode.AUDIO_LOAD_FAILED).shortMessage +
                "，可继续阅读文字"
        }
    }

    Box(modifier = modifier.fillMaxSize().background(Color.Black)) {
        AndroidView(
            factory = { ctx ->
                FilamentSurfaceView(ctx).also { sv ->
                    surfaceViewRef.value = sv
                    sv.onResumeRendering(createSceneObjects = true)
                    attachTouchHandlers(
                        sv = sv,
                        context = ctx,
                        infoSheetOpen = { selectedPropId != null },
                        onPropSelected = { propId -> selectedPropId = propId },
                        onHint = { status = it }
                    )
                    sv.postToRenderThread {
                        runCatching {
                            loadScene(
                                sv = sv,
                                context = ctx,
                                sceneId = sceneId,
                                onProgress = { progress, message ->
                                    sv.post {
                                        status = message
                                        onLoadingProgress(progress)
                                    }
                                },
                                onReady = { cleanup, failedProps ->
                                    sv.post {
                                        cleanupRef.value = cleanup
                                        status = if (!cleanup.orientation.gyroscopeAvailable()) {
                                            AppErrorMessages.recoveryFor(
                                                AppErrorCode.SENSOR_UNAVAILABLE
                                            ).shortMessage
                                        } else if (failedProps.isEmpty()) {
                                            "场景已就绪"
                                        } else {
                                            AppErrorMessages.recoveryFor(
                                                AppErrorCode.PARTIAL_PROP_FAILED
                                            ).shortMessage
                                        }
                                        onReady(cleanup.orientation.mode)
                                    }
                                },
                                onFatalError = { code -> sv.post { onFatalError(code) } }
                            )
                        }.onFailure {
                            sv.post { onFatalError(it.toVrErrorCode()) }
                        }
                    }
                }
            },
            modifier = Modifier.fillMaxSize()
        )

        Column(
            modifier = Modifier.align(Alignment.TopStart).padding(12.dp),
            verticalArrangement = Arrangement.spacedBy(6.dp)
        ) {
            Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                Button(onClick = onExit) { Text("返回首页") }
                Button(
                    onClick = {
                        surfaceViewRef.value?.postToRenderThread {
                            (surfaceViewRef.value?.tag as? SceneCleanup)?.orientation?.recalibrate()
                            surfaceViewRef.value?.post { status = "视角已回正" }
                        }
                    },
                    enabled = exploring != null
                ) { Text("视角回正") }
                Button(
                    onClick = {
                        val target = if (exploring?.sensorMode == SensorMode.GYROSCOPE) {
                            SensorMode.TOUCH
                        } else {
                            SensorMode.GYROSCOPE
                        }
                        requestSensorMode(
                            sv = surfaceViewRef.value,
                            target = target,
                            onChanged = { actual, gyroUnavailable ->
                                if (gyroUnavailable) {
                                    status = AppErrorMessages.recoveryFor(
                                        AppErrorCode.SENSOR_UNAVAILABLE
                                    ).shortMessage
                                }
                                onSensorModeChanged(actual)
                            }
                        )
                    },
                    enabled = exploring != null
                ) {
                    Text(if (exploring?.sensorMode == SensorMode.GYROSCOPE) "切到触屏" else "切到陀螺仪")
                }
            }
            Text(
                text = "$sceneId · $status",
                color = Color.White,
                style = MaterialTheme.typography.labelSmall
            )
        }

        val cleanup = cleanupRef.value
        val selectedContent = if (selectedPropId != null && cleanup != null) {
            cleanup.contentManifest.items.firstOrNull { it.id == selectedPropId }
        } else null
        if (selectedContent != null) {
            InfoSheet(
                content = selectedContent,
                audioState = AudioControlState(
                    available = !narrationState.hasError && narrationState.itemId == selectedContent.id,
                    isPlaying = narrationState.isPlaying,
                    positionLabel = formatTime(narrationState.positionMs),
                    durationLabel = if (narrationState.durationMs > 0) {
                        formatTime(narrationState.durationMs)
                    } else {
                        "${selectedContent.audioDurationSec / 60}:" +
                            (selectedContent.audioDurationSec % 60).toString().padStart(2, '0')
                    }
                ),
                onClose = {
                    selectedPropId = null
                    cleanupRef.value?.picking?.deselect()
                },
                onToggleAudio = {
                    if (narrationState.isPlaying) narration.pause() else narration.resume()
                },
                modifier = Modifier.align(Alignment.BottomCenter)
            )
        }

        val loading = uiState as? SceneUiState.Loading
        if (loading != null) {
            ComposeSurface(
                modifier = Modifier.fillMaxSize(),
                color = Color.Black.copy(alpha = 0.76f)
            ) {
                Column(
                    modifier = Modifier.fillMaxSize().padding(32.dp),
                    horizontalAlignment = Alignment.CenterHorizontally,
                    verticalArrangement = Arrangement.Center
                ) {
                    Text("正在加载 ${loading.sceneId}", color = Color.White)
                    LinearProgressIndicator(
                        progress = { loading.progress },
                        modifier = Modifier.fillMaxWidth(0.6f).padding(top = 16.dp)
                    )
                    Text(
                        "${(loading.progress * 100).toInt()}% · $status",
                        color = Color.White.copy(alpha = 0.8f),
                        modifier = Modifier.padding(top = 8.dp)
                    )
                    TextButton(onClick = onExit, modifier = Modifier.padding(top = 12.dp)) {
                        Text("取消加载", color = Color.White)
                    }
                }
            }
        }
    }

    LaunchedEffect(surfaceViewRef.value) {
        val sv = surfaceViewRef.value ?: return@LaunchedEffect
        sv.post {
            val width = sv.width.coerceAtLeast(1)
            val height = sv.height.coerceAtLeast(1)
            sv.postToRenderThread {
                FilamentSceneConfig.configureBaseline(sv.host, width, height)
            }
        }
    }

    DisposableEffect(lifecycleOwner, sceneId) {
        val observer = LifecycleEventObserver { _, event ->
            val sv = surfaceViewRef.value ?: return@LifecycleEventObserver
            when (event) {
                Lifecycle.Event.ON_RESUME -> {
                    sv.onResumeRendering(createSceneObjects = false)
                    sv.postToRenderThread { (sv.tag as? SceneCleanup)?.orientation?.resume() }
                }
                Lifecycle.Event.ON_PAUSE -> {
                    sv.onPauseRendering()
                    sv.postToRenderThread { (sv.tag as? SceneCleanup)?.orientation?.pause() }
                }
                else -> Unit
            }
        }
        lifecycleOwner.lifecycle.addObserver(observer)
        onDispose { lifecycleOwner.lifecycle.removeObserver(observer) }
    }

    DisposableEffect(sceneId) {
        onDispose {
            narration.stop(StopReason.SCENE_CHANGED)
            narration.release()
            val sv = surfaceViewRef.value
            val cleanup = cleanupRef.value ?: (sv?.tag as? SceneCleanup)
            sv?.setOnTouchListener(null)
            if (sv != null && cleanup != null) {
                sv.postToRenderThread {
                    sv.sceneRenderer.hooks = null
                    cleanup.picking.exitScene()
                    cleanup.orientation.pause()
                    cleanup.loader.reset()
                    cleanup.assetStore.destroyAll(sv.host.scene)
                    cleanup.assetStore.destroy()
                    sv.tag = null
                }
            }
            sv?.shutdown()
            surfaceViewRef.value = null
            cleanupRef.value = null
        }
    }
}

private fun requestSensorMode(
    sv: FilamentSurfaceView?,
    target: SensorMode,
    onChanged: (actual: SensorMode, gyroUnavailable: Boolean) -> Unit
) {
    sv ?: return
    sv.postToRenderThread {
        val orientation = (sv.tag as? SceneCleanup)?.orientation ?: return@postToRenderThread
        orientation.pause()
        orientation.setMode(target)
        val gyroUnavailable = target == SensorMode.GYROSCOPE &&
            orientation.mode != SensorMode.GYROSCOPE
        if (orientation.mode == SensorMode.GYROSCOPE) orientation.resume()
        val actual = orientation.mode
        sv.post { onChanged(actual, gyroUnavailable) }
    }
}

private fun attachTouchHandlers(
    sv: FilamentSurfaceView,
    context: Context,
    infoSheetOpen: () -> Boolean,
    onPropSelected: (String?) -> Unit,
    onHint: (String) -> Unit
) {
    var gestureMoved = false
    val detector = GestureDetector(context, object : GestureDetector.SimpleOnGestureListener() {
        override fun onScroll(
            e1: MotionEvent?, e2: MotionEvent, dx: Float, dy: Float
        ): Boolean {
            gestureMoved = true
            val startX = e1?.x ?: return false
            val screenWidth = sv.width.coerceAtLeast(1)
            sv.postToRenderThread {
                val cleanup = (sv.tag as? SceneCleanup) ?: return@postToRenderThread
                if (startX > screenWidth / 2) {
                    cleanup.orientation.onTouchDrag(dx, dy, sensitivityDegPerPixel = 0.3f)
                } else if (!infoSheetOpen()) {
                    val normalizer = 1f / (screenWidth / 3f)
                    cleanup.movement.setJoystick(dx * normalizer * 5f, -dy * normalizer * 5f)
                }
            }
            return true
        }

        override fun onSingleTapConfirmed(e: MotionEvent): Boolean {
            if (infoSheetOpen()) return false
            val viewport = PickingMath.touchToViewport(e.x, e.y, sv.height.coerceAtLeast(1))
            val cleanup = (sv.tag as? SceneCleanup) ?: return false
            val token = cleanup.picking.currentToken()
            sv.postToRenderThread {
                sv.host.view.pick(
                    viewport[0].toInt(),
                    viewport[1].toInt(),
                    null,
                    com.google.android.filament.View.OnPickCallback { result ->
                        val decision = cleanup.picking.handlePickResult(
                            callbackToken = token,
                            pickedEntity = result.renderable,
                            entityToPropId = cleanup.assetStore.entityToPropIdSnapshot(),
                            props = cleanup.sceneManifest.props,
                            visitorXZ = cleanup.movement.visitorPosition
                        )
                        when (decision) {
                            is PickingController.PickingDecision.SelectProp -> sv.post {
                                onPropSelected(decision.propId)
                            }
                            is PickingController.PickingDecision.Deselect ->
                                sv.post { onPropSelected(null) }
                            is PickingController.PickingDecision.TooFar ->
                                sv.post { onHint("请靠近展品后再查看") }
                            else -> Unit
                        }
                    }
                )
            }
            return true
        }
    })
    sv.setOnTouchListener { _, event ->
        detector.onTouchEvent(event)
        if (event.action == MotionEvent.ACTION_DOWN) gestureMoved = false
        if (event.action == MotionEvent.ACTION_UP || event.action == MotionEvent.ACTION_CANCEL) {
            sv.postToRenderThread {
                (sv.tag as? SceneCleanup)?.movement?.setJoystick(0f, 0f)
            }
            if (event.action == MotionEvent.ACTION_UP && !gestureMoved) sv.performClick()
        }
        true
    }
}

private fun loadScene(
    sv: FilamentSurfaceView,
    context: Context,
    sceneId: String,
    onProgress: (Float, String) -> Unit,
    onReady: (SceneCleanup, List<String>) -> Unit,
    onFatalError: (AppErrorCode) -> Unit
): SceneCleanup? {
    val repository = ManifestRepository(
        AndroidAssetResourceRoot.fromContext(context),
        strict = false
    )
    val bundle = repository.loadSceneBundle(sceneId).getOrElse { error ->
        onFatalError((error as? ManifestLoadException)?.code ?: AppErrorCode.MANIFEST_INVALID)
        return null
    }
    val host = sv.host
    val assetStore = GltfAssetStore(host.engine, context.assets)
    val loader = SceneAssetLoader(host.engine, assetStore)
    val assetBaseDir = ManifestRepository.parentDirOf(bundle.indexItem.sceneManifest)
    val orientation = OrientationController(context).apply {
        initDefaultMode()
        screenRotationDeg = context.screenRotationDegrees()
    }
    val visitorStart = bundle.sceneManifest.visitorStart
    val eyeY = visitorStart.positionM.getOrElse(1) { 1.6f }.toDouble()
    val movement = MovementController(
        movement = bundle.sceneManifest.movement,
        colliders = bundle.sceneManifest.colliders,
        movePoints = bundle.sceneManifest.movePoints,
        startX = visitorStart.positionM.getOrElse(0) { 0f },
        startZ = visitorStart.positionM.getOrElse(2) { 0f }
    )
    val picking = PickingController().apply { enterScene() }
    val cleanup = SceneCleanup(
        assetStore = assetStore,
        loader = loader,
        orientation = orientation,
        movement = movement,
        picking = picking,
        sceneManifest = bundle.sceneManifest,
        contentManifest = bundle.contentManifest,
        assetBaseDir = assetBaseDir
    )
    sv.tag = cleanup
    loader.beginLoading(bundle.sceneManifest, host.scene, assetBaseDir)
    orientation.resume()

    var readyReported = false
    var fatalReported = false
    var loadingElapsedSec = 0f
    var loadState = SceneAssetLoader.State.LOADING
    sv.sceneRenderer.hooks = object : SceneRenderer.FrameUpdateHooks {
        override fun onUpdateResources(dtSec: Float) {
            if (loadState == SceneAssetLoader.State.READY || fatalReported) return
            loadingElapsedSec += dtSec
            if (loadingElapsedSec >= SCENE_LOAD_TIMEOUT_SEC) {
                fatalReported = true
                onFatalError(AppErrorCode.GLB_LOAD_FAILED)
                return
            }
            runCatching { loader.update() }
                .onSuccess { result ->
                    loadState = result.state
                    when (result.state) {
                        SceneAssetLoader.State.READY -> if (!readyReported) {
                            readyReported = true
                            onProgress(1f, "场景资源加载完成")
                            onReady(cleanup, result.failedProps)
                        }
                        SceneAssetLoader.State.FAILED -> if (!fatalReported) {
                            fatalReported = true
                            onFatalError(AppErrorCode.GLB_LOAD_FAILED)
                        }
                        else -> onProgress(
                            result.progress,
                            "正在加载环境与 ${bundle.sceneManifest.props.size} 件展品"
                        )
                    }
                }
                .onFailure {
                    if (!fatalReported) {
                        fatalReported = true
                        onFatalError(it.toVrErrorCode())
                    }
                }
        }

        override fun onUpdateOrientation(dtSec: Float) {
            if (loadState != SceneAssetLoader.State.READY) return
            val quaternion = orientation.updateAndGetCurrent(dtSec)
            val position = movement.visitorPosition
            val lookAt = OrientationMath.lookAtParams(
                quaternion,
                position[0].toDouble(),
                eyeY,
                position[1].toDouble()
            )
            host.camera.lookAt(
                lookAt[0], lookAt[1], lookAt[2],
                lookAt[3], lookAt[4], lookAt[5],
                lookAt[6], lookAt[7], lookAt[8]
            )
        }

        override fun onUpdateMovement(dtSec: Float) {
            if (loadState != SceneAssetLoader.State.READY) return
            val forward = OrientationMath.forwardVector(orientation.updateAndGetCurrent(0f))
            val length = kotlin.math.sqrt(forward[0] * forward[0] + forward[2] * forward[2])
            val forwardXZ = if (length > 1e-4f) {
                floatArrayOf(forward[0] / length, forward[2] / length)
            } else {
                floatArrayOf(0f, -1f)
            }
            movement.update(forwardXZ, dtSec)
        }
    }
    onProgress(0.1f, "场景配置校验通过")
    return cleanup
}

@Suppress("DEPRECATION")
private fun Context.screenRotationDegrees(): Int {
    val rotation = (this as? Activity)?.windowManager?.defaultDisplay?.rotation
        ?: Surface.ROTATION_0
    return when (rotation) {
        Surface.ROTATION_90 -> OrientationMath.SCREEN_ROT_90
        Surface.ROTATION_180 -> OrientationMath.SCREEN_ROT_180
        Surface.ROTATION_270 -> OrientationMath.SCREEN_ROT_270
        else -> OrientationMath.SCREEN_ROT_0
    }
}

private fun Throwable.toVrErrorCode(): AppErrorCode = when (this) {
    is OutOfMemoryError -> AppErrorCode.OUT_OF_MEMORY_RISK
    is ManifestLoadException -> code
    else -> AppErrorCode.GLB_LOAD_FAILED
}

internal data class SceneCleanup(
    val assetStore: GltfAssetStore,
    val loader: SceneAssetLoader,
    val orientation: OrientationController,
    val movement: MovementController,
    val picking: PickingController,
    val sceneManifest: SceneManifest,
    val contentManifest: ContentManifest,
    val assetBaseDir: String
)

private fun formatTime(ms: Long): String {
    val totalSeconds = (ms / 1000).coerceAtLeast(0L)
    return "${totalSeconds / 60}:${(totalSeconds % 60).toString().padStart(2, '0')}"
}

private const val SCENE_LOAD_TIMEOUT_SEC = 30f
