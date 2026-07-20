package cn.bistu.redwave.audio

import android.content.BroadcastReceiver
import android.content.Context
import android.content.Intent
import android.content.IntentFilter
import android.media.AudioManager
import android.net.Uri
import androidx.media3.common.AudioAttributes
import androidx.media3.common.C
import androidx.media3.common.MediaItem
import androidx.media3.common.Player
import androidx.media3.exoplayer.ExoPlayer
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow

/**
 * 单实例音频控制器（计划书 §6.6 audio、§6.15）。
 *
 * 全应用只维护一个 [ExoPlayer]：
 * - play(itemId, source)：打开新文物自动停止旧讲解并从头播放新音频（§6.15）；
 * - 关闭信息卡默认暂停；切场景/返回首页/资源错误停止并清空 MediaItem（§6.15）；
 * - 音频焦点丢失暂停；耳机拔出暂停（§6.15）；
 * - 不做后台播放与通知栏控制（§6.15，MVP）。
 *
 * 状态通过 [state] StateFlow 暴露，UI 据此更新信息卡（§6.15）。
 *
 * 线程：ExoPlayer 在主线程创建与操作；状态更新经 Player.Listener 回调（主线程）。
 */
class NarrationController(private val context: Context) {

    private val _state = MutableStateFlow(NarrationState.IDLE)
    val state: StateFlow<NarrationState> = _state.asStateFlow()

    private var currentPlayer: ExoPlayer? = null
    private var currentItem: String? = null

    private val audioManager: AudioManager =
        context.getSystemService(Context.AUDIO_SERVICE) as AudioManager

    private val audioAttributes = AudioAttributes.Builder()
        .setUsage(C.USAGE_MEDIA)
        .setContentType(C.AUDIO_CONTENT_TYPE_SPEECH)
        .build()

    /**
     * 播放指定文物的讲解。若与当前相同且未播完，从当前位置继续；否则替换。
     * §6.15：打开新文物自动停止旧讲解并从头播放新音频。
     */
    fun play(itemId: String, source: AudioSource, context: Context = this.context) {
        val player = ensurePlayer()
        if (currentItem == itemId && player.currentPosition < player.duration.coerceAtLeast(1) - 200) {
            // 同一文物且未结束：继续播放
            player.play()
            updateState { it.copy(itemId = itemId, isPlaying = true) }
            return
        }
        // 替换：从头播放新音频
        currentItem = itemId
        val uri = when (source) {
            is AudioSource.Asset -> source.toUri(context)
            is AudioSource.File -> source.toUri()
        }
        player.setMediaItem(MediaItem.fromUri(uri))
        player.prepare()
        player.play()
        requestAudioFocus()
        updateState {
            NarrationState(
                itemId = itemId, isPlaying = true, isReady = false,
                hasError = false, positionMs = 0L, durationMs = 0L
            )
        }
    }

    fun pause() {
        currentPlayer?.pause()
        updateState { it.copy(isPlaying = false) }
    }

    fun resume() {
        if (currentItem == null) return
        currentPlayer?.play()
        requestAudioFocus()
        updateState { it.copy(isPlaying = true) }
    }

    /**
     * 停止播放（§6.15）。
     * SCENE_CHANGED / ERROR / SWITCHED 时清空 MediaItem，释放资源引用；
     * CLOSED 时暂停（便于重新打开继续）。
     */
    fun stop(reason: StopReason) {
        val player = currentPlayer ?: return
        when (reason) {
            StopReason.SCENE_CHANGED, StopReason.ERROR, StopReason.SWITCHED -> {
                player.stop()
                player.clearMediaItems()
                currentItem = null
                abandonAudioFocus()
                _state.value = NarrationState.IDLE
            }
            StopReason.CLOSED -> {
                player.pause()
                updateState { it.copy(isPlaying = false) }
            }
            StopReason.TRANSIENT -> {
                // 焦点暂时丢失 / 耳机拔出：暂停（不停止，便于恢复）
                player.pause()
                updateState { it.copy(isPlaying = false) }
            }
        }
    }

    /** 释放 ExoPlayer（App 退出或不再需要音频时）。 */
    fun release() {
        unregisterBecomingNoisy()
        abandonAudioFocus()
        currentPlayer?.release()
        currentPlayer = null
        currentItem = null
        _state.value = NarrationState.IDLE
    }

    // ----------------------------------------------------- 内部

    private fun ensurePlayer(): ExoPlayer {
        currentPlayer?.let { return it }
        val player = ExoPlayer.Builder(context)
            .setAudioAttributes(audioAttributes, /*handleAudioFocus=*/false) // 自管焦点
            .setHandleAudioBecomingNoisy(true) // §6.15 耳机拔出暂停（ExoPlayer 内置）
            .build()
        player.addListener(object : Player.Listener {
            override fun onPlaybackStateChanged(playbackState: Int) {
                when (playbackState) {
                    Player.STATE_READY -> updateState { it.copy(isReady = true, hasError = false) }
                    Player.STATE_ENDED -> {
                        currentItem = null
                        _state.value = NarrationState.IDLE
                    }
                    Player.STATE_BUFFERING -> updateState { it.copy(isReady = false) }
                    Player.STATE_IDLE -> { /* 初始/stop 后 */ }
                }
            }

            override fun onPlayerErrorChanged(error: androidx.media3.common.PlaybackException?) {
                // Media3 1.4.1：错误通过 onPlayerErrorChanged 回调（非 STATE_ERROR）
                if (error != null) {
                    updateState { it.copy(hasError = true, isPlaying = false) }
                }
            }

            override fun onIsPlayingChanged(isPlaying: Boolean) {
                updateState { it.copy(isPlaying = isPlaying) }
            }

            override fun onPositionDiscontinuity(
                oldPosition: Player.PositionInfo,
                newPosition: Player.PositionInfo,
                reason: Int
            ) {
                updatePosition()
            }
        })
        currentPlayer = player
        registerBecomingNoisy()
        return player
    }

    private fun updateState(transform: (NarrationState) -> NarrationState) {
        _state.value = transform(_state.value)
    }

    private fun updatePosition() {
        val player = currentPlayer ?: return
        updateState {
            it.copy(
                positionMs = player.currentPosition.coerceAtLeast(0L),
                durationMs = player.duration.coerceAtLeast(0L)
            )
        }
    }

    /** 供 UI 定时轮询进度（Compose LaunchedEffect 每 500ms 调用）。 */
    fun pollPosition() {
        if (currentItem != null) updatePosition()
    }

    // ----------------------------------------------------- 音频焦点

    private var focusRequest: AudioFocusRequest? = null

    private fun requestAudioFocus() {
        // 用传统 AudioManager.requestAudioFocus（API 26+ 也可用 AudioFocusRequest，
        // 这里简化用 AudioManager，避免引入额外 API 版本判断）
        focusRequest?.let { audioManager.abandonAudioFocusRequestCompat(it) }
        val req = AudioFocusRequest()
        audioManager.requestAudioFocusCompat(req)
        focusRequest = req
    }

    private fun abandonAudioFocus() {
        focusRequest?.let { audioManager.abandonAudioFocusRequestCompat(it) }
        focusRequest = null
    }

    private fun AudioManager.requestAudioFocusCompat(req: AudioFocusRequest) {
        // API 26+ 用 AudioFocusRequest；这里统一用 OnAudioFocusChangeListener 兼容
        val listener = android.media.AudioManager.OnAudioFocusChangeListener { change ->
            when (change) {
                AudioManager.AUDIOFOCUS_LOSS_TRANSIENT,
                AudioManager.AUDIOFOCUS_LOSS_TRANSIENT_CAN_DUCK -> stop(StopReason.TRANSIENT)
                AudioManager.AUDIOFOCUS_LOSS -> stop(StopReason.CLOSED)
            }
        }
        req.listener = listener
        @Suppress("DEPRECATION")
        this.requestAudioFocus(
            listener,
            AudioManager.STREAM_MUSIC,
            AudioManager.AUDIOFOCUS_GAIN
        )
    }

    private fun AudioManager.abandonAudioFocusRequestCompat(req: AudioFocusRequest) {
        req.listener?.let {
            @Suppress("DEPRECATION")
            this.abandonAudioFocus(it)
        }
        req.listener = null
    }

    private class AudioFocusRequest {
        var listener: android.media.AudioManager.OnAudioFocusChangeListener? = null
    }

    // ----------------------------------------------------- 耳机拔出（兜底）

    private val becomingNoisyReceiver = object : BroadcastReceiver() {
        override fun onReceive(context: Context?, intent: Intent?) {
            if (intent?.action == AudioManager.ACTION_AUDIO_BECOMING_NOISY) {
                stop(StopReason.TRANSIENT)
            }
        }
    }

    private fun registerBecomingNoisy() {
        val filter = IntentFilter(AudioManager.ACTION_AUDIO_BECOMING_NOISY)
        context.registerReceiver(becomingNoisyReceiver, filter)
    }

    private fun unregisterBecomingNoisy() {
        runCatching { context.unregisterReceiver(becomingNoisyReceiver) }
    }
}
