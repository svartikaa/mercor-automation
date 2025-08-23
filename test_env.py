# test_env.py
import os
from dotenv import load_dotenv

load_dotenv()  # This will load from .env by default

API_KEY = os.getenv("OPENAI_API_KEY")
print(f"API Key loaded: {API_KEY is not None}")
if API_KEY:
    print("First few characters:", API_KEY[:10] + "...")