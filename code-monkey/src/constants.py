import os
from dotenv import load_dotenv

this_dir = os.path.dirname(os.path.abspath(__file__))

src_root_dir = os.path.abspath(os.path.join(this_dir, "../.."))
artifacts_dir = os.path.abspath(os.path.join(src_root_dir, "artifacts"))

def get_src_dir():
   return src_root_dir

def get_artifacts_dir():
    return artifacts_dir

def load_environment():
  # Load environment variables from .env and .secret.env
  load_dotenv()
  load_dotenv(".env.secret")

# Claude rate limit
CLAUDE_RATE_LIMIT = 40000  # tokens per minute
