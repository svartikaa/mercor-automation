# evaluate_applicants_mock_clean.py
import pandas as pd
import random
import time

print("🧪 Creating clean CSV without line breaks")

# Load your CSV data
try:
    df = pd.read_csv("applicants.csv")
    print(f"✅ Loaded {len(df)} applicants from applicants.csv")
except FileNotFoundError:
    print("ERROR: applicants.csv file not found")
    exit()

# Prepare results
results = []

# Mock evaluation function (SINGLE LINE format for easy copying)
def mock_evaluation(applicant_data):
    time.sleep(1)
    
    score = random.randint(5, 9)
    strengths = ["Strong technical background", "Relevant experience", "Good communication skills", 
                 "Impressive portfolio", "Cultural fit"][:random.randint(2, 3)]
    follow_ups = ["Ask about experience with specific technologies", "Discuss previous project challenges", 
                  "Explore teamwork approach", "Clarify career goals"][:random.randint(2, 3)]
    
    # SINGLE LINE format - no line breaks!
    return f"Score: {score}/10 | Summary: Candidate shows {' and '.join(strengths)}. | Follow-ups: {'; '.join(follow_ups)}"

# Process each applicant
print("Creating clean evaluations...")
for index, row in df.iterrows():
    compressed_data = row.get('Compressed Data', '')
    record_id = row.get('Record ID', f"row_{index+1}")
    name = row.get('Name', 'Unknown')
    
    if pd.isna(compressed_data) or compressed_data == '':
        evaluation = "No data provided for evaluation"
        print(f"⚠️ Skipping applicant {index+1} ({name}): No data")
    else:
        print(f"🔍 Evaluating applicant {index+1}: {name}")
        evaluation = mock_evaluation(compressed_data)
        print(f"   ✅ Clean evaluation created")
    
    results.append({
        'Record ID': record_id,
        'Name': name,
        'LLM Evaluation': evaluation
    })

# Save results
results_df = pd.DataFrame(results)
results_df.to_csv("llm_evaluations_clean.csv", index=False)

print("==========================================")
print("✅ Clean evaluation complete!")
print("📊 Results saved to: llm_evaluations_clean.csv")
print("==========================================")

# Show what the clean data looks like
print("\nClean CSV content preview:")
print("=" * 50)
with open("llm_evaluations_clean.csv", "r") as f:
    content = f.read()
    print(content)
print("=" * 50)