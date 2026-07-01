from openai import OpenAI
from decouple import config
from src.db.data_base import get_daily_metrics

def run_executive_agent() -> str:
    metrics = get_daily_metrics()

    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=config("OPENROUTER_API_KEY")
    )

    response = client.chat.completions.create(
        model="poolside/laguna-xs.2:free",
        messages=[
            {
                "role": "system",
                "content": """You are an executive traffic analyst.
When you receive data from plate detection, generate:
- Executive summary in clear language for managers
- Peak hour identified
- Daily average of vehicles
- Evaluation of OCR quality (average confidence)
- Alert if there are anomalies"""
            },
            {
                "role": "user",
                "content": f"Analyze this data and generate the executive report:\n\n{metrics}"
            }
        ]
    )

    return response.choices[0].message.content