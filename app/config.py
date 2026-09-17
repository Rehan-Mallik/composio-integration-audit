import os

from dotenv import load_dotenv


load_dotenv()


COMPOSIO_API_KEY = os.getenv("COMPOSIO_API_KEY")


if not COMPOSIO_API_KEY:
    raise RuntimeError(
        "COMPOSIO_API_KEY is missing from .env"
    )
