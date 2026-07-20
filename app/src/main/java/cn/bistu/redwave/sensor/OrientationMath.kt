package cn.bistu.redwave.sensor

import kotlin.math.PI
import kotlin.math.abs
import kotlin.math.atan2
import kotlin.math.cos
import kotlin.math.sin
import kotlin.math.sqrt

/**
 * 姿态算法规格（计划书 §6.12）的纯数学实现。
 *
 * 不依赖 Android，可 JVM 单测（覆盖 UT-008 回正、UT-009 pitch 限幅）。
 * SensorManager / 屏幕方向读取由 [OrientationController] 注入。
 */
object OrientationMath {

    /** 屏幕旋转角度（度），对应 Android Surface.ROTATION_0/90/180/270。 */
    const val SCREEN_ROT_0 = 0
    const val SCREEN_ROT_90 = 90
    const val SCREEN_ROT_180 = 180
    const val SCREEN_ROT_270 = 270

    /** pitch 限幅（度），避免翻转（§6.12 触屏模式）。 */
    const val PITCH_LIMIT_DEG = 80f

    /**
     * §6.12-2：按屏幕方向重映射设备坐标到屏幕坐标。
     * 返回绕 Z 轴旋转 screenRotationDeg 的四元数，与 q_device 复合。
     */
    fun applyScreenRotation(qDevice: Quaternion, screenRotationDeg: Int): Quaternion {
        val rad = Math.toRadians(screenRotationDeg.toDouble())
        val half = (rad / 2.0)
        val sin = sin(half)
        val cos = cos(half)
        // 绕屏幕 Z 轴（垂直屏幕向外）旋转
        val qScreen = Quaternion(cos.toFloat(), 0f, 0f, sin.toFloat())
        return qScreen * qDevice
    }

    /**
     * §6.12-3/4：相对姿态 q_relative = inverse(q_reference) * q_screen。
     * 回正即更新 q_reference 为当前 q_screen（§6.12-3）。
     */
    fun relativeTo(qScreen: Quaternion, qReference: Quaternion): Quaternion {
        return qReference.inverse() * qScreen
    }

    /**
     * §6.12-5：默认去 roll，只保留 yaw/pitch。
     * 做法：从 q 提取 yaw/pitch，重新构造无 roll 的四元数。
     *
     * 返回 (yawDeg, pitchDeg) 与去 roll 后的四元数。
     */
    fun removeRoll(q: Quaternion): Pair<Pair<Float, Float>, Quaternion> {
        val (yawDeg, pitchDeg) = extractYawPitchDeg(q)
        val yawRad = Math.toRadians(yawDeg.toDouble())
        val pitchRad = Math.toRadians(pitchDeg.toDouble())
        // 绕 Y（yaw）后绕 X（pitch），无 Z（roll）
        val qYaw = fromAxisAngle(0f, 1f, 0f, yawRad)
        val qPitch = fromAxisAngle(1f, 0f, 0f, pitchRad)
        val noRoll = (qYaw * qPitch).normalized()
        return (yawDeg to pitchDeg) to noRoll
    }

    /**
     * 从四元数提取 yaw（绕世界 Y）与 pitch（绕局部 X），单位度。
     *
     * 约定：右手系，Y-up，-Z 朝前为 yaw=pitch=0。
     * 用旋转矩阵的 forward 向量（-Z 列）反推，对任意旋转稳健、无象限歧义：
     *   forward = R · (0, 0, -1)  即矩阵第三列取反后的水平分量。
     *
     * yaw  = atan2(-forward.x, -forward.z)   （水平朝向角）
     * pitch = atan2(forward.y, |forwardXZ|)  （俯仰角）
     */
    fun extractYawPitchDeg(q: Quaternion): Pair<Float, Float> {
        val w = q.w; val x = q.x; val y = q.y; val z = q.z
        // 旋转矩阵第三列（列向量约定）：R[0][2], R[1][2], R[2][2]
        val c02 = 2f * (x * z + w * y)
        val c12 = 2f * (y * z - w * x)
        val c22 = 1f - 2f * (x * x + y * y)
        // forward = R · (0,0,-1) = (-c02, -c12, -c22)
        val fx = -c02
        val fy = -c12
        val fz = -c22

        val yawRad = atan2(-fx, -fz)
        val horizMag = sqrt(fx * fx + fz * fz)
        val pitchRad = atan2(fy, horizMag)

        return Math.toDegrees(yawRad.toDouble()).toFloat() to
            Math.toDegrees(pitchRad.toDouble()).toFloat()
    }

    /**
     * 由 yaw/pitch 构造四元数（用于触屏模式：拖动改 yaw/pitch）。
     * pitch 会被限幅到 [-PITCH_LIMIT_DEG, PITCH_LIMIT_DEG]（§6.12 触屏）。
     */
    fun fromYawPitchDeg(yawDeg: Float, pitchDeg: Float): Quaternion {
        val limitedPitch = pitchDeg.coerceIn(-PITCH_LIMIT_DEG, PITCH_LIMIT_DEG)
        val qYaw = fromAxisAngle(0f, 1f, 0f, Math.toRadians(yawDeg.toDouble()))
        val qPitch = fromAxisAngle(1f, 0f, 0f, Math.toRadians(limitedPitch.toDouble()))
        return (qYaw * qPitch).normalized()
    }

    /** 绕单位轴 (ax,ay,az) 旋转 angleRad 弧度。 */
    fun fromAxisAngle(ax: Float, ay: Float, az: Float, angleRad: Double): Quaternion {
        val half = angleRad / 2.0
        val s = sin(half)
        return Quaternion(cos(half).toFloat(), (ax * s).toFloat(), (ay * s).toFloat(), (az * s).toFloat()).normalized()
    }

    /**
     * §6.12-6 slerp 平滑：用与帧率无关的 alpha 对 target 做平滑。
     * 返回平滑后的四元数。
     */
    fun smooth(current: Quaternion, target: Quaternion, dtSec: Float, tauSec: Float): Quaternion {
        if (dtSec <= 0f) return current
        val alpha = smoothingAlpha(dtSec, tauSec)
        return slerp(current, target, alpha)
    }

    /** 两个四元数的角度差（度），用于判断是否需要回正或稳定。 */
    fun angleDegBetween(a: Quaternion, b: Quaternion): Float {
        val dot = abs(a.w * b.w + a.x * b.x + a.y * b.y + a.z * b.z).coerceAtMost(1f)
        val theta = 2f * kotlin.math.acos(dot)
        return Math.toDegrees(theta.toDouble()).toFloat()
    }

    /**
     * 由姿态四元数与眼点位置，计算 Filament Camera.lookAt 所需的 9 参数：
     * (eye, center, up)。center = eye + forward，forward = R(q)·(0,0,-1)。
     *
     * 计划书 §6.12-7：相机朝向由姿态算法控制，位置由 MovementController 独立维护。
     * 此处只给定 eye，朝向由 q 决定。
     *
     * 返回 double[9]：[ex,ey,ez, cx,cy,cz, ux,uy,uz]
     */
    fun lookAtParams(q: Quaternion, eyeX: Double, eyeY: Double, eyeZ: Double): DoubleArray {
        val forward = forwardVector(q) // 单位 forward（-Z 方向旋转后）
        val cx = eyeX + forward[0]
        val cy = eyeY + forward[1]
        val cz = eyeZ + forward[2]
        // up = R(q)·(0,1,0)
        val up = upVector(q)
        return doubleArrayOf(
            eyeX, eyeY, eyeZ,
            cx, cy, cz,
            up[0].toDouble(), up[1].toDouble(), up[2].toDouble()
        )
    }

    /** 旋转后的 forward 向量（单位，-Z 朝前）。 */
    fun forwardVector(q: Quaternion): FloatArray {
        val w = q.w; val x = q.x; val y = q.y; val z = q.z
        val c02 = 2f * (x * z + w * y)
        val c12 = 2f * (y * z - w * x)
        val c22 = 1f - 2f * (x * x + y * y)
        // forward = R · (0,0,-1) = (-c02, -c12, -c22)
        return floatArrayOf(-c02, -c12, -c22)
    }

    /** 旋转后的 up 向量（单位，+Y）。 */
    fun upVector(q: Quaternion): FloatArray {
        val w = q.w; val x = q.x; val y = q.y; val z = q.z
        // R · (0,1,0) = 矩阵第二列：(2(xy-wz), 1-2(x²+z²), 2(yz+wx))
        return floatArrayOf(
            2f * (x * y - w * z),
            1f - 2f * (x * x + z * z),
            2f * (y * z + w * x)
        )
    }
}
