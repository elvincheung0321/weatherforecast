from flask import Flask, request, jsonify, render_template
import requests
import json
import pandas as pd
from datetime import datetime

app = Flask(__name__)

def get_weather_data():
    # hong kong observatory api
    url = "https://data.weather.gov.hk/weatherAPI/opendata/weather.php?dataType=fnd&lang=en"
    
    response = requests.get(url)
    weather_data = json.loads(response.content)
    
    # lists for storing data
    date_list = []
    week_list = []
    max_temp_list = []
    min_temp_list = []
    max_rh_list = []
    min_rh_list = []
    
    # get the weather data
    for i in range(0, 9):
        forecast = weather_data["weatherForecast"][i]
        date_list.append(forecast["forecastDate"])
        week_list.append(forecast["week"])
        max_temp_list.append(forecast["forecastMaxtemp"]["value"])
        min_temp_list.append(forecast["forecastMintemp"]["value"])
        max_rh_list.append(forecast["forecastMaxrh"]["value"])
        min_rh_list.append(forecast["forecastMinrh"]["value"])
    
    weather_dict = {
        "Date": date_list,
        "Day": week_list,
        "Max Temp (°C)": max_temp_list,
        "Min Temp (°C)": min_temp_list,
        "Max RH (%)": max_rh_list,
        "Min RH (%)": min_rh_list
    }
    
    return pd.DataFrame(weather_dict)

@app.route('/')
def index():
    df = get_weather_data()
    dates = df['Date'].tolist()
    
    dates_list = []
    for date_string in dates:
        date_object = datetime.strptime(date_string, "%Y%m%d")
        dates_list.append({
            'original': date_string,
            'formatted': date_object.strftime("%Y/%m/%d (%a)")
        })
    
    return render_template('index.html', dates=dates_list)

@app.route('/get_weather', methods=['POST'])
def get_weather():
    selected_date = request.form.get('date')
    
    df = get_weather_data()
    result = df[df['Date'] == selected_date]

    html_table = result.to_html(classes='table table-striped', index=False, escape=False)
    date_object = datetime.strptime(selected_date, "%Y%m%d")
    display_date = date_object.strftime("%Y/%m/%d (%A)")
    
    return jsonify({
        'success': True, 
        'table': html_table,
        'date': display_date
    })