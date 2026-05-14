import requests
import re
import json
import os

README_URL = "https://raw.githubusercontent.com/alistaitsacle/free-llm-api-keys/main/README.md"
SAVE_PATH = os.path.join(os.path.dirname(__file__), "free_keys.json")

def fetch_keys():
    print("Fetching fresh keys from FreeLLMShare...")
    try:
        response = requests.get(README_URL, timeout=15)
        if response.status_code != 200:
            print(f"Failed to fetch README: {response.status_code}")
            return []
        
        # Regex to find sk-... keys in the markdown tables
        # Matches sk- followed by alphanumeric characters, specifically looking for ones in code blocks `sk-xxx`
        keys = re.findall(r"`(sk-[A-Za-z0-9]+)`", response.text)
        
        # Remove duplicates
        unique_keys = list(set(keys))
        
        # Save to JSON
        with open(SAVE_PATH, "w") as f:
            json.dump(unique_keys, f)
            
        print(f"Successfully saved {len(unique_keys)} free keys to {SAVE_PATH}")
        return unique_keys
        
    except Exception as e:
        print(f"Error fetching keys: {e}")
        return []

if __name__ == "__main__":
    fetch_keys()
