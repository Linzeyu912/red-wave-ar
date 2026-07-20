package cn.bistu.redwave.audio

import android.content.Context
import android.net.Uri

/**
 * 音频来源抽象（计划书 §6.15：assets 与下载场景包通过统一 AudioSource，
 * UI 不关心实际 URI）。
 */
sealed class AudioSource {
    /** assets 内的音频（bundled 场景）。 */
    data class Asset(val path: String) : AudioSource() {
        fun toUri(context: Context): Uri =
            Uri.parse("android.resource://${context.packageName}/asset/$path")
                .let {
                    // assets 用 file:///android_asset/ 协议，ExoPlayer 直接支持
                    Uri.parse("file:///android_asset/${path.trimStart('/')}")
                }
    }

    /** 已安装场景包目录下的音频文件。 */
    data class File(val absolutePath: String) : AudioSource() {
        fun toUri(): Uri = Uri.parse(absolutePath)
    }
}

/** 音频播放状态（计划书 §6.15）。 */
data class NarrationState(
    val itemId: String?,
    val isPlaying: Boolean,
    val isReady: Boolean,
    val hasError: Boolean,
    val positionMs: Long,
    val durationMs: Long
) {
    companion object {
        val IDLE = NarrationState(
            itemId = null, isPlaying = false, isReady = false,
            hasError = false, positionMs = 0L, durationMs = 0L
        )
    }
}

/** 停止原因（计划书 §6.15）。 */
enum class StopReason {
    /** 关闭信息卡。 */
    CLOSED,
    /** 切换到新文物。 */
    SWITCHED,
    /** 切场景或返回首页。 */
    SCENE_CHANGED,
    /** 资源错误。 */
    ERROR,
    /** 音频焦点丢失 / 耳机拔出（这类用 pause 而非 stop）。 */
    TRANSIENT
}
