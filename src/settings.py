import os

from dotenv import load_dotenv


load_dotenv()

GITHUB_API_TOKEN = os.getenv("GITHUB_API_TOKEN")
CHATGPT_API_TOKEN = os.getenv("CHATGPT_API_TOKEN")

CANDIDATE_LEVELS = ("Junior", "Middle", "Senior")
