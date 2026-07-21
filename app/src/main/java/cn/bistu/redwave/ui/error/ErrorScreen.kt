package cn.bistu.redwave.ui.error

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.padding
import androidx.compose.material3.Button
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.material3.TextButton
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import cn.bistu.redwave.AppErrorCode
import cn.bistu.redwave.AppErrorMessages

@Composable
fun ErrorScreen(
    code: AppErrorCode,
    recoverable: Boolean,
    onRecovery: () -> Unit,
    onDiagnostics: () -> Unit,
    onHome: () -> Unit,
    modifier: Modifier = Modifier
) {
    val recovery = AppErrorMessages.recoveryFor(code)
    Column(
        modifier = modifier.fillMaxSize().padding(24.dp),
        horizontalAlignment = Alignment.CenterHorizontally,
        verticalArrangement = Arrangement.Center
    ) {
        Text(recovery.shortMessage, style = MaterialTheme.typography.headlineSmall)
        Text(
            "错误码：${code.stableCode}",
            modifier = Modifier.padding(top = 8.dp),
            style = MaterialTheme.typography.bodySmall
        )
        if (recoverable || code == AppErrorCode.MANIFEST_INVALID) {
            Button(onClick = onRecovery, modifier = Modifier.padding(top = 20.dp)) {
                Text(recovery.actionLabel ?: "重试")
            }
        }
        TextButton(onClick = onDiagnostics) { Text("查看诊断") }
        TextButton(onClick = onHome) { Text("返回首页") }
    }
}
