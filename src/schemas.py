from datetime import datetime
from typing import Literal, Optional
from pydantic import BaseModel, Field, field_validator


class WeatherQueryIntent(BaseModel):
    """Schema for extracting validated user query parameters."""
    city: str = Field(description="Target city name extracted from user prompt")
    unit: Literal["celsius", "fahrenheit"] = Field(
        default="celsius",
        description="Standardized temperature measurement unit"
    )

    @field_validator("city")
    @classmethod
    def clean_city(cls, val: str) -> str:
        cleaned = val.strip().title()
        if not cleaned:
            raise ValueError("City name cannot be empty")
        return cleaned


class LiveWeatherReport(BaseModel):
    """Domain model validating live external API data with physical boundary assertions."""
    city_name: str
    country: str
    latitude: float = Field(..., ge=-90.0, le=90.0)
    longitude: float = Field(..., ge=-180.0, le=180.0)
    timestamp: str
    temperature: float = Field(..., ge=-90.0, le=60.0, description="Valid surface temperature bound")
    temperature_unit: Literal["celsius", "fahrenheit"]
    humidity: int = Field(..., ge=0, le=100, description="Relative humidity percentage")
    wind_speed_kmh: float = Field(..., ge=0.0, description="Surface wind speed in km/h")
    condition: str
