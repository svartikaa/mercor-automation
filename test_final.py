# test_final.py
import requests
import os
import time
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
print(f"Testing restricted API key: {GEMINI_API_KEY[:10]}...")

# Use the standard Gemini endpoint
url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={GEMINI_API_KEY}"

payload = {
    "contents": [{
        "parts": [{"text": "Hello! Please respond with a short test message to confirm the API is working."}]
    }],
    "generationConfig": {
        "maxOutputTokens": 100,
        "temperature": 0.7
    }
}

try:
    response = requests.post(url, json=payload, timeout=15)
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print("✅ SUCCESS! Your restricted API key is working!")
        print(f"Response: {result['candidates'][0]['content']['parts'][0]['text']}")
    elif response.status_code == 403:
        print("❌ Permission denied. Please check:")
        print("   - API key is properly restricted to Generative Language API")
        print("   - Wait 2-3 minutes after enabling the API")
        print(f"   Error details: {response.text}")
    else:
        print(f"❌ Other error: {response.text}")
        
except Exception as e:
    print(f"❌ Request failed: {str(e)}")