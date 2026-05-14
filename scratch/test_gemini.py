import asyncio
import os
import sys

# Add the directory to path so we can import the intelligence engine
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'booster_standalone')))

from intelligence import engine

async def test_rotation():
    print("--- Starting Gemini Rotation Test ---")
    print(f"Loaded {len(engine.keys)} keys.")
    
    if not engine.keys:
        print("[FAIL] No keys loaded. Check your .env file.")
        return

    # Test a simple prompt
    print(f"Testing Key #1: {engine.keys[0][:10]}...")
    response = await engine.get_response("Hello, what is your name?", "test_user_123")
    
    if "error" in response.lower() or "Thinking" in response:
        print(f"[FAIL] Test Failed: {response}")
    else:
        print(f"[SUCCESS] Response: {response[:50]}...")

if __name__ == "__main__":
    asyncio.run(test_rotation())
