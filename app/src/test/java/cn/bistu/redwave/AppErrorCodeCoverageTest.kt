package cn.bistu.redwave

import com.google.common.truth.Truth.assertThat
import org.junit.Test

/**
 * 计划书 UT-014：错误码映射——每个错误都有稳定的用户文案与恢复动作。
 *
 * 这是 CODE-00 阶段的基础测试，验证测试基础设施（JUnit + Truth）可用，
 * 同时锁定错误码表不会被遗漏地新增。
 */
class AppErrorCodeCoverageTest {

    @Test
    fun everyErrorCode_hasUserMessageAndRecoveryAction() {
        // 计划书 UT-014：每个错误都有稳定用户文案与恢复动作。
        assertThat(AppErrorMessages.isFullyCovered()).isTrue()

        AppErrorCode.entries.forEach { code ->
            val recovery = AppErrorMessages.recoveryFor(code)
            assertThat(recovery.shortMessage).isNotEmpty()
            assertThat(recovery.actionLabel).isNotEmpty()
        }
    }

    @Test
    fun manifestInvalid_routesToDiagnostics() {
        // MANIFEST_INVALID 不进入场景，但必须给出可执行的诊断入口（CODE-10）。
        val recovery = AppErrorMessages.recoveryFor(AppErrorCode.MANIFEST_INVALID)
        assertThat(recovery.actionLabel).contains("诊断")
        assertThat(recovery.shortMessage).contains("资源配置")
    }

    @Test
    fun sensorUnavailable_suggestsTouchModeFallback() {
        val recovery = AppErrorMessages.recoveryFor(AppErrorCode.SENSOR_UNAVAILABLE)
        assertThat(recovery.actionLabel).contains("触屏")
    }

    @Test
    fun stableCode_isEnumName_forStableDiagnosticLogs() {
        // 计划书 §6.18：错误日志至少包含错误码；码值必须稳定，便于跨版本检索。
        assertThat(AppErrorCode.ENTRY_UNKNOWN.stableCode).isEqualTo("ENTRY_UNKNOWN")
    }

    @Test
    fun entryResult_carriesOnlySceneIdAndSource_notCameraData() {
        // 计划书 §6.8：入口成功事件只携带 scene_id 和入口类型，
        // 不携带 Bitmap、Camera Frame、Anchor 或 Pose。
        val result = EntryResult(sceneId = "S1", source = EntrySource.QR)
        assertThat(result.sceneId).isEqualTo("S1")
        assertThat(result.source).isEqualTo(EntrySource.QR)
        // EntryResult 的业务字段是数据契约的一部分，只有 sceneId 与 source。
        // 任何新增「业务」字段都意味着入口边界被破坏，需要 ADR。
        // 反射中可能出现编译器合成的字段（如 $stable），这些不是业务契约，需要排除。
        val declared = EntryResult::class.java.declaredFields.map { it.name }
        val businessFields = declared.filter { !it.startsWith("$") }
        assertThat(businessFields).containsExactly("sceneId", "source")
        // 明确禁止入口结果携带相机/ARCore 相关数据。
        val forbidden = declared.any { it.lowercase() in setOf("bitmap", "frame", "anchor", "pose") }
        assertThat(forbidden).isFalse()
    }
}
