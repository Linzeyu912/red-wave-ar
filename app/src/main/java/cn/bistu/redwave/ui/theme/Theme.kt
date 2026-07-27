package cn.bistu.redwave.ui.theme

import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Typography
import androidx.compose.material3.darkColorScheme
import androidx.compose.material3.lightColorScheme
import androidx.compose.runtime.Composable
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontFamily
import androidx.compose.ui.text.font.FontWeight

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
    onSecondary = Color.Black,
    secondaryContainer = Color(0xFF6D4C00),
    onSecondaryContainer = Color.White,
    background = Color(0xFF101418),
    onBackground = Color(0xFFE6E6E6),
    surface = Color(0xFF161B22),
    onSurface = Color(0xFFE6E6E6),
    surfaceVariant = Color(0xFF1D242D),
    onSurfaceVariant = Color(0xFFB0B8C4),
    surfaceTint = RedPrimary,
    inverseSurface = Color(0xFFE6E6E6),
    inverseOnSurface = Color(0xFF101418),
    error = Color(0xFFFF5252),
    onError = Color.Black,
    errorContainer = Color(0xFF5C0C0C),
    onErrorContainer = Color(0xFFFFDAD6),
    outline = Color(0xFF3A4654),
    outlineVariant = Color(0xFF252E38),
    scrim = Color.Black
)

private val LightColors = lightColorScheme(
    primary = RedDark,
    onPrimary = Color.White,
    primaryContainer = Color(0xFFFFDAD6),
    onPrimaryContainer = RedDark,
    secondary = Color(0xFF6D4C00),
    onSecondary = Color.White,
    secondaryContainer = Color(0xFFFFE082),
    onSecondaryContainer = Color(0xFF261A00),
    background = Color(0xFFF5F2EF),
    onBackground = Color(0xFF1C1B1F),
    surface = Color(0xFFFFFFFF),
    onSurface = Color(0xFF1C1B1F),
    surfaceVariant = Color(0xFFE3E0DD),
    onSurfaceVariant = Color(0xFF49454F),
    surfaceTint = RedDark,
    inverseSurface = Color(0xFF313033),
    inverseOnSurface = Color(0xFFF4EFF4),
    error = Color(0xFFB3261E),
    onError = Color.White,
    errorContainer = Color(0xFFFFDAD6),
    onErrorContainer = Color(0xFF410E0B),
    outline = Color(0xFF747474),
    outlineVariant = Color(0xFFCAC4D0),
    scrim = Color.Black
)

private val RedWaveTypography = Typography(
    displayLarge = Typography().displayLarge.copy(fontFamily = FontFamily.Serif),
    displayMedium = Typography().displayMedium.copy(fontFamily = FontFamily.Serif),
    displaySmall = Typography().displaySmall.copy(fontFamily = FontFamily.Serif),
    headlineLarge = Typography().headlineLarge.copy(fontFamily = FontFamily.Serif),
    headlineMedium = Typography().headlineMedium.copy(fontFamily = FontFamily.Serif),
    headlineSmall = Typography().headlineSmall.copy(
        fontFamily = FontFamily.Serif,
        fontWeight = FontWeight.SemiBold
    ),
    titleLarge = Typography().titleLarge.copy(fontFamily = FontFamily.Serif),
    titleMedium = Typography().titleMedium.copy(
        fontFamily = FontFamily.Serif,
        fontWeight = FontWeight.SemiBold
    ),
    titleSmall = Typography().titleSmall.copy(fontFamily = FontFamily.Serif),
    bodyLarge = Typography().bodyLarge.copy(fontFamily = FontFamily.SansSerif),
    bodyMedium = Typography().bodyMedium.copy(fontFamily = FontFamily.SansSerif),
    bodySmall = Typography().bodySmall.copy(fontFamily = FontFamily.SansSerif),
    labelLarge = Typography().labelLarge.copy(fontFamily = FontFamily.SansSerif),
    labelMedium = Typography().labelMedium.copy(fontFamily = FontFamily.SansSerif),
    labelSmall = Typography().labelSmall.copy(fontFamily = FontFamily.SansSerif)
)

@Composable
fun RedWaveTheme(
    useDarkTheme: Boolean = true,
    content: @Composable () -> Unit
) {
    MaterialTheme(
        colorScheme = if (useDarkTheme) DarkColors else LightColors,
        typography = RedWaveTypography,
        content = content
    )
}
