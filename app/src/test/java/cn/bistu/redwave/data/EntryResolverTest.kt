package cn.bistu.redwave.data

import cn.bistu.redwave.EntrySource
import cn.bistu.redwave.AppErrorCode
import com.google.common.truth.Truth.assertThat
import org.junit.Test

/**
 * 计划书 UT-001：二维码值映射正确返回唯一 scene_id。
 * 计划书 UT-002：重复 qr_payload / image_name 校验失败。
 * 计划书 UT-007：入口重复结果（去重由调用方，本类保证单次解析稳定）。
 */
class EntryResolverTest {

    private fun resolverFrom(json: String): Result<EntryResolver> =
        EntryResolver.fromManifest(ManifestJson.parseGlobalManifest(json))

    private val validResolver = resolverFrom(ManifestTestFixture.VALID_GLOBAL).getOrThrow()

    @Test
    fun ut001_qrPayload_mapsToCorrectSceneId() {
        // UT-001：正确返回唯一 scene_id
        val result = validResolver.resolveQr("REDWAVE-S1")
        assertThat(result.isSuccess).isTrue()
        val entry = result.getOrThrow()
        assertThat(entry.sceneId).isEqualTo("S1")
        assertThat(entry.source).isEqualTo(EntrySource.QR)
    }

    @Test
    fun qrPayload_isTrimmedButCaseSensitive() {
        // §5.5：去除首尾空白，但区分大小写
        assertThat(validResolver.resolveQr("  REDWAVE-S1  ").isSuccess).isTrue()
        // 大小写不同应解析失败
        assertThat(validResolver.resolveQr("redwave-s1").isFailure).isTrue()
    }

    @Test
    fun ut001_imageName_mapsToCorrectSceneId() {
        val result = validResolver.resolveImage("trigger_S1")
        assertThat(result.isSuccess).isTrue()
        assertThat(result.getOrThrow().sceneId).isEqualTo("S1")
        assertThat(result.getOrThrow().source).isEqualTo(EntrySource.IMAGE)
    }

    @Test
    fun manualEntry_validatesSceneIdExists() {
        assertThat(validResolver.resolveManual("S1").isSuccess).isTrue()
        // 不存在的 scene_id 失败
        val unknown = validResolver.resolveManual("S99")
        assertThat(unknown.isFailure).isTrue()
        val ex = unknown.exceptionOrNull() as EntryResolver.EntryResolutionException
        assertThat(ex.code).isEqualTo(AppErrorCode.ENTRY_UNKNOWN)
    }

    @Test
    fun unknownQr_returnsEntryUnknown() {
        // 不是本项目卡片
        val result = validResolver.resolveQr("https://random.url/x")
        assertThat(result.isFailure).isTrue()
        val ex = result.exceptionOrNull() as EntryResolver.EntryResolutionException
        assertThat(ex.code).isEqualTo(AppErrorCode.ENTRY_UNKNOWN)
    }

    @Test
    fun ut002_duplicateQrPayload_buildFails() {
        // UT-002：重复 qr_payload 校验失败
        val result = resolverFrom(ManifestTestFixture.DUPLICATE_QR)
        assertThat(result.isFailure).isTrue()
        val ex = result.exceptionOrNull() as ManifestLoadException
        assertThat(ex.code).isEqualTo(AppErrorCode.MANIFEST_INVALID)
        assertThat(ex.reasons.joinToString()).contains("REDWAVE-S1")
    }

    @Test
    fun ut002_duplicateSceneId_buildFails() {
        val result = resolverFrom(ManifestTestFixture.DUPLICATE_SCENE_ID)
        assertThat(result.isFailure).isTrue()
        val ex = result.exceptionOrNull() as ManifestLoadException
        assertThat(ex.reasons.joinToString()).contains("S1")
    }

    @Test
    fun ut007_repeatedResolve_isStableAndDeterministic() {
        // UT-007：连续相同输入应得到相同结果（去重由调用方负责）
        val first = validResolver.resolveQr("REDWAVE-S1").getOrThrow()
        repeat(5) {
            val again = validResolver.resolveQr("REDWAVE-S1").getOrThrow()
            assertThat(again).isEqualTo(first)
        }
        // 同一 EntryResult 只携带 scene_id 与 source
        assertThat(first.toString()).contains("S1")
        assertThat(first.toString()).contains("QR")
    }

    @Test
    fun entryResult_neverCarriesCameraOrArData() {
        // 计划书 §6.8：入口成功事件不携带 Bitmap、Camera Frame、Anchor、Pose。
        val entry = validResolver.resolveQr("REDWAVE-S1").getOrThrow()
        val className = entry::class.simpleName
        assertThat(className).isEqualTo("EntryResult")
        // 业务字段只有两个
        val businessFields = entry::class.java.declaredFields
            .map { it.name }
            .filter { !it.startsWith("$") }
        assertThat(businessFields).containsExactly("sceneId", "source")
    }
}
