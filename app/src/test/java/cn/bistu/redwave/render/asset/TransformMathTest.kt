package cn.bistu.redwave.render.asset

import com.google.common.truth.Truth.assertThat
import org.junit.Test

/**
 * TransformMath 矩阵转换测试（计划书 §5.2、§5.5）。
 * 纯数学，不依赖 Filament native，可 JVM 单测。
 */
class TransformMathTest {

    @Test
    fun identityTRS_producesIdentityRotation() {
        // 零旋转、单位缩放、零平移：上 3x3 应为单位矩阵
        val m = TransformMath.composeTRS(
            listOf(0f, 0f, 0f),
            listOf(0f, 0f, 0f),
            1f
        )
        assertThat(m.size).isEqualTo(16)
        // 行主序：m[0,0]=m[0], m[1,1]=m[5], m[2,2]=m[10]
        assertThat(m[0]).isWithin(1e-5f).of(1f)
        assertThat(m[5]).isWithin(1e-5f).of(1f)
        assertThat(m[10]).isWithin(1e-5f).of(1f)
        // 平移列（行主序第 4 列：m[3],m[7],m[11]）为 0
        assertThat(m[3]).isEqualTo(0f)
        assertThat(m[7]).isEqualTo(0f)
        assertThat(m[11]).isEqualTo(0f)
    }

    @Test
    fun translation_appearsInLastColumn() {
        // 行主序 4x4，平移在每行的第 4 元素：m[12],m[13],m[14]
        val m = TransformMath.composeTRS(
            listOf(1.5f, 1.6f, 3.0f),
            listOf(0f, 0f, 0f),
            1f
        )
        assertThat(m[12]).isEqualTo(1.5f)
        assertThat(m[13]).isEqualTo(1.6f)
        assertThat(m[14]).isEqualTo(3.0f)
    }

    @Test
    fun yawRotation_180_pointsForwardNegZ() {
        // 绕 Y 轴 180°：forward（+Z 基向量）应映射到 -Z。
        // §5.2：-Z 朝前。游客起点 rotation_deg=[0,180,0] 即面向 -Z。
        val m = TransformMath.composeTRS(
            listOf(0f, 0f, 0f),
            listOf(0f, 180f, 0f),
            1f
        )
        // 第三行（Z 基向量行主序）：r20, r21, r22
        // 绕 Y 180°：x->-x, z->-z
        assertThat(m[0]).isWithin(1e-4f).of(-1f)   // (1,0,0) -> (-1,0,0)
        assertThat(m[10]).isWithin(1e-4f).of(-1f)  // (0,0,1) -> (0,0,-1)
    }

    @Test
    fun scale_multipliesRotationColumns() {
        val m = TransformMath.composeTRS(
            listOf(0f, 0f, 0f),
            listOf(0f, 0f, 0f),
            2f
        )
        // 单位旋转 × 2 缩放
        assertThat(m[0]).isEqualTo(2f)
        assertThat(m[5]).isEqualTo(2f)
        assertThat(m[10]).isEqualTo(2f)
    }

    @Test
    fun rejectsNonPositiveScale() {
        try {
            TransformMath.composeTRS(listOf(0f, 0f, 0f), listOf(0f, 0f, 0f), 0f)
            assert(false) { "应抛异常" }
        } catch (e: IllegalArgumentException) {
            assertThat(e.message).contains("scale")
        }
    }

    @Test
    fun rejectsWrongDimension() {
        try {
            TransformMath.composeTRS(listOf(0f, 0f), listOf(0f, 0f, 0f), 1f)
            assert(false) { "应抛异常" }
        } catch (e: IllegalArgumentException) { /* ok */ }
    }

    @Test
    fun sceneJsonExampleCoordinates_produceExpectedMatrix() {
        // 计划书 §5.4 示例 prop：position [1.2,0.8,-1.0], rot [0,30,0], scale 1.0
        val m = TransformMath.composeTRS(
            listOf(1.2f, 0.8f, -1.0f),
            listOf(0f, 30f, 0f),
            1.0f
        )
        // 平移正确
        assertThat(m[12]).isEqualTo(1.2f)
        assertThat(m[13]).isEqualTo(0.8f)
        assertThat(m[14]).isEqualTo(-1.0f)
        // 30° Y 旋转：m[0]=cos30≈0.866
        assertThat(m[0]).isWithin(1e-3f).of(0.8660254f)
    }
}
