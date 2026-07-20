package cn.bistu.redwave.render.asset

import android.content.Context
import android.content.res.AssetManager
import com.google.android.filament.Engine
import com.google.android.filament.Entity
import com.google.android.filament.EntityManager
import com.google.android.filament.Scene
import com.google.android.filament.TransformManager
import com.google.android.filament.gltfio.AssetLoader
import com.google.android.filament.gltfio.FilamentAsset
import com.google.android.filament.gltfio.ResourceLoader
import com.google.android.filament.gltfio.UbershaderProvider
import java.nio.ByteBuffer
import java.nio.ByteOrder

/**
 * glTF / GLB 资产加载与释放（计划书 §6.6 render.asset、§6.10、§6.11、§6.21）。
 *
 * 职责：
 * - 持有 [AssetLoader]、[ResourceLoader]、[UbershaderProvider]，生命周期由本类管理；
 * - 从 assets 读取 GLB 字节并创建 [FilamentAsset]；
 * - 异步上传资源（纹理/材质），轮询进度；
 * - 把 asset 的 root entity 加进 Scene，并建立 entity → propId 映射（CODE-06 拾取用）；
 * - 退出/切场景时按 §6.21 顺序显式释放，不依赖 GC。
 *
 * 边界（计划书 §1.2）：只加载纯虚拟展馆的 GLB，不接触 ARCore。
 *
 * 线程：所有 Filament 调用必须落在 Engine 线程（由 [FilamentSurfaceView.postToRenderThread] 保证）。
 *
 * @param engine   FilamentHost.engine（同一渲染线程）
 * @param assetManager Android AssetManager（从 assets 读 GLB 字节）
 */
class GltfAssetStore(
    private val engine: Engine,
    private val assetManager: AssetManager
) {
    private val materialProvider = UbershaderProvider(engine)
    private val assetLoader = AssetLoader(engine, materialProvider, EntityManager.get())
    private val resourceLoader = ResourceLoader(engine, /*normalizeSkinningWeights=*/true)

    /** 单个已加载 asset 的状态。 */
    data class LoadedAsset(
        val key: String,
        val propId: String?,
        val asset: FilamentAsset,
        /** root entity，已加进 Scene；null 表示尚未 attach。 */
        var rootEntity: Int = 0,
        var attachedToScene: Boolean = false
    )

    /** key → 已加载资产。环境用 "environment" 键，文物用 propId。 */
    private val loaded = LinkedHashMap<String, LoadedAsset>()

    /** entity → propId 映射（CODE-06 拾取查表）。环境实体的 propId 为 null，不进入交互映射。 */
    private val entityToPropId = HashMap<Int, String>()

    /**
     * 异步加载并 attach 一个 GLB。
     *
     * @param key 本类内部标识（"environment" 或 propId）
     * @param propId 文物 ID；环境传 null（不参与拾取映射）
     * @param assetRelativePath assets 内的相对路径（如 "scenes/scene_S1/props/radio.glb"）
     * @return 加载的 asset；加载失败返回 null（调用方按 §6.11 决定致命或降级）
     */
    fun loadAndAttach(
        key: String,
        propId: String?,
        assetRelativePath: String
    ): FilamentAsset? {
        val bytes = readAssetBytes(assetRelativePath) ?: return null
        val buffer = ByteBuffer.allocateDirect(bytes.size).order(ByteOrder.nativeOrder())
        buffer.put(bytes)
        buffer.flip()

        val asset = assetLoader.createAsset(buffer) ?: return null
        // 对于单文件 .glb，资源内嵌；asyncBeginLoad 会处理内部 buffer。
        // 若 GLB 引用外部资源，调用方需先 addResourceData；白盒阶段无外部引用。
        resourceLoader.asyncBeginLoad(asset)

        val loadedAsset = LoadedAsset(key, propId, asset)
        loaded[key] = loadedAsset
        return asset
    }

    /**
     * 把已加载 asset 的资源加载推进一帧，并返回当前进度（0..1）。
     * 由 SceneRenderer.onUpdateResources 每帧调用（§6.10 步骤 2）。
     */
    fun updateResourceLoading(): Float {
        if (loaded.isEmpty()) return 1f
        resourceLoader.asyncUpdateLoad()
        var sum = 0f
        var count = 0
        loaded.values.forEach { la ->
            sum += resourceLoader.asyncGetLoadProgress()
            count++
        }
        // 进度取所有 asset 的均值；单个 asset 的 progress 由 ResourceLoader 全局维护。
        // 简化：用最后查询的进度（1.56.0 的 progress 是 ResourceLoader 全局状态）。
        return if (count == 0) 1f else resourceLoader.asyncGetLoadProgress()
    }

    /**
     * 把加载完成的 asset attach 到 Scene。
     * 仅在资源基本就绪（progress 接近 1）时调用，避免显示未完成材质（§6.11）。
     * 建立 entity → propId 映射。
     */
    fun attachToScene(asset: FilamentAsset, scene: Scene, propId: String?) {
        val root = asset.root
        scene.addEntity(root)
        // 建立 entity → propId 映射：该 asset 的所有 renderable entity 都映射到同一 propId。
        // 环境实体 propId 为 null，不进入交互映射（CODE-06 不拾取环境）。
        if (propId != null) {
            val renderables = asset.renderableEntities
            renderables.forEach { entity ->
                entityToPropId[entity] = propId
            }
            // root 也映射，便于点击 root 命中
            entityToPropId[root] = propId
        }
        // 标记已 attach
        loaded.values.firstOrNull { it.asset === asset }?.let {
            it.rootEntity = root
            it.attachedToScene = true
        }
        // 释放源数据，降低内存（纹理已上传到 GPU 后可丢弃 CPU 端原始数据）
        asset.releaseSourceData()
    }

    /** 查询 entity 对应的 propId（CODE-06 拾取用）；环境/未知实体返回 null。 */
    fun propIdForEntity(entity: Int): String? = entityToPropId[entity]

    /** 已加载 asset 数量（诊断用）。 */
    fun loadedCount(): Int = loaded.size

    /**
     * 销毁单个 asset（CODE-06 切场景或 P2 文物降级）。
     * 先从 Scene 移除 entity，再销毁 asset，清理映射。
     */
    fun destroyAsset(key: String, scene: Scene?) {
        val la = loaded.remove(key) ?: return
        if (la.attachedToScene && scene != null && la.rootEntity != 0) {
            runCatching { scene.removeEntity(la.rootEntity) }
        }
        // 清理该 asset 的 entity 映射
        val entities = la.asset.renderableEntities
        entities.forEach { entityToPropId.remove(it) }
        if (la.rootEntity != 0) entityToPropId.remove(la.rootEntity)
        assetLoader.destroyAsset(la.asset)
    }

    /**
     * 销毁所有 asset（§6.21 切场景/退出 VR）。
     * 必须在 Scene 销毁前调用（先移除 entity 再销毁 asset）。
     */
    fun destroyAll(scene: Scene?) {
        // 倒序销毁（后加载的先释放），保持与加载相反的顺序
        val keys = loaded.keys.toList().reversed()
        for (key in keys) {
            destroyAsset(key, scene)
        }
        entityToPropId.clear()
        check(loaded.isEmpty()) { "销毁后仍有残留 asset" }
    }

    /**
     * 销毁 store 自身（§6.10：所有 asset 已释放后销毁 AssetLoader/ResourceLoader）。
     * 必须在 destroyAll 之后、Engine 销毁之前调用。
     */
    fun destroy() {
        if (loaded.isNotEmpty()) {
            // 防御性：未显式 destroyAll 的残留会导致泄漏，记录但不崩溃。
            loaded.clear()
            entityToPropId.clear()
        }
        resourceLoader.destroy()
        assetLoader.destroy()
        materialProvider.destroy()
    }

    private fun readAssetBytes(assetRelativePath: String): ByteArray? {
        val cleaned = assetRelativePath.replace('\\', '/').trimStart('/')
        return runCatching {
            assetManager.open(cleaned).use { it.readBytes() }
        }.getOrNull()
    }

    companion object {
        /** 诊断：当前 entity→propId 映射大小（仅供测试与日志）。 */
        fun mappingSize(store: GltfAssetStore): Int = store.entityToPropId.size
    }
}
