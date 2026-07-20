package cn.bistu.redwave.ui.vr

import android.content.Context
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

// CODE-03 渲染验证页（计划书 CODE-03 完成标准：加载 S1 白盒 GLB 并渲染）。
// CODE-10 接入 SceneCoordinator 后，此页演化为正式 VR 屏。
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
                }
            },
            update = { /* CODE-04/05 接入相机姿态更新时在此按 viewport 重配 */ },
            modifier = Modifier.fillMaxSize()
        )

        // 顶部状态信息
        Column(
            modifier = Modifier
                .align(Alignment.TopStart)
                .padding(12.dp)
        ) {
            Text(
                text = "CODE-03 白盒 GLB 加载",
                color = Color.White,
                style = MaterialTheme.typography.labelSmall
            )
            Text(
                text = status,
                color = Color.White.copy(alpha = 0.85f),
                style = MaterialTheme.typography.labelSmall
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

    // 退出时按 §6.21 释放：停止帧循环 -> 移除实体 -> 销毁 asset -> destroyAll
    DisposableEffect(Unit) {
        onDispose {
            val sv = surfaceViewRef.value
            val cleanup = cleanupRef.value
            if (sv != null && cleanup != null) {
                sv.postToRenderThread {
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

// 在渲染线程加载 S1 白盒。返回 cleanup 句柄供退出释放；失败返回 null。
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

    loader.beginLoading(bundle.sceneManifest, host.scene, sceneDir)
    onStatus("加载中… 环境 + ${bundle.sceneManifest.props.size} 文物")

    // 每帧推进加载进度（CODE-10 抽到 SceneCoordinator）
    sv.sceneRenderer.hooks = object : SceneRenderer.FrameUpdateHooks {
        override fun onUpdateResources(dtSec: Float) {
            val result = loader.update()
            when (result.state) {
                SceneAssetLoader.State.READY -> {
                    val failed = if (result.failedProps.isNotEmpty()) {
                        "（缺失: ${result.failedProps.joinToString()}）"
                    } else ""
                    onStatus("就绪：${assetStore.loadedCount()} 资产已加载$failed")
                }
                SceneAssetLoader.State.FAILED -> {
                    onStatus("失败: ${result.errorMessage?.take(80)}")
                }
                else -> onStatus("加载中… ${(result.progress * 100).toInt()}%")
            }
        }
    }

    return SceneCleanup(assetStore, loader)
}

// 退出释放句柄（§6.21）
internal data class SceneCleanup(
    val assetStore: GltfAssetStore,
    val loader: SceneAssetLoader
)
