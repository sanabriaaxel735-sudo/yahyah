import asyncio
import os
import sys

# Add the directory to path so we can import the intelligence engine
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'booster_standalone')))

from intelligence import IntelligenceEngine

async def test_fallback():
    print("--- Starting Fallback Test ---")
    
    # Create an engine with NO working Gemini keys to force fallback
    engine = IntelligenceEngine()
    engine.keys = [] # Clear keys to force fallback
    
    print(f"Loaded {len(engine.free_keys)} free keys.")
    if not engine.free_keys:
        print("[FAIL] No free keys found in free_keys.json. Run scraper first.")
        return

    # Test a simple prompt (will use proxy)
    print("Testing Fallback to Proxy...")
    response = await engine.get_response("Explain quantum entanglement in one sentence.", "test_user_999")
    
    if "error" in response.lower() or "Thinking" in response:
        print(f"[FAIL] Fallback Failed: {response}")
    else:
        print(f"[SUCCESS] Fallback Response: {response[:100]}...")

if __name__ == "__main__":
    asyncio.run(test_fallback())
