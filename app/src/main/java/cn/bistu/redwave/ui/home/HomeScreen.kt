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
import androidx.compose.material3.HorizontalDivider
import androidx.compose.material3.Icon
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import cn.bistu.redwave.AppInfo
import cn.bistu.redwave.R

/**
 * 首页（计划书 §6.16）。
 *
 * CODE-00 阶段：展示应用标题、版本信息与三个入口按钮。
 * 入口按钮的实际导航在 CODE-08（二维码）、CODE-09（触发图）、CODE-10（场景列表）接入。
 * 此时点击按钮仅回调给上层，由上层在后续 CODE 任务中实现跳转。
 */
@Composable
fun HomeScreen(
    onScanQr: () -> Unit,
    onScanImage: () -> Unit,
    onManualSelect: () -> Unit,
    modifier: Modifier = Modifier
) {
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

                EntryButton(
                    label = stringResource(R.string.entry_qr),
                    icon = { Icon(Icons.Filled.QrCodeScanner, contentDescription = null) },
                    onClick = onScanQr
                )
                EntryButton(
                    label = stringResource(R.string.entry_image),
                    icon = { Icon(Icons.Filled.Image, contentDescription = null) },
                    onClick = onScanImage
                )
                EntryButton(
                    label = stringResource(R.string.entry_manual),
                    icon = { Icon(Icons.Filled.TouchApp, contentDescription = null) },
                    onClick = onManualSelect
                )

                Spacer(Modifier.height(24.dp))
                VersionFooter()
            }
        }
    }
}

@Composable
private fun EntryButton(
    label: String,
    icon: @Composable () -> Unit,
    onClick: () -> Unit
) {
    Button(
        onClick = onClick,
        modifier = Modifier
            .fillMaxWidth()
            .height(56.dp),
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
