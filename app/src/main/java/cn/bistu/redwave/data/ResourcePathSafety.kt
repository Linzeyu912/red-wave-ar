package cn.bistu.redwave.data

import java.io.File

/**
 * 资源路径安全工具（计划书 §5.6 第 4 条）。
 *
 * 所有清单里引用的相对路径（scene_manifest、content_manifest、environment_glb、
 * props[].glb、content[].audio、thumbnail）必须满足：
 *
 * 1. 非空；
 * 2. 是相对路径（拒绝绝对路径 / UNC 路径 / 盘符）；
 * 3. 不包含 `..` 段（拒绝路径穿越）；
 * 4. 解析后仍落在允许的资源根目录内（双保险）。
 *
 * 这些检查与具体存储（assets / 已安装场景包）解耦：路径先做纯字符串与规范化校验，
 * 由 [AssetResourceRoot] 在运行时判断文件是否真实存在。
 */
object ResourcePathSafety {

    private val forbiddenSegments = setOf("..")

    /**
     * 纯字符串级路径校验。不访问文件系统，可离线测试。
     * @return 通过返回 null；失败返回面向诊断的原因。
     */
    fun stringCheck(relativePath: String, field: String): String? {
        if (relativePath.isBlank()) {
            return "$field: 路径为空"
        }
        // 任何路径分隔符统一用 / 切分后再判断，兼容 Windows 的 \。
        val normalized = relativePath.replace('\\', '/')
        // UNC（\\host 或 //host）必须在“绝对路径”之前判断，避免被 / 开头吞掉。
        if (normalized.startsWith("//") || normalized.startsWith("\\\\")) {
            return "$field: 不允许 UNC 路径 '$relativePath'"
        }
        if (normalized.startsWith('/')) {
            return "$field: 不允许绝对路径 '$relativePath'"
        }
        // Windows 盘符（如 C:）。
        if (Regex("^[a-zA-Z]:").containsMatchIn(normalized)) {
            return "$field: 不允许盘符路径 '$relativePath'"
        }
        val segments = normalized.split('/').filter { it.isNotEmpty() }
        if (segments.any { it in forbiddenSegments }) {
            return "$field: 不允许路径穿越 '..' '$relativePath'"
        }
        // 拒绝空段（连续斜杠）与可疑控制字符。
        if (normalized.contains("//")) {
            return "$field: 不允许连续斜杠 '$relativePath'"
        }
        if (relativePath.any { it.code < 0x20 }) {
            return "$field: 路径含控制字符"
        }
        return null
    }

    /**
     * 文件系统级校验：把 [relativePath] 解析到 [root] 后，确认仍在 root 子树内。
     * 这是对 [stringCheck] 的第二道保险，防止符号链接或规范化把路径带出根目录。
     *
     * @return true 表示路径安全且最终落在 root 内；false 表示越界。
     */
    fun resolvesWithin(root: File, relativePath: String): Boolean {
        val cleaned = relativePath.replace('\\', '/').trimStart('/')
        val resolved = File(root, cleaned).canonicalPath
        val rootCanonical = root.canonicalPath
        return resolved == rootCanonical || resolved.startsWith(rootCanonical + File.separator)
    }
}
