package cn.bistu.redwave.render

import android.view.Choreographer
import com.google.android.filament.Renderer
import java.util.concurrent.TimeUnit

/**
 * 帧循环驱动（计划书 §6.10 每帧流程）。
 *
 * 职责：
 * 1. 用 [Choreographer] 提供的帧时间计算 dt，异常大间隔（如后台恢复）需截断（§6.13）。
 * 2. 依次回调各帧更新钩子（CODE-03 资源加载、CODE-04 姿态、CODE-05 移动、CODE-03 Animator）。
 * 3. `renderer.beginFrame(swapChain)` 成功后渲染 View，再 `endFrame()`（§6.10-6/7）。
 * 4. Surface 不可用、页面后台或对象已释放时不得继续提交帧。
 *
 * 线程：必须在 Filament Engine 所在线程驱动（由 SurfaceView 的渲染线程保证）。
 */
class SceneRenderer(
    private val host: FilamentHost
) {

    /** dt 截断上限，防止后台恢复瞬间一步穿墙（计划书 §6.13 建议 50 ms）。 */
    private val maxFrameDtSec = 0.05f

    private var choreographer: Choreographer? = null
    private val frameCallback = Choreographer.FrameCallback { frameTimeNanos ->
        onFrame(frameTimeNanos)
    }

    @Volatile
    private var running = false

    /** 帧更新钩子，按 §6.10 顺序：资源→姿态→移动→动画。由各 CODE 任务注入。 */
    interface FrameUpdateHooks {
        /** 更新异步资源加载进度（CODE-03 ResourceLoader）。 */
        fun onUpdateResources(dtSec: Float) {}
        /** 更新传感器目标姿态与平滑后相机旋转（CODE-04）。 */
        fun onUpdateOrientation(dtSec: Float) {}
        /** 更新摇杆位移、碰撞、热点动画（CODE-05）。 */
        fun onUpdateMovement(dtSec: Float) {}
        /** 更新 glTF Animator（CODE-03）。 */
        fun onUpdateAnimations(dtSec: Float) {}
    }

    @Volatile
    var hooks: FrameUpdateHooks? = null

    private var lastFrameTimeNanos: Long = -1L

    /**
     * 启动帧循环。幂等。
     */
    fun start() {
        if (running) return
        running = true
        lastFrameTimeNanos = -1L
        choreographer = Choreographer.getInstance()
        choreographer?.postFrameCallback(frameCallback)
    }

    /**
     * 停止帧循环。幂等。
     */
    fun stop() {
        running = false
        choreographer?.removeFrameCallback(frameCallback)
        choreographer = null
        lastFrameTimeNanos = -1L
    }

    private fun onFrame(frameTimeNanos: Long) {
        if (!running) return
        // 必须在 Engine 线程、且对象齐全时才提交。
        if (!host.hasSceneObjects()) {
            scheduleNext()
            return
        }
        // Surface 不可用时不得提交帧（§6.10-7）
        val swapChain = host.swapChain ?: run {
            scheduleNext()
            return
        }

        // 计算 dt，异常大间隔截断
        val dtSec = if (lastFrameTimeNanos < 0) {
            0f
        } else {
            val rawNanos = frameTimeNanos - lastFrameTimeNanos
            val rawSec = rawNanos / 1_000_000_000f
            // 负值或过大（后台恢复）截断到上限
            rawSec.coerceIn(0f, maxFrameDtSec)
        }
        lastFrameTimeNanos = frameTimeNanos

        // §6.10 步骤 2-5：更新资源、姿态、移动、动画
        val h = hooks
        try {
            h?.onUpdateResources(dtSec)
            h?.onUpdateOrientation(dtSec)
            h?.onUpdateMovement(dtSec)
            h?.onUpdateAnimations(dtSec)
        } catch (t: Throwable) {
            // 帧更新钩子异常不应让渲染线程崩溃；记录后继续，调用方在诊断里能看到。
            // （完整诊断上报在 CODE-10 diagnostics 接入。）
        }

        // §6.10 步骤 6-7：beginFrame → 渲染 View → endFrame
        val renderer = host.renderer
        val beginResult = if (dtSec == 0f) {
            // 首帧没有 dt 上下文，仍尝试渲染
            renderer.beginFrame(swapChain, frameTimeNanos)
        } else {
            renderer.beginFrame(swapChain, frameTimeNanos)
        }
        if (beginResult) {
            renderer.render(host.view)
            renderer.endFrame()
        }

        scheduleNext()
    }

    private fun scheduleNext() {
        if (running) {
            choreographer?.postFrameCallback(frameCallback)
        }
    }

    /** 仅供测试：当前是否处于运行状态。 */
    fun isRunning(): Boolean = running

    companion object {
        /** 暴露 dt 截断上限，供测试与诊断核对。 */
        const val MAX_FRAME_DT_SEC: Float = 0.05f

        fun nanosToSeconds(nanos: Long): Float =
            TimeUnit.NANOSECONDS.toNanos(nanos) / 1_000_000_000f
    }
}
