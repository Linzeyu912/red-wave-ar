package cn.bistu.redwave

/**
 * 应用元信息访问器。
 *
 * 字段来自 BuildConfig，在 app/build.gradle.kts 的 buildConfigField 中注入。
 * 计划书 §15.4：每次 Release 必须记录 APK SHA-256、Git commit、版本号、资源版本、设备信息和测试日期。
 */
object AppInfo {
    val versionName: String get() = BuildConfig.VERSION_NAME
    val versionCode: Int get() = BuildConfig.VERSION_CODE
    val sceneContentVersion: String get() = BuildConfig.SCENE_CONTENT_VERSION
    val isDebug: Boolean get() = BuildConfig.DEBUG
    val enableDiagnosticsOverlay: Boolean get() = BuildConfig.ENABLE_DIAGNOSTICS_OVERLAY
    val strictReleaseValidation: Boolean get() = BuildConfig.STRICT_RELEASE_VALIDATION
}
