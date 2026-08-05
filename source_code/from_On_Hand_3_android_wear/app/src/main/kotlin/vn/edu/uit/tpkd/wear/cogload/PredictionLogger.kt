// SPDX-License-Identifier: Apache-2.0

package vn.edu.uit.tpkd.wear.cogload

import android.content.Context
import android.util.Log
import java.io.File
import java.text.SimpleDateFormat
import java.util.Date
import java.util.Locale

/**
 * Appends one CSV row per inference window to an app-private file, so it can
 * be retrieved with `adb pull` (no runtime storage permission needed since
 * this uses the app-specific external files directory) and compared against
 * the WAUC training feature distribution -- see
 * `scripts/compare_onboard_calibration.py`. This is what makes the
 * accelerometer unit-mismatch fix (see AccCollector.kt) verifiable with real
 * numbers instead of only the qualitative rest/shake confidence check.
 */
class PredictionLogger(context: Context, fileName: String = "prediction_log.csv") {

    private val externalDir: File? = context.getExternalFilesDir(null)
    private val logFile: File = File(externalDir ?: context.filesDir, fileName)

    init {
        Log.i(TAG, "externalFilesDir=$externalDir, resolved logFile=${logFile.absolutePath}")
        try {
            logFile.parentFile?.mkdirs()
            if (!logFile.exists()) {
                logFile.writeText(
                    "timestamp_iso,acc_mean_magnitude,acc_std_magnitude,acc_dynamic_energy," +
                        "acc_zero_crossing_rate,acc_std_x,acc_std_y,acc_std_z," +
                        "predicted_label,confidence\n"
                )
                Log.i(TAG, "Created log file at ${logFile.absolutePath}")
            }
        } catch (error: Exception) {
            Log.e(TAG, "Failed to create log file at ${logFile.absolutePath}", error)
        }
    }

    fun log(features: DoubleArray, prediction: MlpInferenceEngine.Prediction) {
        require(features.size == 7) { "Expected 7 ACC features, got ${features.size}" }
        val timestamp = ISO_FORMAT.format(Date())
        val row = buildString {
            append(timestamp)
            for (value in features) {
                append(',')
                append(value)
            }
            append(',')
            append(prediction.label)
            append(',')
            append(prediction.confidence)
            append('\n')
        }
        try {
            logFile.appendText(row)
        } catch (error: Exception) {
            Log.e(TAG, "Failed to append log row to ${logFile.absolutePath}", error)
        }
    }

    val path: String get() = logFile.absolutePath

    companion object {
        private const val TAG = "PredictionLogger"
        private val ISO_FORMAT =
            SimpleDateFormat("yyyy-MM-dd'T'HH:mm:ss.SSS", Locale.US)
    }
}
