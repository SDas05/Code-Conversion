from pathlib import Path
from typing import Dict

class BaseValidator:
    def validate(self, original_file: Path, converted_file: Path) -> Dict:
        """
        Validate the converted code against the original code.
        Returns a dict with at least: { 'name': str, 'passed': bool, 'details': str }
        """
        raise NotImplementedError("Subclasses must implement the validate method.") 