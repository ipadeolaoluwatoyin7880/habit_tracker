#!/usr/bin/env python3
"""
Test runner for Habit Tracker
"""
import subprocess
import sys

def run_tests():
    """Run pytest with appropriate arguments"""
    result = subprocess.run([
        sys.executable, "-m", "pytest",
        "tests/", "-v", "--tb=short"
    ])
    return result.returncode

if __name__ == "__main__":
    exit_code = run_tests()
    sys.exit(exit_code)