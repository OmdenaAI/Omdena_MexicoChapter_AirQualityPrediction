def get_text(key, language):
    translations = {
        'nav_title': {
            'en': 'Mexico City Air and Health Index Forecast',
            'es': 'Monitor del Índice Aire y Salud de México'
        },
        'select_page': {
            'en': 'Select Page',
            'es': 'Seleccionar página'
        },
        'page1': {
            'en': 'Air and Health Index Heatmap',
            'es': 'Mapa de Calor Índice Aire y Salud'
        },
        'forecast': {
            'en': 'Forecast',
            'es': 'Pronostico'
        },
        'main': {
            'en': 'Home',
            'es': 'Inicio'
        },
        'information': {
            'en': 'Information',
            'es': 'Información'
        },
        'current_aqi': {
            'en': 'Current Air and Health Index',
            'es': 'Índice Aire y Salud Actual'
        },
        'pollutant_levels': {
            'en': 'Pollutant Levels',
            'es': 'Niveles de Contaminantes'
        },
        'station_aqi': {
            'en': 'Station Air and Health Index',
            'es': 'Niveles del Índice Aire y Salud por Estación'
        },
        'refresh_map': {
            'en': 'Refresh Map',
            'es': 'Actualizar Mapa'
        },
        'aqi_heatmap': {
            'en': 'Air and Health Index Heatmap of Mexico Monitoring Stations',
            'es': 'Mapa de Calor Índice Aire y Salud de Estaciones de Monitoreo'
        },

        # AQI Status translations
        'good': {
            'en': 'Good',
            'es': 'Buena'
        },
        'acceptable': {
            'en': 'Acceptable',
            'es': 'Aceptable'
        },
        'bad': {
            'en': 'Bad',
            'es': 'Mala'
        },
        'verybad': {
            'en': 'Very Bad',
            'es': 'Muy Mala'
        },
        'extremelybad': {
            'en': 'Extremely Bad',
            'es': 'Extremadamente Mala'
        },
        'nodata': {
            'en': 'No data or under maintenance',
            'es': 'Sin datos o en mantenimiento'
        },
        'moderate': {
            'en': 'Moderate',
            'es': 'Moderado'
        },
        'unhealthy_sensitive': {
            'en': 'Unhealthy for Sensitive Groups',
            'es': 'Poco saludable para grupos sensibles'
        },
        'unhealthy': {
            'en': 'Unhealthy',
            'es': 'Poco saludable'
        },
        'very_unhealthy': {
            'en': 'Very Unhealthy',
            'es': 'Muy poco saludable'
        },
        'hazardous': {
            'en': 'Hazardous',
            'es': 'Peligroso'
        },

        # Station translations
        'Ajusco Medio': {
            'en': 'Ajusco Medio',
            'es': 'Ajusco Medio'
        },
        'Ajusco': {
            'en': 'Ajusco',
            'es': 'Ajusco'
        },
        'Benito Juarez': {
            'en': 'Benito Juarez',
            'es': 'Benito Juárez'
        },
        'Hospital General': {
            'en': 'General Hospital',
            'es': 'Hospital General de México'
        },
        'Merced': {
            'en': 'Merced',
            'es': 'Merced'
        },
        'Miguel Hidalgo': {
            'en': 'Miguel Hidalgo',
            'es': 'Miguel Hidalgo'
        },
        'Milpa Alta': {
            'en': 'Milpa Alta',
            'es': 'Milpa Alta'
        },
        'Pedregal': {
            'en': 'Pedregal',
            'es': 'Pedregal'
        },
        'San Agustin': {
            'en': 'San Agustin',
            'es': 'San Agustín'
        },
        'Santa Fe': {
            'en': 'Santa Fe',
            'es': 'Santa Fe'
        },
        'Tlalnepantla': {
            'en': 'Tlalnepantla',
            'es': 'Tlalnepantla'
        },
        'UAM Iztapalapa': {
            'en': 'UAM Iztapalapa',
            'es': 'UAM Iztapalapa'
        },
        'Xalostoc': {
            'en': 'Xalostoc',
            'es': 'Xalostoc'
        },
        'station': {
            'en': 'Station',
            'es': 'Estación'
        },
        'select_station': {
            'en': 'Select Station',
            'es': 'Seleccionar Estación'
        },
        'All Stations': {
            'en': 'All Stations',
            'es': 'Todas las Estaciones'
        },
        'current_forecast': {
            'en': 'Air Quality Forecast',
            'es': 'Pronostico de Calidad del Aire'
        },
        'air_quality_index': {
            'en': 'Air and Health Index',
            'es': 'Índice de calidad del aire'
        },
        'humidity': {
            'en': 'Humidity',
            'es': 'Humedad'
        },
        'relative_humidity': {
            'en': 'Relative Humidity',
            'es': 'Humedad relativa'
        },
        'pressure': {
            'en': 'Pressure',
            'es': 'Presión'
        },
        'wind_speed': {
            'en': 'Wind Speed',
            'es': 'Velocidad del viento'
        },
        'wind_direction': {
            'en': 'Wind Direction',
            'es': 'Dirección del viento'
        },
        'o3': {
            'en': 'Ozone',
            'es': 'Ozono'
        },
        'no2': {
            'en': 'Nitrogen Dioxide',
            'es': 'Dióxido de nitrógeno'
        },
        'pm10': {
            'en': 'PM10',
            'es': 'PM10'
        },
        'pm25': {
            'en': 'PM2.5',
            'es': 'PM2.5'
        },
        'co': {
            'en': 'CO',
            'es': 'CO'
        },
        'so2': {
            'en': 'SO2',
            'es': 'SO2'
        },
        'metric': {
            'en': 'Metric',
            'es': 'Métrica de medida'
        },
        'pollutants': {
            'en': 'Pollutants',
            'es': 'Contaminantes'
        },
        'temperature': {
            'en': 'Temperature',
            'es': 'Temperatura'
        },
        'time_of_day': {
            'en': 'Time of day',
            'es': 'Hora del día'
        },
        ### Main page
        # Title
        'title_mp': {
            'en': 'Current Air and Health Index Map',
            'es': 'Mapa actual del índice de aire y salud'
        },
        # messages for population
        'air_and_heath_index': {
            'en': 'Current Air and Health Index:',
            'es': 'Índice de Aire y Salud Actual:'
        },
        'genaral_population': {
            'en': 'General Population:',
            'es': 'Población en General'
        },
        'sensitive_population': {
            'en': 'Sensitive Population:',
            'es': 'Población Sensible:'
        },
        'forecast_message': {
            'en': 'Forecast Air and Health Index of 24 hours:',
            'es': 'Pronóstico del Índice de Aire y Salud de 24 horas:'
        },
        'health_info': {
            'en': 'Air and Health Index - Risk Associated',
            'es': 'Índice de Aire y Salud - Riesgo Asociado'
        },
        'pollutantst': {
            'en': 'Other Pollutants',
            'es': 'Otros Contaminantes'
        },
        'pollutantst_text': {
            'en': 'Particulate Matter',
            'es': 'Material Particulado'
        },
        'second_col_poll': {
            'en': 'Current levels',
            'es': 'Niveles actuales'
        },
        'tableop': {
            'en': 'Table of pollutants',
            'es': 'Tabla de contaminantes'
        },
        'health_more_details': {
            'en': 'Recommendations for the protection of your health:',
            'es': 'Recomendaciones para la protección de tu salud:'
        },
        'click_here_f': {
            'en': 'Please go to Forecast in the panel for more details',
            'es': 'Por favor, vaya a Pronóstico en el panel para más detalles'
        },
        'click_here_i': {
            'en': 'Please go to Information in the panel for more details',
            'es': 'Por favor, vaya a Información en el panel para más detalles'
        },
        'recommend': {
            'en': 'Recommendations for:',
            'es': 'Recomendaciones para:'
        },
        'municipality': {
            'en': 'Municipality',
            'es': 'Municipio'
        },
        'index': {
            'en': 'Index',
            'es': 'Índice'
        }, 
        'selectzone': {
            'en': 'Please select the zone?',
            'es': '¿Por favor seleccionar la zona?'
        },
        'forexample': {
            'en': 'E.g. Benito Juarez',
            'es': 'Ej. Benito Juárez'
        },
        'mexicocity': {
            'en': 'Mexico City',
            'es': 'Ciudad de México'
        },  
        'best_time': {
            'en': 'Best time to be outside',
            'es': 'El mejor momento para estar al aire libre'
        },
        'worst_time': {
            'en': 'Worst time to be outside',
            'es': 'El peor momento para estar al aire libre'
        },
        'select_time': {
            'en': 'Select time period',
            'es': 'Seleccionar el período de tiempo'
        },
        'select_group': {
            'en': 'Select group',
            'es': 'Seleccionar grupo'
        },
        'selected': {
            'en': 'Selected:',
            'es': 'Seleccionado:'
        },
        'people_cardiovascular': {
            'en': 'People with cardiovascular or respiratory diseases and those over 60 years of age',
            'es': 'Personas con enfermedades cardiovasculares o respiratorias y mayores de 60 años'
        },
        'children_and_pregnant': {
            'en': 'Children under 12 years old and pregnant people',
            'es': 'Menores de 12 años y personas gestantes'
        },
        'general_population': {
            'en': 'General population',
            'es': 'Población en general'
        },
        'notes': {
            'en': 'Data is sourced from the monitoring stations in Mexico City and the application is built following the [guidelines from the local authorities](https://dof.gob.mx/nota_detalle.php?codigo=5715154&fecha=25/01/2024#gsc.tab=0). The Air and Health Index and associated messages are only for information purposes to warn the population. Please consider personal health conditions and stay up-to-date with local authorities and health providers.',
            'es': 'Los datos provienen de las estaciones de monitoreo en la Ciudad de México, y la aplicación se construyó siguiendo [los lineamientos de las autoridades locales](https://dof.gob.mx/nota_detalle.php?codigo=5715154&fecha=25/01/2024#gsc.tab=0). El Índice de Aire y Salud y los mensajes asociados tienen únicamente fines informativos para alertar a la población. Por favor, considere las condiciones personales de salud y manténgase informado a través de las autoridades locales y los proveedores de salud.'
        },
        'information_based_on_selection': {
            'en': 'Information based on selected station, time, and group',
            'es': 'Información basada en la estación, tiempo y grupo seleccionados'
        }

    }
    
    return translations.get(key, {}).get(language, key)
