from pyairtable import Api

API_KEY = "patvI79oemT0pBAW6.d093a077487cd8011aec1bc638f34693b1f4b1bcd80bc0286215ae1f3a5fb8ae"

api = Api(API_KEY)

print("Listing all bases your token can access:\n")
for base in api.bases():
    print(f"Base ID: {base.id} | Name: {base.name}")

