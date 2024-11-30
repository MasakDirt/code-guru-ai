import os

from dotenv import load_dotenv


load_dotenv()

# Environment
GITHUB_API_TOKEN = os.getenv("GITHUB_API_TOKEN")
CHATGPT_API_TOKEN = os.getenv("CHATGPT_API_TOKEN")
REDIS_HOST = os.getenv("REDIS_HOST")
REDIS_PORT = os.getenv("REDIS_PORT")

# Validation
CANDIDATE_LEVELS = ("Junior", "Middle", "Senior")
