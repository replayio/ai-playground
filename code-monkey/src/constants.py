import os
from dotenv import load_dotenv

src_dir = os.path.dirname(os.path.abspath(__file__))
artifacts_dir = os.path.join(src_dir, "..", "artifacts")

# def load_environment():
# Load environment variables from .env and .secret.env
load_dotenv()
load_dotenv(".env.secret")

# Load API keys
# OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
MAX_TOKENS = int(os.getenv("MAX_TOKENS") or 1000)

# Prompt Design

# Claude rate limit
CLAUDE_RATE_LIMIT = 40000  # tokens per minute
