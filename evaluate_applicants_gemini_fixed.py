# evaluate_applicants_gemini_fixed.py
import pandas as pd
import google.generativeai as genai
import os
import time
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get Gemini API key from environment variable
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise ValueError("ERROR: GEMINI_API_KEY not found. Please check your .env file")

print("✅ Gemini API key loaded successfully!")

# Configure Gemini
genai.configure(api_key=GEMINI_API_KEY)

# Try different model names - Gemini frequently changes these
MODEL_NAMES = [
    "gemini-1.0-pro",      # Most common
    "gemini-pro",          # Older name
    "models/gemini-pro",   # Full path version
    "gemini-1.5-pro",      # Newer model
    "gemini-1.0-pro-001",  # Specific version
]

# Find a working model
working_model = None
for model_name in MODEL_NAMES:
    try:
        model = genai.GenerativeModel(model_name)
        # Test with a simple prompt
        response = model.generate_content("Hello")
        working_model = model_name
        print(f"✅ Using model: {working_model}")
        break
    except:
        print(f"❌ Model not available: {model_name}")
        continue

if not working_model:
    raise ValueError("❌ No working Gemini model found. Please check available models.")

# Load your CSV data
try:
    df = pd.read_csv("applicants.csv")
    print(f"✅ Loaded {len(df)} applicants from applicants.csv")
except FileNotFoundError:
    print("ERROR: applicants.csv file not found")
    exit()

# Check if we have the required column
if 'Compressed Data' not in df.columns:
    print("ERROR: 'Compressed Data' column not found")
    print("Available columns:", list(df.columns))
    exit()

# Prepare to process applicants
compressed_data = df['Compressed Data'].dropna().tolist()
print(f"✅ Found {len(compressed_data)} applicants with compressed data")

# Prepare results
results = []

# Function to call Gemini API
def evaluate_with_gemini(applicant_data, retries=3):
    model = genai.GenerativeModel(working_model)
    
    prompt = f"""You are an experienced hiring manager. Evaluate this applicant and provide:
    1. A score from 1-10
    2. A brief summary of qualifications
    3. 2-3 recommended follow-up questions
    
    Format your response as:
    Score: [number]/10
    Summary: [text]
    Follow-ups: [text]
    
    Applicant Data:
    {applicant_data}
    """
    
    for attempt in range(retries):
        try:
            response = model.generate_content(prompt)
            return response.text
            
        except Exception as e:
            if attempt == retries - 1:  # Last attempt
                return f"Gemini API Error: {str(e)}"
            
            wait_time = 5 * (attempt + 1)
            print(f"⚠️ Error (attempt {attempt + 1}): {str(e)}. Waiting {wait_time} seconds...")
            time.sleep(wait_time)
    
    return "Gemini API Error: All attempts failed"

# Process each applicant with delays
print("Starting Gemini evaluation...")
for index, row in df.iterrows():
    compressed_data = row.get('Compressed Data', '')
    record_id = row.get('Record ID', f"row_{index+1}")
    name = row.get('Name', 'Unknown')
    
    if pd.isna(compressed_data) or compressed_data == '':
        evaluation = "No data provided for evaluation"
        print(f"⚠️ Skipping applicant {index+1} ({name}): No data")
    else:
        print(f"🔍 Evaluating applicant {index+1}: {name}")
        evaluation = evaluate_with_gemini(compressed_data)
        print(f"   ✅ Evaluation complete")
        print(f"   Preview: {evaluation[:100]}...")
    
    results.append({
        'Record ID': record_id,
        'Name': name,
        'LLM Evaluation': evaluation
    })
    
    # Add delay between requests
    if index < len(df) - 1:
        time.sleep(2)  # 2-second delay between requests

# Save results
results_df = pd.DataFrame(results)
output_filename = "llm_evaluations_gemini.csv"
results_df.to_csv(output_filename, index=False)

print("==========================================")
print("✅ Gemini evaluation complete!")
print(f"📊 Results saved to: {output_filename}")
print("==========================================")

# Show preview
print("\nPreview of results:")
print(results_df.head().to_string(index=False))