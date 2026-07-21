package cn.bistu.redwave.ui.home

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.PaddingValues
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Image
import androidx.compose.material.icons.filled.QrCodeScanner
import androidx.compose.material.icons.filled.TouchApp
import androidx.compose.material3.Button
import androidx.compose.material3.ButtonDefaults
import androidx.compose.material3.Card
import androidx.compose.material3.CardDefaults
import androidx.compose.material3.AlertDialog
import androidx.compose.material3.HorizontalDivider
import androidx.compose.material3.Icon
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.material3.TextButton
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.saveable.rememberSaveable
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import cn.bistu.redwave.AppInfo
import cn.bistu.redwave.R
import cn.bistu.redwave.data.SceneIndexItem

/**
 * 首页（计划书 §6.16）。
 *
 * CODE-10：展示二维码、已归档的识图入口、由 global_manifest 驱动的手动场景列表，
 * 并提供诊断页入口。具体页面状态由上层 SceneCoordinator 管理。
 */
@Composable
fun HomeScreen(
    scenes: List<SceneIndexItem>,
    isIndexReady: Boolean,
    onScanQr: () -> Unit,
    onManualSelect: (String) -> Unit,
    onDiagnostics: () -> Unit,
    modifier: Modifier = Modifier
) {
    var showManualDialog by rememberSaveable { mutableStateOf(false) }

    Box(
        modifier = modifier
            .fillMaxSize()
            .padding(24.dp),
        contentAlignment = Alignment.Center
    ) {
        Card(
            modifier = Modifier.fillMaxWidth(),
            shape = RoundedCornerShape(20.dp),
            colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surface)
        ) {
            Column(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(28.dp),
                horizontalAlignment = Alignment.CenterHorizontally,
                verticalArrangement = Arrangement.spacedBy(8.dp)
            ) {
                Text(
                    text = stringResource(R.string.home_title),
                    style = MaterialTheme.typography.headlineSmall,
                    fontWeight = FontWeight.SemiBold,
                    color = MaterialTheme.colorScheme.onSurface
                )
                Text(
                    text = stringResource(R.string.home_subtitle),
                    style = MaterialTheme.typography.bodyMedium,
                    color = MaterialTheme.colorScheme.onSurface.copy(alpha = 0.7f)
                )

                Spacer(Modifier.height(20.dp))
                HorizontalDivider(color = MaterialTheme.colorScheme.onSurface.copy(alpha = 0.1f))
                Spacer(Modifier.height(20.dp))

                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.spacedBy(12.dp)
                ) {
                    EntryButton(
                        label = stringResource(R.string.entry_qr),
                        icon = { Icon(Icons.Filled.QrCodeScanner, contentDescription = null) },
                        onClick = onScanQr,
                        enabled = isIndexReady,
                        modifier = Modifier.weight(1f)
                    )
                    EntryButton(
                        label = "识别图片（已归档）",
                        icon = { Icon(Icons.Filled.Image, contentDescription = null) },
                        onClick = {},
                        enabled = false,
                        modifier = Modifier.weight(1f)
                    )
                    EntryButton(
                        label = stringResource(R.string.entry_manual),
                        icon = { Icon(Icons.Filled.TouchApp, contentDescription = null) },
                        onClick = { showManualDialog = true },
                        enabled = isIndexReady && scenes.isNotEmpty(),
                        modifier = Modifier.weight(1f)
                    )
                }

                if (!isIndexReady) {
                    Text(
                        text = "正在读取场景索引…",
                        style = MaterialTheme.typography.labelSmall,
                        color = MaterialTheme.colorScheme.onSurface.copy(alpha = 0.65f)
                    )
                }

                Spacer(Modifier.height(24.dp))
                VersionFooter()
                TextButton(onClick = onDiagnostics) {
                    Text(stringResource(R.string.diag_title))
                }
            }
        }
    }

    if (showManualDialog) {
        AlertDialog(
            onDismissRequest = { showManualDialog = false },
            title = { Text("选择虚拟展馆") },
            text = {
                Column(verticalArrangement = Arrangement.spacedBy(8.dp)) {
                    scenes.forEach { scene ->
                        Button(
                            onClick = {
                                showManualDialog = false
                                onManualSelect(scene.sceneId)
                            },
                            modifier = Modifier.fillMaxWidth()
                        ) {
                            Text("${scene.sceneName}（${scene.sceneId}）")
                        }
                    }
                }
            },
            confirmButton = {
                TextButton(onClick = { showManualDialog = false }) {
                    Text("取消")
                }
            }
        )
    }
}

@Composable
private fun EntryButton(
    label: String,
    icon: @Composable () -> Unit,
    onClick: () -> Unit,
    enabled: Boolean = true,
    modifier: Modifier = Modifier
) {
    Button(
        onClick = onClick,
        enabled = enabled,
        modifier = modifier.height(56.dp),
        shape = RoundedCornerShape(14.dp),
        colors = ButtonDefaults.buttonColors(
            containerColor = MaterialTheme.colorScheme.primary,
            contentColor = MaterialTheme.colorScheme.onPrimary
        ),
        contentPadding = PaddingValues(horizontal = 20.dp)
    ) {
        Row(
            verticalAlignment = Alignment.CenterVertically,
            horizontalArrangement = Arrangement.Center,
            modifier = Modifier.fillMaxWidth()
        ) {
            icon()
            Spacer(Modifier.width(12.dp))
            Text(label, fontSize = 16.sp)
        }
    }
}

@Composable
private fun VersionFooter() {
    Column(horizontalAlignment = Alignment.CenterHorizontally) {
        Text(
            text = "${stringResource(R.string.app_version_label)}: ${AppInfo.versionName}",
            style = MaterialTheme.typography.labelSmall,
            color = MaterialTheme.colorScheme.onSurface.copy(alpha = 0.5f)
        )
        Text(
            text = "content ${AppInfo.sceneContentVersion}",
            style = MaterialTheme.typography.labelSmall,
            color = MaterialTheme.colorScheme.onSurface.copy(alpha = 0.4f)
        )
    }
}
