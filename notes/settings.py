import os
from pathlib import Path

from dotenv import load_dotenv

from notes.utils import setup_logging

LOG_FILE = Path(__file__).resolve().parent.parent / "notes.log"

load_dotenv(override=True)

NOTION_VERSION = "2025-09-03"
NOTION_BASE_URL = "https://api.notion.com/v1"
NOTION_CLIENT_TIMEOUT = 10.0  # sec
NOTION_SECRET = os.getenv("NOTION_SECRET")
NOTION_DB_ID = os.getenv("NOTION_DB_ID")

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_BOT_OWNER_ID = os.getenv("TELEGRAM_BOT_OWNER_ID")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
TELEGRAM_ALLOWED_USER_IDS_RAW = os.getenv("TELEGRAM_ALLOWED_USER_IDS", "")
TELEGRAM_ALLOWED_USER_IDS = TELEGRAM_ALLOWED_USER_IDS_RAW.split()


WORKERS_COUNT = 1
QUEUE_MAXSIZE = 50

global_logger, logger_tg, logger_notion = setup_logging(LOG_FILE)


def _validate_settings() -> None:
    missing = []
    if not NOTION_SECRET:
        missing.append("NOTION_SECRET")
    if not NOTION_DB_ID:
        missing.append("NOTION_DB_ID")
    if not TELEGRAM_BOT_TOKEN:
        missing.append("TELEGRAM_BOT_TOKEN")

    if missing:
        raise ValueError(
            f"Missing required environment variables: {', '.join(missing)}"
        )

    if not TELEGRAM_ALLOWED_USER_IDS:
        raise ValueError("TELEGRAM_ALLOWED_USER_IDS is empty.")


_validate_settings()
