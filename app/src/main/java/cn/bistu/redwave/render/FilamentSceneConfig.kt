package cn.bistu.redwave.render

import com.google.android.filament.Camera
import com.google.android.filament.View

/**
 * 场景渲染配置（CODE-02 阶段：纯色背景 + 相机投影 + 基础光照）。
 *
 * CODE-03 接入真实 GLB 与 IBL；CODE-04 接入姿态。此处只保证帧循环可见：
 * 清屏色 + 透视相机 + 一个主光源，验证 Surface→SwapChain→帧循环链路通畅。
 */
object FilamentSceneConfig {

    /**
     * 在 host 的 View/Camera 上配置初始参数。
     * 必须在 host.createSceneObjects() 之后调用，且在渲染线程上。
     *
     * @param viewportWidth  Surface 宽（像素）
     * @param viewportHeight Surface 高（像素）
     * @param clearColor     RGBA 清屏色，0..1
     */
    fun configureBaseline(
        host: FilamentHost,
        viewportWidth: Int,
        viewportHeight: Int,
        clearColor: FloatArray = floatArrayOf(0.06f, 0.08f, 0.10f, 1.0f)
    ) {
        require(clearColor.size >= 4) { "clearColor 必须是 RGBA" }
        require(viewportWidth > 0 && viewportHeight > 0) { "viewport 必须为正" }

        val view = host.view
        view.viewport = com.google.android.filament.Viewport(0, 0, viewportWidth, viewportHeight)

        // CODE-02：清屏色在 Renderer 上设置（Filament 1.56.0 用 ClearOptions）。
        val clearOptions = host.renderer.clearOptions
        clearOptions.clearColor = clearColor
        clearOptions.clear = true
        host.renderer.setClearOptions(clearOptions)

        // 抗锯齿与默认渲染质量（CODE-11 性能调优时再收紧）
        view.antiAliasing = View.AntiAliasing.FXAA
        view.dithering = View.Dithering.TEMPORAL

        // 相机投影：60° FOV，近 0.05m，远 100m（VR 展馆尺度）
        val camera = host.camera
        val aspect = viewportWidth.toDouble() / viewportHeight.toDouble()
        camera.setProjection(
            60.0,              // fov in degrees (vertical)
            aspect,
            0.05,              // near (m)
            100.0,             // far (m)
            Camera.Fov.VERTICAL
        )
        // 初始相机模型矩阵：眼高 1.6m，朝 -Z（计划书 §4.3 眼高 1.6m）
        // CODE-04 姿态、CODE-05 移动会接管这个矩阵；这里只给一个安全初值。
        val eyeX = 0.0; val eyeY = 1.6; val eyeZ = 0.0
        val cx = 0.0; val cy = 1.6; val cz = -1.0
        val upX = 0.0; val upY = 1.0; val upZ = 0.0
        camera.lookAt(eyeX, eyeY, eyeZ, cx, cy, cz, upX, upY, upZ)
    }
}
