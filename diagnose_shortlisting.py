# diagnose_shortlisting.py
import pandas as pd
import json

def diagnose_applicant(row, index):
    """Diagnose why an applicant wasn't shortlisted"""
    print(f"\n{'='*50}")
    print(f"DIAGNOSING APPLICANT {index + 1}")
    print(f"{'='*50}")
    
    applicant_id = row.get('Applicant ID', f'app_{index+1}')
    name = row.get('Name', 'Unknown')
    email = row.get('Email', '')
    llm_score = row.get('LLM Score', 0)
    compressed_data = row.get('Compressed Data', '')
    
    print(f"Name: {name}")
    print(f"Email: {email}")
    print(f"LLM Score: {llm_score}")
    
    # Check LLM score
    try:
        llm_score_num = float(llm_score) if pd.notna(llm_score) else 0
        llm_ok = llm_score_num >= 70
        print(f"🔍 LLM Score: {llm_score_num} -> {'✅ Meets criteria (≥70)' if llm_ok else '❌ Below threshold'}")
    except:
        print(f"🔍 LLM Score: Invalid -> ❌ Cannot evaluate")
        llm_ok = False
    
    # Check compressed data
    print(f"\n📊 Compressed Data Analysis:")
    if pd.isna(compressed_data) or compressed_data == '':
        print("❌ No compressed data available")
        return
    
    try:
        data = json.loads(compressed_data)
        print("✅ JSON parsed successfully")
        
        # Analyze structure
        personal = data.get('personal', {})
        experience = data.get('experience', [])
        salary = data.get('salary', {})
        
        print(f"   Personal data keys: {list(personal.keys())}")
        print(f"   Experience entries: {len(experience)}")
        print(f"   Salary data keys: {list(salary.keys())}")
        
        # Check business rules
        print(f"\n🔍 Business Rules Check:")
        
        # Experience check
        exp_years = 0
        for exp in experience:
            if exp.get('start_date') and exp.get('end_date'):
                try:
                    start = int(exp['start_date'].split('-')[0])
                    end = int(exp['end_date'].split('-')[0]) if exp['end_date'] != 'Present' else 2025
                    exp_years += (end - start)
                except:
                    pass
        
        tier1 = any(any(tier1 in exp.get('company', '').lower() for tier1 in ['google', 'meta', 'microsoft', 'amazon', 'apple']) for exp in experience)
        exp_ok = exp_years >= 4 or tier1
        print(f"   Experience: {exp_years} years, Tier-1: {tier1} -> {'✅ OK' if exp_ok else '❌ Needs 4+ years or Tier-1'}")
        
        # Salary check
        pref_rate = salary.get('preferred_rate', 0)
        currency = salary.get('currency', 'USD')
        availability = salary.get('availability', 0)
        salary_ok = pref_rate <= 100 and availability >= 20
        print(f"   Salary: ${pref_rate}/{currency}, {availability}h/week -> {'✅ OK' if salary_ok else '❌ Needs ≤$100 & ≥20h'}")
        
        # Location check
        location = personal.get('location', '').lower()
        location_ok = any(country in location for country in ['us', 'usa', 'united states', 'canada', 'uk', 'united kingdom', 'germany', 'india'])
        print(f"   Location: {location} -> {'✅ OK' if location_ok else '❌ Not in approved countries'}")
        
        business_ok = exp_ok and salary_ok and location_ok
        print(f"   Overall Business Rules: {'✅ ALL MET' if business_ok else '❌ NOT MET'}")
        
    except json.JSONDecodeError:
        print("❌ Invalid JSON format")
        print(f"Raw data: {compressed_data[:200]}...")
    except Exception as e:
        print(f"❌ Error analyzing: {str(e)}")

def main():
    """Diagnose why applicants aren't being shortlisted"""
    try:
        df = pd.read_csv("applicants.csv")
        print(f"Analyzing {len(df)} applicants...")
        
        for index, row in df.iterrows():
            diagnose_applicant(row, index)
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    main()