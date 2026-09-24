import pytest
from pydantic import ValidationError
from src.schemas import WeatherQueryIntent, LiveWeatherReport


def test_city_normalization():
    intent = WeatherQueryIntent(city="  los angeles  ", unit="fahrenheit")
    assert intent.city == "Los Angeles"
    assert intent.unit == "fahrenheit"


def test_invalid_temperature_bounds():
    """Verify that values outside Earth temperature limits are rejected."""
    with pytest.raises(ValidationError):
        LiveWeatherReport(
            city_name="Paris",
            country="France",
            latitude=48.85,
            longitude=2.35,
            timestamp="2026-09-24T12:00",
            temperature=120.5,  # Exceeds max bound of 60.0°C
            temperature_unit="celsius",
            humidity=40,
            wind_speed_kmh=12.0,
            condition="Sunny",
        )


def test_invalid_humidity_percentage():
    """Verify humidity must be between 0 and 100."""
    with pytest.raises(ValidationError):
        LiveWeatherReport(
            city_name="Berlin",
            country="Germany",
            latitude=52.52,
            longitude=13.41,
            timestamp="2026-09-24T12:00",
            temperature=18.0,
            temperature_unit="celsius",
            humidity=110,  # Exceeds max 100%
            wind_speed_kmh=5.0,
            condition="Cloudy",
        )
