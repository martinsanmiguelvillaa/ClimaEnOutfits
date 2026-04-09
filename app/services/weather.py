import os
import requests
from sqlalchemy.orm import Session
from app.models.weather_logs import WeatherLog
from datetime import timezone, timedelta
from app.logger import get_logger

log = get_logger("services.weather")

OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")


def get_coordinates(city: str):
    log.debug(f"Obteniendo coordenadas para ciudad: {city}")
    url = "https://api.openweathermap.org/geo/1.0/direct"
    params = {
        "q": city,
        "limit": 1,
        "appid": OPENWEATHER_API_KEY
    }

    response = requests.get(url, params=params)
    response.raise_for_status()
    data = response.json()

    if not data:
        log.warning(f"Ciudad no encontrada: {city}")
        raise ValueError("No se encontró la ciudad")

    log.debug(f"Coordenadas obtenidas: {data[0]['name']} ({data[0]['lat']}, {data[0]['lon']})")
    return {
        "name": data[0]["name"],
        "lat": data[0]["lat"],
        "lon": data[0]["lon"]
    }


def get_weather_data(lat: float, lon: float):
    log.debug(f"Consultando clima para ({lat}, {lon})")
    url = "https://api.openweathermap.org/data/3.0/onecall"
    params = {
        "lat": lat,
        "lon": lon,
        "appid": OPENWEATHER_API_KEY,
        "units": "metric"
    }

    response = requests.get(url, params=params)
    response.raise_for_status()
    data = response.json()
    log.debug(f"Clima recibido: {data.get('current', {}).get('temp')}°C, {data['current']['weather'][0]['description']}")

    current = data.get("current", {})
    daily = data.get("daily", [])
    hourly = data.get("hourly", [])

    max_uv_index = None
    if daily:
        max_uv_index = daily[0].get("uvi")

    pop = 0.0
    if hourly:
        pop = max(hour.get("pop", 0.0) for hour in hourly[:12])

    return {
        "temperature": current.get("temp"),
        "feels_like": current.get("feels_like"),
        "humidity": current.get("humidity"),
        "cloudiness": current.get("clouds"),
        "max_uv_index": max_uv_index,
        "pop": pop,
        "wind_speed": current.get("wind_speed"),
        "description": data["current"]["weather"][0]["description"],
        "sunset": current.get("sunset")

    }


def create_weather_log(db: Session, user_id: int, city: str):
    log.info(f"Creando weather log para user_id={user_id}, ciudad={city}")
    coords = get_coordinates(city)
    weather_data = get_weather_data(coords["lat"], coords["lon"])

    weather_log = WeatherLog(
        user_id=user_id, 
        temperature=weather_data["temperature"],
        feels_like=weather_data["feels_like"],
        humidity=weather_data["humidity"],
        cloudiness=weather_data["cloudiness"],
        max_uv_index=weather_data["max_uv_index"],
        pop=weather_data["pop"],
        wind_speed=weather_data["wind_speed"],
        description=weather_data["description"],
        sunset=weather_data["sunset"]
    )
    

    db.add(weather_log)
    db.commit()
    db.refresh(weather_log)

    arg_tz = timezone(timedelta(hours=-3))

    local_checked_at = weather_log.checked_at.replace( tzinfo=timezone.utc).astimezone(arg_tz)
    return {
        "id": weather_log.id,
        "city": coords["name"],
        "temperature": weather_log.temperature,
        "feels_like": weather_log.feels_like,
        "humidity": weather_log.humidity,
        "cloudiness": weather_log.cloudiness,
        "max_uv_index": weather_log.max_uv_index,
        "pop": weather_log.pop,
        "wind_speed": weather_log.wind_speed,
        "sunset": weather_log.sunset,
        "description": weather_log.description,
        "checked_at": local_checked_at.isoformat()
        

    }