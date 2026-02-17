#!/bin/bash
# Run API Gateway tests with Autopsy
# Autopsy hooks into pytest automatically - no special flags needed
uv run --only-group dev pytest test_api_gateway.py -v
