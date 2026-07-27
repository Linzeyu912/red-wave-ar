package cn.bistu.redwave.ui.home

import androidx.compose.foundation.background
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
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.AccountBalance
import androidx.compose.material.icons.filled.Image
import androidx.compose.material.icons.filled.QrCodeScanner
import androidx.compose.material.icons.filled.TouchApp
import androidx.compose.material3.AlertDialog
import androidx.compose.material3.Button
import androidx.compose.material3.ButtonDefaults
import androidx.compose.material3.Card
import androidx.compose.material3.CardDefaults
import androidx.compose.material3.HorizontalDivider
import androidx.compose.material3.Icon
import androidx.compose.material3.ListItem
import androidx.compose.material3.ListItemDefaults
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.material3.TextButton
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.saveable.rememberSaveable
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextOverflow
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
            .background(MaterialTheme.colorScheme.background),
        contentAlignment = Alignment.Center
    ) {
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(horizontal = 24.dp, vertical = 16.dp),
            horizontalAlignment = Alignment.CenterHorizontally,
            verticalArrangement = Arrangement.Center
        ) {
            // 顶部品牌区
            HeaderSection(
                modifier = Modifier
                    .fillMaxWidth()
                    .clip(RoundedCornerShape(20.dp))
                    .background(
                        Brush.verticalGradient(
                            colors = listOf(
                                MaterialTheme.colorScheme.primaryContainer,
                                MaterialTheme.colorScheme.surface
                            )
                        )
                    )
                    .padding(28.dp)
            )

            Spacer(Modifier.height(24.dp))

            Card(
                modifier = Modifier.fillMaxWidth(),
                shape = RoundedCornerShape(20.dp),
                colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surface)
            ) {
                Column(
                    modifier = Modifier
                        .fillMaxWidth()
                        .padding(20.dp),
                    horizontalAlignment = Alignment.CenterHorizontally,
                    verticalArrangement = Arrangement.spacedBy(10.dp)
                ) {
                    EntryButton(
                        label = stringResource(R.string.entry_qr),
                        icon = { Icon(Icons.Filled.QrCodeScanner, contentDescription = null) },
                        onClick = onScanQr,
                        enabled = isIndexReady,
                        modifier = Modifier.fillMaxWidth()
                    )
                    EntryButton(
                        label = stringResource(R.string.entry_image_archived),
                        icon = { Icon(Icons.Filled.Image, contentDescription = null) },
                        onClick = {},
                        enabled = false,
                        modifier = Modifier.fillMaxWidth()
                    )
                    EntryButton(
                        label = stringResource(R.string.entry_manual),
                        icon = { Icon(Icons.Filled.TouchApp, contentDescription = null) },
                        onClick = { showManualDialog = true },
                        enabled = isIndexReady && scenes.isNotEmpty(),
                        modifier = Modifier.fillMaxWidth()
                    )

                    if (!isIndexReady) {
                        Text(
                            text = stringResource(R.string.home_status_initializing),
                            style = MaterialTheme.typography.labelSmall,
                            color = MaterialTheme.colorScheme.onSurface.copy(alpha = 0.65f)
                        )
                    }
                }
            }

            Spacer(Modifier.height(20.dp))

            VersionFooter(onDiagnostics = onDiagnostics)
        }
    }

    if (showManualDialog) {
        ManualSceneDialog(
            scenes = scenes,
            onSelect = { sceneId ->
                showManualDialog = false
                onManualSelect(sceneId)
            },
            onDismiss = { showManualDialog = false }
        )
    }
}

@Composable
private fun HeaderSection(modifier: Modifier = Modifier) {
    Column(
        modifier = modifier,
        horizontalAlignment = Alignment.CenterHorizontally,
        verticalArrangement = Arrangement.spacedBy(8.dp)
    ) {
        Icon(
            imageVector = Icons.Filled.AccountBalance,
            contentDescription = null,
            modifier = Modifier.size(56.dp),
            tint = MaterialTheme.colorScheme.primary
        )
        Text(
            text = stringResource(R.string.home_title),
            style = MaterialTheme.typography.headlineSmall,
            fontWeight = FontWeight.SemiBold,
            color = MaterialTheme.colorScheme.onSurface
        )
        Text(
            text = stringResource(R.string.home_subtitle),
            style = MaterialTheme.typography.bodyMedium,
            color = MaterialTheme.colorScheme.onSurface.copy(alpha = 0.75f)
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
            contentColor = MaterialTheme.colorScheme.onPrimary,
            disabledContainerColor = MaterialTheme.colorScheme.surfaceVariant.copy(alpha = 0.6f),
            disabledContentColor = MaterialTheme.colorScheme.onSurfaceVariant.copy(alpha = 0.5f)
        ),
        contentPadding = PaddingValues(horizontal = 20.dp)
    ) {
        Row(
            verticalAlignment = Alignment.CenterVertically,
            horizontalArrangement = Arrangement.Start,
            modifier = Modifier.fillMaxWidth()
        ) {
            icon()
            Spacer(Modifier.width(14.dp))
            Text(
                text = label,
                fontSize = 16.sp,
                maxLines = 1,
                overflow = TextOverflow.Ellipsis
            )
        }
    }
}

@Composable
private fun ManualSceneDialog(
    scenes: List<SceneIndexItem>,
    onSelect: (String) -> Unit,
    onDismiss: () -> Unit
) {
    AlertDialog(
        onDismissRequest = onDismiss,
        title = { Text(stringResource(R.string.manual_dialog_title)) },
        text = {
            LazyColumn(verticalArrangement = Arrangement.spacedBy(8.dp)) {
                items(scenes, key = { it.sceneId }) { scene ->
                    Card(
                        onClick = { onSelect(scene.sceneId) },
                        modifier = Modifier.fillMaxWidth(),
                        shape = RoundedCornerShape(12.dp),
                        colors = CardDefaults.cardColors(
                            containerColor = MaterialTheme.colorScheme.surfaceVariant
                        )
                    ) {
                        ListItem(
                            headlineContent = {
                                Text(
                                    scene.sceneName,
                                    maxLines = 1,
                                    overflow = TextOverflow.Ellipsis
                                )
                            },
                            supportingContent = {
                                Text(
                                    scene.sceneId,
                                    style = MaterialTheme.typography.labelMedium
                                )
                            },
                            leadingContent = {
                                Icon(
                                    imageVector = Icons.Filled.AccountBalance,
                                    contentDescription = null,
                                    tint = MaterialTheme.colorScheme.primary
                                )
                            },
                            colors = ListItemDefaults.colors(
                                containerColor = MaterialTheme.colorScheme.surfaceVariant
                            )
                        )
                    }
                }
            }
        },
        confirmButton = {
            TextButton(onClick = onDismiss) {
                Text(stringResource(R.string.manual_dialog_cancel))
            }
        }
    )
}

@Composable
private fun VersionFooter(onDiagnostics: () -> Unit) {
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
        TextButton(onClick = onDiagnostics) {
            Text(stringResource(R.string.diag_title))
        }
    }
}
