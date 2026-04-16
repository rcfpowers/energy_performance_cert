import requests
import pandas as pd
from urllib.parse import urlparse, parse_qs

BASE_URL = "https://data.ademe.fr/data-fair/api/v1/datasets/dpe03existant/lines"

all_rows = []

params = {
    "size": 1000,
    "qs": "date_etablissement_dpe:[2021-01-01 TO 2021-12-31] OR date_etablissement_dpe:[2024-01-01 TO 2024-12-31]",
    "select": "numero_dpe,date_etablissement_dpe",
    "sort": "_id"
}

while True:
    resp = requests.get(BASE_URL, params=params)
    if resp.status_code != 200:
        print(f"Error {resp.status_code}: {resp.text[:300]}")
        break

    data = resp.json()
    results = data.get("results", [])
    if not results:
        break

    all_rows.extend(results)
    print(f"Fetched {len(all_rows)} / {data['total']}")

    # Extract `after` cursor from the next URL
    next_url = data.get("next")
    if not next_url:
        break

    after_value = parse_qs(urlparse(next_url).query).get("after", [None])[0]
    if not after_value:
        break

    params["after"] = after_value

    if len(all_rows) % 100_000 == 0:

        pd.DataFrame(all_rows).to_csv("dpe_2021_2024_partial.csv", index=False)
        print(f"  → checkpoint saved")

df = pd.DataFrame(all_rows)

df = pd.DataFrame(all_rows)
df.to_csv("dpe_2021_2024.csv", index=False)
print(f"Saved {len(df)} rows to dpe_2021_2024.csv")

print(df.shape)
print(df.head())