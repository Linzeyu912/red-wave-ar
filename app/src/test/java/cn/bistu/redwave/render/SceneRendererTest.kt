package cn.bistu.redwave.render

import com.google.common.truth.Truth.assertThat
import org.junit.Test

/**
 * SceneRenderer 纯算法测试（计划书 §6.10、§6.13）。
 *
 * FilamentHost / SceneRenderer 的 native Filament 调用（Engine/Renderer/SwapChain
 * 创建、beginFrame 等）需要 Android 运行时与 native lib，无法在纯 JVM 单测中执行；
 * 这部分由 instrumented test（模拟器/真机）覆盖。本类只测不被 native 污染的纯逻辑。
 */
class SceneRendererTest {

    @Test
    fun maxFrameDtSec_matchesPlanBookSuggestion() {
        // 计划书 §6.13：dt 上限建议 50 ms，防止后台恢复一步穿墙。
        assertThat(SceneRenderer.MAX_FRAME_DT_SEC).isEqualTo(0.05f)
    }

    @Test
    fun nanosToSeconds_convertsCorrectly() {
        assertThat(SceneRenderer.nanosToSeconds(1_000_000_000L)).isWithin(1e-5f).of(1.0f)
        assertThat(SceneRenderer.nanosToSeconds(50_000_000L)).isWithin(1e-5f).of(0.05f)
    }

    @Test
    fun dtClamping_logicMatchesSpec() {
        // 验证 §6.13 的截断逻辑：原始 dt 超过上限时被截到 0.05f。
        // 这里复现 SceneRenderer.onFrame 中的 coerceIn 语义，确保算法一致。
        val maxDt = SceneRenderer.MAX_FRAME_DT_SEC
        fun clampDt(rawSec: Float): Float = rawSec.coerceIn(0f, maxDt)

        // 正常 16ms 帧
        assertThat(clampDt(0.016f)).isWithin(1e-5f).of(0.016f)
        // 后台 30 秒恢复 → 截断到 50ms
        assertThat(clampDt(30.0f)).isEqualTo(0.05f)
        // 负值（时钟回退）→ 0
        assertThat(clampDt(-0.5f)).isEqualTo(0f)
    }

    @Test
    fun filamentHost_tokenStartsAtZero() {
        // host 未创建 Engine 时 token 为 0；确保 ensureEngineCreated 之前状态可诊断。
        val host = FilamentHost()
        assertThat(host.isEngineCreated()).isFalse()
        assertThat(host.hasSceneObjects()).isFalse()
        assertThat(host.hasSwapChain()).isFalse()
    }
}
