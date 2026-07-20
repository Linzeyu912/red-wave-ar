package cn.bistu.redwave

/**
 * 计划书 §6.18 错误码与恢复动作。
 *
 * 每个错误码都有稳定的用户文案与恢复动作（见 [AppErrorMessages]）。
 * 修改错误码需要确认是否影响诊断页文案与日志检索。
 */
enum class AppErrorCode {
    CAMERA_PERMISSION_DENIED,
    ARCORE_UNSUPPORTED,
    ARCORE_INSTALL_REQUIRED,
    ENTRY_UNKNOWN,
    MANIFEST_INVALID,
    SCENE_PACKAGE_MISSING,
    GLB_LOAD_FAILED,
    PARTIAL_PROP_FAILED,
    AUDIO_LOAD_FAILED,
    SENSOR_UNAVAILABLE,
    RENDER_SURFACE_LOST,
    OUT_OF_MEMORY_RISK;

    val stableCode: String get() = name
}
