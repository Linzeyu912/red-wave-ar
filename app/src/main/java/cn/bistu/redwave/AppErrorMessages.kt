package cn.bistu.redwave

/**
 * 计划书 §6.18：每个错误码都有用户可执行的下一步动作。
 * UI 层通过 [AppErrorCode] 查找文案，不在各处硬编码。
 */
object AppErrorMessages {

    data class Recovery(
        val shortMessage: String,
        val actionLabel: String?
    )

    private val table: Map<AppErrorCode, Recovery> = mapOf(
        AppErrorCode.CAMERA_PERMISSION_DENIED to Recovery(
            shortMessage = "未获得相机权限，无法使用扫描入口",
            actionLabel = "返回首页"
        ),
        AppErrorCode.ARCORE_UNSUPPORTED to Recovery(
            shortMessage = "当前设备不支持 ARCore 识图",
            actionLabel = "改用二维码或手动选择"
        ),
        AppErrorCode.ARCORE_INSTALL_REQUIRED to Recovery(
            shortMessage = "需要安装或更新 AR 服务",
            actionLabel = "去安装；失败后改用二维码"
        ),
        AppErrorCode.ENTRY_UNKNOWN to Recovery(
            shortMessage = "未识别为本项目卡片",
            actionLabel = "继续扫描或手动选择"
        ),
        AppErrorCode.MANIFEST_INVALID to Recovery(
            shortMessage = "资源配置损坏",
            actionLabel = null
        ),
        AppErrorCode.SCENE_PACKAGE_MISSING to Recovery(
            shortMessage = "该场景资源尚未安装",
            actionLabel = "下载或重新安装"
        ),
        AppErrorCode.GLB_LOAD_FAILED to Recovery(
            shortMessage = "场景加载失败",
            actionLabel = "重试一次；仍失败则返回"
        ),
        AppErrorCode.PARTIAL_PROP_FAILED to Recovery(
            shortMessage = "部分展品暂不可用",
            actionLabel = "隐藏该文物并继续参观"
        ),
        AppErrorCode.AUDIO_LOAD_FAILED to Recovery(
            shortMessage = "音频暂不可用",
            actionLabel = "保留文字内容"
        ),
        AppErrorCode.SENSOR_UNAVAILABLE to Recovery(
            shortMessage = "无旋转向量传感器，已切换触屏模式",
            actionLabel = "使用触屏环视"
        ),
        AppErrorCode.RENDER_SURFACE_LOST to Recovery(
            shortMessage = "正在恢复画面",
            actionLabel = null
        ),
        AppErrorCode.OUT_OF_MEMORY_RISK to Recovery(
            shortMessage = "场景过大，无法稳定加载",
            actionLabel = "清理资源并返回首页"
        )
    )

    fun recoveryFor(code: AppErrorCode): Recovery =
        table[code] ?: Recovery(
            shortMessage = "未知错误",
            actionLabel = null
        )

    /** 计划书 UT-014：每个错误都有稳定的用户文案与恢复动作。 */
    fun isFullyCovered(): Boolean = AppErrorCode.entries.all { table.containsKey(it) }
}
