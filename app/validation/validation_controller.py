from pathlib import Path
from app.validation.llm_validator import LLMValidator
from app.validation.semantic_validator import SemanticValidator
from app.validation.performance_analyzer import PerformanceAnalyzer

class ValidationController:
    def __init__(self):
        self.validators = [
            LLMValidator(),
            SemanticValidator(),
            PerformanceAnalyzer(),
        ]

    def run_all(self, original_file: Path, converted_file: Path) -> dict:
        results = []
        matrix = []
        for validator in self.validators:
            result = validator.validate(original_file, converted_file)
            results.append(result)
            matrix.append({
                "validator": result.get("name", "Unknown"),
                "passed": result.get("passed", False),
                "details": result.get("details", "")
            })
        overall_passed = all(r['passed'] for r in results)
        return {
            "overall_passed": overall_passed,
            "results": results,
            "matrix": matrix
        } 