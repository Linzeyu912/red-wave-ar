package cn.bistu.redwave.ui.vr

import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.padding
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.DisposableEffect
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.unit.dp
import androidx.compose.ui.viewinterop.AndroidView
import cn.bistu.redwave.render.FilamentSceneConfig
import cn.bistu.redwave.render.FilamentSurfaceView

/**
 * CODE-02 渲染管线验证页（内部调试，计划书 CODE-02 完成标准：稳定渲染页）。
 *
 * 显示一个纯色 Filament 渲染区，验证：
 * - Surface → SwapChain 创建/销毁；
 * - 帧循环（Choreographer → beginFrame → render → endFrame）；
 * - 前后台切换与 Surface 重建无黑屏、无崩溃、无重复帧回调。
 *
 * 真实 GLB 加载在 CODE-03；真实姿态/移动在 CODE-04/05。本页只用纯色背景 +
 * 相机投影占位，确认渲染基础设施稳定。
 *
 * 仅 Debug 构建可达（CODE-10 接入正式入口前的内部验证页）。
 */
@Composable
fun VrPlaceholderScreen(
    modifier: Modifier = Modifier
) {
    // 用 state 持有 factory 实际创建的 view，供配置/释放访问。
    val surfaceViewRef = remember { mutableStateOf<FilamentSurfaceView?>(null) }

    Box(modifier = modifier.fillMaxSize()) {
        AndroidView(
            factory = { ctx ->
                FilamentSurfaceView(ctx).also { sv ->
                    surfaceViewRef.value = sv
                    // 进入时创建场景对象并启动帧循环
                    sv.onResumeRendering(createSceneObjects = true)
                }
            },
            update = { /* CODE-03 接入相机投影更新时在此按 viewport 重配 */ },
            modifier = Modifier.fillMaxSize()
        )

        // 顶部调试信息（确认渲染是否在跑）
        Column(
            modifier = Modifier
                .align(Alignment.TopStart)
                .padding(12.dp)
        ) {
            Text(
                text = "CODE-02 渲染管线验证",
                color = Color.White,
                style = MaterialTheme.typography.labelSmall
            )
            Text(
                text = "若看到深色背景则帧循环正常（GLB 在 CODE-03 接入）",
                color = Color.White.copy(alpha = 0.8f),
                style = MaterialTheme.typography.labelSmall
            )
        }
    }

    // Surface 尺寸就绪后，在渲染线程配置相机/清屏（Filament 要求 Engine 线程）
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

    DisposableEffect(Unit) {
        onDispose {
            surfaceViewRef.value?.shutdown()
            surfaceViewRef.value = null
        }
    }
}
