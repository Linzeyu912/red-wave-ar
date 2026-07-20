package cn.bistu.redwave.ui.theme

import androidx.compose.foundation.isSystemInDarkTheme
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.darkColorScheme
import androidx.compose.material3.lightColorScheme
import androidx.compose.runtime.Composable
import androidx.compose.ui.graphics.Color

// “红色电波”主色调。深色为默认（VR 展馆多为暗场环境）。
private val RedPrimary = Color(0xFFE53935)
private val RedDark = Color(0xFF8B1A1A)
private val AmberAccent = Color(0xFFFFC107)

private val DarkColors = darkColorScheme(
    primary = RedPrimary,
    onPrimary = Color.White,
    primaryContainer = RedDark,
    onPrimaryContainer = Color.White,
    secondary = AmberAccent,
    background = Color(0xFF101418),
    surface = Color(0xFF161B22),
    onSurface = Color(0xFFE6E6E6)
)

private val LightColors = lightColorScheme(
    primary = RedDark,
    onPrimary = Color.White,
    secondary = AmberAccent
)

@Composable
fun RedWaveTheme(
    useDarkTheme: Boolean = isSystemInDarkTheme(),
    content: @Composable () -> Unit
) {
    MaterialTheme(
        colorScheme = if (useDarkTheme) DarkColors else LightColors,
        typography = MaterialTheme.typography,
        content = content
    )
}
