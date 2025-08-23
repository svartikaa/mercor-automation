# create_test_data.py
import pandas as pd
import json

# Create applicant that MEETS all criteria
good_applicant = {
    "personal": {
        "full_name": "Emma Chen",
        "email": "emma.chen@email.com",
        "location": "Toronto, Canada",  # ✅ Approved location
        "linkedin": "https://linkedin.com/in/emmachen"
    },
    "experience": [
        {
            "company": "Microsoft",  # ✅ Tier-1 company
            "title": "Senior Developer",
            "start_date": "2019-06-01",  # ✅ 5+ years experience
            "end_date": "2024-08-01",
            "technologies": ["Python", "Azure", "SQL"]
        },
        {
            "company": "Amazon",
            "title": "Software Engineer", 
            "start_date": "2017-01-01",
            "end_date": "2019-05-31",
            "technologies": ["Java", "AWS", "Docker"]
        }
    ],
    "salary": {
        "preferred_rate": 95,  # ✅ ≤ $100
        "minimum_rate": 80,
        "currency": "USD",
        "availability": 35  # ✅ ≥ 20 hours
    }
}

# Create applicant that FAILS criteria (for comparison)
bad_applicant = {
    "personal": {
        "full_name": "Alex Kim", 
        "email": "alex.kim@email.com",
        "location": "Seoul, South Korea",  # ❌ Not approved
        "linkedin": "https://linkedin.com/in/alexkim"
    },
    "experience": [
        {
            "company": "Local Startup",
            "title": "Junior Developer",
            "start_date": "2023-03-01",  # ❌ Only 1.5 years
            "end_date": "2024-08-01",
            "technologies": ["JavaScript", "React"]
        }
    ],
    "salary": {
        "preferred_rate": 120,  # ❌ > $100
        "minimum_rate": 90,
        "currency": "USD", 
        "availability": 15  # ❌ < 20 hours
    }
}

# Create DataFrame
df = pd.DataFrame({
    'Applicant ID': ['app_001', 'app_002'],
    'Name': ['Emma Chen', 'Alex Kim'],
    'Email': ['emma.chen@email.com', 'alex.kim@email.com'],
    'LLM Score': [88, 62],  # ✅ Meets & ❌ Fails LLM threshold
    'Compressed Data': [json.dumps(good_applicant), json.dumps(bad_applicant)],
    'Shortlist Status': ['', ''],
    'LLM Summary': ['Strong technical background with 5+ years at top tech companies', 'Junior developer with limited experience'],
    'LLM Follow-Ups': ['Ask about cloud architecture experience', 'Discuss career growth goals']
})

# Save to CSV
df.to_csv("applicants.csv", index=False)
print("✅ Created test data with:")
print("   - 1 applicant that MEETS all criteria (should be shortlisted)")
print("   - 1 applicant that FAILS criteria (should not be shortlisted)")