package cn.bistu.redwave.sensor

import kotlin.math.cos
import kotlin.math.sin
import kotlin.math.sqrt

/**
 * 单位四元数运算（计划书 §6.12 姿态算法规格）。
 *
 * 纯数学，不依赖 Android，可 JVM 单测。
 * 约定：(w, x, y, z)，w 为实部；表示旋转 q = w + xi + yj + zk。
 */
data class Quaternion(val w: Float, val x: Float, val y: Float, val z: Float) {

    /** 共轭 / 逆（单位四元数下二者相等）。 */
    fun inverse(): Quaternion = Quaternion(w, -x, -y, -z)

    /** 模长。 */
    fun norm(): Float = sqrt(w * w + x * x + y * y + z * z)

    /** 归一化为单位四元数。 */
    fun normalized(): Quaternion {
        val n = norm()
        if (n < 1e-9f) return IDENTITY
        return Quaternion(w / n, x / n, y / n, z / n)
    }

    /** 四元数乘法（Hamilton 积）：this * other。 */
    operator fun times(other: Quaternion): Quaternion {
        return Quaternion(
            w = this.w * other.w - this.x * other.x - this.y * other.y - this.z * other.z,
            x = this.w * other.x + this.x * other.w + this.y * other.z - this.z * other.y,
            y = this.w * other.y - this.x * other.z + this.y * other.w + this.z * other.x,
            z = this.w * other.z + this.x * other.y - this.y * other.x + this.z * other.w
        )
    }

    companion object {
        val IDENTITY = Quaternion(1f, 0f, 0f, 0f)

        /**
         * 由 Android TYPE_GAME_ROTATION_VECTOR 的 values 构造四元数。
         * values[0..2] = [x*sin(θ/2), y*sin(θ/2), z*sin(θ/2)]，
         * values[3]（可选）= cos(θ/2)，values[4]（可选）= 估计精度弧度。
         */
        fun fromRotationVector(rv: FloatArray): Quaternion {
            require(rv.size >= 3) { "rotation vector 至少 3 维" }
            val qx = rv[0]
            val qy = rv[1]
            val qz = rv[2]
            val qw = if (rv.size >= 4 && rv[3] != 0f) {
                rv[3]
            } else {
                // 由向量部分反推标量：|v| = sin(θ/2)，qw = cos(θ/2) = sqrt(1 - |v|²)
                val sinHalfSq = (qx * qx + qy * qy + qz * qz).coerceAtMost(1f)
                sqrt(1f - sinHalfSq)
            }
            return Quaternion(qw, qx, qy, qz).normalized()
        }
    }
}

/**
 * 球面线性插值（slerp），用于姿态平滑（计划书 §6.12-6）。
 * alpha=0 返回 from，alpha=1 返回 to。
 */
fun slerp(from: Quaternion, to: Quaternion, alpha: Float): Quaternion {
    val a = alpha.coerceIn(0f, 1f)
    var dot = from.w * to.w + from.x * to.x + from.y * to.y + from.z * to.z
    // 若点积为负，取反 to 以走最短路径
    var t = to
    if (dot < 0f) {
        t = Quaternion(-to.w, -to.x, -to.y, -to.z)
        dot = -dot
    }
    // 接近平行时用线性插值避免数值问题
    if (dot > 0.9995f) {
        return Quaternion(
            from.w + (t.w - from.w) * a,
            from.x + (t.x - from.x) * a,
            from.y + (t.y - from.y) * a,
            from.z + (t.z - from.z) * a
        ).normalized()
    }
    val theta0 = kotlin.math.acos(dot)
    val sinTheta0 = sin(theta0)
    val theta = theta0 * a
    val s0 = cos(theta) - dot * sin(theta) / sinTheta0
    val s1 = sin(theta) / sinTheta0
    return Quaternion(
        from.w * s0 + t.w * s1,
        from.x * s0 + t.x * s1,
        from.y * s0 + t.y * s1,
        from.z * s0 + t.z * s1
    )
}

/**
 * 与帧率无关的平滑系数（计划书 §6.12-6）。
 * alpha = 1 - exp(-dt / tau)。
 */
fun smoothingAlpha(dtSec: Float, tauSec: Float): Float {
    require(dtSec >= 0f && tauSec > 0f)
    return (1f - kotlin.math.exp(-dtSec / tauSec)).coerceIn(0f, 1f)
}
