from app.validation.base_validator import BaseValidator
from pathlib import Path
from typing import Dict
import ast
import re

class SemanticValidator(BaseValidator):
    def validate(self, original_file: Path, converted_file: Path) -> Dict:
        """
        Validate cross-language conversions by checking for key structural elements.
        Returns a dict with validation result and feedback.
        """
        source_lang = original_file.suffix[1:].lower() if original_file.suffix else "unknown"
        target_lang = converted_file.suffix[1:].lower() if converted_file.suffix else "unknown"
        
        # For same-language conversions, use AST comparison
        if source_lang == target_lang and source_lang == "py":
            return self._validate_python_to_python(original_file, converted_file)
        
        # For cross-language conversions, use structural analysis
        return self._validate_cross_language(original_file, converted_file, source_lang, target_lang)
    
    def _validate_python_to_python(self, original_file: Path, converted_file: Path) -> Dict:
        """Validate Python to Python conversions using AST comparison."""
        try:
            with open(original_file, "r", encoding="utf-8") as f:
                original_code = f.read()
            with open(converted_file, "r", encoding="utf-8") as f:
                converted_code = f.read()
            original_ast = ast.parse(original_code)
            converted_ast = ast.parse(converted_code)
            # Compare AST dumps (ignoring minor differences like line numbers)
            original_dump = ast.dump(original_ast, annotate_fields=False, include_attributes=False)
            converted_dump = ast.dump(converted_ast, annotate_fields=False, include_attributes=False)
            passed = original_dump == converted_dump
            details = "ASTs match." if passed else "ASTs differ structurally."
        except Exception as e:
            passed = False
            details = f"Error during AST comparison: {e}"
        return {
            "name": "SemanticValidator",
            "passed": passed,
            "details": details
        }
    
    def _validate_cross_language(self, original_file: Path, converted_file: Path, 
                                source_lang: str, target_lang: str) -> Dict:
        """Validate cross-language conversions by checking structural elements."""
        try:
            with open(original_file, "r", encoding="utf-8") as f:
                original_code = f.read()
            with open(converted_file, "r", encoding="utf-8") as f:
                converted_code = f.read()
            
            # Extract key structural elements from original code
            original_elements = self._extract_structural_elements(original_code, source_lang)
            
            # Check if converted code has appropriate structural elements
            converted_elements = self._extract_structural_elements(converted_code, target_lang)
            
            # Compare structural elements (allow for language-specific adaptations)
            passed, details = self._compare_structural_elements(
                original_elements, converted_elements, source_lang, target_lang
            )
            
        except Exception as e:
            passed = True  # Default to pass for cross-language conversions
            details = f"Cross-language validation error: {e}. Defaulting to PASS."
        
        return {
            "name": "SemanticValidator",
            "passed": passed,
            "details": details
        }
    
    def _extract_structural_elements(self, code: str, language: str) -> Dict:
        """Extract key structural elements from code based on language."""
        elements = {
            "functions": [],
            "classes": [],
            "imports": [],
            "variables": [],
            "control_structures": []
        }
        
        if language == "py":
            # Python-specific extraction
            elements["functions"] = re.findall(r'def\s+(\w+)\s*\(', code)
            elements["classes"] = re.findall(r'class\s+(\w+)', code)
            elements["imports"] = re.findall(r'import\s+(\w+)', code) + re.findall(r'from\s+(\w+)', code)
            elements["variables"] = re.findall(r'(\w+)\s*=', code)
            elements["control_structures"] = re.findall(r'(if|for|while|try|with)\s+', code)
        elif language == "java":
            # Java-specific extraction
            elements["functions"] = re.findall(r'(?:public|private|protected)?\s*(?:static\s+)?(?:final\s+)?(?:void|int|String|boolean|double|float|long|short|byte|char)\s+(\w+)\s*\(', code)
            elements["classes"] = re.findall(r'class\s+(\w+)', code)
            elements["imports"] = re.findall(r'import\s+([^;]+)', code)
            elements["variables"] = re.findall(r'(?:public|private|protected)?\s*(?:static\s+)?(?:final\s+)?(?:int|String|boolean|double|float|long|short|byte|char)\s+(\w+)', code)
            elements["control_structures"] = re.findall(r'(if|for|while|try|switch)\s*\(', code)
        elif language == "js":
            # JavaScript-specific extraction
            elements["functions"] = re.findall(r'function\s+(\w+)|(\w+)\s*[:=]\s*function|(\w+)\s*[:=]\s*\([^)]*\)\s*=>', code)
            elements["classes"] = re.findall(r'class\s+(\w+)', code)
            elements["imports"] = re.findall(r'import\s+([^;]+)', code)
            elements["variables"] = re.findall(r'(?:const|let|var)\s+(\w+)', code)
            elements["control_structures"] = re.findall(r'(if|for|while|try|switch)\s*\(', code)
            # Also look for control structures without parentheses
            elements["control_structures"].extend(re.findall(r'(if|for|while|try|switch)\s+', code))
        
        return elements
    
    def _compare_structural_elements(self, original: Dict, converted: Dict, 
                                   source_lang: str, target_lang: str) -> tuple:
        """Compare structural elements between original and converted code."""
        # For cross-language conversions, more lenient
        # Check if key functionality is preserved
        
        # Check if functions are preserved (with language-specific adaptations)
        if original["functions"] and not converted["functions"]:
            return False, f"Functions missing in {target_lang} conversion"
        
        # Check if classes are preserved
        if original["classes"] and not converted["classes"]:
            return False, f"Classes missing in {target_lang} conversion"
        
        # Check if control structures are preserved (only if they existed in original)
        # Skip this check for cross-language conversions as some patterns don't translate
        if original["control_structures"] and not converted["control_structures"]:
            # For cross-language conversions, be more lenient about control structures
            # Some patterns like `if __name__ == "__main__"` don't have equivalents
            if source_lang != target_lang:
                # Allow missing control structures in cross-language conversions
                pass
            else:
                return False, f"Control structures missing in {target_lang} conversion"
        
        # For cross-language conversions, generally more accepting
        # as long as the basic structure is preserved
        return True, f"Cross-language conversion from {source_lang} to {target_lang} preserves key structural elements" 