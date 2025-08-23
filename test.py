import os
import google.genai as genai
from dotenv import load_dotenv

# Load the API key from the .env file
load_dotenv()

# The library automatically looks for the GOOGLE_API_KEY or GEMINI_API_KEY environment variable.
# You don't need to pass the key explicitly.
try:
    genai.configure()
    
    # Get a list of all available models
    all_models = genai.list_models()
    
    # Filter for models that support text generation (gemini-pro is a good example)
    text_models = [
        model for model in all_models 
        if 'generateContent' in model.supported_generation_methods
    ]

    print("Available Gemini Models for Text Generation:")
    for model in text_models:
        print(f"- {model.name}")

    # You can now test a model, for example, 'gemini-pro'
    if 'models/gemini-pro' in [m.name for m in text_models]:
        print("\nTesting 'gemini-pro' model...")
        model = genai.GenerativeModel('gemini-pro')
        response = model.generate_content("Give me a brief summary of how large language models work.")
        print("\nResponse from gemini-pro:")
        print(response.text)
    else:
        print("\n'gemini-pro' not found. Cannot perform a test.")

except genai.APIError as e:
    print(f"An API error occurred: {e}")
    print("Please ensure your API key is correct and you have access to the Gemini API.")