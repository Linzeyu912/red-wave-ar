package cn.bistu.redwave.interaction

import cn.bistu.redwave.data.Collider
import cn.bistu.redwave.data.Movement
import cn.bistu.redwave.data.MovePoint
import kotlin.math.sqrt

/**
 * 虚拟移动控制器（计划书 §6.6 interaction、§6.13）。
 *
 * 职责：
 * - 维护游客位置 [visitorPosition]（§6.13-4）；
 * - 摇杆输入（死区 + 视线投影 + 限速 + bounds + AABB 滑动）；
 * - 热点移动（200-400ms 淡出/淡入切换位置，§6.13）；
 * - 每帧 onUpdateMovement 推进（由 SceneRenderer 调用）。
 *
 * 姿态只改视线方向，不修改位置（§6.13）；位置由本类独立维护。
 * 纯碰撞算法在 [MovementMath]，可单测。
 */
class MovementController(
    movement: Movement,
    colliders: List<Collider>,
    private val movePoints: List<MovePoint>,
    startX: Float,
    startZ: Float
) {
    private val xMin = movement.xMinM
    private val xMax = movement.xMaxM
    private val zMin = movement.zMinM
    private val zMax = movement.zMaxM
    private val speedMps = movement.speedMps

    // collider 转 [minX,minY,minZ,maxX,maxY,maxZ]
    private val colliderAabbs: List<FloatArray> = colliders.map { c ->
        floatArrayOf(c.minM[0], c.minM[1], c.minM[2], c.maxM[0], c.maxM[1], c.maxM[2])
    }

    /** 当前游客水平位置 [x, z]（眼高 Y 固定，不在此维护）。 */
    var visitorPosition: FloatArray = floatArrayOf(startX, startZ)
        private set

    /** 当前摇杆输入（归一化前），由 UI 设置。 */
    @Volatile
    private var joystickInput: FloatArray = floatArrayOf(0f, 0f)

    // 热点移动动画状态
    private var hotspotActive: Boolean = false
    private var hotspotElapsed: Float = 0f
    private var hotspotFrom: FloatArray = visitorPosition.copyOf()
    private var hotspotTo: FloatArray = visitorPosition.copyOf()
    /** 热点淡入淡出总时长（§6.13：200-400ms）。 */
    private val hotspotDurationSec: Float = 0.3f

    /** 热点移动期间是否处于"淡出"（黑屏过渡）阶段，UI 据此显示过渡。 */
    var inHotspotTransition: Boolean = false
        private set

    /** 设置摇杆输入（UI 调用）。 */
    fun setJoystick(x: Float, y: Float) {
        joystickInput = floatArrayOf(x, y)
    }

    /**
     * 触发热点移动（§6.13）。
     * @param movePointId scene.json move_points[].id
     * @return 是否成功触发（id 存在且当前未在移动中）
     */
    fun moveToHotspot(movePointId: String): Boolean {
        if (hotspotActive) return false
        val target = movePoints.firstOrNull { it.id == movePointId } ?: return false
        hotspotFrom = visitorPosition.copyOf()
        hotspotTo = floatArrayOf(target.positionM[0], target.positionM[2])
        hotspotElapsed = 0f
        hotspotActive = true
        inHotspotTransition = true
        return true
    }

    /**
     * 每帧推进移动（由 SceneRenderer.onUpdateMovement 调用）。
     * @param cameraForwardXZ 相机 forward 投影到 XZ 的单位向量 [fx, fz]
     * @param dtSec 帧时间（秒）
     * @return 新位置 [x, z]
     */
    fun update(cameraForwardXZ: FloatArray, dtSec: Float): FloatArray {
        // 热点移动优先（期间禁用摇杆，§6.13 淡入淡出避免眩晕）。
        // 热点是时间动画，用原始 dt（不受穿墙截断影响）。
        if (hotspotActive) {
            hotspotElapsed += dtSec
            val t = (hotspotElapsed / hotspotDurationSec).coerceIn(0f, 1f)
            // 淡出（前半）-> 瞬移 -> 淡入（后半）；位置在 t=0.5 时跳到目标
            visitorPosition = if (t < 0.5f) {
                hotspotFrom
            } else {
                hotspotTo
            }
            if (t >= 1f) {
                hotspotActive = false
                inHotspotTransition = false
                visitorPosition = hotspotTo.copyOf()
            }
            return visitorPosition
        }

        // §6.13：摇杆位移的 dt 上限 50ms，防止后台恢复一步穿墙
        val dt = dtSec.coerceAtMost(0.05f)
        val (jx, jy) = MovementMath.applyJoystick(joystickInput[0], joystickInput[1])
        if (jx == 0f && jy == 0f) return visitorPosition // 死区内不动

        val delta = MovementMath.computeDelta(cameraForwardXZ, jx, jy, speedMps, dt)
        val desired = floatArrayOf(visitorPosition[0] + delta[0], visitorPosition[1] + delta[1])
        // bounds 钳制
        val clamped = MovementMath.clampToBounds(desired, xMin, xMax, zMin, zMax)
        // 碰撞分轴滑动
        visitorPosition = MovementMath.resolveCollisions(visitorPosition, clamped, colliderAabbs)
        return visitorPosition
    }

    /** 供诊断：当前是否在热点移动中。 */
    fun isMovingToHotspot(): Boolean = hotspotActive
}
