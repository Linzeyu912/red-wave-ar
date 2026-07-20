package cn.bistu.redwave.interaction

import cn.bistu.redwave.data.Prop
import java.util.concurrent.atomic.AtomicLong

/**
 * 文物拾取控制器（计划书 §6.6 interaction、§6.14）。
 *
 * 职责：
 * - 触发 Filament View.pick（异步）；
 * - 用 Scene token 核对回调，页面退出/切场景后旧回调作废（§6.14，UT-012）；
 * - entity → propId 解析 + 距离限制（§6.14 interaction_radius_m）；
 * - 维护选中 propId 供 Compose 信息卡展示。
 *
 * 纯判定逻辑在 [PickingMath]，本类管理 native pick 调用与状态。
 */
class PickingController {

    /** 拾取决策结果。 */
    sealed interface PickingDecision {
        /** 命中可交互文物，打开信息卡。 */
        data class SelectProp(val propId: String, val titleHint: String) : PickingDecision
        /** 命中但距离过远，提示靠近（§6.14）。 */
        data class TooFar(val propId: String, val distanceM: Float) : PickingDecision
        /** 命中环境/空白或 UI，关闭信息卡。 */
        data object Deselect : PickingDecision
        /** 旧 token 回调，忽略（§6.14）。 */
        data object Stale : PickingDecision
    }

    private val tokenCounter = AtomicLong(0L)
    private var currentToken: Long = 0L

    /** 当前选中的 propId（供 UI 显示信息卡）；null 表示无选中。 */
    @Volatile
    var selectedPropId: String? = null
        private set

    /** 进入新场景时递增 token，作废旧回调。 */
    fun enterScene() {
        currentToken = tokenCounter.incrementAndGet()
        selectedPropId = null
    }

    /** 退出场景时作废 token。 */
    fun exitScene() {
        currentToken = tokenCounter.incrementAndGet()
        selectedPropId = null
    }

    fun currentToken(): Long = currentToken

    /**
     * 处理一次 View.pick 异步回调结果。
     *
     * @param callbackToken 发起 pick 时的 token（与 currentToken 比对，防旧回调）
     * @param pickedEntity View.pick 返回的 entity（0 表示未命中）
     * @param entityToPropId GltfAssetStore 的映射
     * @param props scene.json 的 prop 配置（含 position、interaction_radius）
     * @param visitorXZ 游客当前水平位置
     * @return 决策（调用方据此更新 UI）
     */
    fun handlePickResult(
        callbackToken: Long,
        pickedEntity: Int,
        entityToPropId: Map<Int, String>,
        props: List<Prop>,
        visitorXZ: FloatArray
    ): PickingDecision {
        // §6.14：核对 Scene token，旧回调忽略（UT-012）
        if (callbackToken != currentToken) return PickingDecision.Stale

        // entity 0 或不在映射中 → 空白/环境 → 取消选中
        val propId = PickingMath.resolvePropId(pickedEntity, entityToPropId)
            ?: run {
                selectedPropId = null
                return PickingDecision.Deselect
            }

        // 距离判定（§6.14 interaction_radius_m）
        val prop = props.firstOrNull { it.id == propId }
        if (prop == null) {
            selectedPropId = null
            return PickingDecision.Deselect
        }
        val propXZ = floatArrayOf(prop.positionM[0], prop.positionM[2])
        val (distance, reachable) = PickingMath.distanceAndReachable(visitorXZ, propXZ, prop.interactionRadiusM)
        return if (reachable) {
            selectedPropId = propId
            PickingDecision.SelectProp(propId, titleHint = propId)
        } else {
            // 距离过远不选中，但告知是哪个文物（UI 提示靠近）
            PickingDecision.TooFar(propId, distance)
        }
    }

    /** 手动关闭信息卡。 */
    fun deselect() {
        selectedPropId = null
    }
}
