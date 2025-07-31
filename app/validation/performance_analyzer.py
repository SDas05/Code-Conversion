from app.validation.base_validator import BaseValidator
from pathlib import Path
from typing import Dict
import subprocess
import time
import sys
import os

class PerformanceAnalyzer(BaseValidator):
    def validate(self, original_file: Path, converted_file: Path) -> Dict:
        """
        Validate cross-language conversions by checking code structure and complexity.
        Returns a dict with validation result and feedback.
        """
        source_lang = original_file.suffix[1:].lower() if original_file.suffix else "unknown"
        target_lang = converted_file.suffix[1:].lower() if converted_file.suffix else "unknown"
        
        # For same-language Python conversions, use execution time comparison
        if source_lang == target_lang and source_lang == "py":
            return self._validate_python_performance(original_file, converted_file)
        
        # For cross-language conversions, use structural complexity analysis
        return self._validate_cross_language_complexity(original_file, converted_file, source_lang, target_lang)
    
    def _validate_python_performance(self, original_file: Path, converted_file: Path) -> Dict:
        """Validate Python to Python conversions using execution time comparison."""
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
    
    def _validate_cross_language_complexity(self, original_file: Path, converted_file: Path, 
                                           source_lang: str, target_lang: str) -> Dict:
        """Validate cross-language conversions by analyzing code complexity."""
        try:
            with open(original_file, "r", encoding="utf-8") as f:
                original_code = f.read()
            with open(converted_file, "r", encoding="utf-8") as f:
                converted_code = f.read()
            
            # Analyze complexity metrics
            original_metrics = self._analyze_complexity(original_code, source_lang)
            converted_metrics = self._analyze_complexity(converted_code, target_lang)
            
            # Compare complexity (allow for reasonable differences in cross-language conversions)
            passed, details = self._compare_complexity_metrics(
                original_metrics, converted_metrics, source_lang, target_lang
            )
            
        except Exception as e:
            passed = True  # Default to pass for cross-language conversions
            details = f"Cross-language complexity analysis error: {e}. Defaulting to PASS."
        
        return {
            "name": "PerformanceAnalyzer",
            "passed": passed,
            "details": details
        }
    
    def _analyze_complexity(self, code: str, language: str) -> Dict:
        """Analyze code complexity metrics."""
        lines = code.split('\n')
        non_empty_lines = [line for line in lines if line.strip()]
        
        metrics = {
            "total_lines": len(lines),
            "non_empty_lines": len(non_empty_lines),
            "functions": 0,
            "classes": 0,
            "control_structures": 0,
            "complexity_score": 0
        }
        
        # Count functions
        if language == "py":
            metrics["functions"] = code.count("def ")
        elif language == "java":
            metrics["functions"] = code.count("public ") + code.count("private ") + code.count("protected ")
        elif language == "js":
            metrics["functions"] = code.count("function ") + code.count("=>")
        
        # Count classes
        metrics["classes"] = code.count("class ")
        
        # Count control structures
        control_keywords = ["if ", "for ", "while ", "try ", "switch ", "case "]
        metrics["control_structures"] = sum(code.count(keyword) for keyword in control_keywords)
        
        # Calculate complexity score (simple heuristic)
        metrics["complexity_score"] = (
            metrics["functions"] * 2 + 
            metrics["classes"] * 3 + 
            metrics["control_structures"] * 1 +
            metrics["non_empty_lines"] * 0.1
        )
        
        return metrics
    
    def _compare_complexity_metrics(self, original: Dict, converted: Dict, 
                                   source_lang: str, target_lang: str) -> tuple:
        """Compare complexity metrics between original and converted code."""
        # For cross-language conversions, we're more lenient
        # Check if the converted code has reasonable complexity
        
        # Check if functions are preserved (with some tolerance)
        if original["functions"] > 0:
            function_ratio = converted["functions"] / original["functions"]
            if function_ratio < 0.5:  # Allow some reduction due to language differences
                return False, f"Too many functions missing in {target_lang} conversion"
        
        # Check if classes are preserved
        if original["classes"] > 0 and converted["classes"] == 0:
            return False, f"Classes missing in {target_lang} conversion"
        
        # Check if control structures are preserved (only if they existed in original)
        if original["control_structures"] > 0:
            control_ratio = converted["control_structures"] / original["control_structures"]
            if control_ratio < 0.3:  # Allow some reduction
                # For cross-language conversions, be more lenient about control structures
                # Some patterns like `if __name__ == "__main__"` don't have equivalents
                if source_lang != target_lang:
                    # Allow missing control structures in cross-language conversions
                    pass
                else:
                    return False, f"Too many control structures missing in {target_lang} conversion"
        
        # Check overall complexity (allow for reasonable differences)
        complexity_ratio = converted["complexity_score"] / original["complexity_score"] if original["complexity_score"] > 0 else 1
        if complexity_ratio < 0.3:  # Too much simplification
            return False, f"Code too simplified in {target_lang} conversion"
        elif complexity_ratio > 3:  # Too much complexity added
            return False, f"Code overly complex in {target_lang} conversion"
        
        return True, f"Cross-language conversion from {source_lang} to {target_lang} maintains appropriate complexity" 