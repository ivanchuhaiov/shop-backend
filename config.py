from dotenv import load_dotenv
import os

load_dotenv()

STRAPI_URL = os.getenv("STRAPI_URL", "http://localhost:1337")
STRAPI_TOKEN = os.getenv("STRAPI_TOKEN", "")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN", "")
CLAUDE_API_KEY = os.getenv("CLAUDE_API_KEY", "")