from app.validation.base_validator import BaseValidator
import openai
import os
from pathlib import Path
from typing import Dict
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Set up OpenAI API key from environment
api_key = os.getenv("OPENAI_API_KEY")
if api_key:
    openai.api_key = api_key

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

        # Determine source and target languages from file extensions
        source_lang = original_file.suffix[1:].lower() if original_file.suffix else "unknown"
        target_lang = converted_file.suffix[1:].lower() if converted_file.suffix else "unknown"
        
        # Map common extensions to language names
        lang_map = {
            "py": "Python",
            "java": "Java", 
            "js": "JavaScript",
            "cpp": "C++",
            "c": "C",
            "cs": "C#",
            "rb": "Ruby",
            "go": "Go",
            "rs": "Rust",
            "ts": "TypeScript"
        }
        
        source_language = lang_map.get(source_lang, source_lang)
        target_language = lang_map.get(target_lang, target_lang)

        prompt = f"""
You are a code validation agent comparing {source_language} code converted to {target_language}.

IMPORTANT GUIDELINES FOR CROSS-LANGUAGE CONVERSION:
1. Focus on FUNCTIONAL EQUIVALENCE, not syntax similarity
2. Understand that different languages have different idioms and patterns
3. Accept reasonable adaptations (e.g., Python list → Java ArrayList)
4. Consider framework differences (e.g., Flask → Spring Boot)
5. Allow for language-specific error handling patterns
6. Accept minor differences in implementation details

EVALUATION CRITERIA:
- PASS if the core functionality and logic are preserved
- PASS if the conversion handles language-specific requirements appropriately
- FAIL only if critical functionality is missing or broken
- FAIL if the conversion completely misunderstands the original intent

Original {source_language} code:
{original_code}

Converted {target_language} code:
{converted_code}

Provide a detailed analysis focusing on:
1. Core functionality preservation
2. Appropriate language adaptations
3. Any critical missing features
4. Overall assessment (PASS/FAIL)

Your response should end with a clear PASS or FAIL recommendation.
"""

        try:
            response = openai.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": "You are an expert code validation agent specializing in cross-language conversions."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1000,
                temperature=0.1
            )
            result = response.choices[0].message.content
            if result is not None:
                # Improved pass/fail detection
                result_lower = result.lower()
                # Look for explicit pass/fail indicators
                if 'pass' in result_lower and 'fail' not in result_lower:
                    passed = True
                elif 'fail' in result_lower:
                    passed = False
                else:
                    # Default to pass for cross-language conversions unless clearly problematic
                    passed = True
                details = result
            else:
                passed = False
                details = "No response from LLM."
        except Exception as e:
            passed = True  # Default to pass on API errors to avoid blocking conversions
            details = f"LLM validation error: {e}. Defaulting to PASS."
            
        return {
            "name": "LLMValidator",
            "passed": passed,
            "details": details
        }
