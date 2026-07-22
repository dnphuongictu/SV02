package vn.edu.uit.tpkd.wear.cogload

import kotlin.math.sqrt

/**
 * Kotlin port of `acc_features()` in `src/on_hand_3/features.py`. Must stay
 * numerically consistent with that function (same ddof=1 sample-std
 * convention as numpy) since it feeds a model trained on Python-computed
 * features -- see `scripts/export_mlp_acc_weights.py` for the parity check
 * against the original sklearn Pipeline.
 *
 * Output order matches `summary.json["feature_columns"]` for `mlp_acc`:
 * [mean_magnitude, std_magnitude, dynamic_energy, zero_crossing_rate,
 *  std_x, std_y, std_z]
 */
object AccFeatureExtractor {

    fun extract(window: List<FloatArray>): DoubleArray {
        val n = window.size
        require(n >= 2) { "Need at least 2 accelerometer samples, got $n" }

        val magnitude = DoubleArray(n)
        var sumX = 0.0
        var sumY = 0.0
        var sumZ = 0.0
        for (i in 0 until n) {
            val sample = window[i]
            val x = sample[0].toDouble()
            val y = sample[1].toDouble()
            val z = sample[2].toDouble()
            magnitude[i] = sqrt(x * x + y * y + z * z)
            sumX += x
            sumY += y
            sumZ += z
        }
        val meanX = sumX / n
        val meanY = sumY / n
        val meanZ = sumZ / n

        val meanMagnitude = magnitude.average()

        var sumSqDevMagnitude = 0.0
        var dynamicEnergySum = 0.0
        var sumSqDevX = 0.0
        var sumSqDevY = 0.0
        var sumSqDevZ = 0.0
        for (i in 0 until n) {
            val sample = window[i]
            val x = sample[0].toDouble()
            val y = sample[1].toDouble()
            val z = sample[2].toDouble()
            val devMag = magnitude[i] - meanMagnitude
            sumSqDevMagnitude += devMag * devMag

            val dx = x - meanX
            val dy = y - meanY
            val dz = z - meanZ
            dynamicEnergySum += dx * dx + dy * dy + dz * dz

            sumSqDevX += dx * dx
            sumSqDevY += dy * dy
            sumSqDevZ += dz * dz
        }
        val stdMagnitude = sqrt(sumSqDevMagnitude / (n - 1))
        val dynamicEnergy = dynamicEnergySum / n
        val stdX = sqrt(sumSqDevX / (n - 1))
        val stdY = sqrt(sumSqDevY / (n - 1))
        val stdZ = sqrt(sumSqDevZ / (n - 1))

        var signChanges = 0
        var previousSign = (magnitude[0] - meanMagnitude) >= 0.0
        for (i in 1 until n) {
            val sign = (magnitude[i] - meanMagnitude) >= 0.0
            if (sign != previousSign) signChanges++
            previousSign = sign
        }
        val zeroCrossingRate = signChanges.toDouble() / (n - 1)

        return doubleArrayOf(
            meanMagnitude,
            stdMagnitude,
            dynamicEnergy,
            zeroCrossingRate,
            stdX,
            stdY,
            stdZ,
        )
    }
}
