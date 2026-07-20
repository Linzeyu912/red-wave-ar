package cn.bistu.redwave.interaction

import kotlin.math.sqrt

/**
 * 文物拾取的纯数学与逻辑（计划书 §6.14）。
 *
 * 不依赖 Android / Filament，可 JVM 单测。
 * View.pick 的异步 native 调用由 [PickingController] 桥接，本类只做可测的判定。
 */
object PickingMath {

    /**
     * §6.14：触摸坐标（左上原点）→ Filament Viewport 坐标（左下原点）。
     * Y 轴翻转：viewportY = surfaceHeight - touchY。
     */
    fun touchToViewport(touchX: Float, touchY: Float, surfaceHeight: Int): FloatArray {
        require(surfaceHeight > 0) { "surfaceHeight 必须为正" }
        return floatArrayOf(touchX, surfaceHeight - touchY)
    }

    /**
     * §6.14：游客到文物的水平距离判定。
     * 即使屏幕拾取命中，距离过远也只提示靠近，不直接打开内容。
     *
     * @param visitorXZ 游客水平位置 [x, z]
     * @param propXZ 文物水平位置 [x, z]
     * @param interactionRadiusM scene.json 的 interaction_radius_m
     * @return 距离（米）与是否在交互范围内
     */
    fun distanceAndReachable(
        visitorXZ: FloatArray,
        propXZ: FloatArray,
        interactionRadiusM: Float
    ): Pair<Float, Boolean> {
        require(visitorXZ.size == 2 && propXZ.size == 2) { "位置必须是 XZ 2 维" }
        require(interactionRadiusM > 0f) { "interactionRadius 必须为正" }
        val dx = visitorXZ[0] - propXZ[0]
        val dz = visitorXZ[1] - propXZ[1]
        val dist = sqrt(dx * dx + dz * dz)
        return dist to (dist <= interactionRadiusM)
    }

    /**
     * §6.14：根据 entity → propId 映射解析拾取结果。
     * 环境/装饰实体不在映射中，返回 null（不触发交互）。
     * 同一文物多个 mesh 都映射到同一 propId，命中任一即返回该 propId。
     */
    fun resolvePropId(pickedEntity: Int, entityToPropId: Map<Int, String>): String? {
        return entityToPropId[pickedEntity]
    }

    /**
     * §6.14：判断触摸点是否落在 UI 区域（避免点击 UI 穿透到 3D）。
     * 简化：UI 区域用矩形列表表示，触摸点在任一矩形内则视为点中 UI。
     */
    fun isTouchOnUi(touchX: Float, touchY: Float, uiRects: List<FloatArray>): Boolean {
        // 每个 rect = [left, top, right, bottom]（像素，左上原点）
        return uiRects.any { r ->
            r.size == 4 && touchX >= r[0] && touchX <= r[2] && touchY >= r[1] && touchY <= r[3]
        }
    }
}
