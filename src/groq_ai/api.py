from groq import Groq

from src.settings import GROQ_API_TOKEN


groq_api = Groq(api_key=GROQ_API_TOKEN)
