import os
import time
import openai
from dotenv import load_dotenv

load_dotenv()

class ModelClient:
    def __init__(self, model_name="gpt-4o", temperature=0.3, max_retries=3, backoff_factor=2):
        self.model_name = model_name
        self.temperature = temperature
        self.max_retries = max_retries
        self.backoff_factor = backoff_factor
        self.api_key = os.getenv("OPENAI_API_KEY")

        if not self.api_key:
            raise ValueError("OPENAI_API_KEY not found in environment.")

        openai.api_key = self.api_key

    def get_completion(self, prompt: str) -> str:
        """
        Sends the prompt to the model and returns the response.
        Includes retry logic with exponential backoff.
        """
        for attempt in range(1, self.max_retries + 1):
            try:
                response = openai.chat.completions.create(
                    model=self.model_name,
                    messages=[
                        {"role": "system", "content": "You are a helpful code conversion assistant."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=self.temperature,
                    max_tokens=2048
                )
                content = response.choices[0].message.content.strip()
                # Remove markdown code blocks if present
                if content.startswith('```') and content.endswith('```'):
                    lines = content.split('\n')
                    if len(lines) >= 3:
                        # Remove first and last lines (```language and ```)
                        content = '\n'.join(lines[1:-1])
                return content
            except openai.OpenAIError as e:
                print(f"Attempt {attempt} failed: {e}")
                if attempt == self.max_retries:
                    print("Max retries exceeded.")
                    return ""
                wait_time = self.backoff_factor ** attempt
                print(f"Retrying in {wait_time} seconds...")
                time.sleep(wait_time)
