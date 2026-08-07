from dotenv import load_dotenv
import os

from google import genai

loaded = load_dotenv()
print("Loaded .env:", loaded)

api_key = os.getenv("GEMINI_API_KEY")
print("API key found:", api_key is not None)

if not api_key:
    raise ValueError("GEMINI_API_KEY was not found.")


print("Available models:")
for model in genai.list_models():
    if "generateContent" in model.supported_generation_methods:
        print(model.name)
