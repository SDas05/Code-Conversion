import openai
import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
openai.api_key = api_key

try:
    models = openai.models.list()
    print("Available models:")
    for model in models.data:
        print(model.id)
except Exception as e:
    print("Error:", e)
