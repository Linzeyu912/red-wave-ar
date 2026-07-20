plugins {
    alias(libs.plugins.android.application)
    alias(libs.plugins.kotlin.android)
    alias(libs.plugins.kotlin.serialization)
    alias(libs.plugins.kotlin.compose)
}

android {
    namespace = "cn.bistu.redwave"
    compileSdk = 34

    defaultConfig {
        applicationId = "cn.bistu.redwave"
        // 计划书 §6.4：最低 Android 8.0（API 26）；ARCore 为可选能力。
        minSdk = 26
        targetSdk = 34
        versionCode = 1
        versionName = "0.1.0"

        testInstrumentationRunner = "androidx.test.runner.AndroidJUnitRunner"
        vectorDrawables { useSupportLibrary = true }

        // 计划书 §15.4 要求记录版本/commit/资源版本；此处注入 BuildConfig。
        buildConfigField("String", "SCENE_CONTENT_VERSION", "\"2026.07.20.1\"")
    }

    // 计划书 §2.3：MVP 全应用固定横屏。
    buildFeatures {
        compose = true
        buildConfig = true
    }

    // 保留 minSdk 以上的原生 ABI；主展示机机型确定后再收紧（计划书 §6.4）。
    splits {
        abi {
            isEnable = false
        }
    }

    bundle {
        // 暂不按 ABI/密度拆分；CODE-11 发布阶段再决定。
        abi { enableSplit = false }
    }

    buildTypes {
        debug {
            isDebuggable = true
            // Debug 默认显示诊断浮层入口（计划书 §6.20）。
            buildConfigField("boolean", "ENABLE_DIAGNOSTICS_OVERLAY", "true")
            buildConfigField("boolean", "STRICT_RELEASE_VALIDATION", "false")
        }
        release {
            isMinifyEnabled = false
            // CODE-11 启用 R8 + 签名；此处先关闭以保证 MVP 编译通过。
            proguardFiles(
                getDefaultProguardFile("proguard-android-optimize.txt"),
                "proguard-rules.pro"
            )
            // Release 关闭诊断浮层并启用严格内容校验（计划书 §5.6 第7条、§6.5）。
            buildConfigField("boolean", "ENABLE_DIAGNOSTICS_OVERLAY", "false")
            buildConfigField("boolean", "STRICT_RELEASE_VALIDATION", "true")
        }
    }

    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_17
        targetCompatibility = JavaVersion.VERSION_17
    }

    kotlinOptions {
        jvmTarget = "17"
    }

    testOptions {
        unitTests {
            isIncludeAndroidResources = true
            isReturnDefaultValues = true
        }
    }

    packaging {
        resources {
            excludes += "/META-INF/{AL2.0,LGPL2.1}"
            excludes += "/META-INF/LICENSE*"
            excludes += "/META-INF/DEPENDENCIES"
        }
    }
}

dependencies {
    // Core / Lifecycle
    implementation(libs.androidx.core.ktx)
    implementation(libs.androidx.lifecycle.runtime.ktx)
    implementation(libs.androidx.lifecycle.viewmodel.compose)
    implementation(libs.androidx.lifecycle.runtime.compose)
    implementation(libs.androidx.activity.compose)

    // Compose
    implementation(platform(libs.androidx.compose.bom))
    implementation(libs.androidx.compose.ui)
    implementation(libs.androidx.compose.ui.graphics)
    implementation(libs.androidx.compose.ui.tooling.preview)
    implementation(libs.androidx.compose.material3)
    implementation(libs.androidx.compose.material.icons.extended)
    implementation(libs.androidx.navigation.compose)
    debugImplementation(libs.androidx.compose.ui.tooling)

    // Kotlinx
    implementation(libs.kotlinx.serialization.json)
    implementation(libs.kotlinx.coroutines.android)

    // Filament 渲染引擎（计划书 §3.2、§6.10，CODE-02+）
    implementation(libs.filament.android)
    implementation(libs.filament.gltfio)
    implementation(libs.filament.utils)

    // Media3 音频（计划书 §3.2、§6.15，CODE-07）
    implementation(libs.androidx.media3.exoplayer)
    implementation(libs.androidx.media3.common)
    implementation(libs.androidx.media3.session)

    // ZXing 二维码扫描（计划书 §3.2、CODE-08）
    implementation(libs.zxing.android.embedded)

    // Test
    testImplementation(libs.junit)
    testImplementation(libs.truth)
    testImplementation(libs.kotlinx.coroutines.test)
    testImplementation(libs.robolectric)
    androidTestImplementation(libs.androidx.junit)
    androidTestImplementation(libs.androidx.espresso.core)
    androidTestImplementation(platform(libs.androidx.compose.bom))
}
