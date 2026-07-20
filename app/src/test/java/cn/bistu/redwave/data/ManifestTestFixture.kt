package cn.bistu.redwave.data

/**
 * CODE-01 测试用 JSON fixture（计划书 §5.4、§15.1 UT-001~007、014）。
 *
 * 集中维护有效样本与各类无效样本，避免测试散落硬编码字符串。
 * 坐标取自建模交付的真实 scene.json 白盒值。
 */
object ManifestTestFixture {

    /** 计划书 §5.4 的有效 global_manifest（S1 单场景）。 */
    const val VALID_GLOBAL = """
{
  "schema_version": 1,
  "content_version": "2026.07.20.1",
  "scenes": [
    {
      "scene_id": "S1",
      "scene_name": "地下情报电台",
      "qr_payload": "REDWAVE-S1",
      "image_name": "trigger_S1",
      "scene_manifest": "scenes/scene_S1/scene.json",
      "content_manifest": "scenes/scene_S1/content.json",
      "thumbnail": "scenes/scene_S1/thumbnail.png",
      "package_version": 1,
      "bundled": true
    }
  ]
}
"""

    /** 坐标取自建模白盒 scene.json。 */
    const val VALID_SCENE = """
{
  "schema_version": 1,
  "scene_id": "S1",
  "environment_glb": "environment_whitebox.glb",
  "visitor_start": { "position_m": [0.0, 1.6, 3.0], "rotation_deg": [0.0, 0.0, 0.0] },
  "movement": { "type": "bounds", "speed_mps": 1.2, "x_min_m": -3.6, "x_max_m": 3.6, "z_min_m": -3.6, "z_max_m": 3.6 },
  "colliders": [
    { "id": "wall_north", "min_m": [-4.2, 0.0, -4.2], "max_m": [4.2, 2.6, -4.0] }
  ],
  "move_points": [
    { "id": "mp_radio", "position_m": [1.15, 1.6, 0.75], "look_at_m": [0.55, 1.0, 1.55] }
  ],
  "props": [
    { "id": "p_s1_radio", "glb": "props/radio_station_whitebox.glb", "position_m": [0.55, 0.78, 1.6], "rotation_deg": [0.0, 0.0, 0.0], "scale": 1.0, "interaction_radius_m": 1.8, "highlight_anchor_m": [0.0, 0.42, 0.0] },
    { "id": "p_s1_key", "glb": "props/telegraph_key_whitebox.glb", "position_m": [0.15, 0.78, 1.28], "rotation_deg": [0.0, 0.0, 0.0], "scale": 1.0, "interaction_radius_m": 1.5, "highlight_anchor_m": [0.0, 0.12, 0.0] },
    { "id": "p_s1_codebook", "glb": "props/code_book_whitebox.glb", "position_m": [1.32, 0.78, 1.35], "rotation_deg": [0.0, 0.0, 0.0], "scale": 1.0, "interaction_radius_m": 1.5, "highlight_anchor_m": [0.0, 0.1, 0.0] }
  ]
}
"""

    /** 文案取自 research/ content_brief.md 的 draft。 */
    const val VALID_CONTENT = """
{
  "schema_version": 1,
  "scene_id": "S1",
  "items": [
    { "id": "p_s1_radio", "title": "秘密电台", "text": "1943 年冬，党组织在涧沟村建立秘密电台。", "audio": "audio/p_s1_radio_zh.mp3", "audio_duration_sec": 70, "sources": [{"title":"北京日报","type":"news","locator":"SRC-005"}], "author": "文创组", "reviewer": "项目负责人", "review_status": "approved" },
    { "id": "p_s1_key", "title": "发报键与电讯联络", "text": "发报键把人工按压转换为电信号。", "audio": "audio/p_s1_key_zh.mp3", "audio_duration_sec": 55, "sources": [{"title":"中国军网","type":"military","locator":"SRC-004"}], "author": "文创组", "reviewer": "项目负责人", "review_status": "approved" },
    { "id": "p_s1_codebook", "title": "电文与保密通信资料包", "text": "隐蔽通信需要严格的保密纪律。", "audio": "audio/p_s1_codebook_zh.mp3", "audio_duration_sec": 60, "sources": [{"title":"人民网","type":"party_history","locator":"SRC-006"}], "author": "文创组", "reviewer": "项目负责人", "review_status": "approved" }
  ]
}
"""

    // ------------------------------------------------------------------ invalid variants

    /** 重复 scene_id（UT-002 衍生）。 */
    const val DUPLICATE_SCENE_ID = """
{
  "schema_version": 1, "content_version": "x",
  "scenes": [
    { "scene_id": "S1", "scene_name": "a", "qr_payload": "REDWAVE-S1", "image_name": "trigger_S1", "scene_manifest": "a/scene.json", "content_manifest": "a/content.json", "thumbnail": "a/t.png", "package_version": 1, "bundled": true },
    { "scene_id": "S1", "scene_name": "b", "qr_payload": "REDWAVE-S2", "image_name": "trigger_S2", "scene_manifest": "b/scene.json", "content_manifest": "b/content.json", "thumbnail": "b/t.png", "package_version": 1, "bundled": true }
  ]
}
"""

    /** 重复 qr_payload（UT-002）。 */
    const val DUPLICATE_QR = """
{
  "schema_version": 1, "content_version": "x",
  "scenes": [
    { "scene_id": "S1", "scene_name": "a", "qr_payload": "REDWAVE-S1", "image_name": "trigger_S1", "scene_manifest": "a/scene.json", "content_manifest": "a/content.json", "thumbnail": "a/t.png", "package_version": 1, "bundled": true },
    { "scene_id": "S2", "scene_name": "b", "qr_payload": "REDWAVE-S1", "image_name": "trigger_S2", "scene_manifest": "b/scene.json", "content_manifest": "b/content.json", "thumbnail": "b/t.png", "package_version": 1, "bundled": true }
  ]
}
"""

    /** 路径穿越（UT-003）。 */
    const val PATH_TRAVERSAL_GLOBAL = """
{
  "schema_version": 1, "content_version": "x",
  "scenes": [
    { "scene_id": "S1", "scene_name": "a", "qr_payload": "REDWAVE-S1", "image_name": "trigger_S1", "scene_manifest": "../escape/scene.json", "content_manifest": "a/content.json", "thumbnail": "a/t.png", "package_version": 1, "bundled": true }
  ]
}
"""

    /** content item id 找不到对应 prop（UT-004）。 */
    const val CONTENT_ORPHAN_ITEM = """
{
  "schema_version": 1, "scene_id": "S1",
  "items": [
    { "id": "p_nonexistent", "title": "x", "text": "y", "audio": "audio/x.mp3", "audio_duration_sec": 10, "sources": [{"title":"s","type":"news","locator":"src"}], "author": "a", "reviewer": "r", "review_status": "approved" }
  ]
}
"""

    /** review_status=draft（UT-005）。 */
    const val CONTENT_DRAFT_REVIEW = """
{
  "schema_version": 1, "scene_id": "S1",
  "items": [
    { "id": "p_s1_radio", "title": "秘密电台", "text": "占位说明。", "audio": "audio/x.mp3", "audio_duration_sec": 70, "sources": [{"title":"s","type":"news","locator":"src"}], "author": "a", "reviewer": "r", "review_status": "draft" }
  ]
}
"""

    /** 起点落入 collider（UT-006）。起点 z=-4.1 落入 wall_north [-4.2..-4.0]。 */
    const val SCENE_START_IN_COLLIDER = """
{
  "schema_version": 1, "scene_id": "S1",
  "environment_glb": "environment_whitebox.glb",
  "visitor_start": { "position_m": [0.0, 1.6, -4.1], "rotation_deg": [0.0, 0.0, 0.0] },
  "movement": { "type": "bounds", "speed_mps": 1.2, "x_min_m": -5.0, "x_max_m": 5.0, "z_min_m": -5.0, "z_max_m": 5.0 },
  "colliders": [
    { "id": "wall_north", "min_m": [-4.2, 0.0, -4.2], "max_m": [4.2, 2.6, -4.0] }
  ],
  "move_points": [],
  "props": [
    { "id": "p_s1_radio", "glb": "props/radio_station_whitebox.glb", "position_m": [0.55, 0.78, 1.6], "rotation_deg": [0.0, 0.0, 0.0], "scale": 1.0, "interaction_radius_m": 1.8, "highlight_anchor_m": [0.0, 0.42, 0.0] }
  ]
}
"""
}
