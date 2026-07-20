package cn.bistu.redwave.data

import cn.bistu.redwave.AppErrorCode

/**
 * 清单加载/构建异常，携带稳定错误码（§6.18）与诊断原因列表。
 *
 * 用于把“清单损坏”与“入口解析失败”统一映射到 [AppErrorCode.MANIFEST_INVALID]
 * 或 [AppErrorCode.ENTRY_UNKNOWN]，供上层转换为用户可理解的错误页。
 */
class ManifestLoadException(
    val code: AppErrorCode,
    val reasons: List<String>,
    cause: Throwable? = null
) : RuntimeException(reasons.joinToString("; "), cause) {
    init {
        require(reasons.isNotEmpty()) { "ManifestLoadException 必须至少有一条 reason" }
    }
}
