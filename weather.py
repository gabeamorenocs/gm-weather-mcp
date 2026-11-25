"""Shared weather fetch logic for both the MCP server and the HTTP UI."""

from typing import Any
import httpx

GEOCODE_URL = "https://geocoding-api.open-meteo.com/v1/search"
FORECAST_URL = "https://api.open-meteo.com/v1/forecast"

WEATHER_CODES = {
    0: "Clear sky", 1: "Mainly clear", 2: "Partly cloudy", 3: "Overcast",
    45: "Fog", 48: "Depositing rime fog",
    51: "Light drizzle", 53: "Moderate drizzle", 55: "Dense drizzle",
    61: "Slight rain", 63: "Moderate rain", 65: "Heavy rain",
    71: "Slight snow", 73: "Moderate snow", 75: "Heavy snow",
    77: "Snow grains",
    80: "Slight rain showers", 81: "Moderate rain showers", 82: "Violent rain showers",
    85: "Slight snow showers", 86: "Heavy snow showers",
    95: "Thunderstorm", 96: "Thunderstorm with slight hail", 99: "Thunderstorm with heavy hail",
}


async def _geocode(client: httpx.AsyncClient, location: str) -> dict[str, Any]:
    r = await client.get(GEOCODE_URL, params={"name": location, "count": 1})
    r.raise_for_status()
    results = r.json().get("results") or []
    if not results:
        raise ValueError(f"No location found for {location!r}")
    return results[0]


async def current_weather(location: str, units: str = "imperial") -> dict[str, Any]:
    metric = units == "metric"
    async with httpx.AsyncClient(timeout=20) as client:
        place = await _geocode(client, location)
        r = await client.get(FORECAST_URL, params={
            "latitude": place["latitude"],
            "longitude": place["longitude"],
            "current": "temperature_2m,relative_humidity_2m,apparent_temperature,"
                       "wind_speed_10m,wind_direction_10m,weather_code,is_day",
            "temperature_unit": "celsius" if metric else "fahrenheit",
            "wind_speed_unit": "kmh" if metric else "mph",
            "timezone": "auto",
        })
        r.raise_for_status()
        cur = r.json()["current"]
        return {
            "place": {
                "name": place["name"],
                "admin1": place.get("admin1"),
                "country": place.get("country"),
                "country_code": place.get("country_code"),
                "latitude": place["latitude"],
                "longitude": place["longitude"],
            },
            "time": cur["time"],
            "temperature": cur["temperature_2m"],
            "feels_like": cur["apparent_temperature"],
            "humidity": cur["relative_humidity_2m"],
            "wind_speed": cur["wind_speed_10m"],
            "wind_direction": cur["wind_direction_10m"],
            "weather_code": cur["weather_code"],
            "conditions": WEATHER_CODES.get(cur["weather_code"], f"Code {cur['weather_code']}"),
            "is_day": bool(cur["is_day"]),
            "units": {
                "temperature": "°C" if metric else "°F",
                "wind": "km/h" if metric else "mph",
            },
        }


async def forecast(location: str, days: int = 5, units: str = "imperial") -> dict[str, Any]:
    days = max(1, min(days, 16))
    metric = units == "metric"
    async with httpx.AsyncClient(timeout=20) as client:
        place = await _geocode(client, location)
        r = await client.get(FORECAST_URL, params={
            "latitude": place["latitude"],
            "longitude": place["longitude"],
            "current": "temperature_2m,relative_humidity_2m,apparent_temperature,"
                       "wind_speed_10m,wind_direction_10m,weather_code,is_day",
            "daily": "weather_code,temperature_2m_max,temperature_2m_min,"
                     "precipitation_sum,precipitation_probability_max,wind_speed_10m_max",
            "forecast_days": days,
            "temperature_unit": "celsius" if metric else "fahrenheit",
            "wind_speed_unit": "kmh" if metric else "mph",
            "timezone": "auto",
        })
        r.raise_for_status()
        j = r.json()
        cur = j["current"]
        d = j["daily"]
        return {
            "place": {
                "name": place["name"],
                "admin1": place.get("admin1"),
                "country": place.get("country"),
                "country_code": place.get("country_code"),
                "latitude": place["latitude"],
                "longitude": place["longitude"],
            },
            "current": {
                "time": cur["time"],
                "temperature": cur["temperature_2m"],
                "feels_like": cur["apparent_temperature"],
                "humidity": cur["relative_humidity_2m"],
                "wind_speed": cur["wind_speed_10m"],
                "wind_direction": cur["wind_direction_10m"],
                "weather_code": cur["weather_code"],
                "conditions": WEATHER_CODES.get(cur["weather_code"], f"Code {cur['weather_code']}"),
                "is_day": bool(cur["is_day"]),
            },
            "daily": [
                {
                    "date": d["time"][i],
                    "weather_code": d["weather_code"][i],
                    "conditions": WEATHER_CODES.get(d["weather_code"][i], f"Code {d['weather_code'][i]}"),
                    "temp_min": d["temperature_2m_min"][i],
                    "temp_max": d["temperature_2m_max"][i],
                    "precipitation_mm": d["precipitation_sum"][i],
                    "precipitation_pct": d["precipitation_probability_max"][i],
                    "wind_max": d["wind_speed_10m_max"][i],
                }
                for i in range(len(d["time"]))
            ],
            "units": {
                "temperature": "°C" if metric else "°F",
                "wind": "km/h" if metric else "mph",
            },
        }
