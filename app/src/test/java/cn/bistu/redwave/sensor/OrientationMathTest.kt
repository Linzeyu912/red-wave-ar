package cn.bistu.redwave.sensor

import com.google.common.truth.Truth.assertThat
import org.junit.Test

/**
 * 姿态算法规格测试（计划书 §6.12，UT-008 回正、UT-009 pitch 限幅）。
 * 纯四元数数学，不依赖 Android。
 */
class OrientationMathTest {

    private fun qApprox(a: Quaternion, b: Quaternion, tol: Float = 1e-3f): Boolean {
        // 四元数 q 与 -q 表示同一旋转，两种都要接受
        return OrientationMath.angleDegBetween(a, b) < 0.5f
    }

    @Test
    fun identityHasZeroYawPitch() {
        val (yaw, pitch) = OrientationMath.extractYawPitchDeg(Quaternion.IDENTITY)
        assertThat(yaw).isWithin(1e-3f).of(0f)
        assertThat(pitch).isWithin(1e-3f).of(0f)
    }

    @Test
    fun pureYaw180_negativeZForward() {
        // 绕 Y 180°：yaw 应为 180
        val q = OrientationMath.fromAxisAngle(0f, 1f, 0f, Math.PI)
        val (yaw, pitch) = OrientationMath.extractYawPitchDeg(q)
        assertThat(pitch).isWithin(1e-2f).of(0f)
        assertThat(kotlin.math.abs(yaw)).isWithin(1f).of(180f)
    }

    @Test
    fun ut008_recalibrate_makesCurrentOrientationZeroPoint() {
        // UT-008：回正后，当前姿态应变为视觉零点（relativeTo 返回近似单位）
        val qReference = OrientationMath.fromAxisAngle(0f, 1f, 0f, Math.toRadians(60.0))
        val qScreen = qReference // 设备姿态 == 基准
        val qRelative = OrientationMath.relativeTo(qScreen, qReference)
        // 回正：相对姿态应为单位四元数（零旋转）
        assertThat(qApprox(qRelative, Quaternion.IDENTITY)).isTrue()
        val (yaw, pitch) = OrientationMath.extractYawPitchDeg(qRelative)
        assertThat(kotlin.math.abs(yaw)).isWithin(0.5f).of(0f)
        assertThat(kotlin.math.abs(pitch)).isWithin(0.5f).of(0f)
    }

    @Test
    fun relativeOrientation_tracksDeviceRotation() {
        // 基准不动，设备再转 30° yaw，相对姿态应为 30° yaw
        val qReference = OrientationMath.fromAxisAngle(0f, 1f, 0f, Math.toRadians(10.0))
        val qScreen = OrientationMath.fromAxisAngle(0f, 1f, 0f, Math.toRadians(40.0))
        val qRelative = OrientationMath.relativeTo(qScreen, qReference)
        val (yaw, _) = OrientationMath.extractYawPitchDeg(qRelative)
        assertThat(kotlin.math.abs(yaw)).isWithin(0.5f).of(30f)
    }

    @Test
    fun ut009_touchPitchBeyondLimit_isClamped() {
        // UT-009：触屏 pitch 超过 ±80° 被限幅
        val q = OrientationMath.fromYawPitchDeg(0f, 135f)
        val (_, pitch) = OrientationMath.extractYawPitchDeg(q)
        assertThat(pitch).isAtMost(OrientationMath.PITCH_LIMIT_DEG + 0.1f)
        assertThat(pitch).isAtLeast(OrientationMath.PITCH_LIMIT_DEG - 0.5f)

        val q2 = OrientationMath.fromYawPitchDeg(0f, -135f)
        val (_, pitch2) = OrientationMath.extractYawPitchDeg(q2)
        assertThat(pitch2).isAtLeast(-OrientationMath.PITCH_LIMIT_DEG - 0.1f)
    }

    @Test
    fun touchPitchWithinLimit_notChanged() {
        val q = OrientationMath.fromYawPitchDeg(0f, 45f)
        val (_, pitch) = OrientationMath.extractYawPitchDeg(q)
        assertThat(pitch).isWithin(0.5f).of(45f)
    }

    @Test
    fun removeRoll_zeroesRollKeepsYawPitch() {
        // 构造一个带 roll 的姿态：yaw 30 + pitch 10 + roll 20
        val qYaw = OrientationMath.fromAxisAngle(0f, 1f, 0f, Math.toRadians(30.0))
        val qPitch = OrientationMath.fromAxisAngle(1f, 0f, 0f, Math.toRadians(10.0))
        val qRoll = OrientationMath.fromAxisAngle(0f, 0f, 1f, Math.toRadians(20.0))
        val qWithRoll = qYaw * qPitch * qRoll
        val (yawPitch, noRoll) = OrientationMath.removeRoll(qWithRoll)
        val yaw = yawPitch.first
        val pitch = yawPitch.second
        // 去 roll 后 yaw/pitch 应接近原值（数值精度内）
        assertThat(kotlin.math.abs(yaw - 30f)).isLessThan(2f)
        assertThat(kotlin.math.abs(pitch - 10f)).isLessThan(2f)
        // noRoll 的 roll 分量应极小：其与纯 yaw*pitch 应近似
        val expected = (qYaw * qPitch).normalized()
        assertThat(qApprox(noRoll, expected)).isTrue()
    }

    @Test
    fun slerp_endpointsReproduce() {
        val a = OrientationMath.fromAxisAngle(0f, 1f, 0f, 0.0)
        val b = OrientationMath.fromAxisAngle(0f, 1f, 0f, Math.PI / 2)
        assertThat(qApprox(slerp(a, b, 0f), a)).isTrue()
        assertThat(qApprox(slerp(a, b, 1f), b)).isTrue()
    }

    @Test
    fun slerp_midpointIsHalfAngle() {
        val a = OrientationMath.fromAxisAngle(0f, 1f, 0f, 0.0)
        val b = OrientationMath.fromAxisAngle(0f, 1f, 0f, Math.PI / 2)
        val mid = slerp(a, b, 0.5f)
        val (yaw, _) = OrientationMath.extractYawPitchDeg(mid)
        assertThat(kotlin.math.abs(yaw)).isWithin(1f).of(45f)
    }

    @Test
    fun smoothingAlpha_isFrameRateIndependent() {
        // §6.12-6: alpha = 1 - exp(-dt/tau)
        // dt=0 时 alpha=0；dt→∞ 时 alpha→1；tau 越大越平滑（alpha 越小）
        assertThat(smoothingAlpha(0f, 0.12f)).isWithin(1e-6f).of(0f)
        assertThat(smoothingAlpha(10f, 0.12f)).isGreaterThan(0.999f)
        // tau 大 -> 同 dt 下 alpha 小（更平滑）
        assertThat(smoothingAlpha(0.016f, 0.12f)).isGreaterThan(smoothingAlpha(0.016f, 0.5f))
    }

    @Test
    fun smooth_convergesToTarget() {
        var current = Quaternion.IDENTITY
        val target = OrientationMath.fromAxisAngle(0f, 1f, 0f, Math.toRadians(90.0))
        // 多帧平滑后应收敛到 target
        for (i in 1..300) {
            current = OrientationMath.smooth(current, target, 0.016f, 0.12f)
        }
        assertThat(qApprox(current, target)).isTrue()
    }

    @Test
    fun screenRotation_composesAroundZ() {
        val qDevice = OrientationMath.fromAxisAngle(0f, 1f, 0f, Math.toRadians(30.0))
        val q0 = OrientationMath.applyScreenRotation(qDevice, OrientationMath.SCREEN_ROT_0)
        val q90 = OrientationMath.applyScreenRotation(qDevice, OrientationMath.SCREEN_ROT_90)
        // ROT_90 相对 ROT_0 应有约 90° 差
        val diff = OrientationMath.angleDegBetween(q0, q90)
        assertThat(diff).isWithin(1f).of(90f)
    }

    @Test
    fun inverse_timesSelf_isIdentity() {
        val q = OrientationMath.fromAxisAngle(0f, 1f, 0f, Math.toRadians(45.0))
        val product = q * q.inverse()
        assertThat(qApprox(product, Quaternion.IDENTITY)).isTrue()
    }
}
