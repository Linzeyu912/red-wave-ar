package cn.bistu.redwave.interaction

import cn.bistu.redwave.data.Prop
import com.google.common.truth.Truth.assertThat
import org.junit.Test

/**
 * 文物拾取逻辑测试（计划书 §6.14，UT-012 token、距离限制、坐标转换）。
 */
class PickingTest {

    private fun prop(
        id: String,
        x: Float, z: Float,
        radius: Float = 1.5f
    ): Prop = Prop(
        id = id,
        glb = "props/$id.glb",
        positionM = listOf(x, 0.8f, z),
        rotationDeg = listOf(0f, 0f, 0f),
        scale = 1f,
        interactionRadiusM = radius,
        highlightAnchorM = listOf(0f, 0.5f, 0f)
    )

    @Test
    fun touchToViewport_flipsYAxis() {
        // §6.14：触摸左上原点 → viewport 左下原点
        val v = PickingMath.touchToViewport(100f, 200f, surfaceHeight = 1080)
        assertThat(v[0]).isEqualTo(100f)
        assertThat(v[1]).isEqualTo(880f) // 1080 - 200
    }

    @Test
    fun distanceAndReachable_withinRadius_isReachable() {
        val (dist, reach) = PickingMath.distanceAndReachable(
            visitorXZ = floatArrayOf(0f, 0f),
            propXZ = floatArrayOf(1f, 0f),
            interactionRadiusM = 1.5f
        )
        assertThat(dist).isWithin(1e-4f).of(1f)
        assertThat(reach).isTrue()
    }

    @Test
    fun distanceAndReachable_beyondRadius_notReachable() {
        val (dist, reach) = PickingMath.distanceAndReachable(
            visitorXZ = floatArrayOf(0f, 0f),
            propXZ = floatArrayOf(2f, 0f),
            interactionRadiusM = 1.5f
        )
        assertThat(dist).isWithin(1e-4f).of(2f)
        assertThat(reach).isFalse()
    }

    @Test
    fun resolvePropId_environmentEntity_returnsNull() {
        // 环境实体不在映射中
        val map = mapOf(100 to "p_s1_radio", 101 to "p_s1_radio")
        assertThat(PickingMath.resolvePropId(999, map)).isNull()
        assertThat(PickingMath.resolvePropId(100, map)).isEqualTo("p_s1_radio")
    }

    @Test
    fun resolvePropId_multipleMeshesSamePropId() {
        // §6.14：同一文物多个 mesh 映射同一 propId
        val map = mapOf(100 to "p_s1_radio", 101 to "p_s1_radio", 102 to "p_s1_radio")
        assertThat(PickingMath.resolvePropId(101, map)).isEqualTo("p_s1_radio")
    }

    @Test
    fun isTouchOnUi_blocksClickThroughTo3D() {
        // §6.14：点击 UI 不穿透到 3D
        val uiRects = listOf(floatArrayOf(0f, 900f, 2400f, 1080f)) // 底部信息卡区
        assertThat(PickingMath.isTouchOnUi(100f, 1000f, uiRects)).isTrue()
        assertThat(PickingMath.isTouchOnUi(100f, 100f, uiRects)).isFalse()
    }

    @Test
    fun ut012_staleToken_isIgnored() {
        // UT-012：场景 token 变化，旧拾取回调被忽略
        val ctrl = PickingController()
        ctrl.enterScene()
        val oldToken = ctrl.currentToken()
        // 模拟页面退出再进入新场景
        ctrl.exitScene()
        ctrl.enterScene()
        val decision = ctrl.handlePickResult(
            callbackToken = oldToken, // 旧 token
            pickedEntity = 100,
            entityToPropId = mapOf(100 to "p_s1_radio"),
            props = listOf(prop("p_s1_radio", 0f, 0f)),
            visitorXZ = floatArrayOf(0f, 0f)
        )
        assertThat(decision).isEqualTo(PickingController.PickingDecision.Stale)
        assertThat(ctrl.selectedPropId).isNull()
    }

    @Test
    fun pickHitInRadius_selectsProp() {
        val ctrl = PickingController()
        ctrl.enterScene()
        val token = ctrl.currentToken()
        val decision = ctrl.handlePickResult(
            callbackToken = token,
            pickedEntity = 100,
            entityToPropId = mapOf(100 to "p_s1_radio"),
            props = listOf(prop("p_s1_radio", 1f, 0f, radius = 2f)),
            visitorXZ = floatArrayOf(0f, 0f)
        )
        assertThat(decision).isInstanceOf(PickingController.PickingDecision.SelectProp::class.java)
        assertThat(ctrl.selectedPropId).isEqualTo("p_s1_radio")
    }

    @Test
    fun pickHitBeyondRadius_returnsTooFar() {
        val ctrl = PickingController()
        ctrl.enterScene()
        val token = ctrl.currentToken()
        val decision = ctrl.handlePickResult(
            callbackToken = token,
            pickedEntity = 100,
            entityToPropId = mapOf(100 to "p_s1_radio"),
            props = listOf(prop("p_s1_radio", 5f, 0f, radius = 1.5f)),
            visitorXZ = floatArrayOf(0f, 0f)
        )
        assertThat(decision).isInstanceOf(PickingController.PickingDecision.TooFar::class.java)
        assertThat(ctrl.selectedPropId).isNull() // 过远不选中
    }

    @Test
    fun pickEnvironment_deselects() {
        val ctrl = PickingController()
        ctrl.enterScene()
        val token = ctrl.currentToken()
        // 先选中一个
        ctrl.handlePickResult(token, 100, mapOf(100 to "p_s1_radio"),
            listOf(prop("p_s1_radio", 0f, 0f)), floatArrayOf(0f, 0f))
        assertThat(ctrl.selectedPropId).isEqualTo("p_s1_radio")
        // 点击空白（entity 0）
        val decision = ctrl.handlePickResult(token, 0, mapOf(100 to "p_s1_radio"),
            listOf(prop("p_s1_radio", 0f, 0f)), floatArrayOf(0f, 0f))
        assertThat(decision).isEqualTo(PickingController.PickingDecision.Deselect)
        assertThat(ctrl.selectedPropId).isNull()
    }
}
