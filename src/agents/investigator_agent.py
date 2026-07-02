from openai import OpenAI
from decouple import config
from src.db.data_base import get_daily_metrics

def investigate() -> str:
    metrics = get_daily_metrics()

    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=config("OPENROUTER_API_KEY")
    )

    return response.choices[0].message.content