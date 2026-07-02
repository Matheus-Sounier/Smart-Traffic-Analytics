from openai import OpenAI
from decouple import config
from src.db.data_base import get_daily_metrics

def investigate() -> str:
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
                "content": """You are an investigative traffic analyst.
When you receive data from plate detection, check:
- Anomalies in vehicle volumes
- Drops in OCR quality (confidence below expected)
- Unusual movement hours
- Possible reading or capture failures"""
            },
            {
                "role": "user",
                "content": f"Investigate this data and report anomalies found:\n\n{metrics}"
            }
        ]
    )

    return response.choices[0].message.content