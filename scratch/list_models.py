import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    print("ERROR: GEMINI_API_KEY missing!")
else:
    genai.configure(api_key=GEMINI_API_KEY)
    print("Fetching available models...")
    try:
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                print(f"Model Found: {m.name}")
    except Exception as e:
        print(f"Error fetching models: {e}")
