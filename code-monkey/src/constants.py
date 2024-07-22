import os
from dotenv import load_dotenv

src_dir = os.path.dirname(os.path.abspath(__file__))
artifacts_dir = os.path.join(src_dir, "..", "artifacts")

def get_artifacts_dir():
    return artifacts_dir

def load_environment():
  # Load environment variables from .env and .secret.env
  load_dotenv()
  load_dotenv(".env.secret")

# Claude rate limit
CLAUDE_RATE_LIMIT = 40000  # tokens per minute
