# evaluate_applicants_gemini_direct.py
import pandas as pd
import requests
import os
import time
import json
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get Gemini API key from environment variable
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise ValueError("ERROR: GEMINI_API_KEY not found. Please check your .env file")

print("✅ Gemini API key loaded successfully!")

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

# Function to call Gemini API directly via REST
def evaluate_with_gemini_direct(applicant_data, retries=3):
    # Use the most common Gemini API endpoint
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={GEMINI_API_KEY}"
    
    headers = {"Content-Type": "application/json"}
    
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
    
    payload = {
        "contents": [{
            "parts": [{"text": prompt}]
        }],
        "generationConfig": {
            "maxOutputTokens": 500,
            "temperature": 0.3
        }
    }
    
    for attempt in range(retries):
        try:
            response = requests.post(url, json=payload, headers=headers, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                # Extract the generated text from the response
                if 'candidates' in result and len(result['candidates']) > 0:
                    return result['candidates'][0]['content']['parts'][0]['text']
                else:
                    return "Error: No response generated from Gemini"
                    
            elif response.status_code == 404:
                # Try alternative endpoint format
                alt_url = f"https://generativelanguage.googleapis.com/v1/models/gemini-pro:generateContent?key={GEMINI_API_KEY}"
                response = requests.post(alt_url, json=payload, headers=headers, timeout=30)
                if response.status_code == 200:
                    result = response.json()
                    if 'candidates' in result and len(result['candidates']) > 0:
                        return result['candidates'][0]['content']['parts'][0]['text']
                
            error_msg = f"API Error: {response.status_code} - {response.text}"
            if attempt == retries - 1:
                return error_msg
            
            wait_time = 10 * (attempt + 1)
            print(f"⚠️ {error_msg}. Waiting {wait_time} seconds...")
            time.sleep(wait_time)
                
        except Exception as e:
            if attempt == retries - 1:
                return f"Request Error: {str(e)}"
            
            wait_time = 5 * (attempt + 1)
            print(f"⚠️ Error (attempt {attempt + 1}): {str(e)}. Waiting {wait_time} seconds...")
            time.sleep(wait_time)
    
    return "Gemini API Error: All attempts failed"

# Process each applicant with delays
print("Starting Gemini evaluation (direct API)...")
for index, row in df.iterrows():
    compressed_data = row.get('Compressed Data', '')
    record_id = row.get('Record ID', f"row_{index+1}")
    name = row.get('Name', 'Unknown')
    
    if pd.isna(compressed_data) or compressed_data == '':
        evaluation = "No data provided for evaluation"
        print(f"⚠️ Skipping applicant {index+1} ({name}): No data")
    else:
        print(f"🔍 Evaluating applicant {index+1}: {name}")
        evaluation = evaluate_with_gemini_direct(compressed_data)
        print(f"   ✅ Evaluation complete")
        if evaluation and len(evaluation) > 100:
            print(f"   Preview: {evaluation[:100]}...")
        else:
            print(f"   Result: {evaluation}")
    
    results.append({
        'Record ID': record_id,
        'Name': name,
        'LLM Evaluation': evaluation
    })
    
    # Add delay between requests
    if index < len(df) - 1:
        time.sleep(3)  # 3-second delay between requests

# Save results
results_df = pd.DataFrame(results)
output_filename = "llm_evaluations_gemini_direct.csv"
results_df.to_csv(output_filename, index=False)

print("==========================================")
print("✅ Gemini evaluation complete!")
print(f"📊 Results saved to: {output_filename}")
print("==========================================")

# Show preview
print("\nPreview of results:")
print(results_df.head().to_string(index=False))