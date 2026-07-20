package cn.bistu.redwave.render

import android.view.Surface
import com.google.android.filament.Camera
import com.google.android.filament.Engine
import com.google.android.filament.Renderer
import com.google.android.filament.Scene
import com.google.android.filament.SwapChain
import com.google.android.filament.View
import java.util.concurrent.atomic.AtomicLong

/**
 * Filament 核心对象的所有者（计划书 §6.6、§6.10）。
 *
 * 创建与销毁顺序固定（§6.10 所有权表）：
 *
 * 创建：Engine → Renderer → Scene → View → Camera(+entity) → SwapChain
 * 销毁：SwapChain → 解绑 View 的 Scene/Camera → 销毁 Camera entity →
 *       销毁 View → 销毁 Scene → 销毁 Renderer → 销毁 Engine
 *
 * 线程模型：Filament 要求 Engine 在创建它的线程上使用。本类不做线程调度，
 * 由 [SceneRenderer]/[FilamentSurfaceView] 保证所有调用落在同一渲染线程。
 *
 * 边界（计划书 §1.2）：本类只服务“纯虚拟展馆”，不接触 ARCore Pose / 现实相机帧。
 */
class FilamentHost {

    /** 当前是否已创建 Engine（进入第一个 VR 页面前懒加载）。 */
    @Volatile
    private var engineRef: Engine? = null

    private var rendererRef: Renderer? = null
    private var sceneRef: Scene? = null
    private var viewRef: View? = null
    // Filament 1.56.0 中 Entity 是 typealias Int；按 Int 持有，0 表示未分配。
    private var cameraEntityRef: Int = 0
    private var cameraRef: Camera? = null
    private var swapChainRef: SwapChain? = null

    /**
     * 当前 SwapChain 配置 flags（Filament 1.56.0 无 CONFIG 常量，0 = 默认不透明）。
     * 如需 sRGB / 受保护内容，按 Engine 特性查询后设置对应位。
     */
    private var swapChainConfig: Long = 0L

    /** 用于诊断的唯一 token，每次创建新 Engine 递增，便于回调核对场景归属。 */
    private val engineTokenCounter = AtomicLong(0L)
    private var currentEngineToken: Long = 0L

    /**
     * 创建 Engine 与 Renderer（§6.10：Engine 懒加载，Renderer 在 Engine 创建后）。
     * 幂等：重复调用不会重复创建。
     */
    fun ensureEngineCreated(): Engine {
        engineRef?.let { return it }
        val engine = Engine.create()
        engineRef = engine
        currentEngineToken = engineTokenCounter.incrementAndGet()
        // Renderer 在 Engine 创建后立即创建。
        rendererRef = engine.createRenderer()
        return engine
    }

    /** 创建场景级对象：Scene、View、Camera。切场景时先调 [destroySceneObjects]。 */
    fun createSceneObjects() {
        val engine = ensureEngineCreated()
        check(sceneRef == null) { "Scene 对象已存在，请先销毁再创建" }
        val scene = engine.createScene()
        sceneRef = scene
        val view = engine.createView()
        viewRef = view
        view.scene = scene

        // Camera + entity（View 建立时创建）
        cameraEntityRef = engine.entityManager.create()
        val camera = engine.createCamera(cameraEntityRef)
        cameraRef = camera
        view.camera = camera
    }

    /**
     * Surface available 时创建 SwapChain（§6.10）。
     * 幂等：已存在则先销毁旧的再创建，保证与当前 Surface 绑定。
     */
    fun onSurfaceAvailable(surface: Surface) {
        val engine = ensureEngineCreated()
        swapChainRef?.let {
            engine.destroySwapChain(it)
            swapChainRef = null
        }
        swapChainRef = engine.createSwapChain(surface, swapChainConfig)
    }

    /**
     * Surface destroyed 时立即销毁 SwapChain（§6.10）。
     */
    fun onSurfaceDestroyed() {
        val engine = engineRef ?: return
        swapChainRef?.let {
            engine.destroySwapChain(it)
            swapChainRef = null
        }
    }

    /**
     * 销毁场景级对象（Scene/View/Camera），保留 Engine/Renderer 与 SwapChain。
     * 用于切场景时按 §6.21 安全释放顺序的前置步骤。
     */
    fun destroySceneObjects() {
        val engine = engineRef ?: return
        viewRef?.let { view ->
            // 先解除 Scene/Camera 绑定再销毁（§6.10）
            view.scene = null
            view.camera = null
        }
        cameraRef?.let { engine.destroyCameraComponent(cameraEntityRef) }
        cameraRef = null
        if (cameraEntityRef != 0) {
            engine.entityManager.destroy(cameraEntityRef)
            cameraEntityRef = 0
        }
        viewRef?.let { engine.destroyView(it) }
        viewRef = null
        sceneRef?.let { engine.destroyScene(it) }
        sceneRef = null
    }

    /**
     * 完整销毁：场景对象 + SwapChain + Renderer + Engine。
     * 用于 App 结束或明确释放 Host（§6.10：Engine 最后销毁）。
     */
    fun destroyAll() {
        destroySceneObjects()
        onSurfaceDestroyed()
        val engine = engineRef ?: return
        rendererRef?.let { engine.destroyRenderer(it) }
        rendererRef = null
        // Renderer 必须在 Engine 前销毁（§6.10）
        engine.destroy()
        engineRef = null
    }

    // ----------------------------------------------------------------- accessors

    /** 当前 Engine；若未创建抛异常。 */
    val engine: Engine get() = engineRef ?: error("Engine 未创建，请先 ensureEngineCreated()")

    val renderer: Renderer get() = rendererRef ?: error("Renderer 未创建")

    val scene: Scene get() = sceneRef ?: error("Scene 未创建，请先 createSceneObjects()")

    val view: View get() = viewRef ?: error("View 未创建，请先 createSceneObjects()")

    val camera: Camera get() = cameraRef ?: error("Camera 未创建")

    val swapChain: SwapChain? get() = swapChainRef

    val engineToken: Long get() = currentEngineToken

    fun isEngineCreated(): Boolean = engineRef != null

    fun hasSceneObjects(): Boolean = sceneRef != null

    fun hasSwapChain(): Boolean = swapChainRef != null
}
