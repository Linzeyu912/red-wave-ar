package cn.bistu.redwave.data

import com.google.common.truth.Truth.assertThat
import org.junit.Test

/**
 * ManifestValidator 的纯 Schema 校验测试（不涉及文件系统）。
 * 覆盖 §5.5 字段约束与 §5.6 第 6 条（缩放有限正数、坐标有限）。
 */
class ManifestValidatorTest {

    private val validator = ManifestValidator(strict = false)

    @Test
    fun validBundle_passesAllChecks() {
        val result = validator.validateBundle(
            ManifestJson.parseGlobalManifest(ManifestTestFixture.VALID_GLOBAL),
            ManifestJson.parseSceneManifest(ManifestTestFixture.VALID_SCENE),
            ManifestJson.parseContentManifest(ManifestTestFixture.VALID_CONTENT)
        )
        assertThat(result).isEqualTo(ManifestValidationResult.Valid)
    }

    @Test
    fun schemaVersionMismatch_fails() {
        val issues = ValidationIssues()
        validator.validateGlobalManifest(
            ManifestJson.parseGlobalManifest(
                ManifestTestFixture.VALID_GLOBAL.replace("\"schema_version\": 1", "\"schema_version\": 99")
            ),
            issues
        )
        assertThat(issues.snapshot().any { it.contains("schema_version") }).isTrue()
    }

    @Test
    fun invalidSceneIdFormat_fails() {
        val scene = ManifestJson.parseSceneManifest(
            ManifestTestFixture.VALID_SCENE.replace("\"scene_id\": \"S1\"", "\"scene_id\": \"scene_one\"")
        )
        val issues = ValidationIssues()
        validator.validateSceneManifest(scene, issues)
        assertThat(issues.snapshot().any { it.contains("scene_one") }).isTrue()
    }

    @Test
    fun environmentGlbNotGlb_fails() {
        val scene = ManifestJson.parseSceneManifest(
            ManifestTestFixture.VALID_SCENE.replace("environment_whitebox.glb", "environment.fbx")
        )
        val issues = ValidationIssues()
        validator.validateSceneManifest(scene, issues)
        assertThat(issues.snapshot().any { it.contains(".glb") }).isTrue()
    }

    @Test
    fun propNonPositiveScale_fails() {
        val scene = ManifestJson.parseSceneManifest(
            ManifestTestFixture.VALID_SCENE.replace("\"scale\": 1.0", "\"scale\": 0.0", false)
        )
        val issues = ValidationIssues()
        validator.validateSceneManifest(scene, issues)
        assertThat(issues.snapshot().any { it.contains("scale") }).isTrue()
    }

    @Test
    fun colliderMinGreaterEqualMax_fails() {
        // §5.5：collider min_m 每一维必须小于 max_m
        val badScene = ManifestTestFixture.VALID_SCENE
            .replace("\"min_m\": [-4.2, 0.0, -4.2]", "\"min_m\": [5.0, 0.0, -4.2]")
        val scene = ManifestJson.parseSceneManifest(badScene)
        val issues = ValidationIssues()
        validator.validateSceneManifest(scene, issues)
        assertThat(issues.snapshot().any { it.contains("wall_north") && it.contains(">=") }).isTrue()
    }

    @Test
    fun hotspotsWithoutMovePoints_fails() {
        // §5.5：movement.type=hotspots 时 move_points 必填。直接构造独立 fixture，
        // 避免 VALID_SCENE 的 move_points 跨行正则替换不稳定。
        val sceneJson = """
{
  "schema_version": 1, "scene_id": "S1",
  "environment_glb": "environment.glb",
  "visitor_start": { "position_m": [0.0, 1.6, 3.0], "rotation_deg": [0.0, 0.0, 0.0] },
  "movement": { "type": "hotspots", "speed_mps": 1.2, "x_min_m": -3.6, "x_max_m": 3.6, "z_min_m": -3.6, "z_max_m": 3.6 },
  "colliders": [],
  "move_points": [],
  "props": [
    { "id": "p_s1_radio", "glb": "props/radio.glb", "position_m": [0.55, 0.78, 1.6], "rotation_deg": [0.0, 0.0, 0.0], "scale": 1.0, "interaction_radius_m": 1.8, "highlight_anchor_m": [0.0, 0.42, 0.0] }
  ]
}
""".trimIndent()
        val scene = ManifestJson.parseSceneManifest(sceneJson)
        val issues = ValidationIssues()
        validator.validateSceneManifest(scene, issues)
        assertThat(issues.snapshot().any { it.contains("hotspots") }).isTrue()
    }

    @Test
    fun contentInvalidReviewStatus_fails() {
        val content = ManifestJson.parseContentManifest(
            ManifestTestFixture.VALID_CONTENT.replace("\"review_status\": \"approved\"", "\"review_status\": \"garbage\"")
        )
        val issues = ValidationIssues()
        validator.validateContentManifest(content, issues)
        assertThat(issues.snapshot().any { it.contains("review_status") }).isTrue()
    }

    @Test
    fun strictRelease_rejectsPlaceholderText() {
        // §5.6-7：Release 禁止占位文本
        val strictValidator = ManifestValidator(strict = true)
        val content = ManifestJson.parseContentManifest(
            ManifestTestFixture.VALID_CONTENT
                .replace("\"text\": \"1943 年冬，党组织在涧沟村建立秘密电台。\"",
                    "\"text\": \"TODO 待填写占位文本\"")
                .replace("\"review_status\": \"approved\"", "\"review_status\": \"draft\"")
        )
        val issues = ValidationIssues()
        strictValidator.validateContentManifest(content, issues)
        val snap = issues.snapshot()
        assertThat(snap.any { it.contains("占位") || it.contains("PLACEHOLDER") }).isTrue()
        assertThat(snap.any { it.contains("approved") }).isTrue()
    }

    @Test
    fun nonStrict_allowsPlaceholderText() {
        val content = ManifestJson.parseContentManifest(
            ManifestTestFixture.VALID_CONTENT
                .replace("\"text\": \"1943 年冬，党组织在涧沟村建立秘密电台。\"",
                    "\"text\": \"TODO 占位\"")
        )
        val issues = ValidationIssues()
        validator.validateContentManifest(content, issues)
        // Debug 下占位文本不触发拒绝
        assertThat(issues.snapshot().none { it.contains("占位内容") }).isTrue()
    }

    @Test
    fun duplicatePropIds_fail() {
        val scene = ManifestJson.parseSceneManifest(
            ManifestTestFixture.VALID_SCENE.replace("\"id\": \"p_s1_codebook\"", "\"id\": \"p_s1_radio\"")
        )
        val issues = ValidationIssues()
        validator.validateSceneManifest(scene, issues)
        assertThat(issues.snapshot().any { it.contains("重复") }).isTrue()
    }
}
