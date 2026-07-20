package cn.bistu.redwave.data

import java.io.File

/**
 * 资源根目录抽象（计划书 §6.3、§6.19）。
 *
 * 资源可能位于：
 * - APK assets（bundled 场景，S1 默认位置）；
 * - 已安装场景包目录（P1 下载场景）。
 *
 * 本接口把“路径解析 + 文件存在性 + 读取文本”统一抽象，让 ManifestRepository
 * 不关心具体存储后端，便于单测注入内存或临时目录实现。
 *
 * 安全约束（§5.6-4）：所有相对路径解析后必须落在根目录内，
 * 由 [ResourcePathSafety.resolvesWithin] 保证。
 */
interface AssetResourceRoot {

    /** 资源根的唯一标识，用于诊断（如 "assets" 或绝对路径）。 */
    val id: String

    /** 读取相对路径下的文本文件；不存在或越界返回 null。 */
    fun readTextOrNull(relativePath: String): String?

    /** 判断相对路径指向的资源是否存在且在根目录内。 */
    fun exists(relativePath: String): Boolean

    /** 解析相对路径为规范化的展示路径（仅供诊断日志，不保证文件存在）。 */
    fun displayPath(relativePath: String): String
}

/**
 * 基于 java.io.File 的资源根（已安装场景包 / 测试临时目录）。
 */
class FileResourceRoot(
    val rootDirectory: File
) : AssetResourceRoot {

    override val id: String get() = rootDirectory.canonicalPath

    override fun readTextOrNull(relativePath: String): String? {
        if (!ResourcePathSafety.resolvesWithin(rootDirectory, relativePath)) return null
        val file = File(rootDirectory, relativePath.replace('\\', '/').trimStart('/'))
        return runCatching { if (file.isFile) file.readText() else null }.getOrNull()
    }

    override fun exists(relativePath: String): Boolean {
        if (!ResourcePathSafety.resolvesWithin(rootDirectory, relativePath)) return false
        val file = File(rootDirectory, relativePath.replace('\\', '/').trimStart('/'))
        return file.exists()
    }

    override fun displayPath(relativePath: String): String =
        File(rootDirectory, relativePath.replace('\\', '/').trimStart('/')).path
}
