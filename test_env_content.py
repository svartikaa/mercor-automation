# test_env_content.py
import os
from dotenv import load_dotenv

print("Testing .env file content...")

# Load environment variables
load_dotenv()

# Check if API key is loaded
api_key = os.getenv("GEMINI_API_KEY")

if api_key:
    print(f"✅ SUCCESS: API key found!")
    print(f"   Key: {api_key[:10]}...{api_key[-4:]}")
    print(f"   Length: {len(api_key)} characters")
else:
    print("❌ FAILED: GEMINI_API_KEY not found or empty")
    print("   Please check your .env file content")