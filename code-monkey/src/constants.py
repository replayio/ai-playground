import os
from dotenv import load_dotenv


def get_src_dir():
    return os.path.dirname(os.path.abspath(__file__))


def get_root_dir():
    return os.path.abspath(os.path.join(get_src_dir(), "../.."))


def get_artifacts_dir():
    return os.path.abspath(os.path.join(get_root_dir(), "artifacts"))


def load_environment():
    # Load environment variables from .env and .secret.env
    load_dotenv()
    load_dotenv(".env.secret")


# Claude rate limit
CLAUDE_RATE_LIMIT = 40000  # tokens per minute
