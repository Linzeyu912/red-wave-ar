package cn.bistu.redwave.data

import com.google.common.truth.Truth.assertThat
import org.junit.Test
import org.junit.rules.TemporaryFolder
import org.junit.Rule
import java.io.File

/**
 * 计划书 UT-003：`../`、绝对路径或空路径必须拒绝。
 * 计划书 §5.6-4：路径必须解析在允许的资源根目录内，拒绝路径穿越。
 */
class ResourcePathSafetyTest {

    @get:Rule
    val tempFolder = TemporaryFolder()

    @Test
    fun rejectsEmptyPath() {
        assertThat(ResourcePathSafety.stringCheck("", "scene_manifest")).contains("为空")
        assertThat(ResourcePathSafety.stringCheck("   ", "scene_manifest")).contains("为空")
    }

    @Test
    fun rejectsParentTraversal() {
        // UT-003：../ 必须拒绝
        assertThat(ResourcePathSafety.stringCheck("../escape/scene.json", "scene_manifest")).isNotNull()
        assertThat(ResourcePathSafety.stringCheck("scenes/../etc/passwd", "scene_manifest")).isNotNull()
        assertThat(ResourcePathSafety.stringCheck("a/../../b", "scene_manifest")).isNotNull()
    }

    @Test
    fun rejectsAbsolutePath() {
        assertThat(ResourcePathSafety.stringCheck("/etc/passwd", "scene_manifest")).contains("绝对路径")
        assertThat(ResourcePathSafety.stringCheck("C:/Users/x", "scene_manifest")).contains("盘符")
        assertThat(ResourcePathSafety.stringCheck("D:\\secrets", "scene_manifest")).contains("盘符")
        assertThat(ResourcePathSafety.stringCheck("//host/share/x", "scene_manifest")).contains("UNC")
    }

    @Test
    fun rejectsControlCharacters() {
        assertThat(ResourcePathSafety.stringCheck("a\tb.json", "scene_manifest")).contains("控制字符")
        assertThat(ResourcePathSafety.stringCheck("a\u0000b.json", "scene_manifest")).contains("控制字符")
    }

    @Test
    fun rejectsDoubleSlashes() {
        assertThat(ResourcePathSafety.stringCheck("a//b.json", "scene_manifest")).contains("连续斜杠")
    }

    @Test
    fun acceptsValidRelativePath() {
        assertThat(ResourcePathSafety.stringCheck("scenes/scene_S1/scene.json", "scene_manifest")).isNull()
        assertThat(ResourcePathSafety.stringCheck("props/radio.glb", "glb")).isNull()
        assertThat(ResourcePathSafety.stringCheck("audio/x.mp3", "audio")).isNull()
        // 反斜杠应被规范化接受（Windows 习惯）
        assertThat(ResourcePathSafety.stringCheck("props\\radio.glb", "glb")).isNull()
    }

    @Test
    fun resolvesWithinBlocksTraversalAtFilesystemLevel() {
        // 第二道保险：即使字符串校验被绕过，规范化后越界仍拒绝。
        val root = tempFolder.newFolder("root")
        val nested = File(root, "scenes").apply { mkdirs() }
        File(nested, "scene.json").writeText("{}")

        assertThat(ResourcePathSafety.resolvesWithin(root, "scenes/scene.json")).isTrue()
        assertThat(ResourcePathSafety.resolvesWithin(root, "scenes/../scenes/scene.json")).isTrue()
        // 指向 root 之外
        assertThat(ResourcePathSafety.resolvesWithin(root, "../outside")).isFalse()
    }
}
