import os
from dataclasses import dataclass
from pathlib import Path
from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(PROJECT_ROOT / ".env")

@dataclass(frozen=True)
class Settings:
    bot_token: str
    database_path: str
    log_level: str

def load_settings() -> Settings:
    token = os.getenv("BOT_TOKEN", "").strip()
    if not token or token == "PUT_YOUR_TELEGRAM_BOT_TOKEN_HERE":
        raise RuntimeError(
            "توکن ربات تنظیم نشده است. فایل .env را بسازید و BOT_TOKEN را وارد کنید."
        )
    db_path = os.getenv("DATABASE_PATH", "languagechain.db").strip()
    if not Path(db_path).is_absolute():
        db_path = str(PROJECT_ROOT / db_path)
    return Settings(
        bot_token=token,
        database_path=db_path,
        log_level=os.getenv("LOG_LEVEL", "INFO").upper(),
    )
