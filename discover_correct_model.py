# discover_correct_model.py
import requests
import os
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    print("❌ ERROR: GEMINI_API_KEY not found in .env file")
    exit()

print(f"Testing API key: {GEMINI_API_KEY[:10]}...")

# Try to list available models
list_url = f"https://generativelanguage.googleapis.com/v1beta/models?key={GEMINI_API_KEY}"

print("🔍 Discovering available models...")
try:
    response = requests.get(list_url, timeout=15)
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print("✅ Available models:")
        for model in data.get('models', []):
            model_name = model['name']
            if 'generateContent' in model.get('supportedGenerationMethods', []):
                print(f"   ✅ {model_name} - Supports generateContent")
            else:
                print(f"   ❌ {model_name} - No generateContent support")
    else:
        print(f"Error: {response.text}")
        
except Exception as e:
    print(f"Request failed: {str(e)}")