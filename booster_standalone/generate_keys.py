import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import ai_database as database
import random
import string

def generate_key():
    return f"NOVA-{''.join(random.choices(string.ascii_uppercase + string.digits, k=4))}-{''.join(random.choices(string.ascii_uppercase + string.digits, k=4))}-{''.join(random.choices(string.ascii_uppercase + string.digits, k=4))}"

def main():
    new_keys = []
    for _ in range(3):
        key = generate_key()
        if database.db.add_ai_license(key, 'lifetime'):
            new_keys.append(key)
            
    print("Generated 3 new AI keys (Lifetime):")
    for k in new_keys:
        print(f"- {k}")

if __name__ == "__main__":
    main()
