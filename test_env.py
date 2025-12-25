"""Quick test to check if .env is loading correctly"""
import os
from dotenv import load_dotenv

load_dotenv()

secret_key = os.getenv('STRIPE_SECRET_KEY')

print("="*60)
print("ENVIRONMENT TEST")
print("="*60)

if secret_key:
    print(f"[SUCCESS] Key found!")
    print(f"   First 20 chars: {secret_key[:20]}")
    print(f"   Last 10 chars: {secret_key[-10:]}")
    print(f"   Total length: {len(secret_key)} characters")
    print(f"   Expected length: ~107 characters")

    if len(secret_key) < 100:
        print("\n[ERROR] KEY IS TOO SHORT! It's incomplete!")
    elif len(secret_key) > 110:
        print("\n[ERROR] KEY IS TOO LONG! Extra spaces or quotes?")
    else:
        print("\n[SUCCESS] Key length looks correct!")
else:
    print("[ERROR] No key found!")

print("="*60)













