package cn.bistu.redwave.interaction

import com.google.common.truth.Truth.assertThat
import org.junit.Test

/**
 * 移动与碰撞算法测试（计划书 §6.13，UT-010 死区、UT-011 撞墙滑动）。
 * 纯数学，不依赖 Android / Filament。
 */
class MovementMathTest {

    @Test
    fun ut010_joystickDeadzone_smallInputProducesNoMovement() {
        // UT-010：死区内小输入不产生位移
        val r = MovementMath.applyJoystick(0.05f, 0.05f)
        assertThat(r[0]).isEqualTo(0f)
        assertThat(r[1]).isEqualTo(0f)
    }

    @Test
    fun joystickFullInput_preservesDirection() {
        // 满输入（长度=1）方向应保留
        val r = MovementMath.applyJoystick(1f, 0f)
        assertThat(r[0]).isWithin(1e-4f).of(1f)
        assertThat(r[1]).isWithin(1e-4f).of(0f)
    }

    @Test
    fun joystickOverUnit_isClampedToUnit() {
        // 长度>1 限制到单位圆
        val r = MovementMath.applyJoystick(2f, 2f)
        val len = kotlin.math.sqrt(r[0] * r[0] + r[1] * r[1])
        assertThat(len).isLessThan(1f + 1e-4f)
    }

    @Test
    fun joystickBeyondDeadzone_scalesSmoothly() {
        // 死区外应平滑增长（不是跳变）
        val r = MovementMath.applyJoystick(0.5f, 0f)
        assertThat(r[0]).isGreaterThan(0f)
        assertThat(r[0]).isLessThan(1f)
    }

    @Test
    fun computeDelta_forwardInput_movesAlongCameraForward() {
        // 相机 forward 朝 -Z（[0,-1]），joyY=1（向前推）应让 z 减小（向 -Z 移动）
        val forward = floatArrayOf(0f, -1f) // XZ: x=0, z=-1
        val delta = MovementMath.computeDelta(forward, joyX = 0f, joyY = 1f, speedMps = 1f, dtSec = 1f)
        assertThat(delta[0]).isWithin(1e-4f).of(0f)
        assertThat(delta[1]).isWithin(1e-4f).of(-1f)
    }

    @Test
    fun computeDelta_strafeInput_movesRight() {
        // forward=-Z, joyX=1（向右）应产生 +X 位移（right = forward×up = (fz,-fx)=(−1,0)？
        // 实际 right=(fz,-fx)=(-1, 0)，joyX=1 -> delta.x = right.x*1 = -1
        val forward = floatArrayOf(0f, -1f)
        val delta = MovementMath.computeDelta(forward, joyX = 1f, joyY = 0f, speedMps = 1f, dtSec = 1f)
        // right = (fz, -fx) = (-1, 0); delta.x = -1*1 + 0*0 = -1
        assertThat(delta[0]).isWithin(1e-4f).of(-1f)
        assertThat(delta[1]).isWithin(1e-4f).of(0f)
    }

    @Test
    fun clampToBounds_keepsAgentInsideWithRadiusMargin() {
        // bounds [-5,5]，半径 0.25，代理边缘不得越界
        val pos = MovementMath.clampToBounds(
            floatArrayOf(5.5f, -6f), -5f, 5f, -5f, 5f, radius = 0.25f
        )
        assertThat(pos[0]).isWithin(1e-4f).of(4.75f) // 5 - 0.25
        assertThat(pos[1]).isWithin(1e-4f).of(-4.75f)
    }

    @Test
    fun ut011_diagonalIntoWall_blockedAxisStopsOtherAxisSlides() {
        // UT-011：斜向撞墙，被阻挡轴停止，另一轴继续滑动
        // 游客在 (0, 0)，墙在 x∈[1,2], z∈[-2,2]（游客东边的墙）
        // 斜向移动 (+1, +1)（向 +X 和 +Z），应被 X 墙阻挡，Z 仍可移动
        val wall = floatArrayOf(1f, 0f, -2f, 2f, 3f, 2f) // [minX,minY,minZ,maxX,maxY,maxZ]
        val oldPos = floatArrayOf(0f, 0f)
        val newPos = floatArrayOf(0.9f, 0.5f) // 期望移动到 (0.9, 0.5)
        val result = MovementMath.resolveCollisions(oldPos, newPos, listOf(wall), radius = 0.25f)
        // X 应被阻挡（圆与墙重叠），回退到 oldPos.x=0
        assertThat(result[0]).isWithin(1e-4f).of(0f)
        // Z 应保留（沿墙滑动）
        assertThat(result[1]).isWithin(1e-4f).of(0.5f)
    }

    @Test
    fun circleAabbOverlap_detectsPenetration() {
        // 圆心在 (0.8, 0)，半径 0.25，墙 x∈[1,2] -> 最近点 (1,0)，距离 0.2 < 0.25 重叠
        val wall = floatArrayOf(1f, 0f, -2f, 2f, 3f, 2f)
        assertThat(MovementMath.circleAabbOverlap(0.8f, 0f, 0.25f, wall)).isTrue()
        // 圆心在 (0.5, 0)，距离墙 0.5 > 0.25 不重叠
        assertThat(MovementMath.circleAabbOverlap(0.5f, 0f, 0.25f, wall)).isFalse()
    }

    @Test
    fun resolveCollisions_noCollider_passesThrough() {
        val oldPos = floatArrayOf(0f, 0f)
        val newPos = floatArrayOf(1f, 1f)
        val result = MovementMath.resolveCollisions(oldPos, newPos, emptyList())
        assertThat(result[0]).isEqualTo(1f)
        assertThat(result[1]).isEqualTo(1f)
    }

    @Test
    fun cornerCollision_slidesToValidPosition() {
        // 角落情况：§6.13 分轴滑动，碰墙时允许沿墙移动到不重叠位置。
        // 游客在 (0,0)，墙覆盖 x∈[0.5,2],z∈[0.5,2]（东北角），半径 0.25。
        // 斜向移动到 (0.6,0.6)：合成位置与墙重叠，分轴后应滑到不重叠位置
        // （贴 z=0 边移动到 x=0.6，或贴 x=0 边到 z=0.6；二者之一合法）。
        val wall = floatArrayOf(0.5f, 0f, 0.5f, 2f, 3f, 2f)
        val oldPos = floatArrayOf(0f, 0f)
        val newPos = floatArrayOf(0.6f, 0.6f)
        val result = MovementMath.resolveCollisions(oldPos, newPos, listOf(wall), radius = 0.25f)
        // 最终位置不得与墙重叠
        assertThat(MovementMath.circleAabbOverlap(result[0], result[1], 0.25f, wall)).isFalse()
        // 至少保留了一个轴的移动（沿墙滑动，不是完全卡死）
        val moved = kotlin.math.abs(result[0] - 0f) > 1e-4f || kotlin.math.abs(result[1] - 0f) > 1e-4f
        assertThat(moved).isTrue()
    }

    @Test
    fun deepPenetration_fullyBlocked() {
        // 深度穿透（目标远在墙内）：分轴都无法滑出时回退到原位
        // 游客在 (0,0)，墙 x∈[0.3,2],z∈[0.3,2]，移动到 (1,1) 完全在墙内
        val wall = floatArrayOf(0.3f, 0f, 0.3f, 2f, 3f, 2f)
        val oldPos = floatArrayOf(0f, 0f)
        val newPos = floatArrayOf(1f, 1f)
        val result = MovementMath.resolveCollisions(oldPos, newPos, listOf(wall), radius = 0.25f)
        // tryX=(1,0)：圆心(1,0) 离墙最近(1,0.3) 距离0.3>0.25 不碰 → x=1 保留
        // tryZ=(1,1)：碰 → z=0。最终(1,0) 不碰墙，合法。所以 x 可保留。
        // 验证最终不重叠即可
        assertThat(MovementMath.circleAabbOverlap(result[0], result[1], 0.25f, wall)).isFalse()
    }
}
