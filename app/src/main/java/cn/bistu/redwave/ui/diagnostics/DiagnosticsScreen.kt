package cn.bistu.redwave.ui.diagnostics

import android.content.ClipData
import android.content.ClipboardManager
import android.content.Context
import android.os.Build
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.material3.Button
import androidx.compose.material3.Card
import androidx.compose.material3.CardDefaults
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.material3.TextButton
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.unit.dp
import cn.bistu.redwave.AppErrorCode
import cn.bistu.redwave.AppInfo

@Composable
fun DiagnosticsScreen(
    sceneCount: Int,
    lastErrorCode: AppErrorCode?,
    onBack: () -> Unit,
    modifier: Modifier = Modifier
) {
    val context = LocalContext.current
    var copied by remember { mutableStateOf(false) }
    val summary = remember(sceneCount, lastErrorCode) {
        buildString {
            appendLine("Red Wave diagnostics")
            appendLine("app=${AppInfo.versionName} (${AppInfo.versionCode})")
            appendLine("content=${AppInfo.sceneContentVersion}")
            appendLine("device=${Build.MANUFACTURER} ${Build.MODEL}")
            appendLine("android=${Build.VERSION.RELEASE} api=${Build.VERSION.SDK_INT}")
            appendLine("scenes=$sceneCount")
            appendLine("last_error=${lastErrorCode?.stableCode ?: "NONE"}")
            append("entry=QR+MANUAL; image_trigger=ARCHIVED")
        }
    }

    Column(
        modifier = modifier.fillMaxSize().padding(24.dp),
        verticalArrangement = Arrangement.spacedBy(12.dp)
    ) {
        Text("诊断", style = MaterialTheme.typography.headlineSmall)
        Card(
            modifier = Modifier.fillMaxWidth(),
            colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surfaceVariant)
        ) {
            Text(summary, modifier = Modifier.padding(16.dp), style = MaterialTheme.typography.bodyMedium)
        }
        Button(onClick = {
            val clipboard = context.getSystemService(Context.CLIPBOARD_SERVICE) as ClipboardManager
            clipboard.setPrimaryClip(ClipData.newPlainText("Red Wave diagnostics", summary))
            copied = true
        }) {
            Text(if (copied) "已复制" else "复制诊断摘要")
        }
        TextButton(onClick = onBack) { Text("返回首页") }
    }
}
