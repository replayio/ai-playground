import os
from dotenv import load_dotenv

src_dir = os.path.dirname(os.path.abspath(__file__))
artifacts_dir = os.path.join(src_dir, "..", "artifacts")

# def load_environment():
# Load environment variables from .env and .secret.env
load_dotenv()
if not load_dotenv(".env.secret"):
    raise FileNotFoundError(".env.secret not found in cwd. Some features may not work correctly.")

# Load API keys
global OPENAI_API_KEY, ANTHROPIC_API_KEY, MAX_TOKENS
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
MAX_TOKENS = int(os.getenv("MAX_TOKENS") or 1000)

# # These variables will be populated when load_environment() is called
# OPENAI_API_KEY = None
# ANTHROPIC_API_KEY = None
# MAX_TOKENS = None

# Prompt Design
SYSTEM_PROMPT = """
1. You are "Code Monkey", a programming agent who tries to help comprehend and fix programming problems.
2. Prefix negative responses with "❌". Prefix responses that indicate a significant success with "✅". Don't prefix neutral responses.
3. Use tools only if necessary.
4. Prefer using replace_in_file over write_file.
5. Don't make white-space-only changes to files.
6. If you have low confidence in a response or don't understand an instruction, explain why and use the ask_user tool to gather clarifications.
7. Don't retry failed commands.
8. Don't suppress Exceptions.
"""

# Claude rate limit
CLAUDE_RATE_LIMIT = 40000  # tokens per minute
