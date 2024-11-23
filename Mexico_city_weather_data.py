import requests
import pandas as pd 




# API endpoint and parameters
URL = "https://archive-api.open-meteo.com/v1/era5"
params = {
    "latitude": 19.437609,
    "longitude": -99.10715,
    "generationtime_ms": 0.0020265579223632812,
    "utc_offset_seconds": -21600,
    "timezone": "America/Mexico_City",
    "timezone_abbreviation": "CST",
    "elevation": 2230,
    "tempreature_2m_max": "true",
    "tempreature_2m_min": "true",
    "precipitation_sum": "true",
    "windspeed_10m_max": "true",
    "humidity_2m_max": "true",
    "humidity_2m_min": "true",
    "start_date": "2019-01-01",
    "end_date": "2024-01-01"
}

# Send the request
response = requests.get(URL, params=params)

# Check if request is succssful
if response.status_code == 200:
    data = response.json()
    print(data)
    # Convert data to DataFrame
    df = pd.DataFrame({
            'date': data["hourly"]['time'],
            'temperature_max': data["hourly"]['temperature_2m_max'],
            'temperature_min': data["hourly"]['temperature_2m_min'],
            'precipitation': data["hourly"]['precipitation_sum'],
            'wind_speed_max': data["hourly"]['windspeed_10m_max'],
            'humidity_max': data["hourly"]['humidity_2m_max'],
            'humidity_min': data["hourly"]['humidity_2m_min']
        })
    # Save to CSV
    df.to_csv('mexico_city_weather_data.csv', index=False)
    print("Data saved successfuly")

else:
    print("Failed to fetch data", response.text)




