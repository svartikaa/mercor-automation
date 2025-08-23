import pandas as pd

# Read your automation results
print("Reading applicants_shortlisted.csv...")
df = pd.read_csv('applicants_shortlisted.csv')

# Create clean export with only needed columns
export_df = df[['Applicant ID', 'Shortlist Status', 'LLM Score', 'Score Reason']]
print("Creating export data...")

# Save to new CSV file
export_df.to_csv('airtable_import_ready.csv', index=False)
print("✅ Success! Created 'airtable_import_ready.csv'")
print(f"Exported {len(export_df)} records")