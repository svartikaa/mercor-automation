# shortlist.py
import pandas as pd
import json

# Tier-1 companies list
TIER_1_COMPANIES = ["Google", "Meta", "OpenAI", "Microsoft", "Amazon", "Apple", "Netflix", "Twitter", "Uber", "Airbnb"]

# Approved countries list
APPROVED_COUNTRIES = ["US", "USA", "United States", "Canada", "UK", "United Kingdom", "Germany", "India"]

def calculate_experience_years(experience_data):
    """Calculate total years of experience from compressed JSON"""
    total_years = 0
    if isinstance(experience_data, list):
        for exp in experience_data:
            if isinstance(exp, dict) and exp.get('start_date') and exp.get('end_date'):
                try:
                    # Simple year calculation from dates
                    start_year = int(exp['start_date'].split('-')[0])
                    end_year = int(exp['end_date'].split('-')[0]) if exp['end_date'] != 'Present' else 2025
                    total_years += (end_year - start_year)
                except:
                    continue
    return total_years

def has_tier_1_experience(experience_data):
    """Check if applicant worked at Tier-1 company"""
    if isinstance(experience_data, list):
        for exp in experience_data:
            if isinstance(exp, dict):
                company = exp.get('company', '').lower()
                for tier1_company in TIER_1_COMPANIES:
                    if tier1_company.lower() in company:
                        return True
    return False

def meets_salary_criteria(salary_data):
    """Check if salary criteria are met"""
    if isinstance(salary_data, dict):
        preferred_rate = salary_data.get('preferred_rate', 0)
        currency = salary_data.get('currency', 'USD')
        availability = salary_data.get('availability', 0)
        
        # Convert to USD if needed
        conversion_rates = {'USD': 1, 'EUR': 1.1, 'GBP': 1.3, 'INR': 0.012}
        usd_rate = preferred_rate * conversion_rates.get(currency, 1)
        
        return usd_rate <= 100 and availability >= 20
    return False

def meets_location_criteria(personal_data):
    """Check if location criteria are met"""
    if isinstance(personal_data, dict):
        location = personal_data.get('location', '').lower()
        return any(country.lower() in location for country in APPROVED_COUNTRIES)
    return False

def evaluate_business_rules(compressed_json):
    """Evaluate applicant against business rules (experience, salary, location)"""
    try:
        if pd.isna(compressed_json) or compressed_json == '':
            return False, "No data"
            
        data = json.loads(compressed_json)
        
        personal_data = data.get('personal', {})
        experience_data = data.get('experience', [])
        salary_data = data.get('salary', {})
        
        # Calculate criteria
        experience_years = calculate_experience_years(experience_data)
        has_tier1 = has_tier_1_experience(experience_data)
        meets_salary = meets_salary_criteria(salary_data)
        meets_location = meets_location_criteria(personal_data)
        
        # Apply business rules
        experience_ok = experience_years >= 4 or has_tier1
        salary_ok = meets_salary
        location_ok = meets_location
        
        meets_all_criteria = experience_ok and salary_ok and location_ok
        
        # Build reason message
        reason_parts = []
        if experience_ok:
            if has_tier1:
                reason_parts.append("Tier-1 company")
            else:
                reason_parts.append(f"{experience_years} years XP")
        if salary_ok:
            reason_parts.append("Good rate/availability")
        if location_ok:
            reason_parts.append("Approved location")
        
        return meets_all_criteria, " + ".join(reason_parts)
        
    except json.JSONDecodeError:
        return False, "Invalid JSON"
    except Exception as e:
        return False, f"Error: {str(e)}"

def main():
    """Main shortlisting function with both LLM scores and business rules"""
    try:
        # Load applicant data
        df = pd.read_csv("applicants.csv")
        print(f"✅ Loaded {len(df)} applicants")
        
        results = []
        
        for index, row in df.iterrows():
            applicant_id = row.get('Applicant ID', f"app_{index+1}")
            name = row.get('Name', 'Unknown')
            email = row.get('Email', '')
            llm_score = row.get('LLM Score', 0)
            compressed_data = row.get('Compressed Data', '')
            current_status = row.get('Shortlist Status', '')
            
            # Skip if already shortlisted
            if current_status == 'Shortlisted':
                results.append({
                    'Applicant ID': applicant_id,
                    'Name': name,
                    'Email': email,
                    'Shortlist Status': 'Already Shortlisted',
                    'Score Reason': 'Previously shortlisted',
                    'LLM Score': llm_score
                })
                continue
            
            # Evaluate based on LLM score
            llm_shortlist = False
            llm_reason = ""
            try:
                llm_score_num = float(llm_score) if pd.notna(llm_score) else 0
                llm_shortlist = llm_score_num >= 70
                llm_reason = f"LLM Score: {llm_score_num}" if llm_shortlist else ""
            except:
                llm_score_num = 0
            
            # Evaluate based on business rules
            business_shortlist, business_reason = evaluate_business_rules(compressed_data)
            
            # Determine final status
            if llm_shortlist or business_shortlist:
                status = "Shortlisted"
                if llm_shortlist and business_shortlist:
                    reason = f"LLM & Business Rules: {llm_reason}, {business_reason}"
                elif llm_shortlist:
                    reason = llm_reason
                else:
                    reason = f"Business Rules: {business_reason}"
            else:
                status = "Not Shortlisted"
                reason = "Does not meet criteria"
            
            results.append({
                'Applicant ID': applicant_id,
                'Name': name,
                'Email': email,
                'Shortlist Status': status,
                'Score Reason': reason,
                'LLM Score': llm_score_num
            })
            
            print(f"🔍 {name}: {status} - {reason}")
        
        # Save results
        results_df = pd.DataFrame(results)
        output_file = "applicants_shortlisted.csv"
        results_df.to_csv(output_file, index=False)
        
        print(f"\n✅ Shortlisting complete! Saved to {output_file}")
        
        # Show summary
        shortlisted = results_df[results_df['Shortlist Status'] == 'Shortlisted']
        print(f"\n📊 Summary: {len(shortlisted)}/{len(results_df)} applicants shortlisted")
        
        if len(shortlisted) > 0:
            print("\n🎯 Shortlisted Applicants:")
            for _, applicant in shortlisted.iterrows():
                print(f"   - {applicant['Name']}: {applicant['Score Reason']}")
                
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    main()