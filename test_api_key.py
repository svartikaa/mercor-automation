# test_api_key.py
import openai
import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("OPENAI_API_KEY")

if not API_KEY:
    print("❌ ERROR: No API key found in .env file")
    exit()

print(f"✅ API key found: {API_KEY[:10]}...{API_KEY[-4:]}")

# Test the API key
openai.api_key = API_KEY

try:
    response = openai.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": "Say 'Hello World'"}],
        max_tokens=5
    )
    print("✅ API key is working!")
    print(f"Response: {response.choices[0].message.content}")
    
except Exception as e:
    print(f"❌ API Error: {str(e)}")
    if "quota" in str(e).lower() or "billing" in str(e).lower():
        print("\n💡 This might be a billing issue. Check:")
        print("1. You have billing set up at https://platform.openai.com/account/billing/overview")
        print("2. You have positive credit balance")
    elif "invalid" in str(e).lower() or "auth" in str(e).lower():
        print("\n💡 This might be an invalid API key")
        print("1. Regenerate your API key at https://platform.openai.com/api-keys")
        print("2. Update your .env file with the new key")