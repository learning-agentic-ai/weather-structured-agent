from src.agent import WeatherAgent

if __name__ == "__main__":
    agent = WeatherAgent()
    query = "Can you tell me the current weather and humidity in Tokyo in Celsius?"

    print("=" * 70)
    print(f"QUERY: \"{query}\"")
    print("=" * 70)

    print("\n--- 1. NORMAL UNSTRUCTURED OUTPUT ---")
    normal_result = agent.run_normal(query)
    print(normal_result)

    print("\n--- 2. STRUCTURED AGENT OUTPUT (Pydantic Model) ---")
    structured_result = agent.run_structured(query)
    print("Direct Property Access:")
    print(f"  • City:        {structured_result.city_name}, {structured_result.country}")
    print(f"  • Temperature: {structured_result.temperature}°{structured_result.temperature_unit[0].upper()}")
    print(f"  • Humidity:    {structured_result.humidity}%")
    print(f"  • Condition:   {structured_result.condition}")
    
    print("\nValidated JSON (Downstream API / Database Ready):")
    print(structured_result.model_dump_json(indent=2))
