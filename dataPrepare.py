import requests
import json
from Database import database
import pandas as pd
from tqdm import tqdm
          
# fetch data from local json file
with open('hdb_data.json', 'r') as file:
    records = json.load(file)

database.clear_data()
for record in tqdm(records):
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

print(f"Inserted {len(records)} records into the database.")