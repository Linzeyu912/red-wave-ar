package cn.bistu.redwave.ui.scan

import android.Manifest
import android.content.pm.PackageManager
import android.os.Handler
import android.os.Looper
import androidx.activity.compose.rememberLauncherForActivityResult
import androidx.activity.result.contract.ActivityResultContracts
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.BoxScope
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.padding
import androidx.compose.material3.Button
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.material3.TextButton
import androidx.compose.runtime.Composable
import androidx.compose.runtime.DisposableEffect
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.unit.dp
import androidx.compose.ui.viewinterop.AndroidView
import androidx.core.content.ContextCompat
import cn.bistu.redwave.EntrySource
import cn.bistu.redwave.EntryResult
import cn.bistu.redwave.AppErrorCode
import cn.bistu.redwave.data.AndroidAssetResourceRoot
import cn.bistu.redwave.data.ManifestRepository
import cn.bistu.redwave.entry.qr.QrScannerController

/**
 * 二维码扫描页（计划书 §6.16、§6.9、CODE-08）。
 *
 * 流程：
 * 1. 检查 CAMERA 权限；拒绝→统一错误页，可返回首页使用手动入口；
 * 2. 扫描得到 payload（去重由 QrScannerController）；
 * 3. EntryResolver 解析：未知码显示"不是本项目卡片"继续扫描（§6.8-4）；
 * 4. 识别成功→冻结→释放相机→导航到 VR（onResolved 回调，只带 scene_id + source）。
 *
 * 边界：onResolved 只带 scene_id + EntrySource.QR，不带相机帧/Bitmap（§6.8-6）。
 *
 * @param onResolved 识别成功，释放相机前提交仅含 scene_id/source 的 EntryResult
 * @param onError 权限或清单错误，交给统一错误恢复页
 * @param onManualSelect 放弃扫描，返回首页使用正式手动列表
 * @param onBack 返回首页（取消/权限拒绝/手动入口引导）
 */
@Composable
fun QrScanScreen(
    onResolved: (EntryResult) -> Unit,
    onError: (AppErrorCode) -> Unit,
    onManualSelect: () -> Unit,
    onBack: () -> Unit,
    modifier: Modifier = Modifier
) {
    val context = LocalContext.current
    var hasCameraPermission by remember {
        mutableStateOf(
            ContextCompat.checkSelfPermission(context, Manifest.permission.CAMERA) ==
                PackageManager.PERMISSION_GRANTED
        )
    }
    var scanStatus by remember { mutableStateOf("对准项目卡片二维码") }

    val permissionLauncher = rememberLauncherForActivityResult(
        ActivityResultContracts.RequestPermission()
    ) { granted ->
        hasCameraPermission = granted
        if (!granted) {
            // §6.18 CAMERA_PERMISSION_DENIED：不循环弹权限框，进入统一错误恢复。
            onError(AppErrorCode.CAMERA_PERMISSION_DENIED)
        }
    }

    // 首次进入若无权限，请求一次
    LaunchedEffect(Unit) {
        if (!hasCameraPermission) {
            permissionLauncher.launch(Manifest.permission.CAMERA)
        }
    }

    Box(modifier = modifier.fillMaxSize().background(Color.Black)) {
        if (hasCameraPermission) {
            QrScannerContent(
                onPayload = { payload ->
                    // 用 EntryResolver 解析（CODE-01）
                    val resolver = ManifestRepository(
                        AndroidAssetResourceRoot.fromContext(context), strict = false
                    ).buildEntryResolver().getOrNull()
                    if (resolver == null) {
                        scanStatus = "资源初始化失败，请用手动入口"
                        onError(AppErrorCode.MANIFEST_INVALID)
                        return@QrScannerContent true
                    }
                    val result = resolver.resolveQr(payload)
                    result.fold(
                        onSuccess = { entry ->
                            scanStatus = "已识别：${entry.sceneId}，正在进入…"
                            onResolved(entry)
                            true
                        },
                        onFailure = {
                            // §6.8-4：不是本项目卡片，继续扫描
                            scanStatus = "不是本项目卡片，继续扫描…"
                            false
                        }
                    )
                },
                scanStatus = scanStatus,
                onManualSelect = onManualSelect,
                onBack = onBack
            )
        } else {
            // 权限请求中（或被拒后已在 LaunchedEffect 返回，这里兜底）
            Column(
                modifier = Modifier.fillMaxSize().padding(24.dp),
                verticalArrangement = Arrangement.Center,
                horizontalAlignment = Alignment.CenterHorizontally
            ) {
                Text("需要相机权限才能扫描二维码", color = Color.White)
                Text("可在设置中开启，或使用手动选择场景",
                    color = Color.White.copy(alpha = 0.7f),
                    style = MaterialTheme.typography.labelSmall,
                    modifier = Modifier.padding(top = 8.dp))
                Button(onClick = onBack, modifier = Modifier.padding(top = 16.dp)) {
                    Text("返回首页")
                }
                TextButton(onClick = onManualSelect) {
                    Text("手动选择场景")
                }
            }
        }
    }
}

@Composable
private fun BoxScope.QrScannerContent(
    onPayload: (String) -> Boolean,
    scanStatus: String,
    onManualSelect: () -> Unit,
    onBack: () -> Unit
) {
    val context = LocalContext.current
    var controller by remember { mutableStateOf<QrScannerController?>(null) }
    var torchOn by remember { mutableStateOf(false) }

    AndroidView(
        factory = { ctx ->
            lateinit var createdController: QrScannerController
            createdController = QrScannerController(ctx) { payload ->
                // 在 ZXing 回调线程，投回主线程
                Handler(Looper.getMainLooper()).post {
                    if (onPayload(payload)) {
                        // 有效入口：先明确释放相机，再由状态切换卸载扫描页。
                        createdController.release()
                    } else {
                        createdController.resumeAfterRejectedResult()
                    }
                }
            }
            val ctrl = createdController
            controller = ctrl
            ctrl.resume()
            // AndroidView factory 必须返回 View：DecoratedBarcodeView 是 FrameLayout
            ctrl.barcodeView
        },
        modifier = Modifier.fillMaxSize()
    )

    // 顶部状态条 + 返回（BoxScope.align）
    Column(
        modifier = Modifier
            .align(Alignment.TopCenter)
            .fillMaxWidth()
            .padding(12.dp),
        horizontalAlignment = Alignment.CenterHorizontally
    ) {
        Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
            TextButton(onClick = onBack) { Text("返回", color = Color.White) }
            TextButton(onClick = {
                torchOn = !torchOn
                controller?.setTorch(torchOn)
            }) { Text(if (torchOn) "关闭手电筒" else "打开手电筒", color = Color.White) }
            TextButton(onClick = onManualSelect) { Text("手动选择", color = Color.White) }
        }
        Text(scanStatus, color = Color.White,
            style = MaterialTheme.typography.labelSmall,
            modifier = Modifier.padding(top = 4.dp))
    }

    // 退出时释放相机（§6.9 onDestroy）
    DisposableEffect(Unit) {
        onDispose {
            controller?.release()
            controller = null
        }
    }
}
