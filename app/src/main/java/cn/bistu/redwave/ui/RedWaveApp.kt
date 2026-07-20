package cn.bistu.redwave.ui

import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import cn.bistu.redwave.ui.home.HomeScreen

/**
 * 应用根 Composable（计划书 §6.5：单 Activity + Compose Navigation）。
 *
 * CODE-00 阶段：仅渲染首页骨架。入口按钮的导航在后续 CODE 任务接入：
 * - 扫描二维码 → CODE-08
 * - 识别触发图 → CODE-09
 * - 手动选择  → CODE-10
 *
 * 此时点击按钮暂不跳转，避免引入未实现的状态机导致崩溃。
 */
@Composable
fun RedWaveApp() {
    Box(modifier = Modifier.fillMaxSize()) {
        HomeScreen(
            onScanQr = { /* CODE-08: QrScanScreen */ },
            onScanImage = { /* CODE-09: ImageScanScreen */ },
            onManualSelect = { /* CODE-10: 场景列表 */ },
            modifier = Modifier.fillMaxSize()
        )
        // 占位：调试时确认主题色生效。
        Text(
            text = "",
            color = MaterialTheme.colorScheme.onSurface,
            modifier = Modifier.align(Alignment.TopCenter)
        )
    }
}
