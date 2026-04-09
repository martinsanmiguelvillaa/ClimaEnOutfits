import os
import requests
from fastapi import APIRouter, HTTPException
from app.services.weather import get_weather_data, get_coordinates

router = APIRouter(tags=["weather"])


def _validate_coordinates(lat: float, lon: float):
    if not (-90 <= lat <= 90) or not (-180 <= lon <= 180):
        raise HTTPException(status_code=400, detail="Coordenadas inválidas")


@router.get("/location")
def read_weather_by_location(lat: float, lon: float):
    _validate_coordinates(lat, lon)
    res = requests.get(
        "https://api.openweathermap.org/geo/1.0/reverse",
        params={"lat": lat, "lon": lon, "limit": 1, "appid": os.getenv("OPENWEATHER_API_KEY")}
    )
    res.raise_for_status()
    geo = res.json()
    city_name = (geo[0].get("local_names", {}).get("es") or geo[0]["name"]) if geo else "Tu ubicación"

    weather = get_weather_data(lat, lon)
    weather["city"] = city_name
    return weather


@router.get("/{city}")
def read_weather(city: str):
    coords = get_coordinates(city)
    return get_weather_data(coords["lat"], coords["lon"])