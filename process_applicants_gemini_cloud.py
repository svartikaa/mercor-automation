# process_applicants_gemini_cloud.py
import pandas as pd
import json
import requests
import os
import time
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Load CSV file
try:
    df = pd.read_csv("applicants.csv")
    compressed_data = df['Compressed Data'].dropna().tolist()
    print(f"✅ Loaded {len(compressed_data)} applicants with data")
except FileNotFoundError:
    print("❌ ERROR: applicants.csv not found")
    exit()
except Exception as e:
    print(f"❌ Error loading CSV: {str(e)}")
    exit()

# Get Gemini API key
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise ValueError("ERROR: GEMINI_API_KEY not found in .env file")

def evaluate_with_gemini(applicant_data, max_retries=3):
    """Evaluate applicant using Gemini Cloud API"""
    # Use gemini-1.5-flash (fast and reliable)
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
    
    prompt = f"""You are a recruiting analyst. Analyze this applicant data:

{json.dumps(applicant_data, indent=2)}

Provide:
1. Brief summary (75 words max)
2. Quality score (1-10)
3. Data gaps/issues
4. 2-3 follow-up questions

Format exactly:
Summary: [text]
Score: [number]
Issues: [text]
Follow-Ups: [text]"""
    
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
        try:
            response = requests.post(url, headers=headers, json=payload, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                if 'candidates' in result and result['candidates']:
                    return result['candidates'][0]['content']['parts'][0]['text']
            else:
                print(f"   ❌ API error: {response.status_code}")
                continue
                
        except Exception as e:
            print(f"   ❌ Request error: {str(e)}")
            if attempt < max_retries - 1:
                time.sleep(2 * (attempt + 1))
    
    return "API Error: Could not get evaluation"

def parse_llm_response(response_text):
    """Parse the LLM response into structured data"""
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
        elif current_section == 'follow_ups' and line:
            result['follow_ups'].append(line.strip())
        elif current_section and line:
            result[current_section] += ' ' + line
    
    return result

# Process applicants
print(f"Starting evaluation of {len(compressed_data)} applicants with Gemini Cloud API...")
for idx, item in enumerate(compressed_data):
    try:
        applicant_data = json.loads(item)
        print(f"🔍 Evaluating applicant {idx+1}...")
        
        evaluation = evaluate_with_gemini(applicant_data)
        llm_results = parse_llm_response(evaluation)
        
        print(f"✅ Applicant {idx+1} evaluation:")
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
        print(f"❌ Error with applicant {idx+1}: {str(e)}")
    
    # Add delay between requests
    if idx < len(compressed_data) - 1:
        time.sleep(2)