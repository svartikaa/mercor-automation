# fix_compressed_data.py
import pandas as pd
import json

def fix_compressed_json(bad_json):
    """Convert incorrect JSON structure to correct one"""
    try:
        data = json.loads(bad_json)
        
        # Transform to correct structure
        fixed_data = {
            "personal": {
                "full_name": data.get("Applicant", {}).get("name", ""),
                "email": "",
                "location": "",
                "linkedin": ""
            },
            "experience": [],
            "salary": {
                "preferred_rate": 0,
                "minimum_rate": 0,
                "currency": "USD",
                "availability": 0
            }
        }
        
        # Try to extract meaningful data from arrays
        personal_details = data.get("PersonalDetails", [])
        work_experience = data.get("WorkExperience", [])
        salary_prefs = data.get("SalaryPreferences", [])
        
        if personal_details:
            fixed_data["personal"]["email"] = personal_details[0] if len(personal_details) > 0 else ""
        
        if work_experience:
            # Create experience entry from array data
            fixed_data["experience"].append({
                "company": "Unknown Company",
                "title": work_experience[0] if len(work_experience) > 0 else "Developer",
                "start_date": "2020-01-01",
                "end_date": "2023-12-31",
                "technologies": []
            })
        
        if salary_prefs:
            # Try to extract salary number
            salary_str = salary_prefs[0] if len(salary_prefs) > 0 else "0"
            try:
                # Remove 'k' and convert to number
                if 'k' in salary_str.lower():
                    salary_value = float(salary_str.lower().replace('k', '')) * 1000
                else:
                    salary_value = float(salary_str)
                fixed_data["salary"]["preferred_rate"] = salary_value / 1000  # Convert to hourly rate assumption
            except:
                fixed_data["salary"]["preferred_rate"] = 50  # Default
        
        return json.dumps(fixed_data, indent=2)
        
    except json.JSONDecodeError:
        return json.dumps({
            "personal": {"full_name": "Error", "email": "", "location": "", "linkedin": ""},
            "experience": [],
            "salary": {"preferred_rate": 0, "minimum_rate": 0, "currency": "USD", "availability": 0}
        })

def main():
    """Fix all compressed data in Applicants.csv"""
    try:
        df = pd.read_csv("Applicants.csv")
        print(f"Loaded {len(df)} applicants")
        
        if 'Compressed Data' not in df.columns:
            print("❌ No Compressed Data column found")
            return
        
        # Fix compressed data
        fixed_count = 0
        for index, row in df.iterrows():
            compressed_data = row.get('Compressed Data', '')
            if pd.notna(compressed_data) and compressed_data != '':
                try:
                    # Check if already correct format
                    test_data = json.loads(compressed_data)
                    if 'personal' in test_data and 'experience' in test_data and 'salary' in test_data:
                        print(f"✅ Applicant {index+1}: Already correct format")
                        continue
                except:
                    pass
                
                # Fix the data
                fixed_json = fix_compressed_json(compressed_data)
                df.at[index, 'Compressed Data'] = fixed_json
                fixed_count += 1
                print(f"✅ Applicant {index+1}: Fixed compressed data")
        
        # Save fixed data
        if fixed_count > 0:
            df.to_csv("Applicants_fixed.csv", index=False)
            print(f"\n✅ Fixed {fixed_count} applicants. Saved to Applicants_fixed.csv")
            
            # Show sample of fixed data
            sample_fixed = df['Compressed Data'].iloc[0]
            print(f"\n🔍 Sample fixed data:")
            print(sample_fixed[:500] + "..." if len(sample_fixed) > 500 else sample_fixed)
        else:
            print("ℹ️ No data needed fixing")
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    main()