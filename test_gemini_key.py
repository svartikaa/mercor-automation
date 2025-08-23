# test_gemini_key.py
import requests
import os
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
print(f"API Key: {GEMINI_API_KEY[:10]}...{GEMINI_API_KEY[-4:]}")

# Test different endpoints
endpoints = [
    "https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent",
    "https://generativelanguage.googleapis.com/v1/models/gemini-pro:generateContent"
]

for endpoint in endpoints:
    url = f"{endpoint}?key={GEMINI_API_KEY}"
    print(f"\nTesting: {endpoint}")
    
    payload = {
        "contents": [{
            "parts": [{"text": "Say hello"}]
        }]
    }
    
    try:
        response = requests.post(url, json=payload, timeout=10)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            print("✅ SUCCESS! API key is working")
            print(f"Response: {response.json()}")
            break
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"Request failed: {str(e)}")