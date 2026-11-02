import asyncio
import hmac
import json
import logging
import os
from http.server import BaseHTTPRequestHandler

from telegram import Update
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    MessageHandler,
    filters,
)

from app.config import load_settings
from app.database.db import Database
from app.database.repository import Repository
from app.database.persistence import PostgresPersistence
from app.logging_setup import setup_logging
from app.bot.handlers import (
    start,
    help_command,
    groups_command,
    join_command,
    callback_handler,
    conversation_message,
    cancel_command,
    error_handler,
)


logger = logging.getLogger("languagechain.webhook")


async def process_telegram_update(payload: dict) -> None:
    settings = load_settings()

    if settings.database_backend != "postgres":
        raise RuntimeError("Webhook requires PostgreSQL backend.")

    db = Database(settings.database_path, settings.database_url)
    db.initialize()
    repo = Repository(db)

    persistence = PostgresPersistence(settings.database_url)

    application = (
        Application.builder()
        .token(settings.bot_token)
        .persistence(persistence)
        .build()
    )

    application.bot_data["repo"] = repo

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("groups", groups_command))
    application.add_handler(CommandHandler("join", join_command))
    application.add_handler(CommandHandler("cancel", cancel_command))
    application.add_handler(CallbackQueryHandler(callback_handler))
    application.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, conversation_message)
    )
    application.add_error_handler(error_handler)

    try:
        await application.initialize()

        update = Update.de_json(payload, application.bot)
        await application.process_update(update)

        # ذخیره فوری وضعیت کاربر، پیش از پایان درخواست Vercel
        await application.update_persistence()

    finally:
        if application.running:
            await application.stop()

        await application.shutdown()


class handler(BaseHTTPRequestHandler):

    def send_text(self, status: int, message: str) -> None:
        body = message.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        self.send_text(200, "LanguageChain webhook is running.")

    def do_POST(self):
        settings_secret = os.getenv("WEBHOOK_SECRET", "").strip()
        request_secret = self.headers.get(
            "X-Telegram-Bot-Api-Secret-Token", ""
        )

        if not settings_secret:
            self.send_text(500, "Webhook secret is not configured.")
            return

        if not hmac.compare_digest(request_secret, settings_secret):
            self.send_text(403, "Forbidden.")
            return

        try:
            content_length = int(self.headers.get("Content-Length", "0"))

            if content_length <= 0 or content_length > 1_000_000:
                self.send_text(400, "Invalid request size.")
                return

            raw_body = self.rfile.read(content_length)
            payload = json.loads(raw_body.decode("utf-8"))

            if not isinstance(payload, dict):
                self.send_text(400, "Invalid update.")
                return

            setup_logging(os.getenv("LOG_LEVEL", "INFO").upper())

            asyncio.run(process_telegram_update(payload))

            self.send_text(200, "OK")

        except (ValueError, UnicodeDecodeError, json.JSONDecodeError):
            self.send_text(400, "Invalid JSON.")

        except Exception:
            logger.exception("Webhook update processing failed.")
            self.send_text(500, "Internal server error.")
