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
    def __init__(self, model: str = "openai/gpt-4o-mini"):
        # Retrieve OpenRouter key
        api_key = os.getenv("OPENROUTER_API_KEY") # or os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise EnvironmentError("OPENROUTER_API_KEY is missing from environment.")

        # 1. Direct standard OpenAI client to OpenRouter endpoint
        self.raw_client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=api_key,
            default_headers={
                "HTTP-Referer": "http://localhost:3000", # Required by OpenRouter for ranking
                "X-Title": "Weather Structured Agent",
            }
        )

        # 2. Patch using instructor with MD_JSON mode for cross-provider compatibility
        self.instructor_client = instructor.from_openai(
            self.raw_client,
            mode=instructor.Mode.MD_JSON
        )
        self.model = model
        self.service = OpenMeteoService()

    def run_normal(self, prompt: str) -> str:
        """Unstructured text response generation via OpenRouter."""
        extract_res = self.raw_client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": "Extract only the city name from the prompt. Respond with strictly the city name and nothing else."
                },
                {"role": "user", "content": prompt}
            ],
            temperature=0.0
        ).choices[0].message.content.strip()

        # Fetch live data from Open-Meteo
        raw_data = self.service.fetch_current_weather(extract_res)

        # Conversational summary
        summary = self.raw_client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": "Write a conversational weather report using the following JSON payload."
                },
                {"role": "user", "content": str(raw_data)}
            ],
            temperature=0.7
        ).choices[0].message.content
        return summary

    def run_structured(self, prompt: str, max_retries: int = 3) -> LiveWeatherReport:
        """Deterministic extraction and Pydantic model validation via OpenRouter."""
        logger.info("Executing structured extraction for prompt: {}", prompt)

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

        telemetry = self.service.fetch_current_weather(city=intent.city, unit=intent.unit)
        report = LiveWeatherReport(**telemetry)
        logger.info("Successfully validated weather report for: {}", report.city_name)
        return report
