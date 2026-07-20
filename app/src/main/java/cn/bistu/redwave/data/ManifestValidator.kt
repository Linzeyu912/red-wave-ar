package cn.bistu.redwave.data

import kotlin.math.abs

/**
 * Schema 与跨文件校验器（计划书 §5.5 字段约束 + §5.6 跨文件校验规则）。
 *
 * 本类只做“数据正确性”校验，不做 IO：调用方传入已解析的三个 manifest，
 * 得到 [ManifestValidationResult]。文件存在性由 [AssetResourceRoot] 单独检查。
 *
 * Release 严格模式（[strict]）下，未批准内容与占位文案直接判失败（§5.6 第 7 条）。
 */
class ManifestValidator(
    private val strict: Boolean = false
) {

    /** 是否处于 Release 严格模式（§5.6-7）。 */
    fun isStrictRelease(): Boolean = strict

    /** 当前期望的 schema 版本。schema_version 不匹配视为不兼容。 */
    private val expectedSchemaVersion: Int = 1

    /** scene_id 正则（§5.5：^S[1-9][0-9]*$）。 */
    private val sceneIdRegex = Regex("""^S[1-9][0-9]*$""")

    /**
     * 对三份 manifest 做完整跨文件校验。
     *
     * §5.6 覆盖项：
     * 1. 三文件 scene_id 一致；
     * 2. qr_payload / image_name / 文物 ID / collider ID / move_point ID 唯一；
     * 3. 每个 content.items[].id 对应一个文物；每个 MVP 文物有已批准内容；
     * 4. 路径安全（字符串级，文件存在性另行检查）；
     * 5. 起点与移动点在 bounds 内、不在 collider 内；
     * 6. 缩放有限正数、坐标有限；
     * 7. Release 拒绝占位/未批准内容。
     */
    fun validateBundle(
        global: GlobalManifest,
        scene: SceneManifest,
        content: ContentManifest
    ): ManifestValidationResult {
        val issues = ValidationIssues()
        validateGlobalManifest(global, issues)
        validateSceneManifest(scene, issues)
        validateContentManifest(content, issues)
        validateCrossFile(global, scene, content, issues)
        return issues.toResult()
    }

    // ---------------------------------------------------------------- global

    fun validateGlobalManifest(global: GlobalManifest, issues: ValidationIssues) {
        issues.addIf(global.schemaVersion != expectedSchemaVersion) {
            "global_manifest.schema_version=${global.schemaVersion} 与期望 $expectedSchemaVersion 不兼容"
        }
        issues.addIf(global.contentVersion.isBlank()) { "global_manifest.content_version 为空" }
        issues.addIf(global.scenes.isEmpty()) { "global_manifest.scenes 为空" }

        // §5.6-2：scene_id 不重复
        val sceneIds = global.scenes.map { it.sceneId }
        sceneIds.duplicates().forEach { dup ->
            issues.add("global_manifest: scene_id '$dup' 重复")
        }
        // qr_payload 全局唯一
        global.scenes.map { it.qrPayload }.duplicates().forEach { dup ->
            issues.add("global_manifest: qr_payload '$dup' 重复")
        }
        // image_name 全局唯一
        global.scenes.map { it.imageName }.duplicates().forEach { dup ->
            issues.add("global_manifest: image_name '$dup' 重复")
        }

        global.scenes.forEach { item ->
            issues.addIf(!sceneIdRegex.matches(item.sceneId)) {
                "global_manifest: scene_id '${item.sceneId}' 不符合 ^S[1-9][0-9]*\$"
            }
            issues.addIf(item.sceneName.isBlank()) { "global_manifest: scene_name 为空 (${item.sceneId})" }
            issues.addIf(item.qrPayload.isBlank()) { "global_manifest: qr_payload 为空 (${item.sceneId})" }
            issues.addIf(item.imageName.isBlank()) { "global_manifest: image_name 为空 (${item.sceneId})" }
            // §5.6-4：清单路径不允许绝对路径或 ..
            checkPath(item.sceneManifest, "scene_manifest (${item.sceneId})", issues)
            checkPath(item.contentManifest, "content_manifest (${item.sceneId})", issues)
            checkPath(item.thumbnail, "thumbnail (${item.sceneId})", issues)
            issues.addIf(item.packageVersion < 1) {
                "global_manifest: package_version 必须 >= 1 (${item.sceneId})"
            }
        }
    }

    // ---------------------------------------------------------------- scene

    fun validateSceneManifest(scene: SceneManifest, issues: ValidationIssues) {
        issues.addIf(scene.schemaVersion != expectedSchemaVersion) {
            "scene.json.schema_version=${scene.schemaVersion} 与期望 $expectedSchemaVersion 不兼容"
        }
        issues.addIf(!sceneIdRegex.matches(scene.sceneId)) {
            "scene.json: scene_id '${scene.sceneId}' 不符合 ^S[1-9][0-9]*\$"
        }
        checkPath(scene.environmentGlb, "environment_glb (${scene.sceneId})", issues)
        issues.addIf(!scene.environmentGlb.endsWith(".glb", ignoreCase = true)) {
            "scene.json: environment_glb 必须是 .glb 文件"
        }

        validateVec3(scene.visitorStart.positionM, "visitor_start.position_m", issues)
        validateVec3(scene.visitorStart.rotationDeg, "visitor_start.rotation_deg", issues)

        // movement
        val movement = scene.movement
        val validTypes = setOf("bounds", "hotspots")
        issues.addIf(movement.type !in validTypes) {
            "scene.json: movement.type '${movement.type}' 非法，允许 ${validTypes}"
        }
        issues.addIf(movement.speedMps.isNaN() || movement.speedMps <= 0f) {
            "scene.json: movement.speed_mps 必须为正数"
        }
        if (movement.type == "bounds") {
            issues.addIf(movement.xMinM >= movement.xMaxM) {
                "scene.json: movement x_min_m (${movement.xMinM}) 必须 < x_max_m (${movement.xMaxM})"
            }
            issues.addIf(movement.zMinM >= movement.zMaxM) {
                "scene.json: movement z_min_m (${movement.zMinM}) 必须 < z_max_m (${movement.zMaxM})"
            }
        }

        // §5.6-6：缩放有限正数、坐标有限
        scene.props.forEach { prop ->
            issues.addIf(prop.scale.isNaN() || prop.scale.isInfinite() || prop.scale <= 0f) {
                "scene.json: prop '${prop.id}' scale 必须为有限正数"
            }
            validateVec3(prop.positionM, "props[${prop.id}].position_m", issues)
            validateVec3(prop.rotationDeg, "props[${prop.id}].rotation_deg", issues)
            validateVec3(prop.highlightAnchorM, "props[${prop.id}].highlight_anchor_m", issues)
            checkPath(prop.glb, "props[${prop.id}].glb", issues)
            issues.addIf(!prop.glb.endsWith(".glb", ignoreCase = true)) {
                "scene.json: prop '${prop.id}' glb 必须是 .glb 文件"
            }
            issues.addIf(prop.interactionRadiusM.isNaN() || prop.interactionRadiusM <= 0f) {
                "scene.json: prop '${prop.id}' interaction_radius_m 必须为正数"
            }
        }

        // props id 唯一
        scene.props.map { it.id }.duplicates().forEach { dup ->
            issues.add("scene.json: prop id '$dup' 重复")
        }
        issues.addIf(scene.props.isEmpty()) { "scene.json: props 至少 1 项" }

        // colliders
        scene.colliders.forEach { c ->
            validateVec3(c.minM, "colliders[${c.id}].min_m", issues)
            validateVec3(c.maxM, "colliders[${c.id}].max_m", issues)
            // §5.5：min_m 每一维必须小于 max_m
            for (i in 0..2) {
                issues.addIf(c.minM[i] >= c.maxM[i]) {
                    "scene.json: collider '${c.id}' 第 ${i} 维 min(${c.minM[i]}) >= max(${c.maxM[i]})"
                }
            }
        }
        scene.colliders.map { it.id }.duplicates().forEach { dup ->
            issues.add("scene.json: collider id '$dup' 重复")
        }

        // move_points
        scene.movePoints.forEach { mp ->
            validateVec3(mp.positionM, "move_points[${mp.id}].position_m", issues)
            validateVec3(mp.lookAtM, "move_points[${mp.id}].look_at_m", issues)
        }
        scene.movePoints.map { it.id }.duplicates().forEach { dup ->
            issues.add("scene.json: move_point id '$dup' 重复")
        }
        issues.addIf(scene.movement.type == "hotspots" && scene.movePoints.isEmpty()) {
            "scene.json: movement.type=hotspots 时 move_points 必填"
        }
    }

    // ---------------------------------------------------------------- content

    fun validateContentManifest(content: ContentManifest, issues: ValidationIssues) {
        issues.addIf(content.schemaVersion != expectedSchemaVersion) {
            "content.json.schema_version=${content.schemaVersion} 与期望 $expectedSchemaVersion 不兼容"
        }
        issues.addIf(!sceneIdRegex.matches(content.sceneId)) {
            "content.json: scene_id '${content.sceneId}' 不符合 ^S[1-9][0-9]*\$"
        }
        val validReview = setOf("draft", "reviewing", "approved")
        content.items.forEach { item ->
            issues.addIf(item.title.isBlank()) { "content.json: item '${item.id}' title 为空" }
            issues.addIf(item.text.isBlank()) { "content.json: item '${item.id}' text 为空" }
            issues.addIf(item.audio.isBlank()) { "content.json: item '${item.id}' audio 为空" }
            checkPath(item.audio, "content.items[${item.id}].audio", issues)
            issues.addIf(item.audioDurationSec <= 0) {
                "content.json: item '${item.id}' audio_duration_sec 必须 > 0"
            }
            issues.addIf(item.sources.isEmpty()) {
                "content.json: item '${item.id}' sources 至少 1 项"
            }
            issues.addIf(item.author.isBlank()) {
                "content.json: item '${item.id}' author 为空"
            }
            issues.addIf(item.reviewer.isBlank()) {
                "content.json: item '${item.id}' reviewer 为空"
            }
            issues.addIf(item.reviewStatus !in validReview) {
                "content.json: item '${item.id}' review_status '${item.reviewStatus}' 非法"
            }
            // §5.6-7：Release 禁止占位文本与未批准内容
            if (strict) {
                issues.addIf(item.reviewStatus != "approved") {
                    "content.json(Release): item '${item.id}' review_status 非 approved"
                }
                issues.addIf(isPlaceholderText(item.text)) {
                    "content.json(Release): item '${item.id}' text 含占位内容"
                }
                issues.addIf(isPlaceholderAuthor(item.author) || isPlaceholderAuthor(item.reviewer)) {
                    "content.json(Release): item '${item.id}' author/reviewer 含占位值"
                }
            }
        }
        content.items.map { it.id }.duplicates().forEach { dup ->
            issues.add("content.json: item id '$dup' 重复")
        }
    }

    // ---------------------------------------------------------------- cross-file

    /**
     * 跨文件校验（§5.6 第 1/3/5 条）。需要三份 manifest 都已单独通过基础校验更有意义，
     * 但本方法对部分缺失也尽量报全问题。
     */
    fun validateCrossFile(
        global: GlobalManifest,
        scene: SceneManifest,
        content: ContentManifest,
        issues: ValidationIssues
    ) {
        // §5.6-1：scene_id 三文件一致
        val globalItem = global.scenes.firstOrNull { it.sceneId == scene.sceneId }
        issues.addIf(globalItem == null) {
            "跨文件: scene.json 的 scene_id '${scene.sceneId}' 在 global_manifest 中找不到"
        }
        issues.addIf(scene.sceneId != content.sceneId) {
            "跨文件: scene.json scene_id '${scene.sceneId}' 与 content.json '${content.sceneId}' 不一致"
        }

        // §5.6-3：每个 content.items[].id 必须能在 scene.props[].id 找到
        val propIds = scene.props.map { it.id }.toSet()
        content.items.forEach { item ->
            issues.addIf(item.id !in propIds) {
                "跨文件: content item '${item.id}' 在 scene.json props 中找不到对应文物"
            }
        }
        // 每个 MVP 文物（这里默认 scene.props 全部）都有内容覆盖
        val contentIds = content.items.map { it.id }.toSet()
        scene.props.forEach { prop ->
            issues.addIf(prop.id !in contentIds) {
                "跨文件: 文物 '${prop.id}' 在 content.json 中缺少内容条目"
            }
        }

        // §5.6-5：起点与移动点在 bounds 内且不在 collider 内
        if (scene.movement.type == "bounds") {
            checkInBounds(scene.visitorStart.positionM, scene.movement, "visitor_start", issues)
            scene.movePoints.forEach { mp ->
                checkInBounds(mp.positionM, scene.movement, "move_point ${mp.id}", issues)
            }
            // 起点不在 collider 内
            checkNotInCollider(scene.visitorStart.positionM, scene.colliders, "visitor_start", issues)
            scene.movePoints.forEach { mp ->
                checkNotInCollider(mp.positionM, scene.colliders, "move_point ${mp.id}", issues)
            }
        }
    }

    // ---------------------------------------------------------------- helpers

    private fun checkPath(path: String, field: String, issues: ValidationIssues) {
        ResourcePathSafety.stringCheck(path, field)?.let { issues.add(it) }
    }

    private fun validateVec3(v: List<Float>, field: String, issues: ValidationIssues) {
        issues.addIf(v.size != 3) { "$field 必须是长度为 3 的数组，实际 ${v.size}" }
        if (v.size == 3) {
            issues.addIf(v.any { it.isNaN() || it.isInfinite() }) {
                "$field 含 NaN 或无穷值"
            }
        }
    }

    private fun checkInBounds(pos: List<Float>, movement: Movement, label: String, issues: ValidationIssues) {
        if (pos.size != 3) return // 已由 vec3 校验报告
        val x = pos[0]; val z = pos[2]
        issues.addIf(x < movement.xMinM || x > movement.xMaxM) {
            "$label 位置 x=$x 不在 movement bounds [${movement.xMinM}, ${movement.xMaxM}] 内"
        }
        issues.addIf(z < movement.zMinM || z > movement.zMaxM) {
            "$label 位置 z=$z 不在 movement bounds [${movement.zMinM}, ${movement.zMaxM}] 内"
        }
    }

    private fun checkNotInCollider(pos: List<Float>, colliders: List<Collider>, label: String, issues: ValidationIssues) {
        if (pos.size != 3) return
        colliders.forEach { c ->
            if (c.minM.size == 3 && c.maxM.size == 3) {
                val inside = pos[0] >= c.minM[0] && pos[0] <= c.maxM[0] &&
                    pos[1] >= c.minM[1] && pos[1] <= c.maxM[1] &&
                    pos[2] >= c.minM[2] && pos[2] <= c.maxM[2]
                issues.addIf(inside) {
                    "$label 位置 ${pos} 落入 collider '${c.id}' 内"
                }
            }
        }
    }

    /** Release 占位文本判定（§5.6-7）。只做明显占位特征检测，不阻断合理文案。 */
    private fun isPlaceholderText(text: String): Boolean {
        val markers = listOf("TODO", "待填写", "占位", "PLACEHOLDER", "lorem ipsum", "示例文本")
        return markers.any { text.contains(it, ignoreCase = true) }
    }

    private fun isPlaceholderAuthor(name: String): Boolean {
        val trimmed = name.trim()
        return trimmed.isEmpty() || trimmed in setOf("待填写", "TODO", "TBD")
    }

    /** 计算重复元素。返回出现次数 > 1 的元素列表。 */
    private fun <T> List<T>.duplicates(): List<T> =
        groupingBy { it }.eachCount().filter { it.value > 1 }.keys.toList()

    companion object {
        /** 容差：用于浮点坐标比较。 */
        const val FLOAT_EPS: Float = 1e-5f

        /** 判断两个浮点近似相等，供测试断言使用。 */
        fun approxEqual(a: Float, b: Float): Boolean = abs(a - b) < FLOAT_EPS
    }
}
