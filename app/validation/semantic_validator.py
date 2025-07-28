from app.validation.base_validator import BaseValidator
from pathlib import Path
from typing import Dict
import ast

class SemanticValidator(BaseValidator):
    def validate(self, original_file: Path, converted_file: Path) -> Dict:
        """
        Compare the ASTs of the original and converted Python code for structural similarity.
        Returns a dict with validation result and feedback.
        """
        if not (str(original_file).endswith('.py') and str(converted_file).endswith('.py')):
            return {
                "name": "SemanticValidator",
                "passed": False,
                "details": "SemanticValidator currently only supports Python files."
            }
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