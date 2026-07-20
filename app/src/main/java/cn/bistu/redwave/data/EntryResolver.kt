package cn.bistu.redwave.data

import cn.bistu.redwave.AppErrorCode
import cn.bistu.redwave.EntryResult
import cn.bistu.redwave.EntrySource

/**
 * 入口解析器（计划书 §6.8）。
 *
 * 三种入口（二维码 / 触发图 / 手动列表）与场景系统之间的唯一桥梁。
 *
 * 规则（§6.8）：
 * 1. 启动时从 global_manifest 建立二维码、图片名、场景 ID 三张不可变索引。
 * 2. 重复值视为清单错误，构建失败，不按“第一个匹配”继续。
 * 3. 扫描控制器收到连续相同结果时，只处理第一次（由调用方负责去重）。
 * 4. 无法识别的二维码显示“不是本项目卡片”，不能把任意 URL 当场景 ID。
 * 5. 入口成功事件只携带 scene_id 和入口类型，不携带 Bitmap、Camera Frame、Anchor、Pose。
 *
 * 本类是不可变的纯逻辑，不持有 Android 组件，便于单元测试。
 */
class EntryResolver private constructor(
    private val qrIndex: Map<String, String>,
    private val imageIndex: Map<String, String>,
    private val sceneIds: Set<String>
) {

    /**
     * 解析二维码 payload。
     * §5.5：解析前去除首尾空白，但区分大小写。
     */
    fun resolveQr(payload: String): Result<EntryResult> {
        val cleaned = payload.trim()
        val sceneId = qrIndex[cleaned]
            ?: return Result.failure(entryError(AppErrorCode.ENTRY_UNKNOWN, cleaned, EntrySource.QR))
        return Result.success(EntryResult(sceneId, EntrySource.QR))
    }

    /**
     * 解析触发图 image_name（来自 ARCore 图片库）。
     */
    fun resolveImage(imageName: String): Result<EntryResult> {
        val cleaned = imageName.trim()
        val sceneId = imageIndex[cleaned]
            ?: return Result.failure(entryError(AppErrorCode.ENTRY_UNKNOWN, cleaned, EntrySource.IMAGE))
        return Result.success(EntryResult(sceneId, EntrySource.IMAGE))
    }

    /**
     * 解析手动选择。手动选择的 scene_id 必须在全局索引中存在。
     */
    fun resolveManual(sceneId: String): Result<EntryResult> {
        val cleaned = sceneId.trim()
        if (cleaned !in sceneIds) {
            return Result.failure(entryError(AppErrorCode.ENTRY_UNKNOWN, cleaned, EntrySource.MANUAL))
        }
        return Result.success(EntryResult(cleaned, EntrySource.MANUAL))
    }

    /** 仅供诊断：当前已索引的场景数量。 */
    fun indexedSceneCount(): Int = sceneIds.size

    private fun entryError(code: AppErrorCode, value: String, source: EntrySource) =
        EntryResolutionException(code, "入口解析失败: source=$source value='$value'")

    /** 入口解析异常，携带稳定错误码（§6.18）。 */
    class EntryResolutionException(
        val code: AppErrorCode,
        override val message: String
    ) : RuntimeException(message)

    companion object {
        /**
         * 从 [GlobalManifest] 构建入口索引。
         *
         * §6.8-2：qr_payload / image_name 重复视为清单错误，直接失败。
         * 返回 Result，便于调用方把清单损坏映射为 MANIFEST_INVALID。
         */
        fun fromManifest(global: GlobalManifest): Result<EntryResolver> {
            val issues = mutableListOf<String>()
            val qrIndex = mutableMapOf<String, String>()
            val imageIndex = mutableMapOf<String, String>()
            val sceneIds = mutableSetOf<String>()

            for (item in global.scenes) {
                if (item.sceneId in sceneIds) {
                    issues += "scene_id '${item.sceneId}' 重复"
                } else {
                    sceneIds += item.sceneId
                }
                val qr = item.qrPayload.trim()
                if (qr.isEmpty()) {
                    issues += "scene '${item.sceneId}' qr_payload 为空"
                } else if (qrIndex.containsKey(qr)) {
                    issues += "qr_payload '$qr' 被多个场景引用（${qrIndex[qr]}, ${item.sceneId}）"
                } else {
                    qrIndex[qr] = item.sceneId
                }
                val img = item.imageName.trim()
                if (img.isEmpty()) {
                    issues += "scene '${item.sceneId}' image_name 为空"
                } else if (imageIndex.containsKey(img)) {
                    issues += "image_name '$img' 被多个场景引用（${imageIndex[img]}, ${item.sceneId}）"
                } else {
                    imageIndex[img] = item.sceneId
                }
            }

            return if (issues.isEmpty()) {
                Result.success(EntryResolver(qrIndex, imageIndex, sceneIds))
            } else {
                Result.failure(
                    ManifestLoadException(AppErrorCode.MANIFEST_INVALID, issues)
                )
            }
        }
    }
}
