package cn.bistu.redwave.entry.qr

import android.content.Context
import com.google.zxing.BarcodeFormat
import com.google.zxing.DecodeHintType
import com.journeyapps.barcodescanner.BarcodeCallback
import com.journeyapps.barcodescanner.BarcodeResult
import com.journeyapps.barcodescanner.DefaultDecoderFactory
import com.journeyapps.barcodescanner.DecoratedBarcodeView

/**
 * 二维码扫描控制器（计划书 §6.6 entry.qr、§6.9、CODE-08）。
 *
 * 职责：
 * - 持有 ZXing [DecoratedBarcodeView]，管理扫描生命周期；
 * - 结果去重：连续相同 payload 只处理第一次（§6.8-3）；
 * - 解析成功后冻结结果，调用方据此停止扫描并释放相机（§6.9）。
 *
 * 边界：本类只负责"扫描得到 payload 字符串"，payload → scene_id 由 EntryResolver 完成。
 * 不把任何相机帧/Bitmap 带出扫描页（§6.8-6）。
 *
 * @param onResult 扫描到（去重后）的 payload；调用方解析 scene_id
 */
class QrScannerController(
    context: Context,
    private val onResult: (String) -> Unit
) {
    /** ZXing 视图，由调用方加入布局（Compose AndroidView）。 */
    val barcodeView: DecoratedBarcodeView = DecoratedBarcodeView(context).apply {
        // 优先识别 QR，兼容常见一维码（现场码型可能不一致）
        val formats = listOf(
            BarcodeFormat.QR_CODE,
            BarcodeFormat.CODE_128,
            BarcodeFormat.CODE_39
        )
        val hints = mapOf<DecodeHintType, Any>(
            DecodeHintType.POSSIBLE_FORMATS to formats,
            DecodeHintType.TRY_HARDER to true
        )
        decoderFactory = DefaultDecoderFactory(formats, hints, "QR", 500)
    }

    @Volatile
    private var lastPayload: String? = null

    @Volatile
    private var frozen: Boolean = false

    private val callback = BarcodeCallback { result: BarcodeResult ->
        if (frozen) return@BarcodeCallback
        val text = result.text ?: return@BarcodeCallback
        // §6.8-3：连续相同结果只处理第一次
        if (text == lastPayload) return@BarcodeCallback
        lastPayload = text
        // §6.9：记录后立即冻结，开始释放相机
        frozen = true
        onResult(text)
    }

    /** resume：页面可见时启动持续扫描。 */
    fun resume() {
        if (frozen) return
        barcodeView.decodeContinuous(callback)
        barcodeView.resume()
    }

    /** pause：页面后台/退出时暂停（§6.9 onPause 必须暂停）。 */
    fun pause() {
        barcodeView.pause()
    }

    /**
     * 完全停止并释放相机（识别成功或退出时）。
     * §6.9：onDestroy 必须关闭并清空引用。
     */
    fun release() {
        frozen = true
        barcodeView.pause()
    }

    /**
     * 当前 payload 不是项目入口时继续扫描其他码。
     * 保留 [lastPayload]，避免镜头仍对着同一未知码时反复刷提示。
     */
    fun resumeAfterRejectedResult() {
        frozen = false
    }

    /** 当前是否已冻结（识别成功，等待导航）。 */
    fun isFrozen(): Boolean = frozen

    /** 手电筒（§6.16 二维码页元素）。 */
    fun setTorch(on: Boolean) {
        if (on) barcodeView.setTorchOn() else barcodeView.setTorchOff()
    }
}
