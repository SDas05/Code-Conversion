from app.validation.base_validator import BaseValidator
import openai
from pathlib import Path
from typing import Dict

# You may need to set your OpenAI API key here or use environment variables
# openai.api_key = "YOUR_API_KEY"

class LLMValidator(BaseValidator):
    def validate(self, original_file: Path, converted_file: Path, model: str = "gpt-4") -> Dict:
        """
        Compare original and converted code using an LLM agent.
        Returns a dict with validation result and feedback.
        """
        with open(original_file, "r", encoding="utf-8") as f:
            original_code = f.read()
        with open(converted_file, "r", encoding="utf-8") as f:
            converted_code = f.read()

        prompt = f"""
                    You are a code validation agent. Compare the following original code and its converted version. 
                    Identify any issues, missing logic, or differences in functionality. 
                    Return a summary of your findings and a pass/fail recommendation.
                    Do not assume correctness based on language syntax alone.

                    Original code:
                    {original_code}

                    Converted code:
                    {converted_code}
                """

        response = openai.chat.completions.create(
            model=model,
            messages=[{"role": "system", "content": "You are a code validation agent."},
                      {"role": "user", "content": prompt}],
            max_tokens=512
        )
        result = response.choices[0].message.content
        if result is not None:
            # Determine pass/fail from LLM response (simple heuristic: look for 'pass' or 'fail')
            passed = 'pass' in result.lower() and 'fail' not in result.lower()
            details = result
        else:
            passed = False
            details = "No response from LLM."
        return {
            "name": "LLMValidator",
            "passed": passed,
            "details": details
        }
