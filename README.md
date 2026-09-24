# Real-Time Structured Weather Agent

A deterministic weather extraction and verification agent built with Python, Pydantic, Instructor, and Open-Meteo. 

The agent transforms unstructured, conversational user queries into type-safe database models, calls real-time weather endpoints, and asserts physical invariants before downstream ingestion.

---

## Prerequisites & API Key Configuration

> **Note**: This project requires an **OpenAI API key** to run the structured extraction engine. The weather telemetry is powered by Open-Meteo, which requires no external weather API key.

1. **Clone the repository:**
```bash
git clone [https://github.com/your-username/weather-structured-agent.git](https://github.com/your-username/weather-structured-agent.git)
cd weather-structured-agent

```

2. **Configure your environment:**
Copy the example environment file:
```bash
cp .env.example .env

```

3. **Add your API key:**
Open `.env` and set your key:
```env
OPENAI_API_KEY=your_actual_openai_api_key_here

```

*(Never commit your `.env` file to version control. It is ignored by default in `.gitignore`.)*

---

## Technical Architecture

1. **Intent Extraction**: User prompts (e.g., *"How's the humidity in Tokyo right now in Celsius?"*) are extracted into a `WeatherQueryIntent` model using `instructor`.
2. **Auto-Retry & Validation**: Enforces schema rules (e.g., string trimming, title capitalization, strict temperature units).
3. **Live Telemetry Ingestion**: Queries Open-Meteo for real-time atmospheric data.
4. **Invariant Enforcement**: Validates that physical metrics conform to realistic Earth bounds (humidity $0\text{--}100\%$, valid temperature ranges, geographical coordinates).

---

## Benchmarking: Normal vs. Structured

| Feature | Normal Output | Structured Agent |
| --- | --- | --- |
| **Format** | Conversational prose | Strictly typed Pydantic object |
| **Parsing Safety** | Requires fragile regex | Native direct attribute access |
| **Physical Invariants** | Unchecked API payloads | Bounded field constraints (`ge`, `le`) |
| **Downstream Ingestion** | High risk of parsing failure | Direct serialization to JSON/SQL |

---

## Installation & Running

```bash
# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -e .

# Run test suite
pytest tests/

# Run the comparative benchmark
python run_comparison.py
```
