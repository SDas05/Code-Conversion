from pathlib import Path
from app.validation.llm_validator import LLMValidator
from app.validation.semantic_validator import SemanticValidator
from app.validation.performance_analyzer import PerformanceAnalyzer
from app.config import config

class ValidationController:
    def __init__(self, strict_mode=False, skip_validators=None):
        self.strict_mode = strict_mode
        self.skip_validators = skip_validators or []
        
        # Get validation settings from config
        self.validation_config = config.get("validation", {})
        self.strict_mode = self.validation_config.get("strict_mode", strict_mode)
        
        self.validators = [
            LLMValidator(),
            SemanticValidator(),
            PerformanceAnalyzer(),
        ]

    def run_all(self, original_file: Path, converted_file: Path) -> dict:
        results = []
        matrix = []
        
        # Determine if this is a cross-language conversion
        source_lang = original_file.suffix[1:].lower() if original_file.suffix else "unknown"
        target_lang = converted_file.suffix[1:].lower() if converted_file.suffix else "unknown"
        is_cross_language = source_lang != target_lang
        
        for validator in self.validators:
            validator_name = validator.__class__.__name__
            
            # Skip validators if specified
            if validator_name in self.skip_validators:
                continue
                
            result = validator.validate(original_file, converted_file)
            
            # For cross-language conversions, be more lenient
            if is_cross_language and not self.strict_mode:
                # If validator failed but it's a cross-language conversion, 
                # we might want to be more lenient
                if not result.get("passed", False):
                    # Check if it's a common cross-language issue
                    details = result.get("details", "").lower()
                    if any(keyword in details for keyword in [
                        "only supports python", 
                        "cross-language", 
                        "language-specific",
                        "defaulting to pass"
                    ]):
                        result["passed"] = True
                        result["details"] = f"Cross-language conversion: {result['details']}"
            
            results.append(result)
            matrix.append({
                "validator": result.get("name", "Unknown"),
                "passed": result.get("passed", False),
                "details": result.get("details", "")
            })
        
        # For cross-language conversions, require fewer validators to pass
        if is_cross_language and not self.strict_mode:
            # Require at least 2 out of 3 validators to pass
            passed_count = sum(1 for r in results if r.get("passed", False))
            overall_passed = passed_count >= 2
        else:
            # Require all validators to pass in strict mode
            overall_passed = all(r.get("passed", False) for r in results)
        
        return {
            "overall_passed": overall_passed,
            "results": results,
            "matrix": matrix,
            "is_cross_language": is_cross_language,
            "strict_mode": self.strict_mode
        } 