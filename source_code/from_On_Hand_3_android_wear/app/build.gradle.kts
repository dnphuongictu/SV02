plugins {
    id("com.android.application")
    id("org.jetbrains.kotlin.android")
}

android {
    namespace   = "vn.edu.uit.tpkd.wear.cogload"
    compileSdk  = 35

    defaultConfig {
        applicationId   = "vn.edu.uit.tpkd.wear.cogload"
        minSdk          = 30
        targetSdk       = 35
        versionCode     = 1
        versionName     = "1.0"
    }

    buildTypes {
        release {
            isMinifyEnabled = true
            proguardFiles(getDefaultProguardFile("proguard-android-optimize.txt"), "proguard-rules.pro")
        }
    }

    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_17
        targetCompatibility = JavaVersion.VERSION_17
    }
    kotlinOptions {
        jvmTarget = "17"
    }
}

dependencies {
    // Wear OS
    implementation("androidx.wear:wear:1.3.0")
    implementation("com.google.android.gms:play-services-wearable:18.1.0")

    // No TFLite: the ACC-only MLP (7->64->32->1, sigmoid) is small enough
    // that its forward pass is hand-implemented directly in Kotlin
    // (MlpInferenceEngine.kt), avoiding sklearn->ONNX->TFLite conversion
    // tooling this project has never used.

    // Core
    implementation("androidx.core:core-ktx:1.12.0")
}
