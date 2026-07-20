package cn.bistu.redwave.ui

import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Modifier
import cn.bistu.redwave.AppInfo
import cn.bistu.redwave.ui.home.HomeScreen
import cn.bistu.redwave.ui.vr.VrPlaceholderScreen

/**
 * 应用根 Composable（计划书 §6.5：单 Activity + Compose Navigation）。
 *
 * CODE-02 阶段：Debug 下提供“渲染测试”内部入口，验证 Filament 帧循环。
 * 正式入口在 CODE-08/09/10 接入；届时移除占位调试入口。
 */
private enum class DebugRoute { HOME, VR_RENDER_TEST }

@Composable
fun RedWaveApp() {
    var route by remember { mutableStateOf(DebugRoute.HOME) }

    when (route) {
        DebugRoute.HOME -> HomeScreen(
            onScanQr = { /* CODE-08 */ },
            onScanImage = { /* CODE-09 */ },
            onManualSelect = {
                // CODE-10 前：Debug 构建临时用“手动入口”按钮进入渲染测试页，
                // 验证 Filament 管线；Release 正式入口在 CODE-10 接入。
                if (AppInfo.isDebug) route = DebugRoute.VR_RENDER_TEST
            },
            modifier = Modifier.fillMaxSize()
        )
        DebugRoute.VR_RENDER_TEST -> Box(modifier = Modifier.fillMaxSize()) {
            VrPlaceholderScreen()
        }
    }
}

