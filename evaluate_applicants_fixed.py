# evaluate_applicants_fixed.py
import pandas as pd
import requests
import os
import time
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get API key from environment variable
API_KEY = os.getenv("OPENAI_API_KEY")
if not API_KEY:
    raise ValueError("ERROR: API key not found. Please check your .env file")

print("✓ API key loaded successfully!")

# Load your CSV data
try:
    df = pd.read_csv("applicants.csv")
    print(f"✓ Loaded {len(df)} applicants from applicants.csv")
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
print(f"✓ Found {len(compressed_data)} applicants with compressed data")

# Prepare results
results = []

# Function to call OpenAI API with error handling
def evaluate_with_llm(applicant_data, retries=3):
    API_URL = "https://api.openai.com/v1/chat/completions"
    
    payload = {
        "model": "gpt-3.5-turbo",  # Using cheaper/faster model to avoid limits
        "messages": [
            {
                "role": "system", 
                "content": """You are a hiring manager. Evaluate applicants and provide:
                1. A score from 1-10
                2. A brief summary
                3. 2-3 follow-up questions
                
                Format as:
                Score: [number]/10
                Summary: [text]
                Follow-ups: [text]"""
            },
            {
                "role": "user", 
                "content": f"Evaluate this applicant data:\n{applicant_data}"
            }
        ],
        "max_tokens": 300,
        "temperature": 0.3
    }

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    
    for attempt in range(retries):
        try:
            response = requests.post(API_URL, json=payload, headers=headers, timeout=60)
            
            if response.status_code == 429:
                # Rate limited - wait and retry
                wait_time = 20 * (attempt + 1)  # Wait 20, 40, then 60 seconds
                print(f"⏳ Rate limited. Waiting {wait_time} seconds...")
                time.sleep(wait_time)
                continue
                
            response.raise_for_status()
            return response.json()['choices'][0]['message']['content']
            
        except requests.exceptions.RequestException as e:
            if attempt == retries - 1:  # Last attempt
                return f"API Error: {str(e)}"
            wait_time = 10 * (attempt + 1)
            print(f"⚠️ Error (attempt {attempt + 1}): {str(e)}. Waiting {wait_time} seconds...")
            time.sleep(wait_time)
    
    return "API Error: All attempts failed"

# Process each applicant with delays
print("Starting LLM evaluation (with rate limiting)...")
for index, row in df.iterrows():
    compressed_data = row.get('Compressed Data', '')
    record_id = row.get('Record ID', f"row_{index+1}")
    name = row.get('Name', 'Unknown')
    
    if pd.isna(compressed_data) or compressed_data == '':
        evaluation = "No data provided for evaluation"
        print(f"⚠️ Skipping applicant {index+1} ({name}): No data")
    else:
        print(f"🔍 Evaluating applicant {index+1}: {name}")
        evaluation = evaluate_with_llm(compressed_data)
        print(f"   ✓ Evaluation complete: {evaluation[:50]}...")
    
    results.append({
        'Record ID': record_id,
        'Name': name,
        'LLM Evaluation': evaluation
    })
    
    # Add delay between requests to avoid rate limiting (5 seconds)
    if index < len(df) - 1:  # Don't wait after the last one
        print("⏳ Waiting 5 seconds before next request...")
        time.sleep(5)

# Save results
results_df = pd.DataFrame(results)
output_filename = "llm_evaluations_fixed.csv"
results_df.to_csv(output_filename, index=False)

print("==========================================")
print("✅ Evaluation complete!")
print(f"📊 Results saved to: {output_filename}")
print("==========================================")

# Show preview
print("\nPreview of results:")
print(results_df.head().to_string(index=False))