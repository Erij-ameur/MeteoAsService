from flask import Blueprint,request, jsonify
import requests
from datetime import datetime, timedelta
from src.constants.http_status_codes import HTTP_200_OK,HTTP_404_NOT_FOUND
from ..models.city import City,db
from itertools import islice

city = Blueprint("weather",__name__,url_prefix="/api/city")


@city.get('/all')
def getAllcities ():
    cities = City.query
    citiesdata =[]
    for c in cities:
        citiesdata.append({
            'id':c.id,
            'name':c.name
        })
    return jsonify({'data': citiesdata}), HTTP_200_OK


@city.route('/weekly/<int:id>')
def weeklyForecast(id):
    c = City.query.filter_by(id=id).first()
    if not c:
        return jsonify({'message': 'Item not found'}), HTTP_404_NOT_FOUND
    else:
        geocoding_url = f'https://geocoding-api.open-meteo.com/v1/search?name={c.name}'
        response = requests.get(geocoding_url).json()
        latitude = response['results'][0]['latitude']
        longitude = response['results'][0]['longitude']
        forecast_url = f'https://api.open-meteo.com/v1/forecast?latitude={latitude}&longitude={longitude}&current_weather=true&timezone=auto&hourly=temperature_2m&daily=temperature_2m_max'
        api_data = requests.get(forecast_url).json()
                
        def save_currentHour_index():
            for i, t in enumerate(api_data['hourly']['time']):
                if t == api_data['current_weather']['time']:
                    return i

        next4hours, next6days = [], []
        for i, t in enumerate(api_data['hourly']['time'][save_currentHour_index():save_currentHour_index()+4]):
            next4hours.append({
                'hour': (datetime.fromisoformat(api_data['hourly']['time'][save_currentHour_index()+i])).strftime("%H:%M"),
                'temperature': api_data['hourly']['temperature_2m'][save_currentHour_index()+i]
            })

        for i, t in enumerate(api_data['daily']['temperature_2m_max'][1:7]):
            date = (datetime.fromisoformat(api_data['daily']['time'][i+1])).strftime("%d %b")
            day_name = (datetime.fromisoformat(api_data['daily']['time'][i+1])).strftime("%A")
            if i < 1:
                day_name = 'Tomorrow'
            next6days.append({
                'day': day_name,
                'date': date,
                'temperature': t
            })

        weekly = {
            'next4hours': next4hours,
            'next6days': next6days
        }

        return weekly, HTTP_200_OK







@city.route('/<int:id>')
def forecast(id):
    c = City.query.filter_by(id=id).first()
    if not c :
        return jsonify ({'message':'Item not found'}),HTTP_404_NOT_FOUND
    else:
        geocoding_url = f'https://geocoding-api.open-meteo.com/v1/search?name={c.name}'
        response = requests.get(geocoding_url).json()
        latitude = response['results'][0]['latitude']
        longitude = response['results'][0]['longitude']
        forecast_url = f'https://api.open-meteo.com/v1/forecast?latitude={latitude}&longitude={longitude}&hourly=temperature_2m,pressure_msl,precipitation_probability,windspeed_10m&current_weather=true&timezone=auto&daily=precipitation_probability_max,precipitation_sum,precipitation_hours,rain_sum,snowfall_sum,sunrise,sunset,uv_index_max,windgusts_10m_max'
        api_data = requests.get(forecast_url).json()
        
        def save__cuurentHour_index():
            i=0
            while i< len(api_data['hourly']['time']) :
                if (api_data['hourly']['time'][i] == api_data['current_weather']['time']):
                    savedindex=i
                    break
                else:
                    i+=1
            return savedindex
        
        def save_hours_index():
            dayChartData = []
            indices = {
                '07:00': 'morning',
                '13:00': 'afternoon',
                '18:00': 'evening',
                '22:00': 'night'
            }
            today = datetime.now().date()
            for i, time in enumerate(api_data['hourly']['time']):
                dt = datetime.fromisoformat(time).date()
                if dt != today:
                    continue
                if time.endswith(tuple(indices.keys())):
                    slot = indices[time[-5:]]
                    dayChartData.append({slot: api_data['hourly']['temperature_2m'][i]})
            return dayChartData
        
        weather ={
            'dayChartData': save_hours_index(),
            'city' : c.name ,
            'temperature' : api_data['current_weather']['temperature'],
            'windspeed' : api_data['current_weather']['windspeed'],
            'winddirection' :api_data['current_weather']['winddirection'],
            'weathercode' :api_data['current_weather']['weathercode'],
            'precipitation_probability_max': api_data['daily']['precipitation_probability_max'][0],
            'precipitation_hours' : api_data['daily']['precipitation_hours'][0],
            'precipitation_sum' :api_data['daily']['precipitation_sum'][0] , 
            'rain_sum' : api_data['daily']['rain_sum'][0], 
            'snowfall_sum' : api_data['daily']['snowfall_sum'][0],  
            'sunrise' : api_data['daily']['sunrise'][0],  
            'sunset' : api_data['daily']['sunset'][0],  
            'uv_index_max' : api_data['daily']['uv_index_max'][0],  
            'windgusts' :api_data['daily']['windgusts_10m_max'][0] ,
            'pressure_msl' : api_data['hourly']['pressure_msl'][save__cuurentHour_index()]
        }
        return weather, HTTP_200_OK



