package cn.bistu.redwave.ui.scan

import android.Manifest
import android.content.pm.PackageManager
import android.os.Handler
import android.os.Looper
import androidx.activity.compose.rememberLauncherForActivityResult
import androidx.activity.result.contract.ActivityResultContracts
import androidx.compose.animation.core.LinearEasing
import androidx.compose.animation.core.RepeatMode
import androidx.compose.animation.core.animateFloat
import androidx.compose.animation.core.infiniteRepeatable
import androidx.compose.animation.core.rememberInfiniteTransition
import androidx.compose.animation.core.tween
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.BoxScope
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.ArrowBack
import androidx.compose.material.icons.filled.FlashlightOff
import androidx.compose.material.icons.filled.FlashlightOn
import androidx.compose.material3.Button
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.IconButtonDefaults
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Surface
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
import androidx.compose.ui.draw.clip
import androidx.compose.ui.draw.drawWithCache
import androidx.compose.ui.geometry.CornerRadius
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.geometry.Size
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.drawscope.Stroke
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.unit.dp
import androidx.compose.ui.viewinterop.AndroidView
import androidx.core.content.ContextCompat
import cn.bistu.redwave.AppErrorCode
import cn.bistu.redwave.EntryResult
import cn.bistu.redwave.R
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
    resolver: cn.bistu.redwave.data.EntryResolver? = null,
    modifier: Modifier = Modifier
) {
    val context = LocalContext.current
    var hasCameraPermission by remember {
        mutableStateOf(
            ContextCompat.checkSelfPermission(context, Manifest.permission.CAMERA) ==
                PackageManager.PERMISSION_GRANTED
        )
    }
    var scanStatus by remember { mutableStateOf(context.getString(R.string.scan_status_initial)) }

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
                    // 优先使用上层已构建的 EntryResolver，避免每次识别都重建仓库。
                    val activeResolver = resolver ?: ManifestRepository(
                        AndroidAssetResourceRoot.fromContext(context), strict = false
                    ).buildEntryResolver().getOrNull()
                    if (activeResolver == null) {
                        scanStatus = context.getString(R.string.home_status_error)
                        onError(AppErrorCode.MANIFEST_INVALID)
                        return@QrScannerContent true
                    }
                    val result = activeResolver.resolveQr(payload)
                    result.fold(
                        onSuccess = { entry ->
                            scanStatus = context.getString(
                                R.string.scan_status_recognized_format,
                                entry.sceneId
                            )
                            onResolved(entry)
                            true
                        },
                        onFailure = {
                            // §6.8-4：不是本项目卡片，继续扫描
                            scanStatus = context.getString(R.string.scan_status_unknown)
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
                Text(
                    stringResource(R.string.scan_permission_title),
                    color = Color.White,
                    style = MaterialTheme.typography.titleMedium
                )
                Text(
                    stringResource(R.string.scan_permission_subtitle),
                    color = Color.White.copy(alpha = 0.7f),
                    style = MaterialTheme.typography.bodySmall,
                    modifier = Modifier.padding(top = 8.dp)
                )
                Button(onClick = onBack, modifier = Modifier.padding(top = 16.dp)) {
                    Text(stringResource(R.string.scan_back))
                }
                TextButton(onClick = onManualSelect) {
                    Text(stringResource(R.string.entry_manual))
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

    // 扫描框与激光动画
    ScanFrameOverlay(
        modifier = Modifier
            .align(Alignment.Center)
            .fillMaxWidth(0.55f)
            .padding(horizontal = 32.dp)
    )

    // 顶部工具栏
    Row(
        modifier = Modifier
            .align(Alignment.TopCenter)
            .fillMaxWidth()
            .padding(12.dp),
        horizontalArrangement = Arrangement.SpaceBetween,
        verticalAlignment = Alignment.CenterVertically
    ) {
        IconButton(
            onClick = onBack,
            colors = IconButtonDefaults.iconButtonColors(
                containerColor = Color.Black.copy(alpha = 0.4f),
                contentColor = Color.White
            )
        ) {
            Icon(
                Icons.AutoMirrored.Filled.ArrowBack,
                contentDescription = stringResource(R.string.scan_back)
            )
        }
        Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
            IconButton(
                onClick = {
                    torchOn = !torchOn
                    controller?.setTorch(torchOn)
                },
                colors = IconButtonDefaults.iconButtonColors(
                    containerColor = Color.Black.copy(alpha = 0.4f),
                    contentColor = Color.White
                )
            ) {
                Icon(
                    imageVector = if (torchOn) Icons.Filled.FlashlightOff else Icons.Filled.FlashlightOn,
                    contentDescription = stringResource(
                        if (torchOn) R.string.scan_torch_on else R.string.scan_torch_off
                    )
                )
            }
            IconButton(
                onClick = onManualSelect,
                colors = IconButtonDefaults.iconButtonColors(
                    containerColor = Color.Black.copy(alpha = 0.4f),
                    contentColor = Color.White
                )
            ) {
                Text(
                    stringResource(R.string.scan_manual),
                    color = Color.White,
                    style = MaterialTheme.typography.labelMedium
                )
            }
        }
    }

    // 底部提示
    Surface(
        modifier = Modifier
            .align(Alignment.BottomCenter)
            .padding(bottom = 48.dp, start = 32.dp, end = 32.dp)
            .clip(RoundedCornerShape(16.dp)),
        color = Color.Black.copy(alpha = 0.55f)
    ) {
        Text(
            scanStatus,
            color = Color.White,
            style = MaterialTheme.typography.bodyMedium,
            modifier = Modifier.padding(horizontal = 20.dp, vertical = 12.dp)
        )
    }

    // 退出时释放相机（§6.9 onDestroy）
    DisposableEffect(Unit) {
        onDispose {
            controller?.release()
            controller = null
        }
    }
}

@Composable
private fun ScanFrameOverlay(modifier: Modifier = Modifier) {
    val frameColor = MaterialTheme.colorScheme.primary
    val laserColor = MaterialTheme.colorScheme.secondary
    val infiniteTransition = rememberInfiniteTransition(label = "laser")
    val laserProgress by infiniteTransition.animateFloat(
        initialValue = 0f,
        targetValue = 1f,
        animationSpec = infiniteRepeatable(
            animation = tween(durationMillis = 1800, easing = LinearEasing),
            repeatMode = RepeatMode.Reverse
        ),
        label = "laserProgress"
    )

    Box(
        modifier = modifier
            .size(260.dp)
            .clip(RoundedCornerShape(20.dp))
            .drawWithCache {
                val cornerLength = size.minDimension * 0.18f
                val strokeWidth = 6f
                val cornerRadius = CornerRadius(20.dp.toPx(), 20.dp.toPx())
                onDrawBehind {
                    // 四角 L 形标记
                    val path = androidx.compose.ui.graphics.Path().apply {
                        // 左上
                        moveTo(0f, cornerLength)
                        lineTo(0f, cornerRadius.y)
                        arcTo(
                            rect = androidx.compose.ui.geometry.Rect(
                                0f, 0f, cornerRadius.x * 2, cornerRadius.y * 2
                            ),
                            startAngleDegrees = 180f,
                            sweepAngleDegrees = 90f,
                            forceMoveTo = false
                        )
                        lineTo(cornerLength, 0f)
                        // 右上
                        moveTo(size.width - cornerLength, 0f)
                        lineTo(size.width - cornerRadius.x, 0f)
                        arcTo(
                            rect = androidx.compose.ui.geometry.Rect(
                                size.width - cornerRadius.x * 2, 0f,
                                size.width, cornerRadius.y * 2
                            ),
                            startAngleDegrees = 270f,
                            sweepAngleDegrees = 90f,
                            forceMoveTo = false
                        )
                        lineTo(size.width, cornerLength)
                        // 右下
                        moveTo(size.width, size.height - cornerLength)
                        lineTo(size.width, size.height - cornerRadius.y)
                        arcTo(
                            rect = androidx.compose.ui.geometry.Rect(
                                size.width - cornerRadius.x * 2,
                                size.height - cornerRadius.y * 2,
                                size.width, size.height
                            ),
                            startAngleDegrees = 0f,
                            sweepAngleDegrees = 90f,
                            forceMoveTo = false
                        )
                        lineTo(size.width - cornerLength, size.height)
                        // 左下
                        moveTo(cornerLength, size.height)
                        lineTo(cornerRadius.x, size.height)
                        arcTo(
                            rect = androidx.compose.ui.geometry.Rect(
                                0f, size.height - cornerRadius.y * 2,
                                cornerRadius.x * 2, size.height
                            ),
                            startAngleDegrees = 90f,
                            sweepAngleDegrees = 90f,
                            forceMoveTo = false
                        )
                        lineTo(0f, size.height - cornerLength)
                    }
                    drawPath(path, color = frameColor, style = Stroke(width = strokeWidth))

                    // 激光线
                    val laserY = size.height * laserProgress
                    drawLine(
                        color = laserColor,
                        start = Offset(cornerLength * 0.5f, laserY),
                        end = Offset(size.width - cornerLength * 0.5f, laserY),
                        strokeWidth = strokeWidth * 0.6f
                    )
                }
            }
    )
}
