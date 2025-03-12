import os
import folium
from pathlib import Path
from folium.plugins import HeatMap
import pandas as pd
import streamlit as st
from scripts.language_utils import get_text
from streamlit_plotly_mapbox_events import plotly_mapbox_events
import plotly.express as px
from scripts.data_handler import STATION_COORDINATES

# New ones
import json
from shapely.geometry import shape
from shapely.wkb import loads
from shapely.wkt import dumps
import branca

# Comment out when actual data is there
BASE_DIR = Path(__file__).resolve().parent.parent
dashboard_data_path = BASE_DIR / 'Dashboard_data' / 'limite-de-las-alcaldas.json'

with open(dashboard_data_path) as f:
	geo_json_data = json.load(f)

# Parse the GeoJSON to extract features
features = geo_json_data["features"]

# Extract the 'geometry' and 'name' into a list of dictionaries
data = [
    {"geometry": shape(feature["geometry"]), "NOMGEO": feature["properties"]["NOMGEO"]}
    for feature in features
]

# Convert the list of dictionaries to a DataFrame
df = pd.DataFrame(data)

# Let's get the current levels of the pollutants from all the stations
list_of_stations = {"PED": "Pedregal",
                   "BJU": "Benito Juarez",
                   "MER": "Merced",
                   "TLA": "Tlalnepantla"}

# Now let's extract the info from the xlsx files

# Path to the data
BASE_DIR_D = Path(__file__).resolve().parent.parent.parent

stations_data = pd.DataFrame()

# Load the data
for i in list(list_of_stations.keys()):
    df_pollutants = pd.read_excel(BASE_DIR_D / '2.Data_Collection' / f'{i}_merged_imputed.xlsx')
    if 'index' in df_pollutants.columns:
        df_pollutants = df_pollutants.drop('index', axis=1)
    df_pollutants['station'] = list_of_stations[i]
    df_pollutants.columns = ['datetime', 'direct_radiation (W/m²)',	'PM25', 'PM10',	'SO2', 'O3', 'NO2',	'CO', 'RH',	'TMP',	'WDR',	'WSP',	'is_festival',	'is_weekend',	'AirQualityIndex', 'station']
    stations_data = pd.concat([stations_data, df_pollutants], ignore_index=True)

forecast_data = pd.DataFrame()

# Load the data
for i in list(list_of_stations.keys()):
    df_pollutants_f = pd.read_excel(BASE_DIR / 'Dashboard_data' / 'forecast_data' / f'{i}_forecast.xlsx')
    if 'index' in df_pollutants_f.columns:
        df_pollutants_f = df_pollutants_f.drop('index', axis=1)
    df_pollutants_f['station'] = list_of_stations[i]
    df_pollutants_f.columns = ['datetime', 'direct_radiation (W/m²)',	'PM25', 'PM10',	'SO2', 'O3', 'NO2',	'CO', 'RH',	'TMP',	'WDR',	'WSP',	'is_festival',	'is_weekend',	'AirQualityIndex', 'station']
    forecast_data = pd.concat([forecast_data, df_pollutants_f], ignore_index=True)


# Dictionary with municipality names and random AQI values
municipalities_aqi = {
    "Azcapotzalco": {"station": "Azcapotzalco", "aqi": "null"},
    "Coyoacan": {"station": "Pedregal", "aqi": 0},
    "Cuajimalpa de Morelos": {"station": "Cuajimalpa de Morelos", "aqi": "null"},
    "Gustavo A. Madero": {"station": "Gustavo A. Madero", "aqi": "null"},
    "Iztacalco": {"station": "Iztacalco", "aqi": "null"},
    "Iztapalapa": {"station": "UAM Iztapalapa", "aqi": 0},
    "La Magdalena Contreras": {"station": "La Magdalena Contreras", "aqi": "null"},
    "Milpa Alta": {"station": "Milpa Alta", "aqi": "null"},
    "Alvaro Obregon": {"station": "Alvaro Obregon", "aqi": "null"},
    "Tlahuac": {"station": "Tlahuac", "aqi": "null"},
    "Tlalpan": {"station": "Tlalpan", "aqi": "null"},
    "Xochimilco": {"station": "Xochimilco", "aqi": "null"},
    "Benito Juarez": {"station": "Benito Juarez", "aqi": 1},
    "Cuauhtemoc": {"station": "Cuauhtemoc", "aqi": "null"},
    "Miguel Hidalgo": {"station": "Miguel Hidalgo", "aqi": "null"},
    "Tlalnepantla": {"station": "Tlalnepantla", "aqi": 1},
    "Venustiano Carranza": {"station": "Merced", "aqi": 1},
}

def update_municipalities_aqi(dataset, municipalities_aqi):
    """
    Update the municipalities_aqi dictionary with the latest AirQualityIndex values
    for each station based on the provided dataset.

    Parameters:
        dataset (pd.DataFrame): A DataFrame containing air quality data.
        municipalities_aqi (dict): A dictionary containing municipality information.

    Returns:
        dict: Updated municipalities_aqi dictionary.
    """
    # Ensure the datetime column is parsed correctly
    dataset['datetime'] = pd.to_datetime(dataset['datetime'])

    # Sort the dataset by datetime to get the latest entries
    dataset = dataset.sort_values(by='datetime')

    # Get the last available AirQualityIndex for each station
    latest_aqi = dataset.groupby('station').last()['AirQualityIndex']

    # Update the municipalities_aqi dictionary
    for municipality, data in municipalities_aqi.items():
        station = data['station']
        if station in latest_aqi:
            municipalities_aqi[municipality]['aqi'] = int(latest_aqi[station])

    return municipalities_aqi

# Update the dictionary
municipalities_aqi = update_municipalities_aqi(stations_data, municipalities_aqi)

# Now let's merge with the municipalities dictionary. We need to bring 2 columns station and aqi
df["station"] = df["NOMGEO"].map(lambda x: municipalities_aqi[x]["station"])
df["aqi"] = df["NOMGEO"].map(lambda x: municipalities_aqi[x]["aqi"])

def wkt_to_geojson(df):
    
    features = []
    
    for _, row in df.iterrows():
        # Get geometry and convert to WKT string if needed
        geom = row['geometry']
        if hasattr(geom, 'wkt'):
            wkt = geom.wkt
        else:
            wkt = str(geom)
            
        # Clean WKT string
        wkt = wkt.replace("POLYGON ((", "").replace("MULTIPOLYGON (((", "").replace(")))", "").replace("))", "")
        
        # Split into coordinate pairs
        rings = wkt.split("), (")
        coordinates = []
        
        for ring in rings:
            # Split coordinates and convert to float pairs
            coords = ring.split(",")
            ring_coords = []
            
            for coord in coords:
                x, y = map(float, coord.strip().split())
                ring_coords.append([x, y])
            
            # Close the ring by adding first coordinate at the end if needed
            if ring_coords[0] != ring_coords[-1]:
                ring_coords.append(ring_coords[0])
                
            coordinates.append(ring_coords)
        
        # Create GeoJSON feature
        feature = {
            "type": "Feature",
            "properties": {
                "NOMGEO": row['NOMGEO'],
                "station": row['station'],
                "aqi": row['aqi']
            },
            "geometry": {
                "type": "Polygon",
                "coordinates": coordinates
            }
        }
        
        features.append(feature)
    
    # Create final GeoJSON structure
    geojson = {
        "type": "FeatureCollection",
        "features": features
    }
    
    # Save to file
    with open('cdmx_zones.geojson', 'w', encoding='utf-8') as f:
        json.dump(geojson, f, ensure_ascii=False, indent=2)
    
    return geojson

# Usage:
geojson_data = wkt_to_geojson(df)

colormap = branca.colormap.LinearColormap(
    vmin=0,
    vmax=5,
    colors=["#00e400", "#ffff00", "#ff7e00", "#ff0000", "#8f3f97"]
)

def classical_map(data):
    """
    Create a classical map with markers for Mexican AQI stations.
    """
    lang = st.session_state.language
    
    m = folium.Map([19.3326, -99.1345], tiles="cartodbpositron", zoom_start=10.6,
            min_zoom=9,
            max_zoom=13)

    popup = folium.GeoJsonPopup(
        fields=["NOMGEO", "aqi"],
        aliases=["Municipality", "Air and Health Index"],
        localize=True,
        labels=True,
        style="background-color: yellow;",
    )

    tooltip = folium.GeoJsonTooltip(
        fields=["NOMGEO", "station", "aqi"],
        aliases=[f"{get_text('municipality', lang)}", f"{get_text('station', lang)}", f"{get_text('index', lang)}"],
        localize=True,
        sticky=False,
        labels=True,
        style="""
            background-color: #F0EFEF;
            border: 2px solid black;
            border-radius: 3px;
            box-shadow: 3px;
        """,
        max_width=800,
    )

    g = folium.GeoJson(
        data,
        style_function=lambda x: {
            "fillColor": colormap(x["properties"]["aqi"]) if isinstance(x["properties"]["aqi"], (int, float)) else "#C0C0C0",
            "color": "black",
            "fillOpacity": 0.4,
        },
        tooltip=tooltip,
        popup=popup,
    ).add_to(m)

    #colormap.add_to(m)
    m

    return m