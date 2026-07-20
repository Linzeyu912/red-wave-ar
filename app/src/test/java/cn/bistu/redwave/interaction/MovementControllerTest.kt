package cn.bistu.redwave.interaction

import cn.bistu.redwave.data.Collider
import cn.bistu.redwave.data.Movement
import cn.bistu.redwave.data.MovePoint
import com.google.common.truth.Truth.assertThat
import org.junit.Test

/**
 * MovementController 集成流程测试（计划书 §6.13）。
 */
class MovementControllerTest {

    private fun makeController(
        startX: Float = 0f,
        startZ: Float = 0f,
        colliders: List<Collider> = emptyList(),
        movePoints: List<MovePoint> = emptyList()
    ): MovementController {
        val movement = Movement(
            type = "bounds", speedMps = 1.0f,
            xMinM = -5f, xMaxM = 5f, zMinM = -5f, zMaxM = 5f
        )
        return MovementController(movement, colliders, movePoints, startX, startZ)
    }

    @Test
    fun joystickForward_movesVisitorInForwardDirection() {
        val ctrl = makeController(startX = 0f, startZ = 0f)
        ctrl.setJoystick(0f, 1f) // 向前
        val forward = floatArrayOf(0f, -1f) // 相机朝 -Z
        // 用 dt=0.05（§6.13 dt 上限内），1m/s × 0.05s = 0.05m 向 -Z
        val pos = ctrl.update(forward, dtSec = 0.05f)
        assertThat(pos[1]).isWithin(1e-4f).of(-0.05f)
        assertThat(pos[0]).isWithin(1e-4f).of(0f)
    }

    @Test
    fun deadzone_noMovement() {
        val ctrl = makeController()
        ctrl.setJoystick(0.05f, 0.05f) // 死区内
        val pos = ctrl.update(floatArrayOf(0f, -1f), dtSec = 1f)
        assertThat(pos[0]).isEqualTo(0f)
        assertThat(pos[1]).isEqualTo(0f)
    }

    @Test
    fun boundsClamp_preventsLeavingPlayableArea() {
        val ctrl = makeController(startX = 4.8f, startZ = 0f)
        ctrl.setJoystick(1f, 0f) // 向 +X 全速
        // 向 +X 但 nears 边界 5-0.25=4.75，从 4.8 出发应被钳制
        val pos = ctrl.update(floatArrayOf(0f, -1f), dtSec = 1f)
        assertThat(pos[0]).isAtMost(4.75f + 1e-4f)
    }

    @Test
    fun hotspotMove_transitionsPosition() {
        val mp = MovePoint(
            id = "mp_radio",
            positionM = listOf(2f, 1.6f, 3f),
            lookAtM = listOf(0f, 1f, 0f)
        )
        val ctrl = makeController(startX = 0f, startZ = 0f, movePoints = listOf(mp))
        val triggered = ctrl.moveToHotspot("mp_radio")
        assertThat(triggered).isTrue()
        assertThat(ctrl.isMovingToHotspot()).isTrue()
        // 推进过半后位置应跳到目标 (2, 3)
        ctrl.update(floatArrayOf(0f, -1f), dtSec = 0.2f) // 淡出阶段
        ctrl.update(floatArrayOf(0f, -1f), dtSec = 0.2f) // 进入淡入，位置=目标
        assertThat(ctrl.visitorPosition[0]).isWithin(1e-4f).of(2f)
        assertThat(ctrl.visitorPosition[1]).isWithin(1e-4f).of(3f)
    }

    @Test
    fun hotspotMove_unknownId_returnsFalse() {
        val ctrl = makeController()
        assertThat(ctrl.moveToHotspot("nonexistent")).isFalse()
    }

    @Test
    fun hotspotMove_blocksJoystickDuringTransition() {
        val mp = MovePoint("mp", listOf(2f, 1.6f, 3f), listOf(0f, 1f, 0f))
        val ctrl = makeController(movePoints = listOf(mp))
        ctrl.moveToHotspot("mp")
        ctrl.setJoystick(1f, 1f) // 移动期间摇杆
        val pos = ctrl.update(floatArrayOf(0f, -1f), dtSec = 0.1f)
        // 热点移动期间摇杆被忽略，位置不变（在 from 处）
        assertThat(pos[0]).isEqualTo(0f)
        assertThat(pos[1]).isEqualTo(0f)
    }

    @Test
    fun dtClamp_preventsTeleportOnLargeDt() {
        // §6.13：dt 上限 50ms，防止后台恢复一步穿墙
        val ctrl = makeController(startX = 0f, startZ = 0f)
        ctrl.setJoystick(0f, 1f)
        val pos = ctrl.update(floatArrayOf(0f, -1f), dtSec = 10f) // 异常大 dt
        // 应被截断到 50ms：1m/s × 0.05s = 0.05m
        assertThat(kotlin.math.abs(pos[1])).isLessThan(0.06f)
    }
}
