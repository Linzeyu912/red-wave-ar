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
import cn.bistu.redwave.ui.scan.QrScanScreen
import cn.bistu.redwave.ui.vr.VrPlaceholderScreen

/**
 * 应用根 Composable（计划书 §6.5：单 Activity + Compose Navigation）。
 *
 * 路由：HOME → QR_SCAN（CODE-08）→ VR（解析到 scene_id 后）。
 * 手动入口（CODE-10）暂用 Debug 调试入口接 VR；CODE-10 接正式场景列表。
 *
 * 边界：QR_SCAN 只返回 scene_id，成功后释放相机进入纯虚拟 VR（§1.2）。
 */
private enum class Route { HOME, QR_SCAN, VR }

@Composable
fun RedWaveApp() {
    var route by remember { mutableStateOf(Route.HOME) }
    var resolvedSceneId by remember { mutableStateOf<String?>(null) }

    when (route) {
        Route.HOME -> HomeScreen(
            onScanQr = { route = Route.QR_SCAN },
            onScanImage = { /* F2 已归档（ADR-0001） */ },
            onManualSelect = {
                // CODE-10 前：Debug 构建用“手动入口”按钮直接进入 VR 验证；
                // CODE-10 接正式场景列表。
                if (AppInfo.isDebug) {
                    resolvedSceneId = "S1"
                    route = Route.VR
                }
            },
            modifier = Modifier.fillMaxSize()
        )

        Route.QR_SCAN -> QrScanScreen(
            onResolved = { sceneId, _ ->
                // §6.9：识别成功后相机已由 QrScanScreen 释放，进入纯虚拟 VR
                resolvedSceneId = sceneId
                route = Route.VR
            },
            onBack = { route = Route.HOME },
            modifier = Modifier.fillMaxSize()
        )

        Route.VR -> Box(modifier = Modifier.fillMaxSize()) {
            // VrPlaceholderScreen 内部按 resolvedSceneId 加载场景（CODE-10 抽 SceneCoordinator）
            VrPlaceholderScreen()
        }
    }
}
