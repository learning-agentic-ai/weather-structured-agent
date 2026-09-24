import os
from typing import Optional
from dotenv import load_dotenv
from loguru import logger
import instructor
from openai import OpenAI

from src.schemas import WeatherQueryIntent, LiveWeatherReport
from src.service import OpenMeteoService

load_dotenv()
logger.add("weather_agent.log", rotation="2 MB", level="INFO")


class WeatherAgent:
    def __init__(self, model: str = "gpt-4o-mini"):
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise EnvironmentError("OPENAI_API_KEY environment variable is missing.")
        
        self.raw_client = OpenAI(api_key=api_key)
        self.instructor_client = instructor.from_openai(self.raw_client)
        self.model = model
        self.service = OpenMeteoService()

    def run_normal(self, prompt: str) -> str:
        """Unstructured text response generation."""
        # Simple extraction
        extract_res = self.raw_client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "Extract the city name only from the query."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.0
        ).choices[0].message.content.strip()

        # Fetch live data and ask LLM for unstructured summary
        raw_data = self.service.fetch_current_weather(extract_res)
        summary = self.raw_client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "Generate a conversational weather report based on this payload."},
                {"role": "user", "content": str(raw_data)}
            ],
            temperature=0.7
        ).choices[0].message.content
        return summary

    def run_structured(self, prompt: str, max_retries: int = 3) -> LiveWeatherReport:
        """Deterministic extraction and Pydantic model validation."""
        logger.info("Executing structured extraction for prompt: {}", prompt)

        # Extraction with Instructor auto-retry validation
        intent: WeatherQueryIntent = self.instructor_client.chat.completions.create(
            model=self.model,
            response_model=WeatherQueryIntent,
            max_retries=max_retries,
            messages=[
                {
                    "role": "system",
                    "content": "Extract target city and measurement unit (celsius or fahrenheit) from user prompt.",
                },
                {"role": "user", "content": prompt},
            ],
            temperature=0.0,
        )

        # Retrieve live external telemetry
        telemetry = self.service.fetch_current_weather(city=intent.city, unit=intent.unit)

        # Validate into domain model
        report = LiveWeatherReport(**telemetry)
        logger.info("Successfully validated weather report for: {}", report.city_name)
        return report
