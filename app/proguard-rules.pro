# ProGuard / R8 规则（CODE-11 发布阶段会扩充）
# 当前 MVP 关闭了 minify（app/build.gradle.kts 中 isMinifyEnabled = false）。
# 启用前需要补充 Filament、kotlinx.serialization、ARCore、Media3 的 keep 规则。

# kotlinx.serialization
-keepattributes *Annotation*, InnerClasses
-dontnote kotlinx.serialization.**
-keepclassmembers class **$$serializer { *; }
-keepclasseswithmembers class kotlinx.serialization.json.** {
    kotlinx.serialization.KSerializer serializer(...);
}

# 保留 BuildConfig
-keep class cn.bistu.redwave.BuildConfig { *; }
