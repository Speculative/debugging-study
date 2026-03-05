"""Sensor data ingestion pipeline.

Deserializes raw JSON sensor readings into typed objects and processes
them through a calibration and correction pipeline. Logs each
deserialization and processing step for observability.
"""

from dataclasses import dataclass
from datetime import datetime

@dataclass
class CalibrationData:
    """Calibration parameters for a sensor."""

    offset: float
    scale_factor: float
    calibrated_at: str
    method: str


@dataclass
class SensorReading:
    """A single reading from a temperature sensor."""

    sensor_id: str
    timestamp: str
    raw_value: float
    unit: str
    sensor_type: str
    location: str
    calibration: CalibrationData


@dataclass
class ProcessingResult:
    """Result of processing a sensor reading through the pipeline."""

    sensor_id: str
    raw_value: float
    adjusted_value: float
    sensor_type: str


class SensorPipeline:
    """Ingests, calibrates, and corrects sensor readings.

    Processes readings through a four-step pipeline:
      1. Ingest — deserialize raw JSON into typed objects
      2. Calibration apply — compute adjusted value from raw reading
      3. Drift correction — compensate for sensor drift since last calibration
      4. Linearization — apply sensor-type-specific linearity correction
    """

    DRIFT_RATES = {
        "thermocouple": 0.0001,   # 0.01% per day
        "rtd": 0.00005,            # 0.005% per day
        "self_calibrating": 0.0,   # continuously recalibrated; no drift
    }

    LINEARIZATION_COEFFICIENTS = {
        "thermocouple": 6e-7,      # thermocouple EMF non-linearity correction
        "rtd": 0.0,                # RTD response is highly linear
        "self_calibrating": 0.0,   # handled internally by sensor
    }

    def _deserialize_field(
        self,
        field_name: str,
        json_value,
        target_class: str,
        converted_value,
        conversion_method: str,
    ):
        return converted_value

    def _deserialize_calibration(self, json_cal: dict | None) -> CalibrationData:
        # Self-calibrating sensors don't need adjustment
        if json_cal is None:
            return CalibrationData(
                offset=0.0,
                scale_factor=0.0,
                calibrated_at="",
                method="none",
            )

        # For all others, use the manual calibration stored on the device
        cal = CalibrationData(
            offset=json_cal["offset"],
            scale_factor=json_cal["scale_factor"],
            calibrated_at=json_cal["calibrated_at"],
            method=json_cal["method"],
        )
        return cal

    def _deserialize_reading(self, json_data: dict) -> SensorReading:
        sensor_id = self._deserialize_field(
            "sensor_id", json_data["sensor_id"], "SensorReading",
            json_data["sensor_id"], "primitive",
        )
        timestamp = self._deserialize_field(
            "timestamp", json_data["timestamp"], "SensorReading",
            json_data["timestamp"], "primitive",
        )
        raw_value = self._deserialize_field(
            "raw_value", json_data["raw_value"], "SensorReading",
            float(json_data["raw_value"]), "primitive",
        )
        unit = self._deserialize_field(
            "unit", json_data["unit"], "SensorReading",
            json_data["unit"], "primitive",
        )
        sensor_type = self._deserialize_field(
            "sensor_type", json_data["sensor_type"], "SensorReading",
            json_data["sensor_type"], "primitive",
        )
        location = self._deserialize_field(
            "location", json_data["location"], "SensorReading",
            json_data["location"], "primitive",
        )
        calibration = self._deserialize_calibration(json_data.get("calibration"))

        return SensorReading(
            sensor_id=sensor_id,
            timestamp=timestamp,
            raw_value=raw_value,
            unit=unit,
            sensor_type=sensor_type,
            location=location,
            calibration=calibration,
        )

    def _apply_calibration(self, reading: SensorReading) -> float:
        """Apply the sensor's stored calibration and convert the result to Kelvin.

        Raw sensor output is an uncorrected voltage or resistance reading that has
        been factory-mapped to a Celsius value. The stored scale_factor and offset
        correct for individual sensor characteristics determined at calibration time
        (gain error and zero-point error respectively). The result is then converted
        to Kelvin, which is the canonical unit used for all downstream processing.
        """
        celsius = reading.raw_value * reading.calibration.scale_factor + reading.calibration.offset
        return celsius + 273.15

    def _apply_drift_correction(self, reading: SensorReading, adjusted_value: float) -> float:
        """Compensate for sensor drift accumulated since last calibration.

        All physical sensors drift over time: their output shifts slowly as
        component properties change with thermal cycling and aging. The drift
        rate varies by sensor type — thermocouples drift faster than RTDs due
        to grain boundary migration in the thermocouple wire. Self-calibrating
        sensors recalibrate against an internal reference on every reading, so
        their drift rate is effectively zero.

        Drift is modelled as a linear fractional gain error: the true value is
        estimated as measured * (1 + rate * days), where rate is the empirically
        determined drift coefficient for that sensor family.
        """
        drift_rate = self.DRIFT_RATES.get(reading.sensor_type, 0.0)
        if drift_rate == 0.0:
            return adjusted_value
        calibrated_at = datetime.fromisoformat(
            reading.calibration.calibrated_at.replace("Z", "+00:00")
        )
        reading_time = datetime.fromisoformat(
            reading.timestamp.replace("Z", "+00:00")
        )
        days_since_calibration = (reading_time - calibrated_at).days
        return adjusted_value * (1.0 + drift_rate * days_since_calibration)

    def _apply_linearization(self, reading: SensorReading, drift_corrected_value: float) -> float:
        """Apply a quadratic linearity correction for sensor-type-specific non-linearity.

        Thermocouples generate a voltage via the Seebeck effect, and the
        voltage-to-temperature conversion is not perfectly linear — it curves
        slightly across the operating range. A first-order correction adds a
        term proportional to the square of the reading, which accounts for this
        curvature. At laboratory temperatures the correction is small (< 0.1 K)
        but it becomes more significant at extreme temperatures.

        RTDs have a nearly linear resistance-to-temperature relationship and
        require no correction here. Self-calibrating sensors handle non-linearity
        internally.
        """
        coeff = self.LINEARIZATION_COEFFICIENTS.get(reading.sensor_type, 0.0)
        if coeff == 0.0:
            return drift_corrected_value
        return drift_corrected_value + coeff * (drift_corrected_value ** 2)

    def process_reading(self, json_data: dict) -> ProcessingResult:
        """Process a single sensor reading through the full pipeline."""

        # Step 1: Ingest
        reading = self._deserialize_reading(json_data)

        # Step 2: Apply calibration
        recalibrated_value = self._apply_calibration(reading)

        # Step 3: Drift correction
        drift_corrected = self._apply_drift_correction(reading, recalibrated_value)

        # Step 4: Linearization
        final_value = self._apply_linearization(reading, drift_corrected)

        return ProcessingResult(
            sensor_id=reading.sensor_id,
            raw_value=reading.raw_value,
            adjusted_value=final_value,
            sensor_type=reading.sensor_type,
        )

    def process_batch(self, json_documents: list[dict]) -> list[ProcessingResult]:
        """Process a batch of sensor readings."""
        return [self.process_reading(doc) for doc in json_documents]
