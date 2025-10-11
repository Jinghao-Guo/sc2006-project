import requests
from Database import database
import pandas as pd
from tqdm import tqdm
from io import StringIO


dataset_id = "d_2d5ff9ea31397b66239f245f57751537"
response = requests.get(f"https://api-open.data.gov.sg/v1/public/api/datasets/{dataset_id}/poll-download")
# download file from response.url
url = response.json().get('data', {}).get('url', '')
if not url:
    raise ValueError("Failed to get download URL from the API response.")
response = requests.get(url)
csv_data = StringIO(response.text)
df = pd.read_csv(csv_data)

database.clear_data()
for _, record in tqdm(df.iterrows()):
    database.insert_flat(
        town=record.get('town', ''),
        flat_type=record.get('flat_type', ''),
        block=record.get('block', ''),
        street_name=record.get('street_name', ''),
        storey_range=record.get('storey_range', ''),
        floor_area_sqm=float(record.get('floor_area_sqm', 0)),
        flat_model=record.get('flat_model', ''),
        lease_commence_date=int(record.get('lease_commence_date', 0)),
        resale_price=float(record.get('resale_price', 0)),
    )

print(f"Inserted {df.shape[0]} records into the database.")