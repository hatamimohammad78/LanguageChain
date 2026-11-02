import logging
from telegram.ext import Application, CallbackQueryHandler, CommandHandler, MessageHandler, filters
from app.config import load_settings
from app.database.db import Database
from app.database.repository import Repository
from app.logging_setup import setup_logging
from app.bot.handlers import start, help_command, groups_command, join_command, callback_handler, conversation_message, cancel_command, error_handler

def main():
    settings = load_settings()
    setup_logging(settings.log_level)
    log = logging.getLogger("languagechain")

    db = Database(settings.database_path, settings.database_url if settings.database_backend == "postgres" else "")
    db.initialize()
    repo = Repository(db)

    application = (
        Application.builder()
        .token(settings.bot_token)
        .build()
    )
    application.bot_data["repo"] = repo

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("groups", groups_command))
    application.add_handler(CommandHandler("join", join_command))
    application.add_handler(CommandHandler("cancel", cancel_command))
    application.add_handler(CallbackQueryHandler(callback_handler))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, conversation_message))
    application.add_error_handler(error_handler)

    log.info("LanguageChain is starting...")
    application.run_polling(allowed_updates=["message", "callback_query"])

if __name__ == "__main__":
    main()
