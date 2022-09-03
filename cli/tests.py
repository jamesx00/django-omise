import pytest
import sys


def run_test_coverage():
    pytest.main(["--cov-report", "term", "--cov", "."])