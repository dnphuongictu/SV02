// SPDX-License-Identifier: Apache-2.0

package vn.edu.uit.tpkd.wear.cogload

import android.content.Context
import org.json.JSONArray
import org.json.JSONObject
import kotlin.math.exp

/**
 * Hand-written forward pass for the WAUC ACC-only MLP
 * (`artifacts/wauc_baselines_60s/mlp_acc/final_model.joblib`), loaded from
 * `mlp_acc_weights.json` (produced by `scripts/export_mlp_acc_weights.py`,
 * which verifies this exact forward pass reproduces the sklearn Pipeline's
 * predictions on the full WAUC feature table before export).
 *
 * No TFLite/ONNX involved: the model is a tiny 7->64->32->1 fully-connected
 * network, small enough to run as plain matrix multiplication. sklearn's
 * `MLPClassifier` collapses binary classification to a single sigmoid
 * output unit (not a 2-way softmax) -- see the last layer shape (32, 1).
 */
class MlpInferenceEngine(context: Context, assetFileName: String = "mlp_acc_weights.json") {

    data class Prediction(val label: String, val confidence: Float)

    private val featureCount: Int
    private val imputerMedian: DoubleArray
    private val scalerMean: DoubleArray
    private val scalerScale: DoubleArray
    private val coefs: Array<Array<DoubleArray>> // [layer][inputUnit][outputUnit]
    private val intercepts: Array<DoubleArray>   // [layer][outputUnit]
    private val classes: IntArray

    init {
        val json = context.assets.open(assetFileName).bufferedReader().use { it.readText() }
        val root = JSONObject(json)

        val featureColumns = root.getJSONArray("feature_columns")
        featureCount = featureColumns.length()

        imputerMedian = readDoubleArray(root.getJSONArray("imputer_median"))
        scalerMean = readDoubleArray(root.getJSONArray("scaler_mean"))
        scalerScale = readDoubleArray(root.getJSONArray("scaler_scale"))

        val coefsJson = root.getJSONArray("coefs")
        coefs = Array(coefsJson.length()) { layer -> readMatrix(coefsJson.getJSONArray(layer)) }

        val interceptsJson = root.getJSONArray("intercepts")
        intercepts = Array(interceptsJson.length()) { layer -> readDoubleArray(interceptsJson.getJSONArray(layer)) }

        val classesJson = root.getJSONArray("classes")
        classes = IntArray(classesJson.length()) { classesJson.getInt(it) }

        val outActivation = root.optString("out_activation", "logistic")
        require(outActivation == "logistic") {
            "Unsupported out_activation '$outActivation' -- this engine assumes a binary " +
                "sigmoid output unit, matching scripts/export_mlp_acc_weights.py's parity check."
        }
        require(intercepts.last().size == 1) {
            "Expected a single sigmoid output unit, got ${intercepts.last().size}"
        }
    }

    /** @param features raw (unscaled) values in [AccFeatureExtractor] order, length [featureCount]. */
    fun predict(features: DoubleArray): Prediction {
        require(features.size == featureCount) {
            "Expected $featureCount features, got ${features.size}"
        }

        val scaled = DoubleArray(featureCount) { i ->
            val value = if (features[i].isNaN()) imputerMedian[i] else features[i]
            (value - scalerMean[i]) / scalerScale[i]
        }

        var activations = scaled
        for (layer in coefs.indices) {
            val isOutputLayer = layer == coefs.size - 1
            activations = denseForward(activations, coefs[layer], intercepts[layer], applyRelu = !isOutputLayer)
        }

        val logit = activations[0]
        val probabilityHigh = sigmoid(logit)
        val predictedClass = if (probabilityHigh >= 0.5) classes[1] else classes[0]
        val confidence = if (predictedClass == classes[1]) probabilityHigh else 1.0 - probabilityHigh
        val label = if (predictedClass == 1) "HIGH MENTAL WORKLOAD" else "LOW MENTAL WORKLOAD"
        return Prediction(label, confidence.toFloat())
    }

    private fun denseForward(input: DoubleArray, weight: Array<DoubleArray>, bias: DoubleArray, applyRelu: Boolean): DoubleArray {
        val outputSize = bias.size
        val output = DoubleArray(outputSize)
        for (j in 0 until outputSize) {
            var sum = bias[j]
            for (i in input.indices) {
                sum += input[i] * weight[i][j]
            }
            output[j] = if (applyRelu) maxOf(sum, 0.0) else sum
        }
        return output
    }

    private fun sigmoid(x: Double): Double = 1.0 / (1.0 + exp(-x))

    private fun readDoubleArray(array: JSONArray): DoubleArray =
        DoubleArray(array.length()) { array.getDouble(it) }

    private fun readMatrix(array: JSONArray): Array<DoubleArray> =
        Array(array.length()) { readDoubleArray(array.getJSONArray(it)) }
}
