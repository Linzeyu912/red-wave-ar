package cn.bistu.redwave.ui.scan

import android.Manifest
import android.content.pm.PackageManager
import androidx.activity.compose.rememberLauncherForActivityResult
import androidx.activity.result.contract.ActivityResultContracts
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.BoxScope
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
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
import cn.bistu.redwave.data.AndroidAssetResourceRoot
import cn.bistu.redwave.data.ManifestRepository
import cn.bistu.redwave.entry.qr.QrScannerController

/**
 * 二维码扫描页（计划书 §6.16、§6.9、CODE-08）。
 *
 * 流程：
 * 1. 检查 CAMERA 权限；拒绝→返回首页并突出手动入口（§6.18 CAMERA_PERMISSION_DENIED）；
 * 2. 扫描得到 payload（去重由 QrScannerController）；
 * 3. EntryResolver 解析：未知码显示"不是本项目卡片"继续扫描（§6.8-4）；
 * 4. 识别成功→冻结→释放相机→导航到 VR（onResolved 回调，只带 scene_id + source）。
 *
 * 边界：onResolved 只带 scene_id + EntrySource.QR，不带相机帧/Bitmap（§6.8-6）。
 *
 * @param onResolved 识别成功，释放相机后回调（scene_id, source）
 * @param onBack 返回首页（取消/权限拒绝/手动入口引导）
 */
@Composable
fun QrScanScreen(
    onResolved: (sceneId: String, source: EntrySource) -> Unit,
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
            // §6.18 CAMERA_PERMISSION_DENIED：返回首页突出手动入口
            // 不循环弹权限框（§6.9），直接返回
            onBack()
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
                        return@QrScannerContent
                    }
                    val result = resolver.resolveQr(payload)
                    result.fold(
                        onSuccess = { entry ->
                            scanStatus = "已识别：${entry.sceneId}，正在进入…"
                            // onResolved 由调用方在释放相机后调用
                            onResolved(entry.sceneId, EntrySource.QR)
                        },
                        onFailure = {
                            // §6.8-4：不是本项目卡片，继续扫描
                            scanStatus = "不是本项目卡片，继续扫描…"
                        }
                    )
                },
                scanStatus = scanStatus,
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
            }
        }
    }
}

@Composable
private fun BoxScope.QrScannerContent(
    onPayload: (String) -> Unit,
    scanStatus: String,
    onBack: () -> Unit
) {
    val context = LocalContext.current
    var controller by remember { mutableStateOf<QrScannerController?>(null) }

    AndroidView(
        factory = { ctx ->
            val ctrl = QrScannerController(ctx) { payload ->
                // 在 ZXing 回调线程，投回主线程
                (ctx as? android.app.Activity)?.runOnUiThread { onPayload(payload) }
            }
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
        TextButton(onClick = onBack) { Text("返回", color = Color.White) }
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
