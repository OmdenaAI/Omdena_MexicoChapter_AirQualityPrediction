import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime, timedelta

# other libraries
import openmeteo_requests
import requests_cache
import pandas as pd
from retry_requests import retry
import numpy as np
import pickle
from datetime import datetime, timedelta
import lightgbm as lgb

# Log handling
lgb.basic._log_info = lambda *args, **kwargs: None

# Handle warnings
import warnings
warnings.filterwarnings("ignore")

ADJUSTMENT_FACTORS = {
  'PM25': 0.694,
  'PM10': 0.714
}

def naive_formula(df: pd.DataFrame, column: str, station=None) -> int:
  """
    Use historical data and simple average to return a naive prediction for the model.
  """
  if station != None:
    df = df[df["station"] == station]
  else:
    return 0
  
  current_date = datetime.today().day
  data_points = df[df['datetime'].dt.day == current_date]
  naive_average = data_points[column].mean()
  return naive_average

def naive_formula_24h(
  df: pd.DataFrame, 
  current_datetime: datetime, 
  column: str, 
  station=None
) -> pd.DataFrame:
    """
    Use historical data to return naive predictions for the next 24 hours based on historical averages.
    
    Args:
        df: DataFrame with datetime column and measurements
        current_datetime: The reference datetime to start predictions from
        column: The column to make predictions for
        station: Optional station filter
        
    Returns:
        DataFrame with predictions for next 24 hours
    """
    if station is not None:
        df = df[df["station"] == station]
    
    # Initialize results
    predictions = []
    hours = []
    
    # Get predictions for each of the next 24 hours
    for hour in range(24):
        target_datetime = current_datetime + pd.Timedelta(hours=hour)
        
        # Get historical data points matching the hour and minute
        historical_points = df[
            (df['datetime'].dt.dayofyear == target_datetime.timetuple().tm_yday) &
            (df['datetime'].dt.hour == target_datetime.hour)
        ]
        
        # Calculate average for this hour
        prediction = historical_points[column].mean() * ADJUSTMENT_FACTORS.get(column, 1)
        
        predictions.append(prediction)
        hours.append(target_datetime)
        # hours.append(target_datetime.strftime('%H:00'))
    
    # Create results DataFrame
    results = pd.DataFrame({
        'datetime': hours,
        'formatted_time': list(map(lambda x: x.strftime('%H:00'), hours)),
        f'predicted_{column}': predictions
    })
    
    return results

def calculate_pollutant_weighted_average(df: pd.DataFrame, pollutant: str, adjustment_factor: int = 1, station: str = None):
  """
  Calculate weighted average concentrations for different pollutants.
  """
  if station != None:
    df = df[df["station"] == station]
  else:
      return 0
  
  # Handle non-PM/CO cases early
  if pollutant not in ['PM25', 'PM10', 'CO']:
      return round(np.mean(df[pollutant][-3:].values), 3)
  
  # Get appropriate window size and data
  window_size = 8 if pollutant == 'CO' else 12
  concentrations = df[pollutant][-window_size:].values
  
  # Handle CO separately
  if pollutant == 'CO':
      if len(concentrations) < 8 or np.isnan(concentrations).sum() > len(concentrations) * 0.25:
          return "No info"
      return round(np.mean(concentrations), 3)
  
  # Process PM data
  last_three = concentrations[-3:]
  last_three_null_count = np.isnan(last_three).sum()
  
  # Check last three values
  if last_three_null_count >= 2:
      return "No info"
  
  # Handle single null in last three values
  if last_three_null_count == 1:
      concentrations = concentrations.copy()
      concentrations[-3:] = np.nan_to_num(last_three, nan=0)
  
  # Check total null count
  total_null_count = np.isnan(concentrations).sum()
  if total_null_count > len(concentrations) * 0.25:
      return "No info"
  
  # Calculate PM average
  try:
      Cmax = np.nanmax(concentrations)
      Cmin = np.nanmin(concentrations)
      w = max(0.5, 1 - ((Cmax - Cmin) / Cmax))
      powers = np.arange(len(concentrations)-1, -1, -1)
      weights = w ** powers
      
      weighted_sum = np.sum(concentrations * weights)
      weight_sum = np.sum(weights)
  except ValueError:
      return 0

  return int((weighted_sum / weight_sum) * ADJUSTMENT_FACTORS.get(pollutant, 1))

def calculate_pollutant_time_only(
    forecast_df: pd.DataFrame, 
    current_datetime: datetime,
    column: str, 
    station_acronym: str = None
):
  '''
    This formula naively extracts the forecasted pollutant using the attached forecast
    data.
  '''
  
  try:
    # get the matching time_index
    # Initialize results
    predictions = []
    hours = []
   
    # Get predictions for each of the next 24 hours
    for hour in range(24):
      target_datetime = current_datetime + pd.Timedelta(hours=hour)
      
      # Get historical data points matching the hour and minute
      historical_points = forecast_df[
          (forecast_df['datetime'].dt.hour == target_datetime.hour)
      ]
      
      # Calculate average for this hour
      # NOTE: account for adjustment value?
      prediction = historical_points[f'{column}_{station_acronym}'].values[0]
      
      predictions.append(prediction)
      hours.append(target_datetime)
      # hours.append(target_datetime.strftime('%H:00'))
    
      # Create results DataFrame
      results = pd.DataFrame({
          'datetime': hours,
          'formatted_time': list(map(lambda x: x.strftime('%H:00'), hours)),
          f'predicted_{column}': predictions
      })
      
    return results
  except Exception as e:
    print(f"Error processing pollutants: {e}")
  
    
def get_highest_aqi(df, station=None, forecast=False, output=None):
  # Ensure datetime is in proper format
  df['datetime'] = pd.to_datetime(df['datetime'])

  # Check station
  if station is None and forecast==False:
      # Get the last row for each station based on datetime
      last_rows = df.sort_values('datetime').groupby('station').last().reset_index()

      # Find the station with the highest AirQualityIndex
      highest_aqi_row = last_rows.loc[last_rows['AirQualityIndex'].idxmax()]

      # Extract the station name and AQI value
      #highest_station = highest_aqi_row['station']
      highest_aqi = highest_aqi_row['AirQualityIndex']

      if output is None:
        return highest_aqi
      elif output == 'time':
         return highest_aqi_row['datetime']

  # Check station
  if station is None and forecast:
      # Let's get the data from that station
      lowest_fore = df.loc[df["AirQualityIndex"].idxmin()]
      max_fore = df.loc[df["AirQualityIndex"].idxmax()]

      highest_aqi_fore = max_fore['AirQualityIndex']
      lowest_aqi_fore = lowest_fore['AirQualityIndex']

      low_max = [lowest_aqi_fore, highest_aqi_fore]

      if output is None:
        return low_max
      elif output == 'time':
        return [max_fore['datetime'], lowest_fore['datetime']]
  
  elif station in list(df["station"].values) and forecast == False:
      # Let's get the data from that station
      filter_station = df[df["station"] == station].iloc[-1:, -2].values[0]

      return filter_station
  
  elif station in list(df["station"].values) and forecast:
      # Let's get the data from that station
      lowest_fore = df.loc[df[df["station"] == station]["AirQualityIndex"].idxmin()]
      max_fore = df.loc[df[df["station"] == station]["AirQualityIndex"].idxmax()]

      highest_aqi_fore = max_fore['AirQualityIndex']
      lowest_aqi_fore = lowest_fore['AirQualityIndex']

      low_max = [lowest_aqi_fore, highest_aqi_fore]

      if output is None:
        return low_max
      elif output == 'time':
        return [max_fore['datetime'], lowest_fore['datetime']]
  
  elif station not in df.columns:
      "No data for selected station"
      return 6
  

# Jesus' prediction function to generate forecast excel files


# Let's get the forecast of the weather data
# We are going to use the Open-Meteo API to get them
def get_weather_data(start_date, end_date):
	# Setup the Open-Meteo API client with cache and retry on error
	cache_session = requests_cache.CachedSession('.cache', expire_after = -1)
	retry_session = retry(cache_session, retries = 5, backoff_factor = 0.2)
	openmeteo = openmeteo_requests.Client(session = retry_session)

	url = "https://archive-api.open-meteo.com/v1/archive"
	params = {
		"latitude": 19.4326, # Mexico City latitude
		"longitude": 99.1332, # Mexico City longitude
		"start_date": start_date,
		"end_date": end_date,
		"hourly": ["temperature_2m", "relative_humidity_2m", "wind_speed_10m", "wind_direction_10m", "direct_radiation"] # Variables to retrieve and used in training
	}
	responses = openmeteo.weather_api(url, params=params)
	response = responses[0]

	# Process hourly data
	hourly = response.Hourly()
	hourly_temperature_2m = hourly.Variables(0).ValuesAsNumpy()
	hourly_relative_humidity_2m = hourly.Variables(1).ValuesAsNumpy()
	hourly_wind_speed_10m = hourly.Variables(2).ValuesAsNumpy()
	hourly_wind_direction_10m = hourly.Variables(3).ValuesAsNumpy()
	hourly_direct_radiation = hourly.Variables(4).ValuesAsNumpy()

	hourly_data = {"date": pd.date_range(
		start = pd.to_datetime(hourly.Time(), unit = "s", utc = True),
		end = pd.to_datetime(hourly.TimeEnd(), unit = "s", utc = True),
		freq = pd.Timedelta(seconds = hourly.Interval()),
		inclusive = "left"
	)}

	hourly_data["direct_radiation"] = hourly_direct_radiation
	hourly_data["relative_humidity_2m"] = hourly_relative_humidity_2m
	hourly_data["temperature_2m"] = hourly_temperature_2m
	hourly_data["wind_direction_10m"] = hourly_wind_direction_10m
	hourly_data["wind_speed_10m"] = hourly_wind_speed_10m

	hourly_dataframe = pd.DataFrame(data = hourly_data)
	hourly_dataframe.columns = ["datetime", "direct_radiation (W/m²)", "RH", "TMP", "WDR", "WSP"]
	
	hourly_dataframe["is_festival"] = 1
	hourly_dataframe["is_weekend"] = 0
	
	return hourly_dataframe


# Function to have time features in the dataframe
def preprocess_data(df):
    df.columns = df.columns.str.replace(' ', '_', regex=False)
    df['datetime'] = pd.to_datetime(df['datetime'])
    df['day'] = df['datetime'].dt.day
    df['month'] = df['datetime'].dt.month
    df['year'] = df['datetime'].dt.year
    df['hour'] = df['datetime'].dt.hour
    df['weekday'] = df['datetime'].dt.weekday
    return df



# Function to create future data with lags
def create_future_data_with_lags(current_data, target_col='PM25_MER', future_steps=24, lags=[1, 2, 3, 24, 48, 72]):
    # Initialize predictions list
    predictions = []
    
    # Get last known values
    last_known_values = current_data[target_col].tail(max(lags)).values
        
    # Create future dates once
    last_date = current_data['datetime'].max()
    future_dates = pd.date_range(
        start=last_date + pd.Timedelta(hours=1),
        periods=future_steps,
        freq='h'
    )
    
    # Pre-create rows for future data
    future_rows = []
    
    # For each future step
    for step in range(future_steps):
        # Create a dictionary for the current row
        current_row = {'datetime': future_dates[step]}
        
        # Add lag features
        for lag in lags:
            if step < lag:
                # If we don't have enough predictions yet, use historical data
                lag_value = last_known_values[-(lag-step)]
            else:
                # Use previously generated predictions
                lag_value = predictions[step-lag]
            
            current_row[f'{target_col}_log_lag_{lag}'] = lag_value
        
        future_rows.append(current_row)

        # Here you would normally make a prediction and append to predictions list
        # For now, let's just append a placeholder
        predictions.append(None)  # Replace this with actual model prediction
    
    # Create the future data DataFrame once
    future_data = pd.DataFrame(future_rows)
    
    # Preprocess all data at once
    future_data = preprocess_data(future_data)
    
    return future_data

# Function to calculate the Air and Health Index for each pollutant
def check_pollution(value, pollutant):
    categories = {
        "O3": [(0, 0.058), (0.058, 0.09), (0.09, 0.135), (0.135, 0.175), (0.175, float('inf'))],
        "NO2": [(0, 0.053), (0.053, 0.106), (0.106, 0.16), (0.16, 0.213), (0.213, float('inf'))],
        "SO2": [(0, 0.035), (0.035, 0.075), (0.075, 0.185), (0.185, 0.304), (0.304, float('inf'))],
        "CO": [(0, 5), (5, 9), (9, 12), (12, 16), (16, float('inf'))],
        "PM10": [(0, 45), (45, 60), (60, 132), (132, 213), (213, float('inf'))],
        "PM25": [(0, 15), (15, 33), (33, 79), (79, 130), (130, float('inf'))]
    }

    if pollutant not in categories:
        return "Unknown pollutant"

    for i, (low, high) in enumerate(categories[pollutant], start=1):
        if low <= value <= high:
            return i  # Return category (1-5)

    return "Invalid value"

# Path to the models
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Let's get the list of the pollutants
pollutants = ['CO', 'NO2', 'O3', 'PM10', 'PM25', 'SO2']

# List of our stations
stations = ['MER', 'BJU', 'PED', 'TLA']
#BASE_DIR / 'Dashboard_data' / 'current_data' / f'{i}_merged_imputed.xlsx'
# Load all models at once at the beginning
models = {
    f"{poll}_{station}": lgb.Booster(model_str=pickle.load(open(BASE_DIR / '4.Model_Development' / 'models' / f"{poll}_{station}_model_.pkl", "rb"))._handle)
    for station in stations
    for poll in pollutants
}

for station_name in stations:
    
    # Let's load our dataset
    current_data = pd.read_excel(BASE_DIR / '2.Data_Collection' / f"{station_name}_merged_imputed.xlsx")
    
    # We need only 72 hours from our previous dataset
    last_rows = current_data.tail(72)
    
    # Let's get the last date of the current data
    last_date = last_rows['datetime'].max().strftime('%Y-%m-%d')

    # Get hourly data from weather api
    hourly_dataframe = get_weather_data(last_date, last_date) # Because it is the same date

    # Let's remove the first from the hourly_data
    #hourly_dataframe = hourly_dataframe.iloc[1:, :]
    
    # Convert to datetime and format
    hourly_dataframe['datetime'] = pd.to_datetime(hourly_dataframe['datetime']).dt.strftime('%Y-%m-%d %H:%M:%S')
    
    for polls in pollutants:
        # We are going to process the last 72 hours of the current data
        future_data = create_future_data_with_lags(
            current_data=last_rows,
            target_col=f'{polls}_{station_name}',
            future_steps=24,
            lags=[1, 2, 3, 24, 48, 72])
        
        future_data['datetime'] = pd.to_datetime(future_data['datetime']).dt.strftime('%Y-%m-%d %H:%M:%S')

        # Merge the dataframes
        df = pd.merge(hourly_dataframe, future_data, on='datetime', how='left').sort_values(by="datetime")
        
        # Let's load the model for the pollutants and station
        model_out = models[f"{polls}_{station_name}"]
        
        expected_features = model_out.feature_name()

        #df = merged_data.sort_values(by="datetime")  # Ensure chronological order

        # Create a new column for predictions
        df[f"{polls}_PRED"] = np.nan

        # remove the datetime column
        df = df.drop(columns=['datetime'])

        # Let's rename the columns to include MER
        df = df.rename(columns={'direct_radiation (W/m²)': 'direct_radiation_(W/m²)', 'RH': f'RH_{station_name}', 'TMP': f'TMP_{station_name}', 'WDR': f'WDR_{station_name}', 'WSP': f'WSP_{station_name}'})
        
        # I need to use log transformation to my lag features
        lag_columns = [f'{polls}_{station_name}_log_lag_1', f'{polls}_{station_name}_log_lag_2', f'{polls}_{station_name}_log_lag_3', f'{polls}_{station_name}_log_lag_24', f'{polls}_{station_name}_log_lag_48', f'{polls}_{station_name}_log_lag_72']
        df[lag_columns] = np.log1p(df[lag_columns])
        
        # 1. First, identify all rows that need prediction
        mask_needs_prediction = pd.isna(df[f"{polls}_PRED"])
        indices_to_predict = df[mask_needs_prediction].index


        # 2. Process these rows in sequence (necessary because of the lag dependencies)
        for i in indices_to_predict:
            # Extract features more efficiently (slicing is faster than to_frame().T)
            input_data = df.loc[i:i, expected_features].astype(float)
            
            try:
                # Make prediction
                predicted_pm25_log = model_out.predict(input_data)[0]
            except Exception as e:
                print(f"Error at index {i}: {e}")
            
            
            predicted_pm25 = np.expm1(predicted_pm25_log)
            
            # Store prediction using .at (faster than .loc for single values)
            df.at[i, f"{polls}_PRED"] = predicted_pm25
            
            # Update future lag values more efficiently
            for lag in range(1, 4):
                future_idx = i + lag
                if future_idx < len(df):
                    df.at[future_idx, f"{polls}_{station_name}_log_lag_{lag}"] = predicted_pm25_log

        hourly_dataframe[f"{polls}_{station_name}"] = df[f"{polls}_PRED"]

    hourly_dataframe["Air_index"] = np.nan

    # Let's iterate through the pollutants columns and check their pollution levels, then storage the max value of each iteration
    for poll in pollutants:
        # Let's create one variable that will storage the max value of each iteration
        max_value = 0
        for i in range(len(hourly_dataframe)):
            value = hourly_dataframe.loc[i, f"{poll}_{station_name}"]
            category = check_pollution(value, poll)
            if category == "Invalid value":
                continue
            if category == "Unknown pollutant":
                continue
            if category > max_value:
                max_value = category
        hourly_dataframe["Air_index"] = max_value

    # Save the dataframe
    hourly_dataframe.to_excel(BASE_DIR / '5.Model_Deployment' / 'Dashboard_data' / 'forecast_data' / f"{station_name}_forecast.xlsx", index=False)