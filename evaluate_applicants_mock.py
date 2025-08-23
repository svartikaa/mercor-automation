# evaluate_applicants_mock.py
import pandas as pd
import random
import time

print("🧪 Running in MOCK MODE (no API calls)")
print("💡 This generates sample evaluations for testing")

# Load your CSV data
try:
    df = pd.read_csv("applicants.csv")
    print(f"✅ Loaded {len(df)} applicants from applicants.csv")
except FileNotFoundError:
    print("ERROR: applicants.csv file not found")
    exit()

# Prepare results
results = []

# Mock evaluation function
def mock_evaluation(applicant_data):
    time.sleep(1)  # Simulate API delay
    
    score = random.randint(5, 9)
    strengths = ["Strong technical background", "Relevant experience", "Good communication skills", 
                 "Impressive portfolio", "Cultural fit"][:random.randint(2, 3)]
    follow_ups = ["Ask about experience with specific technologies", "Discuss previous project challenges", 
                  "Explore teamwork approach", "Clarify career goals"][:random.randint(2, 3)]
    
    return f"""Score: {score}/10
Summary: Candidate shows {' and '.join(strengths)}. Shows potential for the role.
Follow-ups: {'; '.join(follow_ups)}"""

# Process each applicant
print("Starting mock evaluation...")
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
        print(f"   ✅ Mock evaluation complete")
    
    results.append({
        'Record ID': record_id,
        'Name': name,
        'LLM Evaluation': evaluation
    })

# Save results
results_df = pd.DataFrame(results)
output_filename = "llm_evaluations_mock.csv"
results_df.to_csv(output_filename, index=False)

print("==========================================")
print("✅ Mock evaluation complete!")
print(f"📊 Results saved to: {output_filename}")
print("==========================================")

print("\nPreview of results:")
print(results_df.head().to_string(index=False))