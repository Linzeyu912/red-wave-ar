package cn.bistu.redwave.render

import android.content.Context
import android.os.Handler
import android.os.HandlerThread
import android.view.SurfaceHolder
import android.view.SurfaceView

/**
 * Filament 渲染表面（计划书 §6.5、§6.10）。
 *
 * 职责：
 * - 持有一个专用渲染线程（[HandlerThread]），所有 Filament Engine 调用落在线程；
 * - 在 [SurfaceHolder.Callback] 中把 Surface 生命周期转给 [FilamentHost]：
 *   surfaceCreated → onSurfaceAvailable；surfaceDestroyed → onSurfaceDestroyed；
 * - 暂停/恢复时启动/停止 [SceneRenderer] 帧循环（§6.10：后台不提交帧）。
 *
 * 边界：本 View 只渲染纯虚拟场景，从不显示现实相机画面（计划书 §1.2）。
 *
 * 生命周期约定（§6.21）：
 * - 进入 VR 页：attach → surfaceCreated → resume
 * - 退出 VR 页：pause → surfaceDestroyed → detach → destroyAll（由 SceneCoordinator 调用）
 */
class FilamentSurfaceView(
    context: Context,
    val host: FilamentHost = FilamentHost(),
    private val renderer: SceneRenderer = SceneRenderer(host)
) : SurfaceView(context), SurfaceHolder.Callback {

    private val renderThread = HandlerThread("FilamentRenderThread").apply { start() }
    private val renderHandler = Handler(renderThread.looper)

    @Volatile
    private var surfaceReady = false
    @Volatile
    private var resumed = false

    init {
        holder.addCallback(this)
    }

    val sceneRenderer: SceneRenderer get() = renderer

    /**
     * 页面 resume：在渲染线程创建场景对象并启动帧循环。
     * sceneObjectsReady 由调用方确认（CODE-03 加载完 GLB 后再真正可见）。
     */
    fun onResumeRendering(createSceneObjects: Boolean) {
        renderHandler.post {
            if (createSceneObjects && !host.hasSceneObjects()) {
                host.createSceneObjects()
            }
            resumed = true
            if (surfaceReady) {
                renderer.start()
            }
        }
    }

    /**
     * 页面 pause：停止帧循环（§6.10：后台不提交帧）。保留对象，便于快速恢复。
     */
    fun onPauseRendering() {
        renderHandler.post {
            resumed = false
            renderer.stop()
        }
    }

    /**
     * 完整销毁（退出 VR 或切场景，§6.21）。
     * 必须在渲染线程执行，保证销毁顺序。
     */
    fun destroyRendering() {
        renderHandler.post {
            renderer.stop()
            host.destroyAll()
        }
    }

    // ----------------------------------------------------- SurfaceHolder.Callback

    override fun surfaceCreated(holder: SurfaceHolder) {
        // 在渲染线程创建 SwapChain
        renderHandler.post {
            host.onSurfaceAvailable(holder.surface)
            surfaceReady = true
            if (resumed) {
                renderer.start()
            }
        }
    }

    override fun surfaceChanged(holder: SurfaceHolder, format: Int, width: Int, height: Int) {
        // 视口尺寸变化在帧循环里由调用方按 width/height 设置 View.viewport；
        // CODE-02 不在此处理，CODE-03 接入相机投影时一并更新。
    }

    override fun surfaceDestroyed(holder: SurfaceHolder) {
        // §6.10：Surface destroyed 时立即销毁 SwapChain
        renderHandler.post {
            renderer.stop()
            surfaceReady = false
            host.onSurfaceDestroyed()
        }
    }

    /**
     * 把任务投递到 Filament 渲染线程执行。
     *
     * Filament 要求所有 Engine/Scene/View/Camera 调用落在创建 Engine 的线程（§6.10）。
     * 调用方必须通过本方法把配置、加载、姿态更新等操作切到渲染线程，
     * 不允许直接在主线程操作 Filament 对象。
     */
    fun postToRenderThread(action: () -> Unit) {
        renderHandler.post(action)
    }

    /**
     * 退出时清理渲染线程。
     */
    fun shutdown() {
        destroyRendering()
        renderThread.quitSafely()
    }
}
