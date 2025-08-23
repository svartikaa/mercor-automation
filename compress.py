from pyairtable import Api
import json
import sys

API_KEY = "patvI79oemT0pBAW6.d093a077487cd8011aec1bc638f34693b1f4b1bcd80bc0286215ae1f3a5fb8ae"           
BASE_ID = "appuDo3kplD9qwALY"             
TABLES = {
    "Applicants": "tblijenr8VSFb4ta1",
    "Personal Details": "tbldsJ1Cn9Fx89F34",
    "Work Experience": "tblSnAv3MZgEiFDu7",
    "Salary Preferences": "tbltap9k91tSfm0F9",
    "Shortlisted Leads": "tblGgkAQLVgHrWBqT",
}

# Name of the linked-record field in each child table that points to Applicants
# If your child tables use a different name (e.g. "Candidate" instead of "Applicant"),
# change this value.
LINK_FIELD_NAME = "Applicant"

# Field in Applicants where we store the JSON
OUTPUT_FIELD = "Compressed Data"

# Candidate field names to match an "Applicant ID" when the user passes a number
APPLICANT_ID_FIELDS = ["Applicant ID", "Applicant_ID", "ApplicantId", "ID", "Id"]
# -------------------------------------------------------


api = Api(API_KEY)

def _normalize(s):
    return str(s).strip().lower()

def find_applicant_record(applicant_input):
    """
    Find the applicant record either by record id (rec...) OR by Applicant ID fields.
    Returns the full record dict or None.
    """
    applicants = api.table(BASE_ID, TABLES["Applicants"])

    # If the input looks like a record id, fetch directly
    if str(applicant_input).startswith("rec"):
        try:
            return applicants.get(str(applicant_input))
        except Exception:
            return None

    # Otherwise, try to match by Applicant ID-like fields (case/spacing tolerant)
    records = applicants.all()
    target = _normalize(applicant_input)
    cand_keys_sets = []
    for r in records:
        fields = r.get("fields", {})
        # Try configured candidates exactly
        for key in APPLICANT_ID_FIELDS:
            if key in fields and _normalize(fields[key]) == target:
                return r
        # Fallback: auto-detect a field that looks like an applicant id field
        for k, v in fields.items():
            nk = k.lower().replace(" ", "").replace("_", "")
            if nk in ("applicantid", "id", "candidateid"):
                if _normalize(v) == target:
                    return r
    return None

def child_records_for(applicant_rec_id, child_table_id):
    """
    Get all records from a child table linked to the given Applicant record id.
    Works even if the link field allows multiple records.
    """
    tbl = api.table(BASE_ID, child_table_id)
    # Robust formula: search the rec id within the linked field converted to text
    formula = f"SEARCH('{applicant_rec_id}', ARRAYJOIN({{{LINK_FIELD_NAME}}}))"
    try:
        return tbl.all(formula=formula)
    except Exception:
        # If LINK_FIELD_NAME is wrong, you'll get 422. In that case, no results.
        return []

def compress_applicant(applicant_input):
    applicants_tbl = api.table(BASE_ID, TABLES["Applicants"])

    # 1) Find the Applicant record
    applicant_rec = find_applicant_record(applicant_input)
    if not applicant_rec:
        print(f"❌ Could not find applicant for input: {applicant_input}")
        return

    applicant_rec_id = applicant_rec["id"]
    applicant_fields = applicant_rec.get("fields", {})

    # 2) Pull child data
    details = child_records_for(applicant_rec_id, TABLES["Personal Details"])
    work = child_records_for(applicant_rec_id, TABLES["Work Experience"])
    salary = child_records_for(applicant_rec_id, TABLES["Salary Preferences"])
    shortlisted = child_records_for(applicant_rec_id, TABLES["Shortlisted Leads"])

    # 3) Combine into one JSON object
    compressed = {
        "Applicant": applicant_fields,
        "PersonalDetails": [r.get("fields", {}) for r in details],
        "WorkExperience": [r.get("fields", {}) for r in work],
        "SalaryPreferences": [r.get("fields", {}) for r in salary],
        "ShortlistedLeads": [r.get("fields", {}) for r in shortlisted],
    }

    # 4) Update Applicants -> Compressed Data
    try:
        applicants_tbl.update(applicant_rec_id, {OUTPUT_FIELD: json.dumps(compressed, indent=2)})
        print(f"✅ Stored compressed JSON in '{OUTPUT_FIELD}' for record {applicant_rec_id}")
    except Exception as e:
        print("❌ Failed to update Applicants table. Make sure:")
        print("   - Your token has data.records:write")
        print(f"   - The field '{OUTPUT_FIELD}' exists (Long text)")
        print("Error:", e)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python compress.py <Applicant ID or recXXXXXXXXXXXX>")
        print("Examples:")
        print("  python compress.py 2")
        print("  python compress.py rec1VdTVCGnbLOats")
        sys.exit(1)

    compress_applicant(sys.argv[1])
