import requests
import json
import pandas as pd
import calendar
import datetime



url = "https://api.openaq.org/v2/measurements"
params = {
    "city": "Mexico",
    "country": "MX",
    "limit": 1000,
    "page": 1,
    "parameter": ["pm25", "pm10", "no2", "so2", "o3", "co"],
    "date_from": "2023-01-01T00:00:00Z",
    "date_to": "2024-12-31T23:59:59Z"
}

all_results = []
page = 1

while True:
    params["page"] = page
    response = requests.get(url, params=params)

    # Check the response status and content
    if response.status_code != 200:
        print(f"Error: Received status code {response.status_code}")
        print("Response content:", response.text)
        break

    data = response.json()
    results = data.get("results", [])

    # If no results are returned, exit the loop
    if not results:
        print("No more data found.")
        break

    all_results.extend(results)
    print(f"Fetched page {page} with {len(results)} records")
    page += 1

# Convert to DataFrame and save
df = pd.DataFrame(all_results)
print(f"Total records fetched: {len(df)}")

if not df.empty:
    df.to_csv("mexico_city_air_quality.csv", index=False)
    print("Data saved to mexico_city_air_quality.csv")
else:
    print("No data to save.")
