from flask import Flask, request, jsonify, render_template
import requests
import pandas as pd
from datetime import datetime

app = Flask(__name__)

def get_weather_data():
    url = "https://data.weather.gov.hk/weatherAPI/opendata/weather.php?dataType=fnd&lang=en"
    
    response = requests.get(url)
    weather_data = response.json()
    
    date = []
    day = []
    max_temp = []
    min_temp = []
    max_humid = []
    min_humid = []
    
    for i in range(0, 9):
        forecast = weather_data["weatherForecast"][i]

        date.append(forecast["forecastDate"])
        day.append(forecast["week"])

        max_temp.append(forecast["forecastMaxtemp"]["value"])
        min_temp.append(forecast["forecastMintemp"]["value"])
        max_humid.append(forecast["forecastMaxrh"]["value"])
        min_humid.append(forecast["forecastMinrh"]["value"])
    
    weather_dict = {
        "Date": date,
        "Day": day,
        "Max Temp(°C)": max_temp,
        "Min Temp(°C)": min_temp,
        "Max Humidity(%)": max_humid,
        "Min Humidity(%)": min_humid
    }
    
    return pd.DataFrame(weather_dict)

@app.route('/')
def index():
    df = get_weather_data()
    dates = df['Date'].tolist()
    
    formated_dates = []
    for date in dates:
        format_date = datetime.strptime(date, "%Y%m%d")

        formated_dates.append({
            'original': date,
            'formatted': format_date.strftime("%Y/%m/%d (%a)")
        })
    
    return render_template('index.html', dates = formated_dates)

@app.route('/get_weather', methods=['POST'])
def get_weather():
    select_date = request.form.get('date')
    
    df = get_weather_data()
    result = df[df['Date'] == select_date]

    table = result.to_html(classes='table', index=False, escape=False)
    format_date = datetime.strptime(select_date, "%Y%m%d")
    display_date = format_date.strftime("%Y/%m/%d (%a)")
    
    return jsonify({
        'success': True, 
        'table': table,
        'date': display_date
    })