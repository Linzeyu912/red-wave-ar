package cn.bistu.redwave.ui.vr

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.PaddingValues
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.displayCutoutPadding
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.heightIn
import androidx.compose.foundation.layout.navigationBarsPadding
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.Card
import androidx.compose.material3.CardDefaults
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Close
import androidx.compose.material.icons.filled.VolumeUp
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import cn.bistu.redwave.data.ContentItem

/**
 * 文物信息卡（计划书 §6.16 信息卡页面规格）。
 *
 * 展示：标题、正文、来源摘要、音频控制（CODE-07 接入实际播放）。
 * 失败状态：音频失败时仍展示文字（§6.18 AUDIO_LOAD_FAILED）。
 *
 * @param content 选中文物的内容条目（content.json）；null 时不显示
 * @param onClose 关闭回调（点击空白或关闭按钮）
 * @param audioState 音频状态（CODE-07），CODE-06 阶段为占位
 */
@Composable
fun InfoSheet(
    content: ContentItem?,
    audioState: AudioControlState,
    onClose: () -> Unit,
    onToggleAudio: () -> Unit,
    modifier: Modifier = Modifier
) {
    if (content == null) return
    Card(
        modifier = modifier
            .fillMaxWidth()
            .navigationBarsPadding()
            .displayCutoutPadding()
            .heightIn(min = 120.dp, max = 320.dp),
        shape = RoundedCornerShape(topStart = 20.dp, topEnd = 20.dp),
        colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surface)
    ) {
        Column(
            modifier = Modifier
                .fillMaxWidth()
                .padding(20.dp)
                .verticalScroll(rememberScrollState())
        ) {
            Row(
                verticalAlignment = Alignment.CenterVertically,
                horizontalArrangement = Arrangement.SpaceBetween,
                modifier = Modifier.fillMaxWidth()
            ) {
                Text(
                    text = content.title,
                    style = MaterialTheme.typography.titleMedium,
                    fontWeight = FontWeight.SemiBold,
                    color = MaterialTheme.colorScheme.onSurface,
                    modifier = Modifier.weight(1f)
                )
                IconButton(onClick = onClose) {
                    Icon(Icons.Filled.Close, contentDescription = "关闭",
                        tint = MaterialTheme.colorScheme.onSurface)
                }
            }
            Spacer(Modifier.padding(top = 8.dp))
            Text(
                text = content.text,
                style = MaterialTheme.typography.bodyMedium,
                color = MaterialTheme.colorScheme.onSurface.copy(alpha = 0.9f)
            )
            // 来源摘要（§4.9 内容质量要求记录史料来源）
            if (content.sources.isNotEmpty()) {
                Spacer(Modifier.padding(top = 12.dp))
                Text(
                    text = "来源：${content.sources.joinToString("；") { it.title }}",
                    style = MaterialTheme.typography.labelSmall,
                    color = MaterialTheme.colorScheme.onSurface.copy(alpha = 0.6f)
                )
            }
            // 音频控制（CODE-07 接实际播放）
            Spacer(Modifier.padding(top = 12.dp))
            AudioControl(state = audioState, onToggle = onToggleAudio)
        }
    }
}

/** 音频控件状态（CODE-07 NarrationController 接入）。 */
data class AudioControlState(
    val available: Boolean,
    val isPlaying: Boolean,
    val positionLabel: String,
    val durationLabel: String
)

@Composable
private fun AudioControl(state: AudioControlState, onToggle: () -> Unit) {
    Row(verticalAlignment = Alignment.CenterVertically) {
        IconButton(onClick = onToggle, enabled = state.available) {
            Icon(
                imageVector = if (state.isPlaying) Icons.Filled.Close else Icons.Filled.VolumeUp,
                contentDescription = if (state.isPlaying) "暂停" else "播放讲解",
                tint = if (state.available) MaterialTheme.colorScheme.primary
                       else MaterialTheme.colorScheme.onSurface.copy(alpha = 0.3f)
            )
        }
        Spacer(Modifier.width(8.dp))
        if (state.available) {
            Text(
                text = "${state.positionLabel} / ${state.durationLabel}",
                style = MaterialTheme.typography.labelMedium,
                color = MaterialTheme.colorScheme.onSurface.copy(alpha = 0.7f)
            )
        } else {
            // §6.18 AUDIO_LOAD_FAILED：音频失败仍展示文字
            Text(
                text = "音频暂不可用",
                style = MaterialTheme.typography.labelMedium,
                color = MaterialTheme.colorScheme.onSurface.copy(alpha = 0.5f)
            )
        }
    }
}
