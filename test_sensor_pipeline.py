"""Tests for the sensor data ingestion and calibration pipeline.

Processes 25 sensor readings through the full pipeline and verifies
that the batch reports consistent temperature measurements, as expected
from sensors deployed in a controlled laboratory environment.
"""

import statistics

from sensor_pipeline import SensorPipeline
from sensor_readings import get_sensor_readings


def test_batch_sensor_alignment():
    """Process a full sensor batch and verify inter-sensor alignment.

    All 25 sensors are monitoring the same controlled environment.
    After calibration, readings should cluster tightly — a standard
    deviation above 2.0K indicates one or more sensors are reporting
    values inconsistent with the rest of the batch.
    """
    pipeline = SensorPipeline()
    results = pipeline.process_batch(get_sensor_readings())

    adjusted = [r.adjusted_value for r in results]
    batch_mean = statistics.mean(adjusted)
    batch_std = statistics.stdev(adjusted)

    assert batch_std < 2.0, (
        f"Sensor batch alignment check failed: "
        f"standard deviation {batch_std:.2f}K exceeds 2.0K threshold.\n"
        f"Expected sensors in controlled environment to report consistent readings.\n"
        f"Batch mean: {batch_mean:.2f}K, "
        f"range: [{min(adjusted):.2f}, {max(adjusted):.2f}]K"
    )
