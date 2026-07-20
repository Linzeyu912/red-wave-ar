package cn.bistu.redwave.data

import kotlinx.serialization.json.Json

/**
 * JSON 解析配置（计划书 §6.7）。
 *
 * - snake_case → camelCase 由 @SerialName 映射；
 * - 默认忽略未知字段，便于 schema 向前兼容（旧 App 读新资源不立即崩溃），
 *   但编码方必须用 Schema 版本与跨文件校验保证已知字段正确；
 * - 不把契约必填字段设成可空，遇到缺失直接解析失败。
 */
object ManifestJson {

    val json: Json = Json {
        ignoreUnknownKeys = true
        isLenient = false
        explicitNulls = false
        coerceInputValues = true
    }

    fun parseGlobalManifest(text: String): GlobalManifest =
        json.decodeFromString(GlobalManifest.serializer(), text)

    fun parseSceneManifest(text: String): SceneManifest =
        json.decodeFromString(SceneManifest.serializer(), text)

    fun parseContentManifest(text: String): ContentManifest =
        json.decodeFromString(ContentManifest.serializer(), text)
}
