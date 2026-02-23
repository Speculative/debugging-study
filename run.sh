#!/bin/bash
# Run sensor calibration pipeline tests with Autopsy
# Autopsy hooks into pytest automatically - no special flags needed
uv run --only-group dev pytest test_sensor_pipeline.py -v
