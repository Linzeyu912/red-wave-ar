package cn.bistu.redwave

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.SystemBarStyle
import androidx.activity.compose.setContent
import androidx.activity.enableEdgeToEdge
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Surface
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import cn.bistu.redwave.ui.RedWaveApp
import cn.bistu.redwave.ui.theme.RedWaveTheme

/**
 * 计划书 §6.5：单 Activity + Compose。
 * 入口、VR、传感器、音频由独立 owner 管理生命周期，Activity 仅承载 Compose 导航。
 */
class MainActivity : ComponentActivity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        // Filament 的 Java 层不会自动加载 native lib，必须显式 init()
        // （否则 Engine.create() 抛 UnsatisfiedLinkError）。
        // 在进入 VR 页（创建 Engine）前完成加载。
        com.google.android.filament.Filament.init()
        // 沉浸式边到边渲染（VR 铺满屏幕做准备）。
        enableEdgeToEdge(
            statusBarStyle = SystemBarStyle.auto(Color.Transparent.hashCode(), Color.Transparent.hashCode()),
            navigationBarStyle = SystemBarStyle.auto(Color.Transparent.hashCode(), Color.Transparent.hashCode())
        )
        setContent {
            RedWaveTheme {
                Surface(
                    modifier = Modifier
                        .fillMaxSize()
                        .background(Color.Black),
                    color = Color.Black
                ) {
                    RedWaveApp()
                }
            }
        }
    }
}
