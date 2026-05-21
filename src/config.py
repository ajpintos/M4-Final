import os
from dotenv import load_dotenv

load_dotenv()

REQUIRED_VARS = [
    "OPENAI_API_KEY",
    "LANGFUSE_PUBLIC_KEY",
    "LANGFUSE_SECRET_KEY",
]


def validate_config() -> None:
    missing = [var for var in REQUIRED_VARS if not os.getenv(var)]
    if missing:
        raise EnvironmentError(
            f"Missing required environment variables: {', '.join(missing)}\n"
            f"Copy .env.example to .env and fill in your keys."
        )
