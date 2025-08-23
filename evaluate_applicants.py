# evaluate_applicants.py
import pandas as pd
import requests
import os
import json
from dotenv import load_dotenv

# Step 1: Load environment variables from .env file
load_dotenv()

# Step 2: Get API key from environment variable
API_KEY = os.getenv("OPENAI_API_KEY")
if not API_KEY:
    raise ValueError("ERROR: API key not found. Please check your .env file")

print("✓ API key loaded successfully!")

# Step 3: Load your CSV data
try:
    df = pd.read_csv("applicants.csv")
    print(f"✓ Loaded {len(df)} applicants from applicants.csv")
except FileNotFoundError:
    print("ERROR: applicants.csv file not found")
    print("Please make sure applicants.csv is in the same folder as this script")
    exit()

# Step 4: Check if we have the required column
if 'Compressed Data' not in df.columns:
    print("ERROR: 'Compressed Data' column not found in applicants.csv")
    print("Available columns:", list(df.columns))
    exit()

# Step 5: Prepare to process applicants
compressed_data = df['Compressed Data'].dropna().tolist()
print(f"✓ Found {len(compressed_data)} applicants with compressed data")

# Prepare results
results = []

# Function to call OpenAI API
def evaluate_with_llm(applicant_data):
    API_URL = "https://api.openai.com/v1/chat/completions"
    
    payload = {
        "model": "gpt-4o",
        "messages": [
            {
                "role": "system", 
                "content": """You are an experienced hiring manager. Evaluate applicants and provide:
                1. A score from 1-10
                2. A brief summary
                3. Recommended follow-up questions
                
                Format your response as:
                Score: [number]/10
                Summary: [text]
                Follow-ups: [text]"""
            },
            {
                "role": "user", 
                "content": f"Evaluate this applicant data:\n{applicant_data}"
            }
        ],
        "max_tokens": 500,
        "temperature": 0.3
    }

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.post(API_URL, json=payload, headers=headers, timeout=30)
        response.raise_for_status()  # Raise exception for bad status codes
        return response.json()['choices'][0]['message']['content']
    except requests.exceptions.RequestException as e:
        return f"API Error: {str(e)}"

# Step 6: Process each applicant
print("Starting LLM evaluation...")
for index, row in df.iterrows():
    compressed_data = row.get('Compressed Data', '')
    record_id = row.get('Record ID', f"row_{index+1}")
    name = row.get('Name', 'Unknown')
    
    if pd.isna(compressed_data) or compressed_data == '':
        evaluation = "No data provided for evaluation"
        print(f"⚠️  Skipping applicant {index+1} ({name}): No data")
    else:
        print(f"🔍 Evaluating applicant {index+1}: {name}")
        evaluation = evaluate_with_llm(compressed_data)
        print(f"   ✓ Evaluation complete")
    
    results.append({
        'Record ID': record_id,
        'Name': name,
        'LLM Evaluation': evaluation
    })

# Step 7: Save results to a new CSV file
results_df = pd.DataFrame(results)
output_filename = "llm_evaluations.csv"
results_df.to_csv(output_filename, index=False)

print("==========================================")
print("✅ Evaluation complete!")
print(f"📊 Results saved to: {output_filename}")
print("==========================================")

# Step 8: Show preview of results
print("\nPreview of results:")
print(results_df.head().to_string(index=False))