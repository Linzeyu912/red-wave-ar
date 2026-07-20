package cn.bistu.redwave.data

import com.google.common.truth.Truth.assertThat
import org.junit.Test
import java.io.File

/**
 * 用 app/src/main/assets 的真实白盒数据做端到端校验。
 *
 * 验证三件事（计划书“通过 manifest 和 JSON 数据契约读取”）：
 * 1. 我写的 global_manifest.json 能解析；
 * 2. 建模交付的 scene.json（modeling_delivery 复制到 assets）能解析并过校验；
 * 3. 三份文件 + 真实 GLB 位置能通过跨文件校验（音频/缩略图为软检查）。
 *
 * 这条测试是建模交付与编码校验的接合点：一旦 scene.json 字段、坐标或文件名变化，
 * 这里会先于真机报错。
 */
class RealAssetsIntegrationTest {

    private val assetsDir = File("src/main/assets")

    @Test
    fun realGlobalManifest_parsesAndValidates() {
        val text = File(assetsDir, "global_manifest.json").readText()
        val global = ManifestJson.parseGlobalManifest(text)
        val issues = ValidationIssues()
        ManifestValidator().validateGlobalManifest(global, issues)
        assertThat(text).isNotEmpty()
        assertThat(global.scenes).hasSize(1)
        assertThat(issues.hasIssues()).isFalse()
    }

    @Test
    fun realSceneManifest_parsesAndValidates() {
        // 来自建模交付的白盒 scene.json
        val text = File(assetsDir, "scenes/scene_S1/scene.json").readText()
        val scene = ManifestJson.parseSceneManifest(text)
        val issues = ValidationIssues()
        ManifestValidator().validateSceneManifest(scene, issues)
        assertThat(scene.sceneId).isEqualTo("S1")
        assertThat(scene.props.map { it.id })
            .containsExactly("p_s1_radio", "p_s1_key", "p_s1_codebook")
        // 白盒 scene.json 必须通过 Schema 校验
        assertThat(issues.snapshot()).isEmpty()
    }

    @Test
    fun realContentManifest_parsesAndValidatesInDebug() {
        val text = File(assetsDir, "scenes/scene_S1/content.json").readText()
        val content = ManifestJson.parseContentManifest(text)
        val issues = ValidationIssues()
        ManifestValidator(strict = false).validateContentManifest(content, issues)
        assertThat(content.items).hasSize(3)
        // Debug 模式下 draft 内容不触发拒绝
        assertThat(issues.hasIssues()).isFalse()
    }

    @Test
    fun realBundle_crossFileValidationPasses() {
        val root = FileResourceRoot(assetsDir)
        val repo = ManifestRepository(root, strict = false)
        val bundle = repo.loadSceneBundle("S1").getOrThrow()
        assertThat(bundle.sceneManifest.environmentGlb).isEqualTo("environment_whitebox.glb")
        // 三个 MVP 文物 + 三条内容，一一对应
        val propIds = bundle.sceneManifest.props.map { it.id }.toSet()
        val contentIds = bundle.contentManifest.items.map { it.id }.toSet()
        assertThat(propIds).isEqualTo(contentIds)
        // 白盒阶段：GLB 全部存在（致命检查通过），音频为软缺失
        // 缩略图 thumbnail.png 我们生成了占位，故不应缺失
        assertThat(bundle.missingAssets.none { it.contains("thumbnail") }).isTrue()
    }

    @Test
    fun realResolver_mapsQrAndImageToS1() {
        val root = FileResourceRoot(assetsDir)
        val repo = ManifestRepository(root, strict = false)
        val resolver = repo.buildEntryResolver().getOrThrow()
        assertThat(resolver.resolveQr("REDWAVE-S1").getOrThrow().sceneId).isEqualTo("S1")
        assertThat(resolver.resolveImage("trigger_S1").getOrThrow().sceneId).isEqualTo("S1")
        assertThat(resolver.resolveManual("S1").getOrThrow().sceneId).isEqualTo("S1")
    }
}
