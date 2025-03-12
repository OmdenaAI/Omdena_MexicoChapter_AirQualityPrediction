# Update this to follow page_1 / page_2 conventions
'''
  This is the forecast component of the application.
'''
from pathlib import Path
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import altair as alt
from datetime import datetime, timedelta
from babel.dates import format_date, format_time, format_datetime
from pathlib import Path
from scripts.prediction import (
  naive_formula, 
  naive_formula_24h, 
  calculate_pollutant_time_only,
  get_highest_aqi
)
from scripts.language_utils import get_text
from scripts.map_helpers import stations_data, forecast_data, list_of_stations
from scripts.data_handler import (
  get_current_hour_data, 
  get_all_stations, 
  get_some_stations, 
  get_pollutants, 
  get_pollutant_measuremnents, 
  round_to_nearest_hour, 
  get_wind_dir,
  STATION_ACRONYMS
)

def create_aqi_header(aqi_range, lang):
  """Create a range of lowest and higheset possible AQI based on prediction"""
  color_ranges = {
      1: {"color": "#00e400", "condition": "good"},        # Good
      2: {"color": "#ffff00", "condition": "acceptable"},  # Acceptable
      3: {"color": "#ff7e00", "condition": "bad"},         # Bad
      4: {"color": "#ff0000", "condition": "very bad"},    # Very Bad
      5: {"color": "#8f3f97", "condition": "extremely bad"} # Extremely Bad
    }
  min_aqi = aqi_range[0]
  max_aqi = aqi_range[1]
  lowest_aqi_condition = get_text(color_ranges.get(min_aqi, 'nodata')['condition'], lang).replace('_', ' ').title()
  highest_aqi_condition = get_text(color_ranges.get(max_aqi, 'nodata')['condition'], lang).replace('_', ' ').title()

  return f"""
    <div class='forecast-aqi-container' 
      style='background: linear-gradient(to right, {color_ranges.get(min_aqi, '#42424')['color']}, {color_ranges.get(max_aqi, '#42424')['color']}'; 
    color: {'black' if max_aqi <= 2 else 'white'}'>
      <div style='display: flex; justify-content: between'>
        <h4 style='margin: 0; padding: 0'>{get_text('air_quality_index', lang)}</h4>
      </div>
      <div style='display: flex; justify-content: flex-start; align-items: flex-end; margin-top: 10px'>
        <span>
            <h2 style='margin: 0; padding: 0'>{min_aqi}-{max_aqi}</h2>
            <span>{lowest_aqi_condition} to {highest_aqi_condition}</span>
        </span>
      </div>
    </div>
  """

def get_24hr_forecast(data, selected_station, metric='temperature', lang='en'):
   # Get the current time rounded to nearest hour
  current_datetime = round_to_nearest_hour(datetime.now())
  
  data = data.copy()
  data = data[data['station'] == selected_station]

  # get forecast_df
  BASE_DIR = Path(__file__).resolve().parent.parent
  acronym = STATION_ACRONYMS.get(selected_station)
  forecast_dir = BASE_DIR / 'Dashboard_data' / 'forecast_data' / f'{acronym}_forecast.xlsx'
  selected_forecast_data = pd.read_excel(forecast_dir, parse_dates=['datetime'])
  naive_24h_df = calculate_pollutant_time_only(selected_forecast_data, current_datetime, metric, acronym)

  chart = alt.Chart(naive_24h_df).mark_line(
      color='#2563EB',
      point=alt.MarkConfig(
          filled=True,
          size=120
      )
  ).encode(
      x=alt.X('formatted_time:O',
          sort=None,
          axis=alt.Axis(
              values=naive_24h_df['formatted_time'].tolist(),
              title=get_text('time_of_day', lang),
              titleColor='black',
              labelColor='black',
              labelAngle=-45,  # Angle labels for better readability
          ),
      ),
      y=alt.Y(f'predicted_{metric}:Q',
          axis=alt.Axis(
              title=get_pollutant_measuremnents(metric),
              titleColor='black',
              labelColor='black'
          )
      )
  ).properties(
      width=800,
      height=500,
      title=alt.TitleParams(
          text=f'24-Hour Forecast - {get_text(metric, lang)}',
          anchor='start',
          fontSize=16,
          fontWeight='bold',
          color='black',
          offset=15
      )
  )
  
  next_day_index = naive_24h_df[naive_24h_df['datetime'].dt.day != naive_24h_df['datetime'].dt.day.iloc[0]].index[0]
  next_day_time = naive_24h_df['formatted_time'].iloc[next_day_index]
  next_day_line = alt.Chart(pd.DataFrame({'formatted_time': [next_day_time]})).mark_rule(
    strokeDash=[12, 6],
    stroke='#64748B',
    strokeWidth=2
  ).encode(
    x=alt.X('formatted_time:O', sort=None)
  )

  chart += chart + next_day_line

    # Configure the theme
  chart = chart.configure_view(
      strokeWidth=0  # Removes the frame
  ).configure_axis(
      domainColor='black',
      domain=True,
      grid=False
  ).configure_title(
      align='left'
  )

  return chart

def home():
  """Main function to render the forecast page"""
  # Get language from session state
  lang = st.session_state.language
  nearest_hour = round_to_nearest_hour(datetime.now())
  end_hour = nearest_hour + timedelta(hours=23)
  
  # Set page title with language support
  st.title(get_text('current_forecast', lang))

  station_col, whitespace_1, day_forecast_col = st.columns([1,1,1])
  with station_col:
    selected_station = st.selectbox((get_text('station', lang)).capitalize(), get_some_stations())
  with day_forecast_col:
    st.markdown(f"""
      ##### Predictions for
      *{format_datetime(nearest_hour, 'MMMM d, H:00 a', locale=lang)}* - *{format_datetime(end_hour, 'MMMM d, H:00 a', locale=lang)}*
    """)

  # get AQI ranges
  aqi_range = get_highest_aqi(forecast_data, selected_station, True)

  with st.container():
    st.markdown(create_aqi_header(aqi_range, lang), unsafe_allow_html=True)
  wind_dir = get_wind_dir(int(naive_formula(stations_data, 'WDR', selected_station)))

  with st.container():
    st.write(f"""
      <div class="forecast-thw-container">
        
        <div class="forecast-thw-column">
          <span class="thw-header">{get_text('temperature', lang)}</span>
          <h3>{"{:.1f}°C".format(naive_formula(stations_data, 'TMP', selected_station))}</h3>
        </div>
             
        <div class="forecast-thw-column">
          <span class="thw-header">{get_text('relative_humidity', lang)}</span>
          <h3>{"{:.0f}%".format(naive_formula(stations_data, 'RH', selected_station))}</h3>
        </div>
             
        <div class="forecast-thw-column">
          <span class="thw-header">{get_text('wind_speed', lang)}</span>
          <h3>{"{:.0f} km/h".format(naive_formula(stations_data, 'WSP', selected_station))}</h3>
        </div>

        <div class="forecast-thw-column">
          <span class="thw-header">{get_text('wind_direction', lang)}</span>
          <h3>{wind_dir['direction']}</h3>
        </div>     
        
      </div>
    """, unsafe_allow_html=True)
  
  pollutant_select_col, whitespace_3, whitespace_4 = st.columns(3)
  with pollutant_select_col:
    pollutant_selection = st.selectbox(get_text('pollutants', lang), get_pollutants(stations_data), format_func=lambda x: x.upper())
  
  today = pd.Timestamp.now().date()
  day_fig = get_24hr_forecast(stations_data, selected_station, pollutant_selection, lang)
  with st.container():
    st.altair_chart(day_fig, use_container_width=True)

  st.write('*The forecast data listed above is approximately 85% accurate based on multiple tests.*')
  # Add explanatory notes
  st.markdown(get_text('notes', lang))
