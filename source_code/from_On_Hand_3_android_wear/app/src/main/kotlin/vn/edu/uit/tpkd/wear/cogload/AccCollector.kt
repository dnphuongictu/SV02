package vn.edu.uit.tpkd.wear.cogload

import android.content.Context
import android.hardware.Sensor
import android.hardware.SensorEvent
import android.hardware.SensorEventListener
import android.hardware.SensorManager
import java.util.ArrayDeque

/**
 * Collects raw 3-axis accelerometer samples and delivers a sliding time
 * window to [onWindowReady].
 *
 * Unlike the WAUC/WESAD training data (fixed-rate Empatica E4, 32 Hz), the
 * Pixel Watch 2's on-board accelerometer does not report samples at a
 * guaranteed fixed rate under `SENSOR_DELAY_GAME` -- so windowing here is
 * done by elapsed wall-clock time (event timestamps), not by sample count.
 * `acc_features()` (ported in [AccFeatureExtractor]) is pure window
 * statistics and does not require a specific sample rate, only a
 * consistently-sized time window.
 *
 * Unit conversion: the trained model saw Empatica E4 accelerometer data,
 * which is raw ADC counts (+-2g full scale at 8-bit resolution, so 1g ~= 64
 * counts -- confirmed empirically: at-rest magnitude in `data/raw/wauc/raw/S02/e4_acc.csv`
 * is ~63). Android's `Sensor.TYPE_ACCELEROMETER` reports SI units (m/s^2,
 * ~9.8 at rest). Feeding raw Android values into the model without
 * conversion pushes every feature far outside the training distribution and
 * saturates the MLP's sigmoid output to a single class regardless of actual
 * motion (observed on-device: prediction did not change even when shaking
 * the wrist vigorously). Samples are rescaled to E4-count-equivalent units
 * ([E4_COUNTS_PER_G] / [STANDARD_GRAVITY]) before buffering.
 */
class AccCollector(
    context: Context,
    private val onWindowReady: (List<FloatArray>) -> Unit // each element: [x, y, z]
) : SensorEventListener {

    private data class Sample(val timestampNanos: Long, val x: Float, val y: Float, val z: Float)

    private val sensorManager = context.getSystemService(Context.SENSOR_SERVICE) as SensorManager
    private val buffer = ArrayDeque<Sample>()
    private var lastEmitNanos = 0L

    fun start() {
        val accelerometer = sensorManager.getDefaultSensor(Sensor.TYPE_ACCELEROMETER)
        sensorManager.registerListener(this, accelerometer, SensorManager.SENSOR_DELAY_GAME)
    }

    fun stop() {
        sensorManager.unregisterListener(this)
    }

    override fun onSensorChanged(event: SensorEvent) {
        if (event.sensor.type != Sensor.TYPE_ACCELEROMETER) return

        val now = event.timestamp
        buffer.addLast(
            Sample(
                now,
                event.values[0] * COUNTS_PER_METER_PER_SECOND_SQUARED,
                event.values[1] * COUNTS_PER_METER_PER_SECOND_SQUARED,
                event.values[2] * COUNTS_PER_METER_PER_SECOND_SQUARED,
            )
        )

        val windowStart = now - WINDOW_NANOS
        while (true) {
            val oldest = buffer.peekFirst() ?: break
            if (oldest.timestampNanos >= windowStart) break
            buffer.removeFirst()
        }

        val spanNanos = now - (buffer.peekFirst()?.timestampNanos ?: now)
        val readyToEmit = spanNanos >= (WINDOW_NANOS * MIN_WINDOW_FILL_RATIO).toLong() &&
            (now - lastEmitNanos) >= STRIDE_NANOS

        if (readyToEmit) {
            lastEmitNanos = now
            val snapshot = buffer.map { floatArrayOf(it.x, it.y, it.z) }
            onWindowReady(snapshot)
        }
    }

    override fun onAccuracyChanged(sensor: Sensor, accuracy: Int) = Unit

    companion object {
        const val WINDOW_SECONDS = 60.0
        const val STRIDE_SECONDS = 30.0
        const val MIN_WINDOW_FILL_RATIO = 0.9

        private const val NANOS_PER_SECOND = 1_000_000_000L
        private val WINDOW_NANOS = (WINDOW_SECONDS * NANOS_PER_SECOND).toLong()
        private val STRIDE_NANOS = (STRIDE_SECONDS * NANOS_PER_SECOND).toLong()

        // Empatica E4 accelerometer: +-2g full scale at 8-bit resolution -> 1g ~= 64 raw counts.
        private const val E4_COUNTS_PER_G = 64.0
        private const val STANDARD_GRAVITY = 9.80665
        private const val COUNTS_PER_METER_PER_SECOND_SQUARED = (E4_COUNTS_PER_G / STANDARD_GRAVITY).toFloat()
    }
}
