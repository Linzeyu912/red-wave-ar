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
    var status by remember { mutableStateOf("初始化中…") }

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
                    // CODE-04：触屏拖动改 yaw/pitch
                    attachTouchLook(sv, ctx)
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
            Text("CODE-04 白盒 + 触屏环视", color = Color.White,
                style = MaterialTheme.typography.labelSmall)
            Text(status, color = Color.White.copy(alpha = 0.85f),
                style = MaterialTheme.typography.labelSmall)
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

    // 退出按 §6.21 释放
    DisposableEffect(Unit) {
        onDispose {
            val sv = surfaceViewRef.value
            val cleanup = cleanupRef.value
            if (sv != null && cleanup != null) {
                sv.postToRenderThread {
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

// 触屏拖动：通过 GestureDetector 把 scroll 转成 yaw/pitch 增量。
private fun attachTouchLook(sv: FilamentSurfaceView, context: Context) {
    val detector = GestureDetector(context, object : GestureDetector.SimpleOnGestureListener() {
        override fun onScroll(
            e1: MotionEvent?, e2: MotionEvent, dx: Float, dy: Float
        ): Boolean {
            // 触屏灵敏度（度/像素），CODE-10 设置页可调
            val sensitivity = 0.3f
            // 在渲染线程更新姿态（OrientationController 状态非 native，但为线程一致统一切线程）
            sv.postToRenderThread {
                // cleanupRef 在 Composable 里，这里通过 tag 取
                val cleanup = (sv.tag as? SceneCleanup)
                cleanup?.orientation?.onTouchDrag(dx, dy, sensitivity)
            }
            return true
        }
    })
    sv.setOnTouchListener { _, e ->
        detector.onTouchEvent(e); true
    }
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

    // 游客起点（CODE-05 移动控制器接管前用 scene.json 的 visitor_start）
    val vs = bundle.sceneManifest.visitorStart
    val eyeX = vs.positionM.getOrElse(0) { 0f }.toDouble()
    val eyeY = vs.positionM.getOrElse(1) { 1.6 }.toDouble()
    val eyeZ = vs.positionM.getOrElse(2) { 0f }.toDouble()

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
            // 每帧更新姿态并把朝向写入相机（位置暂用 visitor_start，CODE-05 接管）
            if (loader.update().state != SceneAssetLoader.State.READY) return
            val q = orientation.updateAndGetCurrent(dtSec)
            val lookAt = cn.bistu.redwave.sensor.OrientationMath.lookAtParams(q, eyeX, eyeY, eyeZ)
            host.camera.lookAt(
                lookAt[0], lookAt[1], lookAt[2],   // eye
                lookAt[3], lookAt[4], lookAt[5],   // center
                lookAt[6], lookAt[7], lookAt[8]    // up
            )
        }
    }

    val cleanup = SceneCleanup(assetStore, loader, orientation)
    sv.tag = cleanup // 供触屏 handler 取
    orientation.resume()
    return cleanup
}

internal data class SceneCleanup(
    val assetStore: GltfAssetStore,
    val loader: SceneAssetLoader,
    val orientation: OrientationController
)
