from pyairtable import Api

API_KEY = "patvI79oemT0pBAW6.d093a077487cd8011aec1bc638f34693b1f4b1bcd80bc0286215ae1f3a5fb8ae"
BASE_ID = "appuDo3kplD9qwALY"
TABLE_ID = "tblijenr8VSFb4ta1"   # Applicants table ID

api = Api(API_KEY)
table = api.table(BASE_ID, TABLE_ID)

print("Listing all Applicants (with available fields):\n")
records = table.all()

for rec in records:
    rec_id = rec["id"]  # Airtable record ID (recXXXXXX)
    fields = rec["fields"]
    print(f"Record ID: {rec_id}")
    print("Available fields:", list(fields.keys()))  # show real field names
    print("Raw data:", fields)
    print("-" * 50)

