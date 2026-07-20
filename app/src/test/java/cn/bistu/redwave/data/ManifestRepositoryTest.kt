package cn.bistu.redwave.data

import cn.bistu.redwave.AppErrorCode
import com.google.common.truth.Truth.assertThat
import org.junit.Rule
import org.junit.Test
import org.junit.rules.TemporaryFolder
import java.io.File

/**
 * 计划书 §15.1 UT-004~006：跨文件校验、Release 严格模式、起点落入 collider。
 * 通过 [ManifestRepository] + [FileResourceRoot] 验证完整加载链路。
 */
class ManifestRepositoryTest {

    @get:Rule
    val tempFolder = TemporaryFolder()

    /** 搭建一个完整的有效 S1 资源目录（含占位 GLB/audio/thumbnail 文件）。 */
    private fun buildValidRoot(suffix: String = "assets"): File {
        val root = tempFolder.newFolder(suffix)
        File(root, "global_manifest.json").writeText(ManifestTestFixture.VALID_GLOBAL)
        val sceneDir = File(root, "scenes/scene_S1").apply { mkdirs() }
        File(sceneDir, "scene.json").writeText(ManifestTestFixture.VALID_SCENE)
        File(sceneDir, "content.json").writeText(ManifestTestFixture.VALID_CONTENT)
        File(sceneDir, "environment_whitebox.glb").writeBytes(byteArrayOf(1, 2, 3))
        val propsDir = File(sceneDir, "props").apply { mkdirs() }
        File(propsDir, "radio_station_whitebox.glb").writeBytes(byteArrayOf(1))
        File(propsDir, "telegraph_key_whitebox.glb").writeBytes(byteArrayOf(1))
        File(propsDir, "code_book_whitebox.glb").writeBytes(byteArrayOf(1))
        val audioDir = File(sceneDir, "audio").apply { mkdirs() }
        File(audioDir, "p_s1_radio_zh.mp3").writeBytes(byteArrayOf(1))
        File(audioDir, "p_s1_key_zh.mp3").writeBytes(byteArrayOf(1))
        File(audioDir, "p_s1_codebook_zh.mp3").writeBytes(byteArrayOf(1))
        File(sceneDir, "thumbnail.png").writeBytes(byteArrayOf(1))
        return root
    }

    private fun repo(root: File, strict: Boolean = false) =
        ManifestRepository(FileResourceRoot(root), strict = strict)

    @Test
    fun loadGlobalManifest_validBundle_succeeds() {
        val r = repo(buildValidRoot())
        val global = r.loadGlobalManifest().getOrThrow()
        assertThat(global.scenes).hasSize(1)
        assertThat(global.scenes[0].sceneId).isEqualTo("S1")
    }

    @Test
    fun loadGlobalManifest_missingFile_returnsManifestInvalid() {
        val r = repo(tempFolder.newFolder("empty"))
        val result = r.loadGlobalManifest()
        assertThat(result.isFailure).isTrue()
        val ex = result.exceptionOrNull() as ManifestLoadException
        assertThat(ex.code).isEqualTo(AppErrorCode.MANIFEST_INVALID)
        assertThat(ex.reasons.joinToString()).contains("global_manifest.json")
    }

    @Test
    fun loadSceneBundle_valid_completesWithCrossFileCheck() {
        val r = repo(buildValidRoot())
        val bundle = r.loadSceneBundle("S1").getOrThrow()
        assertThat(bundle.sceneManifest.props).hasSize(3)
        assertThat(bundle.contentManifest.items).hasSize(3)
        assertThat(bundle.missingAssets).isEmpty()
    }

    @Test
    fun ut004_contentItemWithoutProp_failsCrossFileCheck() {
        // UT-004：content ID 找不到 prop
        val root = buildValidRoot()
        File(root, "scenes/scene_S1/content.json").writeText(ManifestTestFixture.CONTENT_ORPHAN_ITEM)
        val r = repo(root)
        val result = r.loadSceneBundle("S1")
        assertThat(result.isFailure).isTrue()
        val ex = result.exceptionOrNull() as ManifestLoadException
        assertThat(ex.reasons.joinToString()).contains("p_nonexistent")
        // 同时报告：文物缺少内容（孤儿 content 没有匹配 prop，反向也触发）
    }

    @Test
    fun ut005_draftContent_allowedInDebug_rejectedInRelease() {
        // UT-005：review_status=draft，Debug 可加载，Release 拒绝
        val root = buildValidRoot()
        File(root, "scenes/scene_S1/content.json").writeText(ManifestTestFixture.CONTENT_DRAFT_REVIEW)

        val debugRepo = repo(root, strict = false)
        // Debug 下 draft 文物能加载（注意：该 fixture 只覆盖 p_s1_radio，另两个 prop 会缺内容，仍报错）
        // 这里只验证 draft 本身在 Debug 不触发 Release 专属拒绝
        val debugResult = debugRepo.loadSceneBundle("S1")
        assertThat(debugResult.isFailure).isTrue()
        val debugEx = debugResult.exceptionOrNull() as ManifestLoadException
        // Debug 下 draft 不应触发 "非 approved" 拒绝
        assertThat(debugEx.reasons.none { it.contains("review_status 非 approved") }).isTrue()

        val releaseRepo = repo(root, strict = true)
        val releaseResult = releaseRepo.loadSceneBundle("S1")
        assertThat(releaseResult.isFailure).isTrue()
        val releaseEx = releaseResult.exceptionOrNull() as ManifestLoadException
        // Release 下应明确拒绝 draft
        assertThat(releaseEx.reasons.any { it.contains("review_status 非 approved") }).isTrue()
    }

    @Test
    fun ut006_visitorStartInsideCollider_fails() {
        // UT-006：起点落入 collider 校验失败
        val root = buildValidRoot()
        File(root, "scenes/scene_S1/scene.json").writeText(ManifestTestFixture.SCENE_START_IN_COLLIDER)
        val r = repo(root)
        val result = r.loadSceneBundle("S1")
        assertThat(result.isFailure).isTrue()
        val ex = result.exceptionOrNull() as ManifestLoadException
        assertThat(ex.reasons.joinToString()).contains("visitor_start")
        assertThat(ex.reasons.joinToString()).contains("collider")
    }

    @Test
    fun missingGlb_failsHard_missingAudioSoftInDebug() {
        // GLB 缺失：致命（CODE-03 无法渲染）
        val root = buildValidRoot()
        File(root, "scenes/scene_S1/props/radio_station_whitebox.glb").delete()
        val r = repo(root)
        val result = r.loadSceneBundle("S1")
        assertThat(result.isFailure).isTrue()
        val ex = result.exceptionOrNull() as ManifestLoadException
        assertThat(ex.reasons.any { it.contains("radio_station_whitebox.glb") }).isTrue()

        // 音频缺失（Debug 软）：加载成功，记入 missingAssets
        val root2 = buildValidRoot(suffix = "assets2")
        File(root2, "scenes/scene_S1/audio/p_s1_radio_zh.mp3").delete()
        val bundle = repo(root2).loadSceneBundle("S1").getOrThrow()
        assertThat(bundle.missingAssets.any { it.contains("p_s1_radio_zh.mp3") }).isTrue()
    }

    @Test
    fun sceneIdMismatch_acrossFiles_fails() {
        // §5.6-1：三文件 scene_id 必须一致
        val root = buildValidRoot()
        // 改 content 的 scene_id
        val content = File(root, "scenes/scene_S1/content.json").readText()
            .replace("\"scene_id\": \"S1\"", "\"scene_id\": \"S2\"")
        File(root, "scenes/scene_S1/content.json").writeText(content)
        val r = repo(root)
        val result = r.loadSceneBundle("S1")
        assertThat(result.isFailure).isTrue()
        assertThat((result.exceptionOrNull() as ManifestLoadException).reasons.joinToString())
            .contains("不一致")
    }
}
