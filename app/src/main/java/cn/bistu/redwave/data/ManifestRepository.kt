package cn.bistu.redwave.data

import cn.bistu.redwave.AppErrorCode

/**
 * 清单仓库（计划书 §6.3、§6.6）。
 *
 * 职责：
 * - 从 [AssetResourceRoot] 读取并解析三份 JSON；
 * - 运行 Schema + 跨文件校验（[ManifestValidator]）；
 * - 验证引用的资源文件存在（§5.6-4）；
 * - 失败一律返回 [ManifestRepositoryError]，不崩溃、不静默跳过。
 *
 * 线程：本类不持有锁，调用方应在非主线程调用（§6.5：IO 离开主线程）。
 *
 * @param root bundled assets 根（S1 位于此）。
 * @param strict Release 严格模式（§5.6-7）。
 */
class ManifestRepository(
    private val root: AssetResourceRoot,
    strict: Boolean = false
) {
    private val validator = ManifestValidator(strict = strict)

    /** 解析并校验后的完整场景包。 */
    data class SceneBundle(
        val indexItem: SceneIndexItem,
        val sceneManifest: SceneManifest,
        val contentManifest: ContentManifest,
        val resourceRootId: String,
        /** 白盒阶段软缺失的资产（音频/缩略图），Release 严格模式下这些会致命。 */
        val missingAssets: List<String> = emptyList()
    )

    /** 仓库错误，携带稳定错误码（§6.18）。 */
    data class ManifestRepositoryError(
        val code: AppErrorCode,
        val reasons: List<String>
    )

    /** 全局清单与场景索引的缓存，启动后只读。 */
    @Volatile
    private var cachedGlobal: GlobalManifest? = null

    /**
     * 加载全局清单。返回解析后的 [GlobalManifest] 或错误。
     * 计划书 §6.3：启动时读取 global_manifest.json 并校验 Schema。
     */
    fun loadGlobalManifest(): Result<GlobalManifest> {
        cachedGlobal?.let { return Result.success(it) }
        val text = root.readTextOrNull(GLOBAL_MANIFEST_PATH)
            ?: return failure("找不到 $GLOBAL_MANIFEST_PATH（根: ${root.id}）")
        return runCatching { ManifestJson.parseGlobalManifest(text) }
            .onSuccess {
                val issues = ValidationIssues()
                validator.validateGlobalManifest(it, issues)
                if (issues.hasIssues()) {
                    return failure(issues.snapshot())
                }
                cachedGlobal = it
            }
            .recoverCatching { ex ->
                throw ManifestLoadException(
                    AppErrorCode.MANIFEST_INVALID,
                    listOf("$GLOBAL_MANIFEST_PATH 解析失败: ${ex.message ?: ex::class.simpleName}")
                )
            }
    }

    /**
     * 根据 scene_id 加载完整场景包（scene.json + content.json + 跨文件校验 + 文件存在性）。
     */
    fun loadSceneBundle(sceneId: String): Result<SceneBundle> {
        val global = loadGlobalManifest().getOrElse { ex ->
            return Result.failure(ex)
        }
        val indexItem = global.scenes.firstOrNull { it.sceneId == sceneId }
            ?: return failure("scene_id '$sceneId' 不在全局索引中")

        // 读取 scene.json
        val sceneText = root.readTextOrNull(indexItem.sceneManifest)
            ?: return failure("找不到 scene.json: ${indexItem.sceneManifest}")
        val sceneManifest = runCatching { ManifestJson.parseSceneManifest(sceneText) }
            .getOrElse { return failure("${indexItem.sceneManifest} 解析失败: ${it.message}") }

        // 读取 content.json
        val contentText = root.readTextOrNull(indexItem.contentManifest)
            ?: return failure("找不到 content.json: ${indexItem.contentManifest}")
        val contentManifest = runCatching { ManifestJson.parseContentManifest(contentText) }
            .getOrElse { return failure("${indexItem.contentManifest} 解析失败: ${it.message}") }

        // 跨文件 + Schema 校验
        val result = validator.validateBundle(global, sceneManifest, contentManifest)
        if (result is ManifestValidationResult.Invalid) {
            return failure(result.reasons)
        }

        // 资源文件存在性（§5.6-4）
        // - GLB（环境 + 文物）：CODE-03 渲染必需，缺失即致命。
        // - 音频 / 缩略图：CODE-07 / CODE-10 接入真实资产前，白盒阶段为软检查
        //   （缺失记入 [SceneBundle.missingAssets]，不阻断加载；Release 严格模式仍致命）。
        val missing = mutableListOf<String>()
        val sceneDir = parentDir(indexItem.sceneManifest)
        if (!root.exists("${sceneDir}/${sceneManifest.environmentGlb}")) {
            missing += "environment_glb: ${sceneManifest.environmentGlb}"
        }
        sceneManifest.props.forEach { p ->
            if (!root.exists("${sceneDir}/${p.glb}")) {
                missing += "prop '${p.id}' glb: ${p.glb}"
            }
        }
        val missingSoft = mutableListOf<String>()
        contentManifest.items.forEach { item ->
            if (!root.exists("${sceneDir}/${item.audio}")) {
                missingSoft += "content '${item.id}' audio: ${item.audio}"
            }
        }
        if (!root.exists(indexItem.thumbnail)) {
            missingSoft += "thumbnail: ${indexItem.thumbnail}"
        }
        // GLB 缺失致命（CODE-03 无法渲染）。
        if (missing.isNotEmpty()) {
            return failure(missing)
        }
        // Release 严格模式：音频/缩略图缺失也致命（§5.6-7）。
        if (validator.isStrictRelease() && missingSoft.isNotEmpty()) {
            return failure(missingSoft)
        }

        return Result.success(
            SceneBundle(indexItem, sceneManifest, contentManifest, root.id, missingSoft)
        )
    }

    /**
     * 构建入口解析器（计划书 §6.8：启动时建立三张不可变索引）。
     */
    fun buildEntryResolver(): Result<EntryResolver> {
        val global = loadGlobalManifest().getOrElse { return Result.failure(it) }
        return EntryResolver.fromManifest(global)
    }

    /** 仅供测试/诊断：清空全局缓存。 */
    internal fun clearCache() {
        cachedGlobal = null
    }

    // ---------------------------------------------------------------- helpers

    private fun failure(reason: String): Result<Nothing> =
        Result.failure(ManifestLoadException(AppErrorCode.MANIFEST_INVALID, listOf(reason)))

    private fun failure(reasons: List<String>): Result<Nothing> =
        Result.failure(ManifestLoadException(AppErrorCode.MANIFEST_INVALID, reasons))

    private fun parentDir(path: String): String = parentDirOf(path)

    companion object {
        /** 全局清单在资源根的固定路径（计划书 §5.1）。 */
        const val GLOBAL_MANIFEST_PATH = "global_manifest.json"

        /** 提取相对路径的父目录（"scenes/scene_S1/scene.json" -> "scenes/scene_S1"）。 */
        fun parentDirOf(path: String): String {
            val normalized = path.replace('\\', '/')
            val idx = normalized.lastIndexOf('/')
            return if (idx >= 0) normalized.substring(0, idx) else ""
        }
    }
}
