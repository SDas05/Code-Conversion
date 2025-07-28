from app.validation.base_validator import BaseValidator
from pathlib import Path
from typing import Dict
import subprocess
import time
import sys

class PerformanceAnalyzer(BaseValidator):
    def validate(self, original_file: Path, converted_file: Path) -> Dict:
        """
        Run both Python scripts and compare their execution times.
        Returns a dict with validation result and feedback.
        """
        if not (str(original_file).endswith('.py') and str(converted_file).endswith('.py')):
            return {
                "name": "PerformanceAnalyzer",
                "passed": False,
                "details": "PerformanceAnalyzer currently only supports Python files."
            }
        try:
            # Run original file
            start = time.time()
            orig_proc = subprocess.run([sys.executable, str(original_file)], capture_output=True, timeout=10)
            orig_time = time.time() - start
            if orig_proc.returncode != 0:
                return {
                    "name": "PerformanceAnalyzer",
                    "passed": False,
                    "details": f"Original file failed to run: {orig_proc.stderr.decode('utf-8')}"
                }
            # Run converted file
            start = time.time()
            conv_proc = subprocess.run([sys.executable, str(converted_file)], capture_output=True, timeout=10)
            conv_time = time.time() - start
            if conv_proc.returncode != 0:
                return {
                    "name": "PerformanceAnalyzer",
                    "passed": False,
                    "details": f"Converted file failed to run: {conv_proc.stderr.decode('utf-8')}"
                }
            # Compare execution times (allow up to 2x slower)
            if conv_time <= 2 * orig_time:
                passed = True
                details = f"Converted file ran in {conv_time:.3f}s, original in {orig_time:.3f}s. Performance acceptable."
            else:
                passed = False
                details = f"Converted file ran in {conv_time:.3f}s, original in {orig_time:.3f}s. Performance regression detected."
        except subprocess.TimeoutExpired:
            passed = False
            details = "Execution timed out."
        except Exception as e:
            passed = False
            details = f"Error during performance analysis: {e}"
        return {
            "name": "PerformanceAnalyzer",
            "passed": passed,
            "details": details
        } 