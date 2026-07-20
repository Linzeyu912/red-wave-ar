package cn.bistu.redwave.sensor

import android.content.Context
import android.hardware.Sensor
import android.hardware.SensorEvent
import android.hardware.SensorEventListener
import android.hardware.SensorManager
import cn.bistu.redwave.SensorMode

/**
 * 姿态输入控制器（计划书 §6.6 sensor、§6.12）。
 *
 * 职责：
 * - 陀螺仪模式：监听 TYPE_GAME_ROTATION_VECTOR，经屏幕重映射 → 回正 → 去 roll → slerp 平滑；
 * - 触屏模式：拖动改 yaw/pitch，pitch 限幅，模式切换不跳变；
 * - 无旋转向量传感器时降级为触屏（§6.18 SENSOR_UNAVAILABLE）；
 * - 提供 [currentOrientation] 供 SceneRenderer 每帧读取并写入相机。
 *
 * 纯算法在 [OrientationMath]，本类只做 Android Sensor 桥接与状态持有。
 */
class OrientationController(private val context: Context) : SensorEventListener {

    // 默认平滑时间常数（§6.12-6：tau 0.08–0.15 s）
    var tauSec: Float = 0.12f

    private val sensorManager: SensorManager =
        context.getSystemService(Context.SENSOR_SERVICE) as SensorManager
    private val gameRotationSensor: Sensor? =
        sensorManager.getDefaultSensor(Sensor.TYPE_GAME_ROTATION_VECTOR)

    @Volatile
    var mode: SensorMode = SensorMode.TOUCH
        private set

    // 陀螺仪模式状态
    private var qReference: Quaternion = Quaternion.IDENTITY
    private var qSmoothed: Quaternion = Quaternion.IDENTITY
    private var hasReference: Boolean = false

    // 触屏模式状态：累积 yaw/pitch（度）
    private var touchYawDeg: Float = 0f
    private var touchPitchDeg: Float = 0f

    /** 设备是否支持陀螺仪（TYPE_GAME_ROTATION_VECTOR 存在）。 */
    fun gyroscopeAvailable(): Boolean = gameRotationSensor != null

    /**
     * 根据设备能力初始化默认模式（§6.18 SENSOR_UNAVAILABLE 降级）：
     * 有旋转向量传感器→陀螺仪；否则→触屏。
     * 在页面进入、OrientationController 创建后调用一次。
     */
    fun initDefaultMode() {
        mode = if (gyroscopeAvailable()) SensorMode.GYROSCOPE else SensorMode.TOUCH
    }

    /**
     * 设置模式（§6.12：切换时以当前画面姿态初始化新模式，不跳变）。
     */
    fun setMode(newMode: SensorMode) {
        if (newMode == mode) return
        when (newMode) {
            SensorMode.GYROSCOPE -> {
                if (!gyroscopeAvailable()) {
                    // §6.18 SENSOR_UNAVAILABLE：自动启用 Touch
                    mode = SensorMode.TOUCH
                    return
                }
                // 切换瞬间以当前触屏 yaw/pitch 作为陀螺仪基准的视觉起点：
                // 把当前触屏姿态注入 qSmoothed，并重置 reference（下次采样重置回正）
                qSmoothed = OrientationMath.fromYawPitchDeg(touchYawDeg, touchPitchDeg)
                hasReference = false
                mode = SensorMode.GYROSCOPE
            }
            SensorMode.TOUCH -> {
                // 从当前陀螺仪平滑姿态提取 yaw/pitch 作为触屏起点
                val (yaw, pitch) = OrientationMath.extractYawPitchDeg(qSmoothed)
                touchYawDeg = yaw
                touchPitchDeg = pitch
                mode = SensorMode.TOUCH
            }
        }
    }

    /**
     * 回正：以当前姿态为视觉零点（§6.12-3）。
     */
    fun recalibrate() {
        if (mode == SensorMode.GYROSCOPE) {
            // 下次 onSensorChanged 时用当前 q_screen 作 reference
            hasReference = false
        } else {
            touchYawDeg = 0f
            touchPitchDeg = 0f
        }
    }

    /**
     * 触屏拖动：水平改 yaw，垂直改 pitch（§6.12 触屏模式）。
     * @param dx, dy 自上次事件的像素位移
     * @param sensitivityDegPerPixel 每像素对应角度
     */
    fun onTouchDrag(dx: Float, dy: Float, sensitivityDegPerPixel: Float) {
        if (mode != SensorMode.TOUCH) return
        touchYawDeg -= dx * sensitivityDegPerPixel
        touchPitchDeg -= dy * sensitivityDegPerPixel
        // pitch 限幅在 OrientationMath.fromYawPitchDeg 内处理
    }

    /**
     * 每帧更新平滑姿态（由 SceneRenderer.onUpdateOrientation 调用）。
     * 返回当前应写入相机的四元数（已去 roll、已平滑）。
     */
    fun updateAndGetCurrent(dtSec: Float): Quaternion {
        return when (mode) {
            SensorMode.TOUCH -> {
                val target = OrientationMath.fromYawPitchDeg(touchYawDeg, touchPitchDeg)
                qSmoothed = OrientationMath.smooth(qSmoothed, target, dtSec, tauSec)
                qSmoothed
            }
            SensorMode.GYROSCOPE -> {
                // 陀螺仪采样在 onSensorChanged 更新 qSmoothed（已含 slerp），
                // 此处仅返回；dt 主要用于触屏平滑。
                qSmoothed
            }
        }
    }

    // ----------------------------------------------------- SensorEventListener

    override fun onSensorChanged(event: SensorEvent) {
        if (event.sensor.type != Sensor.TYPE_GAME_ROTATION_VECTOR) return
        if (mode != SensorMode.GYROSCOPE) return
        val qDevice = Quaternion.fromRotationVector(event.values)
        val qScreen = OrientationMath.applyScreenRotation(qDevice, screenRotationDeg)
        if (!hasReference) {
            qReference = qScreen
            hasReference = true
            qSmoothed = Quaternion.IDENTITY
            return
        }
        val qRelative = OrientationMath.relativeTo(qScreen, qReference)
        // §6.12-5 去 roll
        val (_, noRoll) = OrientationMath.removeRoll(qRelative)
        // §6.12-6 slerp 平滑（用估计的传感器采样间隔）
        val dt = 1f / 60f.coerceAtLeast(1f) // 保守默认；SensorManager 不直接给 dt
        qSmoothed = OrientationMath.smooth(qSmoothed, noRoll, dt, tauSec)
    }

    override fun onAccuracyChanged(sensor: Sensor?, accuracy: Int) {}

    /** 当前屏幕旋转角度（度）。由 VR 页注入 Display.rotation。 */
    @Volatile
    var screenRotationDeg: Int = OrientationMath.SCREEN_ROT_0

    /**
     * 注册监听（页面 resume 时）。返回是否成功启用陀螺仪。
     */
    fun resume(): Boolean {
        val sensor = gameRotationSensor
        return if (sensor != null && mode == SensorMode.GYROSCOPE) {
            sensorManager.registerListener(this, sensor, SensorManager.SENSOR_DELAY_GAME)
            true
        } else {
            false
        }
    }

    /** 注销监听（页面 pause 时，§6.12 后台暂停）。 */
    fun pause() {
        sensorManager.unregisterListener(this)
    }
}
