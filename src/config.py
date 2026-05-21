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
            f"Variables de entorno faltantes: {', '.join(missing)}\n"
            f"Copiá .env.example a .env y completá tus claves."
        )
