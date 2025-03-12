### Page 2

import streamlit as st
import numpy as np
from datetime import datetime
import locale
import pandas as pd
from pathlib import Path
from streamlit_folium import folium_static, st_folium
from streamlit.components.v1 import html
from Dashboard_pages import forecast, information
from scripts.map_helpers import classical_map, geojson_data, stations_data, forecast_data
from scripts.prediction import calculate_pollutant_weighted_average, get_highest_aqi
from scripts.language_utils import get_text
from scripts.data_handler import get_current_hour_data, load_data
from scripts.data_handler import STATION_COORDINATES

# Get current data of stations and forecast of the stations
data = stations_data
forecast = forecast_data

# Set locale to Spanish (replace 'es_MX' with your system's Spanish locale if needed)
#locale.setlocale(locale.LC_TIME, "es_ES.UTF-8")  # Use "es_MX.UTF-8" for Mexico-specific locale
temperature = int(data["TMP"][-1:].values[0])  # Replace with dynamic temperature value

# Function to get formatted date and time in a specific language
# def get_date_time(lang):
#     if lang == "en":
#         locale.setlocale(locale.LC_TIME, "en_US.UTF-8")  # Set locale to English
#     elif lang == "es":
#         locale.setlocale(locale.LC_TIME, "es_ES.UTF-8")  # Set locale to Spanish
#     else:
#         raise ValueError("Unsupported language. Please choose 'English' or 'Spanish'.")

#     current_date = datetime.now().strftime("%A %d de %B de %Y")
#     formatted_date = current_date.capitalize()
#     current_time = datetime.now().strftime("%H:%M")
#     return formatted_date, current_time

#def get_date_time(lang):
#    if lang == "en":
#        locale.setlocale(locale.LC_TIME, "en_US.UTF-8")  # Set locale to English
#        date_format = "%A, %B %d, %Y"
#    elif lang == "es":
#        locale.setlocale(locale.LC_TIME, "es_ES.UTF-8")  # Set locale to Spanish
#        date_format = "%A %d de %B de %Y"
#    else:
#        raise ValueError("Unsupported language. Please choose 'en' or 'es'.")

#    current_date = datetime.now().strftime(date_format).capitalize()
#    current_time = datetime.now().strftime("%H:%M")
#    return current_date, current_time

# Because we are using streamlit cloud we skip the code above and use the below:
# Spanish month and day name mappings
SPANISH_MONTHS = {
    "January": "Enero", "February": "Febrero", "March": "Marzo",
    "April": "Abril", "May": "Mayo", "June": "Junio",
    "July": "Julio", "August": "Agosto", "September": "Septiembre",
    "October": "Octubre", "November": "Noviembre", "December": "Diciembre"
}

SPANISH_DAYS = {
    "Monday": "Lunes", "Tuesday": "Martes", "Wednesday": "Miércoles",
    "Thursday": "Jueves", "Friday": "Viernes", "Saturday": "Sábado", "Sunday": "Domingo"
}

def get_date_time(lang):
    now = datetime.now()
    
    if lang == "en":
        date_format = now.strftime("%A, %B %d, %Y")  # English format
    elif lang == "es":
        day_en = now.strftime("%A")
        month_en = now.strftime("%B")
        date_format = f"{SPANISH_DAYS[day_en]} {now.strftime('%d')} de {SPANISH_MONTHS[month_en]} de {now.year}"
    else:
        raise ValueError("Unsupported language. Please choose 'en' or 'es'.")

    current_time = now.strftime("%H:%M")
    return date_format, current_time



# Let's create a function to pick the color for the index
def get_color(aqi):
    if aqi == 1:
        return "#00e400"
    elif aqi == 2:
        return "#ffff00"
    elif aqi == 3:
        return "#ff7e00"
    elif aqi == 4:
        return "#ff0000"
    elif aqi == 5:
        return "#8f3f97"
    else:
        return "#C0C0C0"


def get_index(ind, lang):
    status = {
        
        1: {
            'en': 'Good',
            'es': 'Buena'
        },
        2: {
            'en': 'Acceptable',
            'es': 'Aceptable'
        },
        3: {
            'en': 'Bad',
            'es': 'Mala'
        },
        4: {
            'en': 'Very Bad',
            'es': 'Muy Mala'
        },
        5: {
            'en': 'Extremely Bad',
            'es': 'Extremadamente Mala'
        },
        6: {
            'en': 'No data',
            'es': 'Sin Datos'
        }
        }
    
    return status[ind][lang]

# Get message:
def air_message(index: int, population_type: str, lang: str) -> str:
    """
    Returns the air quality message for a given color and population type.
    
    Args:
        color (str): The air quality color ("Verde", "Amarillo", "Naranja", "Rojo", "Morado").
        population_type (str): The population type ("generalp" or "sensiblep").
    
    Returns:
        str: The message corresponding to the color and population type.
    """
    air_quality_data = {
        1: {
            "es": {  # Spanish
                "generalp": "El riesgo en salud es mínimo o nulo.",
                "sensiblep": "El riesgo en salud es mínimo o nulo."
            },
            "en": {  # English
                "generalp": "The health risk is minimal or nonexistent.",
                "sensiblep": "The health risk is minimal or nonexistent."
            }
        },
        2: {
            "es": {  # Spanish
                "generalp": "El riesgo en salud es mínimo.",
                "sensiblep": ("Personas que son sensibles al ozono (O3) o material particulado "
                            "(PM10 y PM2.5) pueden experimentar irritación de ojos y síntomas "
                            "respiratorios como tos, irritación de vías respiratorias, expectoración o flema, "
                            "dificultad para respirar o sibilancias.")
            },
            "en": {  # English
                "generalp": "The health risk is minimal.",
                "sensiblep": ("People sensitive to ozone (O3) or particulate matter (PM10 and PM2.5) may experience eye "
                            "irritation and respiratory symptoms such as cough, airway irritation, sputum, difficulty breathing, or wheezing.")
            }
        },
        3: {
            "es": {  # Spanish
                "generalp": "Es poco probable que se vea afectada.",
                "sensiblep": ("Incremento en el riesgo de tener síntomas respiratorios y/o disminución "
                            "en la función pulmonar.")
            },
            "en": {  # English
                "generalp": "It is unlikely to be affected.",
                "sensiblep": ("Increased risk of experiencing respiratory symptoms and/or reduced lung function.")
            }
        },
        4: {
            "es": {  # Spanish
                "generalp": "Se puede presentar daños a la salud.",
                "sensiblep": ("Pueden experimentar un agravamiento de asma, enfermedad pulmonar obstructiva crónica "
                            "o evento cardiovascular e incremento en la probabilidad de muerte prematura en personas "
                            "con enfermedad pulmonar obstructiva crónica y cardiaca.")
            },
            "en": {  # English
                "generalp": "Health damage may occur.",
                "sensiblep": ("They may experience worsening of asthma, chronic obstructive pulmonary disease, or cardiovascular events, "
                            "and an increased likelihood of premature death in people with chronic obstructive pulmonary and heart disease.")
            }
        },
        5: {
            "es": {  # Spanish
                "generalp": "Es más probable que cualquier persona se vea afectada por efectos graves a la salud.",
                "sensiblep": "Es más probable que cualquier persona se vea afectada por efectos graves a la salud."
            },
            "en": {  # English
                "generalp": "It is more likely that anyone will be affected by severe health effects.",
                "sensiblep": "It is more likely that anyone will be affected by severe health effects."
            }
        },
        6: {
            "es": {  # Spanish
                "generalp": "Sin Datos",
                "sensiblep": "Sin Datos"
            },
            "en": {  # English
                "generalp": "No Data",
                "sensiblep": "No Data"
            }
        }
    }  
    # Return the message
    return air_quality_data[index][lang][population_type]

# Define pollutant thresholds as a constant dictionary
POLLUTANT_THRESHOLDS = {
    'CO': [5.00, 9.00, 12.00, 16.00],
    'PM25': [45.00, 60.00, 132.00, 213.00],
    'PM10': [15.00, 33.00, 79.00, 130.00],
    'SO2': [0.0035, 0.0075, 0.185, 0.304],
    'O3': [0.0058, 0.0090, 0.135, 0.175],
    'NO2': [0.0053, 0.0106, 0.160, 0.213]
}

# Define categories as a constant list
CATEGORIES = [f"Buena", "Aceptable", "Mala", "Muy Mala", "Extremadamente Mala"]

def get_air_quality_category(pollutant, value):
    """
    Determines the air quality category based on pollutant measurements.

    Parameters:
        pollutant (str): The type of pollutant being measured
        value (float): The measurement value

    Returns:
        str: The air quality category
    """
    if pollutant not in POLLUTANT_THRESHOLDS:
        raise ValueError(f"Unknown pollutant: {pollutant}")

    thresholds = POLLUTANT_THRESHOLDS[pollutant]
    
    for i, threshold in enumerate(thresholds):
        if value <= threshold:
            return CATEGORIES[i]
    
    return CATEGORIES[-1]


def new_home():
    
    lang = st.session_state.language

    data = stations_data

    # Store the initial value of widgets in session state
    if "visibility" not in st.session_state:
        st.session_state.visibility = "visible"
        st.session_state.disabled = False
    
    col1, col2 = st.columns([3, 2])  # Adjust the width ratio as needed
    # First column is for the map
    with col1:
        st.title(get_text('title_mp', lang))
        # Legend Bar
        st.markdown(
            f"""
            <style>
                /* Scope styles to only affect the legend container */
                .unique-legend-container {{
                    display: flex;
                    align-items: center;
                    justify-content: space-between;
                    padding: 0px 0;
                }}
                .unique-legend-container .legend-item {{
                    display: flex;
                    align-items: center;
                    margin-right: 25px;
                }}
                .unique-legend-container .legend-circle {{
                    width: 15px;
                    height: 15px;
                    border-radius: 50%;
                    margin-right: 10px;
                }}
                .unique-legend-container .green {{ background-color: #00e400; }}
                .unique-legend-container .yellow {{ background-color: #ffff00; }}
                .unique-legend-container .orange {{ background-color: #ff7e00; }}
                .unique-legend-container .red {{ background-color: #ff0000; }}
                .unique-legend-container .purple {{ background-color: #8f3f97; }}
                .unique-legend-container .gray {{ background-color: #C0C0C0; }}
            </style>
            <div class="unique-legend-container">
                <div class="legend-item">
                    <div class="legend-circle green"></div>
                    <span>{get_text("good", lang)}</span>
                </div>
                <div class="legend-item">
                    <div class="legend-circle yellow"></div>
                    <span>{get_text("acceptable", lang)}</span>
                </div>
                <div class="legend-item">
                    <div class="legend-circle orange"></div>
                    <span>{get_text("bad", lang)}</span>
                </div>
                <div class="legend-item">
                    <div class="legend-circle red"></div>
                    <span>{get_text("verybad", lang)}</span>
                </div>
                <div class="legend-item">
                    <div class="legend-circle purple"></div>
                    <span>{get_text("extremelybad", lang)}</span>
                </div>
                <div class="legend-item">
                    <div class="legend-circle gray"></div>
                    <span>{get_text("nodata", lang)}</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
    with col2:
        formatted_date, current_time = get_date_time(lang)
        # Custom CSS for bordered container
        option = st.selectbox(
            f"{get_text('selectzone', lang)}",
            sorted(list(data["station"].unique())),  # Sort the list of stations alphabetically
            label_visibility=st.session_state.visibility,
            index=0,
            placeholder=f"{get_text('forexample', lang)}",
            disabled=st.session_state.disabled,
        )
        st.markdown(
                f"""
                
                📅 {formatted_date} &nbsp;&nbsp;&nbsp;&nbsp;
                🕒 {current_time} &nbsp;&nbsp;&nbsp;&nbsp; 🌡️ {temperature} 
                """,
                unsafe_allow_html=True
            )
        st.markdown(
                f"""
                <div line-height: 0.8;">
                <h4>{get_text("health_info", lang)}</h4>
                </div>
                """, 
                        unsafe_allow_html=True
            )

    col1, col2 = st.columns([3, 2]) #if st.session_state.window_size > 768 else st.columns([1])  # Adjust columns  # Adjust the width ratio as needed
    # First column is for the map
    with col1:
        # Update map based on selected zone
        selected_zone = option
        if selected_zone == None:
            m = classical_map(data=geojson_data)
            st_folium(m, width=800, height=800)
        else:
            filtered_geojson_data = {
                "type": "FeatureCollection",
                "features": [
                    feature for feature in geojson_data["features"]
                    if feature["properties"]["station"] == selected_zone
                ]
            }
            m = classical_map(data=filtered_geojson_data)
            st_folium(m, width=800, height=800)

    with col2:
        
        data = stations_data
        
        pollutants = ['PM25', 'PM10', 'SO2', 'O3', 'NO2', 'CO']
        pollutant_values = {pollutant: calculate_pollutant_weighted_average(data, pollutant,station=selected_zone) for pollutant in pollutants}
            

        # Get the markdown for the table and recommendations

        st.markdown("""
            <style>
            .bordered-box {
            border: 1px solid #000000;
            border-radius: 20px;
            padding: 10px;
            margin-top: 0px;
            background-color: #ffffff;
            }
            .bordered-box h4 {
            margin-top: 0;
            }
            </style>
            """, unsafe_allow_html=True)
        
        select_index = get_highest_aqi(data, selected_zone)
        forecast_index = get_highest_aqi(forecast, selected_zone, forecast=True)

        # Content inside the bordered box
        st.markdown(
            f"""
            <div class="bordered-box" style="font-size: 18px; line-height: 1.2; color: black;">
            <strong>{get_text("air_and_heath_index", lang)}</strong> 
            <span style="display: inline-block; padding: 5px 10px; border-radius: 20px; background-color: {get_color(select_index)}; color: black;">{get_index(select_index, lang)}</span>
            <br><br>
            <strong>{get_text('sensitive_population', lang)}</strong> {air_message(select_index, "sensiblep", lang)}
            <br><br>
            <strong>{get_text('genaral_population', lang)}</strong> {air_message(select_index, "generalp", lang)}
            <br><br><br>
            <strong>{get_text('forecast_message', lang)}</strong>
            <span style="display: inline-block; padding: 5px 10px; border-radius: 20px; background-color: {get_color(forecast_index[0])}; color: black;">{get_index(forecast_index[0], lang)}</span> 
            -
            <span style="display: inline-block; padding: 5px 10px; border-radius: 20px; background-color: {get_color(forecast_index[1])}; color: black;">{get_index(forecast_index[1], lang)}</span>
            ({get_text("click_here_f", lang)})
            <br><br>
            {get_text("health_more_details", lang)} {get_text("click_here_i", lang)}
            </div>

            """,
            unsafe_allow_html=True,
        )
            
        # Custom CSS for the table
        #### Need to include the weighted average of the 12h and the average of 24h
        st.markdown(
            f"""
            <style>
                /* Container and general layout styles */
                .unique-legend-container {{
                    display: flex;
                    align-items: center;
                    justify-content: space-between;
                    flex-wrap: wrap; /* Enable wrapping on smaller screens */
                    padding: 10px 0;
                    max-width: 100%;
                    box-sizing: border-box; /* Prevent overflow */
                }}
                .unique-legend-container .legend-item {{
                    display: flex;
                    align-items: center;
                    margin-right: 25px;
                    margin-bottom: 10px; /* Add spacing for wrapping rows */
                    flex: 1 1 30%; /* Allow items to shrink and wrap */
                }}
                .unique-legend-container .legend-circle {{
                    width: 20px;
                    height: 20px;
                    border-radius: 50%;
                    margin-right: 10px;
                }}
                
                /* Table styles */
                .pollutant-table {{
                    width: 100%;
                    border-collapse: collapse;
                    background-color: white;
                    color: black;
                    font-size: 14px;
                }}
                .pollutant-table th, .pollutant-table td {{
                    border: 1px solid black;
                    padding: 5px;
                    text-align: center;
                }}
                .pollutant-table th {{
                    font-weight: bold;
                    background-color: #f0f0f0; /* Light gray header background */
                }}
                .pollutant-table td span {{
                    font-weight: bold;
                }}
                .dark-green {{ color: #006400; }}
                .yellow {{ color: #FFD700; }}
                .red {{ color: #FF4500; }}
                .purple {{ color: #A020F0; }}
                .orange {{ color: #FFA500; }}

                /* Responsiveness: Adjust styles for smaller screens */
                @media (max-width: 768px) {{
                    .unique-legend-container {{
                        justify-content: center; /* Center-align items */
                    }}
                    .unique-legend-container .legend-item {{
                        flex: 1 1 45%; /* Adjust item width for smaller screens */
                    }}
                    .pollutant-table {{
                        font-size: 12px; /* Reduce font size for tables */
                    }}
                }}
                @media (max-width: 480px) {{
                    .unique-legend-container .legend-item {{
                        flex: 1 1 100%; /* Stack items vertically */
                        justify-content: center;
                    }}
                    .pollutant-table {{
                        font-size: 10px; /* Further reduce font size */
                    }}
                }}
            </style>
            """,
            unsafe_allow_html=True,
        )
        
        # Table Content
        # Add the rest of your markdown and tables
        st.markdown(
            f"""
            <br>
            <div>
                <h4>{get_text("tableop", lang)}</h4>
            </div>
            <br>
            <table class="pollutant-table">
                <tr>
                    <th>{get_text("pollutantst_text", lang)} (µg/m³)</th>
                    <th>{get_text("second_col_poll", lang)}</th>
                </tr>
                <tr>
                    <td>PM10</td>
                    <td><span class="dark-green">{pollutant_values["PM10"]}</span> µg/m³</td>
                </tr>
                <tr>
                    <td>PM2.5</td>
                    <td><span class="yellow">{pollutant_values["PM25"]}</span> µg/m³</td>
                </tr>
                <tr>
                    <td>O₃</td>
                    <td><span class="red">{pollutant_values["O3"]}</span> ppm</td>
                </tr>
                <tr>
                    <td>NO₂</td>
                    <td><span class="purple">{pollutant_values["NO2"]}</span> ppm</td>
                </tr>
                <tr>
                    <td>SO₂</td>
                    <td><span class="orange">{pollutant_values["SO2"]}</span> ppm</td>
                </tr>
                <tr>
                    <td>CO</td>
                    <td><span class="red">{pollutant_values["CO"]}</span> ppm</td>
                </tr>
            </table>
            """,
            unsafe_allow_html=True,
        )

    # Add explanatory notes
    st.markdown(get_text('notes', lang))
