import os
import json
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

class IntelligenceEngine:
    def __init__(self):
        # Load free proxy keys (Scraped from FreeLLMShare)
        self.free_keys = []
        self.free_key_index = 0
        self.load_free_keys()

    def load_free_keys(self):
        try:
            path = os.path.join(os.path.dirname(__file__), "free_keys.json")
            if os.path.exists(path):
                with open(path, "r") as f:
                    self.free_keys = json.load(f)
                    print(f"Intelligence: Loaded {len(self.free_keys)} free keys.")
        except Exception as e:
            print(f"Intelligence Error loading keys: {e}")

    def rotate_free_key(self):
        if len(self.free_keys) > 1:
            self.free_key_index = (self.free_key_index + 1) % len(self.free_keys)
            return True
        return False

    async def get_response(self, prompt, user_id):
        if not self.free_keys:
            return "Thinking error: No free keys found. Please run the scraper."

        # Try every single key in the pool if needed
        for attempt in range(len(self.free_keys)):
            current_free_key = self.free_keys[self.free_key_index]
            try:
                client = OpenAI(
                    base_url="https://aiapiv2.pekpik.com/v1",
                    api_key=current_free_key
                )
                # Use smart-chat which is the most compatible on this proxy
                response = client.chat.completions.create(
                    model="smart-chat",
                    messages=[
                        {"role": "system", "content": "You are Nova GPT, an elite AI assistant for developers. Respond with deep technical insight."},
                        {"role": "user", "content": f"User {user_id}: {prompt}"}
                    ],
                    timeout=8 # Fast skip for dead keys
                )
                return response.choices[0].message.content
            except Exception as e:
                # Rotate and try next
                if not self.rotate_free_key(): break

        return "Thinking error: All free keys are currently exhausted. The bot will automatically refresh them soon."

engine = IntelligenceEngine()
