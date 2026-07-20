package cn.bistu.redwave.data

import kotlinx.serialization.SerialName
import kotlinx.serialization.Serializable

/**
 * 数据契约模型（计划书 §5.4、§6.7）。
 *
 * JSON 使用 snake_case，Kotlin 使用 camelCase，通过 [SerialName] 映射。
 * 禁止为省事把契约明确必填的字段做成 nullable；只有契约明确可选的字段才允许空值。
 *
 * 字段语义不得擅自改变；任何变更必须走 ADR（计划书 §17）。
 */

// ---------------------------------------------------------------- global_manifest.json

@Serializable
data class GlobalManifest(
    @SerialName("schema_version") val schemaVersion: Int,
    @SerialName("content_version") val contentVersion: String,
    @SerialName("scenes") val scenes: List<SceneIndexItem>
)

@Serializable
data class SceneIndexItem(
    @SerialName("scene_id") val sceneId: String,
    @SerialName("scene_name") val sceneName: String,
    @SerialName("qr_payload") val qrPayload: String,
    @SerialName("image_name") val imageName: String,
    @SerialName("scene_manifest") val sceneManifest: String,
    @SerialName("content_manifest") val contentManifest: String,
    @SerialName("thumbnail") val thumbnail: String,
    @SerialName("package_version") val packageVersion: Int,
    @SerialName("bundled") val bundled: Boolean
)

// ---------------------------------------------------------------- scene.json

@Serializable
data class SceneManifest(
    @SerialName("schema_version") val schemaVersion: Int,
    @SerialName("scene_id") val sceneId: String,
    @SerialName("environment_glb") val environmentGlb: String,
    @SerialName("visitor_start") val visitorStart: VisitorStart,
    @SerialName("movement") val movement: Movement,
    @SerialName("colliders") val colliders: List<Collider> = emptyList(),
    @SerialName("move_points") val movePoints: List<MovePoint> = emptyList(),
    @SerialName("props") val props: List<Prop>
)

@Serializable
data class VisitorStart(
    @SerialName("position_m") val positionM: List<Float>,
    @SerialName("rotation_deg") val rotationDeg: List<Float>
)

/** 计划书 §5.4：movement.type 枚举为 bounds / hotspots。 */
@Serializable
data class Movement(
    @SerialName("type") val type: String,
    @SerialName("speed_mps") val speedMps: Float,
    @SerialName("x_min_m") val xMinM: Float = 0f,
    @SerialName("x_max_m") val xMaxM: Float = 0f,
    @SerialName("z_min_m") val zMinM: Float = 0f,
    @SerialName("z_max_m") val zMaxM: Float = 0f
)

@Serializable
data class Collider(
    @SerialName("id") val id: String,
    @SerialName("min_m") val minM: List<Float>,
    @SerialName("max_m") val maxM: List<Float>
)

@Serializable
data class MovePoint(
    @SerialName("id") val id: String,
    @SerialName("position_m") val positionM: List<Float>,
    @SerialName("look_at_m") val lookAtM: List<Float>
)

@Serializable
data class Prop(
    @SerialName("id") val id: String,
    @SerialName("glb") val glb: String,
    @SerialName("position_m") val positionM: List<Float>,
    @SerialName("rotation_deg") val rotationDeg: List<Float>,
    @SerialName("scale") val scale: Float,
    @SerialName("interaction_radius_m") val interactionRadiusM: Float,
    @SerialName("highlight_anchor_m") val highlightAnchorM: List<Float>
)

// ---------------------------------------------------------------- content.json

@Serializable
data class ContentManifest(
    @SerialName("schema_version") val schemaVersion: Int,
    @SerialName("scene_id") val sceneId: String,
    @SerialName("items") val items: List<ContentItem>
)

@Serializable
data class ContentItem(
    @SerialName("id") val id: String,
    @SerialName("title") val title: String,
    @SerialName("text") val text: String,
    @SerialName("audio") val audio: String,
    @SerialName("audio_duration_sec") val audioDurationSec: Int,
    @SerialName("sources") val sources: List<ContentSource>,
    @SerialName("author") val author: String,
    @SerialName("reviewer") val reviewer: String,
    @SerialName("review_status") val reviewStatus: String
)

@Serializable
data class ContentSource(
    @SerialName("title") val title: String,
    @SerialName("type") val type: String,
    @SerialName("locator") val locator: String
)
