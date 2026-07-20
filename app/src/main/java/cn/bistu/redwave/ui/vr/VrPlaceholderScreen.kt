package cn.bistu.redwave.ui.vr

import android.content.Context
import android.view.GestureDetector
import android.view.MotionEvent
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.padding
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
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
import cn.bistu.redwave.data.AndroidAssetResourceRoot
import cn.bistu.redwave.data.ManifestRepository
import cn.bistu.redwave.render.FilamentSceneConfig
import cn.bistu.redwave.render.FilamentSurfaceView
import cn.bistu.redwave.render.SceneRenderer
import cn.bistu.redwave.render.asset.GltfAssetStore
import cn.bistu.redwave.render.asset.SceneAssetLoader
import cn.bistu.redwave.sensor.OrientationController

// CODE-03/04 渲染验证页（CODE-03 GLB 加载 + CODE-04 触屏环视）。
// CODE-10 接入 SceneCoordinator 后演化为正式 VR 屏。
@Composable
fun VrPlaceholderScreen(
    modifier: Modifier = Modifier
) {
    val context = LocalContext.current
    val surfaceViewRef = remember { mutableStateOf<FilamentSurfaceView?>(null) }
    val cleanupRef = remember { mutableStateOf<SceneCleanup?>(null) }
    // CODE-07：单实例音频控制器
    val narration = remember { cn.bistu.redwave.audio.NarrationController(context) }
    val narrationState by narration.state.collectAsState()
    var status by remember { mutableStateOf("初始化中…") }
    var selectedPropId by remember { mutableStateOf<String?>(null) }

    // CODE-07：选中/取消文物时播放/停止音频（§6.15）
    LaunchedEffect(selectedPropId) {
        val cleanup = cleanupRef.value
        val propId = selectedPropId
        if (propId == null || cleanup == null) {
            narration.stop(cn.bistu.redwave.audio.StopReason.CLOSED)
        } else {
            val item = cleanup.contentManifest.items.firstOrNull { it.id == propId }
            if (item != null) {
                val source = cn.bistu.redwave.audio.AudioSource.Asset(item.audio)
                narration.play(propId, source)
            }
        }
    }

    // CODE-07：进度轮询（§6.15 UI 显示进度）
    LaunchedEffect(narration) {
        while (true) {
            narration.pollPosition()
            kotlinx.coroutines.delay(500)
        }
    }

    Box(modifier = modifier.fillMaxSize()) {
        AndroidView(
            factory = { ctx ->
                FilamentSurfaceView(ctx).also { sv ->
                    surfaceViewRef.value = sv
                    sv.onResumeRendering(createSceneObjects = true)
                    // 在渲染线程加载 S1 白盒
                    sv.postToRenderThread {
                        val cleanup = loadSceneS1Whitebox(sv, ctx) { newStatus ->
                            sv.post { status = newStatus }
                        }
                        if (cleanup != null) cleanupRef.value = cleanup
                    }
                    // CODE-04/06：触屏拖动环视/移动 + 单击拾取
                    attachTouchHandlers(sv, ctx) { propId ->
                        selectedPropId = propId
                    }
                }
            },
            update = { /* CODE-05 viewport 重配 */ },
            modifier = Modifier.fillMaxSize()
        )

        Column(
            modifier = Modifier
                .align(Alignment.TopStart)
                .padding(12.dp)
        ) {
            Text("CODE-06 白盒 + 环视 + 拾取", color = Color.White,
                style = MaterialTheme.typography.labelSmall)
            Text(status, color = Color.White.copy(alpha = 0.85f),
                style = MaterialTheme.typography.labelSmall)
        }

        // CODE-06：底部信息卡（选中文物时显示）
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
                    durationLabel = if (narrationState.durationMs > 0) formatTime(narrationState.durationMs)
                                    else "${selectedContent.audioDurationSec / 60}:${(selectedContent.audioDurationSec % 60).toString().padStart(2, '0')}"
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
    }

    // Surface 尺寸就绪后配置相机/清屏（渲染线程）
    LaunchedEffect(surfaceViewRef.value) {
        val sv = surfaceViewRef.value ?: return@LaunchedEffect
        sv.post {
            val w = sv.width.coerceAtLeast(1)
            val h = sv.height.coerceAtLeast(1)
            sv.postToRenderThread {
                FilamentSceneConfig.configureBaseline(sv.host, w, h)
            }
        }
    }

    // 退出按 §6.21 释放（音频按 §6.15 切场景停止）
    DisposableEffect(Unit) {
        onDispose {
            narration.stop(cn.bistu.redwave.audio.StopReason.SCENE_CHANGED)
            narration.release()
            val sv = surfaceViewRef.value
            val cleanup = cleanupRef.value
            if (sv != null && cleanup != null) {
                sv.postToRenderThread {
                    cleanup.picking.exitScene()
                    cleanup.orientation.pause()
                    cleanup.loader.reset()
                    cleanup.assetStore.destroyAll(sv.host.scene)
                    cleanup.assetStore.destroy()
                }
            }
            surfaceViewRef.value?.shutdown()
            surfaceViewRef.value = null
            cleanupRef.value = null
        }
    }
}

// 触屏分区：右半屏拖动环视、左半屏拖动摇杆移动、单击触发拾取（§6.14）。
// CODE-10 接入正式摇杆组件后替换。
private fun attachTouchHandlers(
    sv: FilamentSurfaceView,
    context: Context,
    onPropSelected: (String?) -> Unit
) {
    val detector = GestureDetector(context, object : GestureDetector.SimpleOnGestureListener() {
        override fun onScroll(
            e1: MotionEvent?, e2: MotionEvent, dx: Float, dy: Float
        ): Boolean {
            val startX = e1?.x ?: return false
            val screenW = sv.width.coerceAtLeast(1)
            val sensitivity = 0.3f
            sv.postToRenderThread {
                val cleanup = (sv.tag as? SceneCleanup) ?: return@postToRenderThread
                if (startX > screenW / 2) {
                    cleanup.orientation.onTouchDrag(dx, dy, sensitivity)
                } else {
                    val norm = 1f / (screenW / 3f)
                    cleanup.movement.setJoystick(dx * norm * 5f, -dy * norm * 5f)
                }
            }
            return true
        }

        override fun onSingleTapConfirmed(e: MotionEvent): Boolean {
            // §6.14：单击触发 View.pick（异步）
            val screenH = sv.height.coerceAtLeast(1)
            val viewport = cn.bistu.redwave.interaction.PickingMath.touchToViewport(
                e.x, e.y, screenH
            )
            val cleanup = (sv.tag as? SceneCleanup) ?: return false
            val token = cleanup.picking.currentToken()
            sv.postToRenderThread {
                // View.pick 回调在 Filament 线程；用 handler 投回渲染线程处理
                sv.host.view.pick(
                    viewport[0].toInt(), viewport[1].toInt(),
                    null,
                    com.google.android.filament.View.OnPickCallback { result ->
                        val entity = result.renderable
                        val decision = cleanup.picking.handlePickResult(
                            callbackToken = token,
                            pickedEntity = entity,
                            entityToPropId = cleanup.assetStore.entityToPropIdSnapshot(),
                            props = cleanup.sceneManifest.props,
                            visitorXZ = cleanup.movement.visitorPosition
                        )
                        when (decision) {
                            is cn.bistu.redwave.interaction.PickingController.PickingDecision.SelectProp ->
                                sv.post { onPropSelected(decision.propId) }
                            is cn.bistu.redwave.interaction.PickingController.PickingDecision.Deselect ->
                                sv.post { onPropSelected(null) }
                            is cn.bistu.redwave.interaction.PickingController.PickingDecision.TooFar ->
                                sv.post { statusHint(sv, "靠近 ${decision.propId} 后再查看") }
                            else -> { /* Stale 忽略 */ }
                        }
                    }
                )
            }
            return true
        }
    })
    sv.setOnTouchListener { _, e ->
        detector.onTouchEvent(e)
        if (e.action == MotionEvent.ACTION_UP || e.action == MotionEvent.ACTION_CANCEL) {
            sv.postToRenderThread {
                (sv.tag as? SceneCleanup)?.movement?.setJoystick(0f, 0f)
            }
        }
        true
    }
}

private fun statusHint(sv: FilamentSurfaceView, text: String) {
    // 简易提示；CODE-10 接 Toast/Snackbar
}

// 在渲染线程加载 S1 白盒并接入姿态更新。
private fun loadSceneS1Whitebox(
    sv: FilamentSurfaceView,
    context: Context,
    onStatus: (String) -> Unit
): SceneCleanup? {
    val host = sv.host
    val repo = ManifestRepository(
        AndroidAssetResourceRoot.fromContext(context),
        strict = false
    )
    val bundle = repo.loadSceneBundle("S1").getOrElse { ex ->
        onStatus("加载失败: ${ex.message?.take(80)}")
        return null
    }
    val assetStore = GltfAssetStore(host.engine, context.assets)
    val loader = SceneAssetLoader(host.engine, assetStore)
    val sceneDir = ManifestRepository.parentDirOf(bundle.indexItem.sceneManifest)

    // CODE-04：姿态控制器，按设备能力选默认模式
    val orientation = OrientationController(context)
    orientation.initDefaultMode()

    // CODE-05：移动控制器，位置由它维护；姿态只改视线方向（§6.13）
    val vs = bundle.sceneManifest.visitorStart
    val eyeY = vs.positionM.getOrElse(1) { 1.6f }.toDouble() // 眼高固定
    val movement = cn.bistu.redwave.interaction.MovementController(
        movement = bundle.sceneManifest.movement,
        colliders = bundle.sceneManifest.colliders,
        movePoints = bundle.sceneManifest.movePoints,
        startX = vs.positionM.getOrElse(0) { 0f },
        startZ = vs.positionM.getOrElse(2) { 0f }
    )

    loader.beginLoading(bundle.sceneManifest, host.scene, sceneDir)
    onStatus("加载中… 环境 + ${bundle.sceneManifest.props.size} 文物")

    sv.sceneRenderer.hooks = object : SceneRenderer.FrameUpdateHooks {
        override fun onUpdateResources(dtSec: Float) {
            val result = loader.update()
            when (result.state) {
                SceneAssetLoader.State.READY -> {
                    val failed = if (result.failedProps.isNotEmpty()) {
                        "（缺失: ${result.failedProps.joinToString()}）"
                    } else ""
                    onStatus("就绪：${assetStore.loadedCount()} 资产$failed")
                }
                SceneAssetLoader.State.FAILED -> {
                    onStatus("失败: ${result.errorMessage?.take(80)}")
                }
                else -> onStatus("加载中… ${(result.progress * 100).toInt()}%")
            }
        }

        override fun onUpdateOrientation(dtSec: Float) {
            // 每帧更新姿态并把朝向写入相机；位置取自 MovementController（§6.13-7）
            if (loader.update().state != SceneAssetLoader.State.READY) return
            val q = orientation.updateAndGetCurrent(dtSec)
            val pos = movement.visitorPosition
            val lookAt = cn.bistu.redwave.sensor.OrientationMath.lookAtParams(
                q, pos[0].toDouble(), eyeY, pos[1].toDouble()
            )
            host.camera.lookAt(
                lookAt[0], lookAt[1], lookAt[2],
                lookAt[3], lookAt[4], lookAt[5],
                lookAt[6], lookAt[7], lookAt[8]
            )
        }

        override fun onUpdateMovement(dtSec: Float) {
            if (loader.update().state != SceneAssetLoader.State.READY) return
            // 用当前相机 forward 的 XZ 投影作为移动方向基准
            val q = orientation.updateAndGetCurrent(0f)
            val forwardXZ = cn.bistu.redwave.sensor.OrientationMath.forwardVector(q)
                .let { f -> floatArrayOf(f[0], f[2]) }
            // 归一化
            val len = kotlin.math.sqrt(forwardXZ[0] * forwardXZ[0] + forwardXZ[1] * forwardXZ[1])
            val unit = if (len > 1e-4f) floatArrayOf(forwardXZ[0] / len, forwardXZ[1] / len)
                       else floatArrayOf(0f, -1f)
            movement.update(unit, dtSec)
        }
    }

    val picking = cn.bistu.redwave.interaction.PickingController()
    picking.enterScene()

    val cleanup = SceneCleanup(
        assetStore, loader, orientation, movement, picking,
        sceneManifest = bundle.sceneManifest,
        contentManifest = bundle.contentManifest
    )
    sv.tag = cleanup // 供触屏 handler 取
    orientation.resume()
    return cleanup
}

internal data class SceneCleanup(
    val assetStore: GltfAssetStore,
    val loader: SceneAssetLoader,
    val orientation: OrientationController,
    val movement: cn.bistu.redwave.interaction.MovementController,
    val picking: cn.bistu.redwave.interaction.PickingController,
    val sceneManifest: cn.bistu.redwave.data.SceneManifest,
    val contentManifest: cn.bistu.redwave.data.ContentManifest
)

// 毫秒 → "M:SS" 显示
private fun formatTime(ms: Long): String {
    val totalSec = (ms / 1000).coerceAtLeast(0L)
    val m = totalSec / 60
    val s = totalSec % 60
    return "$m:${s.toString().padStart(2, '0')}"
}
