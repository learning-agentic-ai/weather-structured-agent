import httpx
from typing import Dict, Any

WMO_CODE_MAP: Dict[int, str] = {
    0: "Clear sky",
    1: "Mainly clear",
    2: "Partly cloudy",
    3: "Overcast",
    45: "Fog",
    48: "Depositing rime fog",
    51: "Light drizzle",
    61: "Slight rain",
    63: "Moderate rain",
    65: "Heavy rain",
    71: "Slight snow",
    75: "Heavy snow",
    95: "Thunderstorm",
}


class OpenMeteoService:
    def __init__(self, timeout: float = 10.0):
        self.client = httpx.Client(timeout=timeout)

    def fetch_current_weather(self, city: str, unit: str = "celsius") -> Dict[str, Any]:
        """Resolves coordinates and fetches current weather telemetry."""
        # 1. Geocode city name
        geo_url = "https://geocoding-api.open-meteo.com/v1/search"
        geo_resp = self.client.get(
            geo_url, 
            params={"name": city, "count": 1, "language": "en", "format": "json"}
        ).json()

        if not geo_resp.get("results"):
            raise ValueError(f"Could not resolve geocoding coordinates for '{city}'")

        location = geo_resp["results"][0]
        lat, lon = location["latitude"], location["longitude"]

        # 2. Fetch current forecast
        forecast_url = "https://api.open-meteo.com/v1/forecast"
        params = {
            "latitude": lat,
            "longitude": lon,
            "current": "temperature_2m,relative_humidity_2m,weather_code,wind_speed_10m",
            "temperature_unit": unit,
        }
        raw_weather = self.client.get(forecast_url, params=params).json()
        current = raw_weather.get("current", {})

        return {
            "city_name": location.get("name", city),
            "country": location.get("country", "Unknown"),
            "latitude": lat,
            "longitude": lon,
            "timestamp": current.get("time", ""),
            "temperature": current.get("temperature_2m"),
            "temperature_unit": unit,
            "humidity": current.get("relative_humidity_2m"),
            "wind_speed_kmh": current.get("wind_speed_10m"),
            "condition": WMO_CODE_MAP.get(current.get("weather_code", 0), "Unknown"),
        }
