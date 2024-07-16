import os
from dotenv import load_dotenv

# Load environment variables from .env and .secret.env
load_dotenv()
if not load_dotenv(".env.secret"):
    raise Exception(".env.secret not found in cwd")

# Load API keys
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
MAX_TOKENS = int(os.getenv("MAX_TOKENS")) or 1000

if not OPENAI_API_KEY or not ANTHROPIC_API_KEY:
    raise ValueError(
        "API keys not found. Please check your .env and .secret.env files."
    )