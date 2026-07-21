package cn.bistu.redwave.data

import com.google.common.truth.Truth.assertThat
import com.google.common.truth.Truth.assertWithMessage
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
    private val frozenS1RuntimeDir = File("../modeling_delivery/S1/runtime")
    private val packagedS1RuntimeDir = File(assetsDir, "scenes/scene_S1")

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
    fun realSceneManifest_matchesFrozenCompactCellarContract() {
        val text = File(packagedS1RuntimeDir, "scene.json").readText()
        val scene = ManifestJson.parseSceneManifest(text)

        assertThat(scene.visitorStart.positionM).containsExactly(0.0f, 1.55f, 1.65f).inOrder()
        assertThat(scene.visitorStart.rotationDeg).containsExactly(0.0f, 0.0f, 0.0f).inOrder()
        assertThat(scene.movement.type).isEqualTo("bounds")
        assertThat(scene.movement.xMinM).isEqualTo(-2.25f)
        assertThat(scene.movement.xMaxM).isEqualTo(2.25f)
        assertThat(scene.movement.zMinM).isEqualTo(-1.95f)
        assertThat(scene.movement.zMaxM).isEqualTo(1.95f)
        assertThat(scene.colliders).hasSize(8)

        val radio = scene.props.single { it.id == "p_s1_radio" }
        assertThat(radio.glb).isEqualTo("props/radio_station_whitebox.glb")
        assertThat(radio.positionM).containsExactly(0.32f, 0.78f, 0.04f).inOrder()
        assertThat(radio.rotationDeg).containsExactly(0.0f, 180.0f, 0.0f).inOrder()
    }

    @Test
    fun packagedS1Runtime_isByteIdenticalToFrozenModelingDelivery() {
        assertThat(frozenS1RuntimeDir.isDirectory).isTrue()

        val frozenFiles = frozenS1RuntimeDir.walkTopDown()
            .filter { it.isFile && it.name != ".gitkeep" }
            .sortedBy { it.relativeTo(frozenS1RuntimeDir).invariantSeparatorsPath }
            .toList()

        assertThat(frozenFiles.map { it.relativeTo(frozenS1RuntimeDir).invariantSeparatorsPath })
            .containsExactly(
                "environment_whitebox.glb",
                "props/code_book_whitebox.glb",
                "props/radio_station_whitebox.glb",
                "props/telegraph_key_whitebox.glb",
                "scene.json"
            )

        frozenFiles.forEach { frozenFile ->
            val relativePath = frozenFile.relativeTo(frozenS1RuntimeDir).invariantSeparatorsPath
            val packagedFile = File(packagedS1RuntimeDir, relativePath)
            assertWithMessage("Packaged S1 asset is missing: %s", relativePath)
                .that(packagedFile.isFile)
                .isTrue()
            assertWithMessage("Packaged S1 asset differs from frozen source: %s", relativePath)
                .that(packagedFile.readBytes().contentEquals(frozenFile.readBytes()))
                .isTrue()
        }
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
