"""Sensor reading data source.

Provides raw JSON documents representing temperature sensor readings
from a controlled laboratory environment. This module is a data
fixture — it is not the subject of debugging.
"""


def get_sensor_readings() -> list[dict]:
    """Return 25 sensor reading JSON documents for batch processing.

    The batch contains thermocouple sensors, RTD sensors, and
    self-calibrating optical reference sensors. All are monitoring
    ambient temperature in the same controlled environment.
    Thermocouple and RTD sensors include a calibration record;
    self-calibrating sensors do not.
    """
    return [
        # --- Thermocouple sensors (8) ---
        {
            "sensor_id": "TC-001",
            "timestamp": "2024-03-15T09:00:01Z",
            "raw_value": 22.8,
            "unit": "celsius",
            "sensor_type": "thermocouple",
            "location": "rack-A-shelf-1",
            "calibration": {
                "offset": 0.3,
                "scale_factor": 1.00,
                "calibrated_at": "2024-01-10T08:00:00Z",
                "method": "two_point",
            },
        },
        {
            "sensor_id": "TC-002",
            "timestamp": "2024-03-15T09:00:02Z",
            "raw_value": 23.5,
            "unit": "celsius",
            "sensor_type": "thermocouple",
            "location": "rack-A-shelf-2",
            "calibration": {
                "offset": -0.7,
                "scale_factor": 1.01,
                "calibrated_at": "2024-01-10T08:00:00Z",
                "method": "two_point",
            },
        },
        {
            "sensor_id": "TC-003",
            "timestamp": "2024-03-15T09:00:03Z",
            "raw_value": 24.1,
            "unit": "celsius",
            "sensor_type": "thermocouple",
            "location": "rack-A-shelf-3",
            "calibration": {
                "offset": 0.6,
                "scale_factor": 0.99,
                "calibrated_at": "2024-01-10T08:05:00Z",
                "method": "two_point",
            },
        },
        {
            "sensor_id": "TC-004",
            "timestamp": "2024-03-15T09:00:04Z",
            "raw_value": 21.9,
            "unit": "celsius",
            "sensor_type": "thermocouple",
            "location": "rack-B-shelf-1",
            "calibration": {
                "offset": 0.1,
                "scale_factor": 1.02,
                "calibrated_at": "2024-01-10T08:05:00Z",
                "method": "two_point",
            },
        },
        {
            "sensor_id": "TC-005",
            "timestamp": "2024-03-15T09:00:05Z",
            "raw_value": 25.2,
            "unit": "celsius",
            "sensor_type": "thermocouple",
            "location": "rack-B-shelf-2",
            "calibration": {
                "offset": -1.5,
                "scale_factor": 1.00,
                "calibrated_at": "2024-01-11T08:00:00Z",
                "method": "two_point",
            },
        },
        {
            "sensor_id": "TC-006",
            "timestamp": "2024-03-15T09:00:06Z",
            "raw_value": 22.3,
            "unit": "celsius",
            "sensor_type": "thermocouple",
            "location": "rack-B-shelf-3",
            "calibration": {
                "offset": 0.4,
                "scale_factor": 1.01,
                "calibrated_at": "2024-01-11T08:00:00Z",
                "method": "two_point",
            },
        },
        {
            "sensor_id": "TC-007",
            "timestamp": "2024-03-15T09:00:07Z",
            "raw_value": 24.8,
            "unit": "celsius",
            "sensor_type": "thermocouple",
            "location": "rack-C-shelf-1",
            "calibration": {
                "offset": 0.5,
                "scale_factor": 0.98,
                "calibrated_at": "2024-01-11T08:05:00Z",
                "method": "two_point",
            },
        },
        {
            "sensor_id": "TC-008",
            "timestamp": "2024-03-15T09:00:08Z",
            "raw_value": 23.0,
            "unit": "celsius",
            "sensor_type": "thermocouple",
            "location": "rack-C-shelf-2",
            "calibration": {
                "offset": -0.4,
                "scale_factor": 1.00,
                "calibrated_at": "2024-01-11T08:05:00Z",
                "method": "two_point",
            },
        },
        # --- RTD sensors (7) ---
        {
            "sensor_id": "RTD-001",
            "timestamp": "2024-03-15T09:00:09Z",
            "raw_value": 23.4,
            "unit": "celsius",
            "sensor_type": "rtd",
            "location": "rack-A-shelf-4",
            "calibration": {
                "offset": -0.2,
                "scale_factor": 1.01,
                "calibrated_at": "2024-01-12T08:00:00Z",
                "method": "factory",
            },
        },
        {
            "sensor_id": "RTD-002",
            "timestamp": "2024-03-15T09:00:10Z",
            "raw_value": 22.1,
            "unit": "celsius",
            "sensor_type": "rtd",
            "location": "rack-A-shelf-5",
            "calibration": {
                "offset": 1.1,
                "scale_factor": 1.00,
                "calibrated_at": "2024-01-12T08:00:00Z",
                "method": "factory",
            },
        },
        {
            "sensor_id": "RTD-003",
            "timestamp": "2024-03-15T09:00:11Z",
            "raw_value": 24.7,
            "unit": "celsius",
            "sensor_type": "rtd",
            "location": "rack-B-shelf-4",
            "calibration": {
                "offset": 0.3,
                "scale_factor": 0.99,
                "calibrated_at": "2024-01-12T08:05:00Z",
                "method": "factory",
            },
        },
        {
            "sensor_id": "RTD-004",
            "timestamp": "2024-03-15T09:00:12Z",
            "raw_value": 21.5,
            "unit": "celsius",
            "sensor_type": "rtd",
            "location": "rack-B-shelf-5",
            "calibration": {
                "offset": 0.8,
                "scale_factor": 1.02,
                "calibrated_at": "2024-01-12T08:05:00Z",
                "method": "factory",
            },
        },
        {
            "sensor_id": "RTD-005",
            "timestamp": "2024-03-15T09:00:13Z",
            "raw_value": 25.5,
            "unit": "celsius",
            "sensor_type": "rtd",
            "location": "rack-C-shelf-3",
            "calibration": {
                "offset": 0.2,
                "scale_factor": 0.98,
                "calibrated_at": "2024-01-13T08:00:00Z",
                "method": "factory",
            },
        },
        {
            "sensor_id": "RTD-006",
            "timestamp": "2024-03-15T09:00:14Z",
            "raw_value": 23.8,
            "unit": "celsius",
            "sensor_type": "rtd",
            "location": "rack-C-shelf-4",
            "calibration": {
                "offset": -0.6,
                "scale_factor": 1.01,
                "calibrated_at": "2024-01-13T08:00:00Z",
                "method": "factory",
            },
        },
        {
            "sensor_id": "RTD-007",
            "timestamp": "2024-03-15T09:00:15Z",
            "raw_value": 22.6,
            "unit": "celsius",
            "sensor_type": "rtd",
            "location": "rack-C-shelf-5",
            "calibration": {
                "offset": 0.9,
                "scale_factor": 1.00,
                "calibrated_at": "2024-01-13T08:05:00Z",
                "method": "factory",
            },
        },
        # --- Self-calibrating optical reference sensors (10) ---
        # These sensors perform internal calibration against a built-in
        # reference standard; no external calibration record is needed.
        {
            "sensor_id": "SC-001",
            "timestamp": "2024-03-15T09:00:16Z",
            "raw_value": 22.3,
            "unit": "celsius",
            "sensor_type": "self_calibrating",
            "location": "rack-A-shelf-6",
            "calibration": None,
        },
        {
            "sensor_id": "SC-002",
            "timestamp": "2024-03-15T09:00:17Z",
            "raw_value": 23.8,
            "unit": "celsius",
            "sensor_type": "self_calibrating",
            "location": "rack-A-shelf-7",
            "calibration": None,
        },
        {
            "sensor_id": "SC-003",
            "timestamp": "2024-03-15T09:00:18Z",
            "raw_value": 21.9,
            "unit": "celsius",
            "sensor_type": "self_calibrating",
            "location": "rack-B-shelf-6",
            "calibration": None,
        },
        {
            "sensor_id": "SC-004",
            "timestamp": "2024-03-15T09:00:19Z",
            "raw_value": 24.5,
            "unit": "celsius",
            "sensor_type": "self_calibrating",
            "location": "rack-B-shelf-7",
            "calibration": None,
        },
        {
            "sensor_id": "SC-005",
            "timestamp": "2024-03-15T09:00:20Z",
            "raw_value": 23.1,
            "unit": "celsius",
            "sensor_type": "self_calibrating",
            "location": "rack-C-shelf-6",
            "calibration": None,
        },
        {
            "sensor_id": "SC-006",
            "timestamp": "2024-03-15T09:00:21Z",
            "raw_value": 22.7,
            "unit": "celsius",
            "sensor_type": "self_calibrating",
            "location": "rack-C-shelf-7",
            "calibration": None,
        },
        {
            "sensor_id": "SC-007",
            "timestamp": "2024-03-15T09:00:22Z",
            "raw_value": 24.2,
            "unit": "celsius",
            "sensor_type": "self_calibrating",
            "location": "rack-D-shelf-1",
            "calibration": None,
        },
        {
            "sensor_id": "SC-008",
            "timestamp": "2024-03-15T09:00:23Z",
            "raw_value": 21.6,
            "unit": "celsius",
            "sensor_type": "self_calibrating",
            "location": "rack-D-shelf-2",
            "calibration": None,
        },
        {
            "sensor_id": "SC-009",
            "timestamp": "2024-03-15T09:00:24Z",
            "raw_value": 23.5,
            "unit": "celsius",
            "sensor_type": "self_calibrating",
            "location": "rack-D-shelf-3",
            "calibration": None,
        },
        {
            "sensor_id": "SC-010",
            "timestamp": "2024-03-15T09:00:25Z",
            "raw_value": 22.9,
            "unit": "celsius",
            "sensor_type": "self_calibrating",
            "location": "rack-D-shelf-4",
            "calibration": None,
        },
    ]
