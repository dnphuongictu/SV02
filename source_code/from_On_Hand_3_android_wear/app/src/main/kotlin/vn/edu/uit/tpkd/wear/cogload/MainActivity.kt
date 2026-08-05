// SPDX-License-Identifier: Apache-2.0

package vn.edu.uit.tpkd.wear.cogload

import android.app.Activity
import android.os.Bundle
import android.os.Handler
import android.os.Looper
import android.widget.TextView
import java.util.concurrent.Executors

/**
 * Main activity for the On_Hand_3 accelerometer-only cognitive-load demo on
 * Pixel Watch 2.
 *
 * Raw PPG is not accessible to third-party apps on this device (its raw
 * health-sensor permissions are `signature|privileged`), so this demo runs
 * the ACC-only MLP baseline instead of the full HRV+ACC pipeline. See
 * PROJECT_STATUS.md for the full finding.
 *
 * Flow: AccCollector (60s sliding window, 30s stride) -> AccFeatureExtractor
 * (7 handcrafted features) -> MlpInferenceEngine -> TextView.
 *
 * Plain accelerometer access requires no runtime permission on Android, so
 * collection starts immediately in onCreate.
 */
class MainActivity : Activity() {

    private lateinit var accCollector: AccCollector
    private lateinit var inferenceEngine: MlpInferenceEngine
    private lateinit var predictionLogger: PredictionLogger
    private lateinit var tvWorkload: TextView
    private lateinit var tvConfidence: TextView
    private lateinit var tvLatency: TextView

    private val bgExecutor = Executors.newSingleThreadExecutor()
    private val uiHandler = Handler(Looper.getMainLooper())

    private var totalInferences = 0L
    private var totalLatencyMs = 0.0

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        tvWorkload = findViewById(R.id.tv_workload)
        tvConfidence = findViewById(R.id.tv_confidence)
        tvLatency = findViewById(R.id.tv_latency)

        inferenceEngine = MlpInferenceEngine(this)
        predictionLogger = PredictionLogger(this)

        accCollector = AccCollector(this) { window ->
            bgExecutor.execute {
                val t0 = System.nanoTime()
                val features = AccFeatureExtractor.extract(window)
                val prediction = inferenceEngine.predict(features)
                val latencyMs = (System.nanoTime() - t0) / 1_000_000.0
                predictionLogger.log(features, prediction)

                totalInferences++
                totalLatencyMs += latencyMs
                val avgLatency = totalLatencyMs / totalInferences

                uiHandler.post {
                    tvWorkload.text = prediction.label
                    tvConfidence.text = "%.1f%%".format(prediction.confidence * 100)
                    tvLatency.text = "%.1f ms (avg %.1f)".format(latencyMs, avgLatency)
                }
            }
        }
        accCollector.start()
    }

    override fun onDestroy() {
        super.onDestroy()
        if (::accCollector.isInitialized) {
            accCollector.stop()
        }
        bgExecutor.shutdown()
    }
}
