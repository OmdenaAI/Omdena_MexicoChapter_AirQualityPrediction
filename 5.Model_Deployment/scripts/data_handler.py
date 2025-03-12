import os
import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path

STATION_COORDINATES = {
    'Ajusco Medio': {'lat': 19.272222222222, 'lon': -99.207777777778},
    'Ajusco': {'lat': 19.204499182, 'lon': -99.254832314},
    'Benito Juarez': {'lat': 19.371666666667, 'lon': -99.159166666667},
    'Hospital General de México': {'lat': 19.4135, 'lon': -99.149},
    'Merced': {'lat': 19.424722222222, 'lon': -99.119722222222},
    'Miguel Hidalgo': {'lat': 19.404, 'lon': -99.202722222222},
    'Milpa Alta': {'lat': 19.1928, 'lon': -99.0238},
    'Pedregal': {'lat': 19.325277777778, 'lon': -99.204166666667},
    'San Agustin': {'lat': 19.533055555556, 'lon': -99.030555555556},
    'Santa Fe': {'lat': 19.354375, 'lon': -99.25915},
    'Tlalnepantla': {'lat': 19.529166666667, 'lon': -99.204722222222},
    'UAM Iztapalapa': {'lat': 19.36, 'lon': -99.07},
    'Xalostoc': {'lat': 19.526111111111, 'lon': -99.0825}
}

STATION_ACRONYMS = {
    "Pedregal": "PED",
    "Tlalnepantla": "TLA",
    "Benito Juarez": "BJU",
    "Merced": "MER"
}

BASE_DIR = Path(__file__).resolve().parent.parent
dummy_data = BASE_DIR / 'Dashboard_data' / 'AQI_dummy_data.xlsx'
def load_data(file_path=dummy_data):
    """Load data from Excel file"""
    try:
        df = pd.read_excel(file_path)
        #print(df.head())
        required_columns = [
            'AQI_STATION', 'HOUR_DAY', 'AQI', 'PM_2.5', 'PM_10',
            'NO2', 'SO2', 'CO', 'O3', 'TRAFFIC_CONGESTION_INDEX'
        ]
        missing_columns = set(required_columns) - set(df.columns)
        if missing_columns:
            raise ValueError(f"Missing columns in Excel file: {missing_columns}")
        return df
    except FileNotFoundError:
        print(f"Error: Data file not found at {file_path}")
        return None
    except Exception as e:
        print(f"Error loading data: {str(e)}")
        return None

def get_current_hour_data(station='All Stations'):
    """Get data for current hour of the day"""
    current_hour = datetime.now().hour
    df = load_data()
    
    if df is None or df.empty:
        return None
        
    # Filter data for the current hour
    current_data = df[df['HOUR_DAY'] == current_hour]
    
    if current_data.empty:
        return None

    # If specific station is selected
    if station != 'All Stations':
        station_data = current_data[current_data['AQI_STATION'] == station]
        if station_data.empty:
            return None
        return station_data.iloc[0].to_dict()
    
    # Return all stations data for the current hour
    return current_data.to_dict('records')

def get_station_coordinates(station_name):
    """Get coordinates for a specific station"""
    return STATION_COORDINATES.get(station_name)

def get_some_stations(stations=["Benito Juarez", "Merced", "Pedregal", "Tlalnepantla"]):
    return list(filter(lambda x: x in stations, list(STATION_COORDINATES.keys())))

def get_all_stations():
    """Get list of all station names"""
    return list(STATION_COORDINATES.keys())

def get_data_by_station(station_name):
    """Get all data for a specific station"""
    df = load_data()
    if df is None or df.empty:
        return None
    
    station_data = df[df['AQI_STATION'] == station_name]
    if station_data.empty:
        return None
        
    return station_data.iloc[0].to_dict()

def get_all_hours_data():
    """Get data for all hours"""
    df = load_data()
    if df is None or df.empty:
        return None
    
    return df.to_dict('records')
 
def get_pollutants(data: pd.DataFrame):
    """Get all possible pollutant metrics to choose from."""
    # NOTE: Update when real-world data is connected
    exclude_cols = ['date', 'date_w_timestamp', 'hour', 'datetime', 'direct_radiation (W/m²)', 'is_festival', 'is_weekend', 'station', 'AirQualityIndex']
    exclude_non_pollutants = ['wind_speed', 'humidity', 'pressure', 'WSP', 'WDR', 'RH', 'TMP']
    return list(filter(lambda x: x not in [*exclude_cols, *exclude_non_pollutants], data.columns))

def get_pollutant_measuremnents(pollutant: str):
    pollutant_map = {
        'pm25': 'μg/m³',
        'pm10': 'μg/m³',
        'o3': 'ppb',
        'no2': 'ppb',
        'co': 'ppm',
        'so2': 'ppb'
    }
    return pollutant_map.get(pollutant, 'units')

def round_to_nearest_hour(dt: datetime):
	return dt.replace(minute=0, second=0, microsecond=0) + timedelta(hours=dt.minute // 30)

def get_wind_dir(degrees: int) -> dict:
  if degrees == 0:
      return {
        'direction': 'N',
        'latex': 'narrow'
			}
  if degrees == 90:
      return {
        'direction': 'E',
        'latex': 'earrow'
			}
  if degrees == 180:
      return {
        'direction': 'S',
        'latex': 'sarrow'
			}
  if degrees == 270:
      return {
        'direction': 'W',
        'latex': 'warrow'
			}
  
	# for ranges
  if degrees > 0 and degrees < 90:
      return {
        'direction': f"{degrees}°NE",
        'latex': 'nearrow'
			}
  if degrees > 90 and degrees < 180:
      adjusted_angle = 180 - degrees
      return {
        'direction': f"{adjusted_angle}°SE",
        'latex': 'searrow'
			}
  if degrees > 180 and degrees < 270:
      adjusted_angle = 270 - degrees
      return {
        'direction': f"{adjusted_angle}°SW",
        'latex': 'swarrow'
			}
  if degrees > 270 and degrees < 360:
      adjusted_angle = 360 - degrees
      return {
        'direction': f"{adjusted_angle}°NW",
        'latex': 'nwarrow'
			}