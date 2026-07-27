package cn.bistu.redwave.ui.error

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Error
import androidx.compose.material.icons.filled.Warning
import androidx.compose.material3.Button
import androidx.compose.material3.ButtonDefaults
import androidx.compose.material3.Icon
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.material3.TextButton
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import cn.bistu.redwave.AppErrorCode
import cn.bistu.redwave.AppErrorMessages
import cn.bistu.redwave.R

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
        modifier = modifier
            .fillMaxSize()
            .padding(28.dp),
        horizontalAlignment = Alignment.CenterHorizontally,
        verticalArrangement = Arrangement.Center
    ) {
        Icon(
            imageVector = if (recoverable) Icons.Filled.Warning else Icons.Filled.Error,
            contentDescription = null,
            modifier = Modifier.size(72.dp),
            tint = if (recoverable) MaterialTheme.colorScheme.secondary else MaterialTheme.colorScheme.error
        )
        Text(
            text = recovery.shortMessage,
            style = MaterialTheme.typography.headlineSmall,
            textAlign = TextAlign.Center,
            modifier = Modifier.padding(top = 20.dp)
        )
        Text(
            text = stringResource(R.string.error_code_format, code.stableCode),
            modifier = Modifier.padding(top = 8.dp),
            style = MaterialTheme.typography.bodySmall,
            color = MaterialTheme.colorScheme.onSurface.copy(alpha = 0.7f)
        )
        if (recoverable || code == AppErrorCode.MANIFEST_INVALID) {
            Button(
                onClick = onRecovery,
                modifier = Modifier.padding(top = 24.dp),
                colors = ButtonDefaults.buttonColors(
                    containerColor = if (recoverable) {
                        MaterialTheme.colorScheme.primary
                    } else {
                        MaterialTheme.colorScheme.errorContainer
                    },
                    contentColor = if (recoverable) {
                        MaterialTheme.colorScheme.onPrimary
                    } else {
                        MaterialTheme.colorScheme.onErrorContainer
                    }
                )
            ) {
                Text(recovery.actionLabel ?: stringResource(R.string.error_home))
            }
        }
        TextButton(onClick = onDiagnostics, modifier = Modifier.padding(top = 4.dp)) {
            Text(stringResource(R.string.error_diag))
        }
        TextButton(onClick = onHome) { Text(stringResource(R.string.error_home)) }
    }
}
