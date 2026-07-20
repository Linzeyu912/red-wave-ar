package cn.bistu.redwave.interaction

import kotlin.math.PI
import kotlin.math.abs
import kotlin.math.cos
import kotlin.math.sin
import kotlin.math.sqrt

/**
 * 虚拟移动与碰撞的纯数学（计划书 §6.13）。
 *
 * 不依赖 Android / Filament，可 JVM 单测（UT-010 死区、UT-011 撞墙滑动）。
 *
 * 约定：Y-up，水平面为 XZ；游客用半径 r 的 2D 圆形代理（不是无体积点）。
 */
object MovementMath {

    /** 游客圆形代理半径（§6.13：约 0.25 m）。 */
    const val VISITOR_RADIUS_M = 0.25f

    /** 摇杆死区（输入幅度低于此值视为 0，避免漂移）。 */
    const val JOYSTICK_DEADZONE = 0.12f

    /**
     * §6.13：摇杆输入归一化。
     * 长度先限制到 1，再应用死区；死区内输出 (0,0)。
     * @return 归一化后的 (x, y)，长度 <= 1
     */
    fun applyJoystick(inputX: Float, inputY: Float, deadzone: Float = JOYSTICK_DEADZONE): FloatArray {
        val len = sqrt(inputX * inputX + inputY * inputY)
        if (len < deadzone) return floatArrayOf(0f, 0f)
        // 限制到单位圆
        val clampedLen = len.coerceAtMost(1f)
        // 死区外重新映射幅度，使越过死区后从 0 平滑增长
        val scaled = (clampedLen - deadzone) / (1f - deadzone).coerceAtLeast(1e-6f)
        val k = scaled / len
        return floatArrayOf(inputX * k, inputY * k)
    }

    /**
     * §6.13：把摇杆输入投影到水平移动方向。
     * forward = normalize(projectToXZ(cameraForward))
     * right = normalize(cross(forward, worldUp))
     * delta = (right * joyX + forward * joyY) * speed * dt
     *
     * @param cameraForwardXZ 相机 forward 投影到 XZ 后的单位向量 [fx, fz]
     * @param joyX, joyY 归一化摇杆输入
     * @return 位移增量 (dx, dz)
     */
    fun computeDelta(
        cameraForwardXZ: FloatArray,
        joyX: Float,
        joyY: Float,
        speedMps: Float,
        dtSec: Float
    ): FloatArray {
        require(cameraForwardXZ.size == 2) { "forward 必须是 XZ 2 维" }
        val fx = cameraForwardXZ[0]
        val fz = cameraForwardXZ[1]
        // right = forward × up(0,1,0) = (fz, 0, -fx) 投影到 XZ -> (fz, -fx)
        val rx = fz
        val rz = -fx
        // §6.13 dt 上限 50ms 由调用方（SceneRenderer/MovementController）保证；
        // 本纯函数不重复截断，便于单测用任意 dt 验证速度。
        val dx = (rx * joyX + fx * joyY) * speedMps * dtSec
        val dz = (rz * joyX + fz * joyY) * speedMps * dtSec
        return floatArrayOf(dx, dz)
    }

    /**
     * §6.13：movement bounds 钳制。
     * 游客圆形代理的边界检查：代理边缘不得超出 bounds。
     */
    fun clampToBounds(
        pos: FloatArray, // [x, z]
        xMin: Float, xMax: Float,
        zMin: Float, zMax: Float,
        radius: Float = VISITOR_RADIUS_M
    ): FloatArray {
        val x = pos[0].coerceIn(xMin + radius, xMax - radius)
        val z = pos[1].coerceIn(zMin + radius, zMax - radius)
        return floatArrayOf(x, z)
    }

    /**
     * §6.13：圆形代理与 AABB collider 的分轴滑动碰撞。
     *
     * 算法：对每个 collider，检查新位置（代理圆）是否与之重叠；
     * 若重叠，按分轴（X、Z 分别）回退到不重叠位置，允许沿墙滑动。
     *
     * @param oldPos 上一帧位置 [x, z]（未碰墙）
     * @param newPos 本帧期望位置 [x, z]（经 bounds 钳制后）
     * @param colliders AABB 列表，每个 [minX, minY, minZ, maxX, maxY, maxZ]
     * @param radius 代理半径
     * @return 碰撞处理后的位置 [x, z]（碰墙轴被阻挡，另一轴保留）
     */
    fun resolveCollisions(
        oldPos: FloatArray,
        newPos: FloatArray,
        colliders: List<FloatArray>, // 每个 [minX,minY,minZ,maxX,maxY,maxZ]
        radius: Float = VISITOR_RADIUS_M
    ): FloatArray {
        var x = newPos[0]
        var z = newPos[1]
        val ox = oldPos[0]
        val oz = oldPos[1]

        for (c in colliders) {
            require(c.size == 6) { "collider 必须是 6 维 AABB" }
            // 跳过 Y 不重叠的 collider（游客在地面，collider 的 Y 范围覆盖地面即可）
            // 这里假设所有 collider 都可能阻挡地面游客，不提前按 Y 剔除。

            // 分轴检查：先尝试只移动 X
            val tryX = floatArrayOf(x, oz)
            if (circleAabbOverlap(tryX[0], tryX[1], radius, c)) {
                // X 轴被阻挡：回退到 oldPos.x（保持原 X，允许 Z 变化=沿墙滑动）
                x = ox
            }
            // 再尝试只移动 Z（基于可能更新后的 x）
            val tryZ = floatArrayOf(x, z)
            if (circleAabbOverlap(tryZ[0], tryZ[1], radius, c)) {
                z = oz
            }
            // 用最终位置再做一次整体检查，若仍重叠则两轴都回退（角落情况）
            if (circleAabbOverlap(x, z, radius, c)) {
                x = ox
                z = oz
            }
        }
        return floatArrayOf(x, z)
    }

    /**
     * 圆 (cx,cz,r) 与 AABB [minX..maxX, minZ..maxZ] 是否重叠（2D，忽略 Y）。
     * 找 AABB 上离圆心最近的点，比较距离与半径。
     */
    fun circleAabbOverlap(cx: Float, cz: Float, r: Float, aabb: FloatArray): Boolean {
        val nearestX = cx.coerceIn(aabb[0], aabb[3])
        val nearestZ = cz.coerceIn(aabb[2], aabb[5])
        val dx = cx - nearestX
        val dz = cz - nearestZ
        return (dx * dx + dz * dz) < (r * r)
    }
}
