package cn.bistu.redwave.render.asset

import cn.bistu.redwave.data.Prop
import cn.bistu.redwave.data.SceneManifest
import com.google.android.filament.Engine
import com.google.android.filament.Scene
import com.google.android.filament.TransformManager
import com.google.android.filament.gltfio.FilamentAsset
import java.util.concurrent.atomic.AtomicLong

// 单场景 GLB 加载协调器（计划书 §6.11 加载管线、CODE-03）。
// 状态机：Idle -> beginLoading -> Loading -> Ready / Failed。
// 加载步骤：environment（致命）-> props（分批，P2 可降级）-> attach + transform。
// 场景 token（§6.14）：每次 beginLoading 递增，作废旧回调。
// 线程：必须在 Engine 线程调用。
class SceneAssetLoader(
    private val engine: Engine,
    private val assetStore: GltfAssetStore
) {
    private val transformManager: TransformManager = engine.transformManager

    enum class State { IDLE, LOADING, READY, FAILED }

    // §6.11 建议进度权重：配置 10% + 环境 40% + 文物 35% + 资源 15%
    enum class Phase(val progressWeight: Float) {
        CONFIG(0.10f), ENVIRONMENT(0.40f), PROPS(0.35f), RESOURCES(0.15f)
    }

    data class LoadResult(
        val state: State,
        val progress: Float,
        // P2 文物加载失败时记入；调用方可显示部分展品暂不可用（§6.18 PARTIAL_PROP_FAILED）
        val failedProps: List<String> = emptyList(),
        val errorMessage: String? = null
    )

    private val tokenCounter = AtomicLong(0L)
    private var activeToken = 0L

    private var state: State = State.IDLE
    private var sceneManifest: SceneManifest? = null
    private var scene: Scene? = null
    private var environmentRelativePath: String? = null
    private var propRelativePaths: List<Pair<String, String>> = emptyList()
    private var propsLoaded: Int = 0
    private var failedProps: MutableList<String> = mutableListOf()
    private var environmentLoaded: Boolean = false

    // 启动加载。token 递增作废旧加载。
    // assetBaseDir 来自 global_manifest.scene_manifest 所在目录，如 scenes/scene_S1
    fun beginLoading(
        manifest: SceneManifest,
        scene: Scene,
        assetBaseDir: String
    ): LoadResult {
        activeToken = tokenCounter.incrementAndGet()
        sceneManifest = manifest
        this.scene = scene
        failedProps.clear()
        propsLoaded = 0
        environmentLoaded = false
        state = State.LOADING

        val base = assetBaseDir.trimEnd('/')
        environmentRelativePath = "$base/${manifest.environmentGlb}"
        propRelativePaths = manifest.props.map { it.id to "$base/${it.glb}" }

        return currentResult(Phase.CONFIG.progressWeight)
    }

    // 每帧推进加载（由 SceneRenderer.onUpdateResources 调用）。
    fun update(): LoadResult {
        val manifest = sceneManifest ?: return LoadResult(State.IDLE, 0f)
        val targetScene = this.scene ?: return LoadResult(State.FAILED, 0f, errorMessage = "Scene 未提供")
        if (state == State.READY || state == State.FAILED) return currentResult(1f)

        // 1. 先加载环境（致命：失败则整场景失败）
        if (!environmentLoaded) {
            val envAsset = assetStore.loadAndAttach(
                key = "environment",
                propId = null,
                assetRelativePath = environmentRelativePath!!
            )
            if (envAsset == null) {
                state = State.FAILED
                return LoadResult(
                    State.FAILED,
                    Phase.ENVIRONMENT.progressWeight,
                    errorMessage = "environment GLB 加载失败: $environmentRelativePath"
                )
            }
            assetStore.attachToScene(envAsset, targetScene, propId = null)
            environmentLoaded = true
            return currentResult(Phase.ENVIRONMENT.progressWeight)
        }

        // 2. 分批加载 props（每帧加载一个，避免单帧卡顿）
        val propIndex = propsLoaded
        if (propIndex < propRelativePaths.size) {
            val (propId, glbPath) = propRelativePaths[propIndex]
            val propAsset = assetStore.loadAndAttach(propId, propId, glbPath)
            if (propAsset != null) {
                assetStore.attachToScene(propAsset, targetScene, propId = propId)
                val propConfig = manifest.props.firstOrNull { it.id == propId }
                if (propConfig != null) {
                    applyPropTransform(propAsset, propConfig)
                }
            } else {
                failedProps += propId
            }
            propsLoaded++
            val propsProgress = Phase.ENVIRONMENT.progressWeight +
                Phase.PROPS.progressWeight * (propsLoaded.toFloat() / propRelativePaths.size)
            return currentResult(propsProgress)
        }

        // 3. 资源上传进度
        val resProgress = assetStore.updateResourceLoading()
        if (resProgress >= 0.999f) {
            state = State.READY
            return currentResult(1f)
        }
        val combined = Phase.ENVIRONMENT.progressWeight + Phase.PROPS.progressWeight +
            Phase.RESOURCES.progressWeight * resProgress
        return currentResult(combined.coerceIn(0f, 0.99f))
    }

    // 当前 token（异步回调核对用）
    fun currentToken(): Long = activeToken

    // 配置 prop 世界 transform（§5.4 position/rotation/scale -> 4x4）
    private fun applyPropTransform(asset: FilamentAsset, prop: Prop) {
        val root = asset.root
        if (!transformManager.hasComponent(root)) {
            transformManager.create(root)
        }
        val instance = transformManager.getInstance(root)
        val matrix = TransformMath.composeTRS(prop.positionM, prop.rotationDeg, prop.scale)
        transformManager.setTransform(instance, matrix)
    }

    private fun currentResult(progress: Float): LoadResult {
        return LoadResult(
            state = state,
            progress = progress.coerceIn(0f, 1f),
            failedProps = failedProps.toList()
        )
    }

    // 重置为 Idle（切场景或退出时，配合 assetStore.destroyAll）
    fun reset() {
        activeToken = tokenCounter.incrementAndGet()
        state = State.IDLE
        sceneManifest = null
        scene = null
        environmentRelativePath = null
        propRelativePaths = emptyList()
        propsLoaded = 0
        environmentLoaded = false
        failedProps.clear()
    }
}
