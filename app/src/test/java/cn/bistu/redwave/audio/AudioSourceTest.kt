package cn.bistu.redwave.audio

import com.google.common.truth.Truth.assertThat
import org.junit.Test
import org.junit.runner.RunWith
import org.robolectric.RobolectricTestRunner
import org.robolectric.RuntimeEnvironment

/**
 * 音频源与状态契约测试（计划书 §6.15）。
 * ExoPlayer 实际播放需真机；此处测可独立验证的 URI 构造与状态语义。
 */
@RunWith(RobolectricTestRunner::class)
class AudioSourceTest {

    @Test
    fun assetSource_buildsAndroidAssetUri() {
        val src = AudioSource.Asset("scenes/scene_S1/audio/p_s1_radio_zh.mp3")
        val uri = src.toUri(RuntimeEnvironment.getApplication())
        // ExoPlayer 用 file:///android_asset/ 协议读 assets
        assertThat(uri.toString()).contains("android_asset")
        assertThat(uri.toString()).contains("p_s1_radio_zh.mp3")
    }

    @Test
    fun fileSource_buildsFileUri() {
        val src = AudioSource.File("/data/scenes/S1/audio/x.mp3")
        assertThat(src.toUri().toString()).isEqualTo("/data/scenes/S1/audio/x.mp3")
    }

    @Test
    fun narrationState_idleDefaults() {
        val idle = NarrationState.IDLE
        assertThat(idle.isPlaying).isFalse()
        assertThat(idle.itemId).isNull()
        assertThat(idle.positionMs).isEqualTo(0L)
    }

    @Test
    fun stopReason_semanticsDistinct() {
        // §6.15：各 StopReason 有不同语义，确保枚举完整
        val reasons = StopReason.values()
        assertThat(reasons).hasLength(5)
        assertThat(reasons).asList()
            .containsAtLeast(
                StopReason.CLOSED, StopReason.SWITCHED,
                StopReason.SCENE_CHANGED, StopReason.ERROR, StopReason.TRANSIENT
            )
    }

    @Test
    fun narrationController_initialStateIsIdle() {
        val ctrl = NarrationController(RuntimeEnvironment.getApplication())
        val state = ctrl.state.value
        assertThat(state.isPlaying).isFalse()
        assertThat(state.itemId).isNull()
        ctrl.release()
    }
}
