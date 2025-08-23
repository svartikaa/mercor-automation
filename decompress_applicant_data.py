import pandas as pd
import json

# Read the CSV
df = pd.read_csv("applicants.csv")

# Create a list to hold decompressed rows
decompressed_rows = []

for idx, row in df.iterrows():
    compressed = row.get("Compressed Data")
    if pd.notna(compressed):  # Only process non-empty
        try:
            data = json.loads(compressed)
            # Merge original row with decompressed data
            decompressed_rows.append({**row.to_dict(), **data})
        except json.JSONDecodeError:
            print(f"Skipping row {idx}: Invalid JSON")
    else:
        decompressed_rows.append(row.to_dict())

# Convert to DataFrame
decompressed_df = pd.DataFrame(decompressed_rows)

# Save decompressed version
decompressed_df.to_csv("applicants_decompressed.csv", index=False)

print("Decompression completed! Saved as applicants_decompressed.csv")
