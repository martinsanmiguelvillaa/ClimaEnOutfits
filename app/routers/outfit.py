import os
import requests
from types import SimpleNamespace
from fastapi import APIRouter, HTTPException, Request
from app.limiter import limiter
from app.services.weather import get_weather_data, get_coordinates
from app.services.outfit import get_outfit_recommendation
from app.schemas.outfit import OutfitResponse

router = APIRouter(tags=["outfit"])


generic_user = SimpleNamespace(gender=None)


def _validate_coordinates(lat: float, lon: float):
    if not (-90 <= lat <= 90) or not (-180 <= lon <= 180):
        raise HTTPException(status_code=400, detail="Coordenadas inválidas")


@router.get("/location", response_model=OutfitResponse)
@limiter.limit("10/minute")
def read_outfit_by_location(request: Request, lat: float, lon: float):
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
    return get_outfit_recommendation(weather, generic_user)


@router.get("/{city}", response_model=OutfitResponse)
@limiter.limit("10/minute")
def read_outfit(request: Request, city: str):
    coords = get_coordinates(city)
    weather = get_weather_data(coords["lat"], coords["lon"])
    weather["city"] = coords["name"]
    return get_outfit_recommendation(weather, generic_user)
