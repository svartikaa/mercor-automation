import pandas as pd
import json
import requests
import os
import time
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Step 1: Load the CSV file
df = pd.read_csv("applicants.csv")

# Step 2: Extract the Compressed JSON data
compressed_data = df['Compressed Data'].dropna().tolist()

# Step 3: Get Gemini API key
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY_1")
if not GEMINI_API_KEY:
    raise ValueError("ERROR: GEMINI_API_KEY not found in .env file")

# Function to evaluate with Gemini using direct REST API
def evaluate_with_gemini_direct(applicant_data, max_retries=3):
    """Evaluate using direct Gemini REST API"""
    # Try different API endpoints
    api_endpoints = [
        f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={GEMINI_API_KEY}",
        f"https://generativelanguage.googleapis.com/v1/models/gemini-pro:generateContent?key={GEMINI_API_KEY}",
        f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.0-pro:generateContent?key={GEMINI_API_KEY}"
    ]
    
    prompt = f"""You are a recruiting analyst. Given this applicant data, do four things:

1. Provide a concise 75-word summary.
2. Rate overall candidate quality from 1-10 (higher is better).
3. List any data gaps or inconsistencies you notice.
4. Suggest up to three follow-up questions to clarify gaps.

Return exactly:

Summary: <text>
Score: <integer>
Issues: <comma-separated list or 'None'>
Follow-Ups: <bullet list>

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
    
    headers = {"Content-Type": "application/json"}
    
    for attempt in range(max_retries):
        for url in api_endpoints:
            try:
                response = requests.post(url, headers=headers, json=payload, timeout=30)
                
                if response.status_code == 200:
                    result = response.json()
                    if 'candidates' in result and len(result['candidates']) > 0:
                        return result['candidates'][0]['content']['parts'][0]['text']
                    else:
                        continue  # Try next endpoint
                elif response.status_code == 404:
                    continue  # Try next endpoint
                else:
                    error_msg = f"API Error: {response.status_code}"
                    print(f"⚠️ {error_msg} for endpoint: {url}")
                    
            except Exception as e:
                print(f"⚠️ Request failed for {url}: {str(e)}")
                continue  # Try next endpoint
        
        # If all endpoints failed, wait and retry
        if attempt < max_retries - 1:
            wait_time = 10 * (attempt + 1)
            print(f"⏳ All endpoints failed. Waiting {wait_time} seconds before retry...")
            time.sleep(wait_time)
    
    return "Gemini API Error: All endpoints and retries failed"

def parse_llm_response(response_text):
    """Parse the LLM response into structured data"""
    # If it's an error message, return it as the summary
    if "API Error" in response_text:
        return {
            "summary": response_text,
            "score": 0,
            "issues": "API Error",
            "follow_ups": ["Check API configuration"]
        }
    
    lines = response_text.split('\n')
    result = {"summary": "", "score": 0, "issues": "None", "follow_ups": []}
    
    current_section = None
    for line in lines:
        line = line.strip()
        if line.startswith('Summary:'):
            current_section = 'summary'
            result['summary'] = line.replace('Summary:', '').strip()
        elif line.startswith('Score:'):
            current_section = 'score'
            try:
                result['score'] = int(line.replace('Score:', '').strip())
            except:
                result['score'] = 0
        elif line.startswith('Issues:'):
            current_section = 'issues'
            result['issues'] = line.replace('Issues:', '').strip()
        elif line.startswith('Follow-Ups:'):
            current_section = 'follow_ups'
        elif current_section == 'follow_ups' and line.startswith('•'):
            result['follow_ups'].append(line.replace('•', '').strip())
        elif current_section and line:
            if current_section == 'follow_ups':
                result['follow_ups'].append(line)
            else:
                result[current_section] += ' ' + line
    
    return result

# Step 4: Iterate over each applicant's data
print(f"Starting evaluation of {len(compressed_data)} applicants using direct Gemini API...")
for idx, item in enumerate(compressed_data):
    try:
        # Convert string to JSON (if already JSON, it will parse)
        applicant_data = json.loads(item)

        print(f"🔍 Evaluating applicant {idx+1} with Gemini Direct API...")
        
        # Use Gemini direct API
        evaluation = evaluate_with_gemini_direct(applicant_data)
        llm_results = parse_llm_response(evaluation)
        
        print(f"✅ Applicant {idx+1} evaluation result:")
        print(f"   Score: {llm_results['score']}/10")
        if llm_results['summary']:
            summary_preview = llm_results['summary'][:100] + "..." if len(llm_results['summary']) > 100 else llm_results['summary']
            print(f"   Summary: {summary_preview}")
        if llm_results['follow_ups']:
            print(f"   Follow-ups: {llm_results['follow_ups']}")
        print("-" * 50)

    except json.JSONDecodeError:
        print(f"⚠️ Skipping applicant {idx+1} - Invalid JSON format")
    except Exception as e:
        print(f"❌ Error processing applicant {idx+1}: {str(e)}")
    
    # Add delay between requests to avoid rate limiting
    if idx < len(compressed_data) - 1:
        time.sleep(3)  # 3-second delay between requests