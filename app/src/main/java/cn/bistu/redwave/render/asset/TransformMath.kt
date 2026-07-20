package cn.bistu.redwave.render.asset

import kotlin.math.cos
import kotlin.math.sin

/**
 * 将 scene.json 的 position / rotation_deg / scale 转为 Filament 4x4 世界矩阵。
 *
 * 计划书 §5.2：Y-up、右手系、-Z 朝前、米制。
 * §5.5：rotation_deg 顺序固定 X/Y/Z，加载时转矩阵。
 *
 * 输出为 16 元素行主序 float[]（Filament TransformManager 接受行主序）。
 */
object TransformMath {

    /**
     * 由 position（米）、欧拉角（度，XYZ 顺序）、统一缩放构造 4x4 矩阵。
     * 接受 List<Float>（与 scene.json 数据模型的 position_m / rotation_deg 一致）。
     */
    fun composeTRS(
        positionM: List<Float>,
        rotationDegXYZ: List<Float>,
        scale: Float
    ): FloatArray {
        require(positionM.size == 3) { "position 必须是 3 维" }
        require(rotationDegXYZ.size == 3) { "rotation 必须是 3 维" }
        require(scale > 0f) { "scale 必须为正" }

        val rx = Math.toRadians(rotationDegXYZ[0].toDouble())
        val ry = Math.toRadians(rotationDegXYZ[1].toDouble())
        val rz = Math.toRadians(rotationDegXYZ[2].toDouble())
        val cx = cos(rx); val sx = sin(rx)
        val cy = cos(ry); val sy = sin(ry)
        val cz = cos(rz); val sz = sin(rz)

        // R = Rz * Ry * Rx（XYZ 顺序：先 X 再 Y 再 Z），右手系。
        val r00 = (cy * cz).toFloat()
        val r01 = (cy * sz).toFloat()
        val r02 = (-sy).toFloat()
        val r10 = (sx * sy * cz - cx * sz).toFloat()
        val r11 = (sx * sy * sz + cx * cz).toFloat()
        val r12 = (sx * cy).toFloat()
        val r20 = (cx * sy * cz + sx * sz).toFloat()
        val r21 = (cx * sy * sz - sx * cz).toFloat()
        val r22 = (cx * cy).toFloat()

        // 行主序 4x4：旋转 × 缩放 + 平移
        return floatArrayOf(
            r00 * scale, r01 * scale, r02 * scale, 0f,
            r10 * scale, r11 * scale, r12 * scale, 0f,
            r20 * scale, r21 * scale, r22 * scale, 0f,
            positionM[0], positionM[1], positionM[2], 1f
        )
    }
}
