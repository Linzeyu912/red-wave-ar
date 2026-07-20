package cn.bistu.redwave.data

import cn.bistu.redwave.AppErrorCode

/**
 * 资源校验结果（计划书 §5.6、§6.18）。
 *
 * 校验失败一律返回 [ManifestError]，不静默跳过，不崩溃。
 * 错误码稳定为 [AppErrorCode.MANIFEST_INVALID]，附带可诊断的 reason 列表。
 */
sealed interface ManifestValidationResult {
    /** 校验通过。 */
    data object Valid : ManifestValidationResult

    /**
     * 校验失败。reasons 是面向诊断的人类可读说明（不进入正式 UI，但写入诊断日志）。
     */
    data class Invalid(val errorCode: AppErrorCode, val reasons: List<String>) : ManifestValidationResult {
        init {
            require(reasons.isNotEmpty()) { "Invalid 校验结果必须至少有一条 reason" }
        }
    }
}

/**
 * 一次跨文件校验中累积的错误原因。
 * 内部使用，便于在多处校验点收集问题后统一返回。
 */
class ValidationIssues {
    private val reasons = mutableListOf<String>()

    fun add(reason: String) {
        reasons += reason
    }

    /**
     * 惰性添加：仅当 [condition] 为真时才求值并追加 [reasonSupplier]。
     * 避免在条件不满足时仍拼接诊断字符串。
     */
    fun addIf(condition: Boolean, reasonSupplier: () -> String) {
        if (condition) reasons += reasonSupplier()
    }

    fun hasIssues(): Boolean = reasons.isNotEmpty()

    fun toResult(): ManifestValidationResult =
        if (reasons.isEmpty()) ManifestValidationResult.Valid
        else ManifestValidationResult.Invalid(AppErrorCode.MANIFEST_INVALID, reasons.toList())

    /** 仅供测试与诊断使用。 */
    fun snapshot(): List<String> = reasons.toList()
}
