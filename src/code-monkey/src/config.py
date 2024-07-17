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

# Prompt Design
SYSTEM_PROMPT = """
1. Your max_tokens are {MAX_TOKENS}. If any assistant message might exceed the token limit, don't try and respond negatively with an explanation instead.
2. Prefix negative responses with "❌". Prefix responses that indicate a significant success with "✅". Don't prefix neutral responses.
3. Use tools only if necessary.
4. Prefer using replace_in_file over write_file.
5. Don't make white-space-only changes to files.
6. If you have low confidence in a response or don't understand an instruction, explain why and use the ask_user tool to gather clarifications.
"""

if not OPENAI_API_KEY or not ANTHROPIC_API_KEY:
    raise ValueError(
        "API keys not found. Please check your .env and .secret.env files."
    )
