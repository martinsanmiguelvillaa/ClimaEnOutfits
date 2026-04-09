from pydantic import BaseModel

class WeatherResponse(BaseModel):
    city: str
    temperature: float
    feels_like: float
    humidity: int
    cloudiness: int
    max_uv_index: float | None = None
    pop: float
    wind_speed: float
    description: str
    sunset: int
    checked_at: str