package cn.bistu.redwave.data

import android.content.Context
import android.content.res.AssetManager
import java.io.File

/**
 * 基于 Android [AssetManager] 的资源根（计划书 §5.1：S1 位于 APK assets）。
 *
 * assets 内的文件不可通过 java.io.File 直接访问，需用 AssetManager.open()。
 * 路径安全检查（§5.6-4）仍通过 [ResourcePathSafety.stringCheck] 做字符串级校验，
 * 存在性通过 [AssetManager.list] 递归判定。
 */
class AndroidAssetResourceRoot(
    private val assetManager: AssetManager
) : AssetResourceRoot {

    override val id: String get() = "assets"

    override fun readTextOrNull(relativePath: String): String? {
        if (ResourcePathSafety.stringCheck(relativePath, "asset") != null) return null
        return runCatching {
            val cleaned = relativePath.replace('\\', '/').trimStart('/')
            assetManager.open(cleaned).bufferedReader().use { it.readText() }
        }.getOrNull()
    }

    override fun exists(relativePath: String): Boolean {
        if (ResourcePathSafety.stringCheck(relativePath, "asset") != null) return false
        return runCatching {
            val cleaned = relativePath.replace('\\', '/').trimStart('/')
            // assets 无直接 exists，用 list 判断。list 返回该路径下的文件名数组。
            val segments = cleaned.split('/').filter { it.isNotEmpty() }
            if (segments.isEmpty()) return false
            val fileName = segments.last()
            val dirPath = segments.dropLast(1).joinToString("/")
            val listing = if (dirPath.isEmpty()) {
                assetManager.list("") ?: emptyArray()
            } else {
                assetManager.list(dirPath) ?: emptyArray()
            }
            // assets.list 只列直接子项；需要递归进入子目录。
            assetExistsRecursive(segments, fileName, "")
        }.getOrDefault(false)
    }

    /**
     * 递归查找：assets.list 只返回直接子项，子目录需要递归进入。
     */
    private fun assetExistsRecursive(
        segments: List<String>,
        fileName: String,
        accumulated: String
    ): Boolean {
        if (segments.isEmpty()) return false
        val target = segments.first()
        val rest = segments.dropLast(1)
        val currentDir = accumulated
        val listing = assetManager.list(currentDir) ?: return false
        if (segments.size == 1) {
            return listing.any { it == target }
        }
        // 多层：进入子目录继续
        val subDir = if (currentDir.isEmpty()) segments.first() else "$currentDir/${segments.first()}"
        val remaining = segments.drop(1)
        val subListing = assetManager.list(subDir) ?: return false
        return assetExistsRecursive(remaining, remaining.last(), subDir)
    }

    override fun displayPath(relativePath: String): String =
        "assets://${relativePath.replace('\\', '/').trimStart('/')}"

    companion object {
        fun fromContext(context: Context): AndroidAssetResourceRoot =
            AndroidAssetResourceRoot(context.assets)
    }
}
