"""Pytest configuration for autopsy integration."""

import pytest

from autopsy import report
from autopsy.report import generate_html


def pytest_addoption(parser):
    """Add command-line option to generate autopsy report."""
    parser.addoption(
        "--generate-report",
        action="store_true",
        default=True,
        help="Generate autopsy report after running tests",
    )
    parser.addoption(
        "--report-output",
        action="store",
        default="autopsy_report.html",
        help="Output path for autopsy report (default: autopsy_report.html)",
    )


@pytest.fixture(scope="session", autouse=True)
def init_report(request):
    """Initialize autopsy report at the start of the test session."""
    report.init()
    report.timeline("API Gateway test session started")

    yield

    report.timeline("Test session completed")

    # Generate report if requested
    if request.config.getoption("--generate-report", default=True):
        output_path = request.config.getoption(
            "--report-output", default="autopsy_report.html"
        )
        generate_html(output_path=output_path)
        print(f"\n✓ Autopsy report saved to {output_path}")


@pytest.fixture(autouse=True)
def log_test_name(request):
    """Log the start and end of each test for tracing."""
    test_name = request.node.name
    report.log("test_start", test_name)
    yield
    report.log("test_end", test_name)
