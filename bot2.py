import os
import base64
import logging
import requests
from telegram import Update, File
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

OLLAMA_URL = "http://localhost:11434/api/generate"
TELEGRAM_TOKEN = "YOUR_TELEGRAM_BOT_TOKEN"
MODEL_NAME = "llava"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.info(f"Користувач {update.message.chat.id} запустив команду /start")
    await update.message.reply_text("Привіт! Надішли мені зображення, і я його опишу 😎")

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        photo = update.message.photo[-1]
        file: File = await context.bot.get_file(photo.file_id)
        file_path = f"temp_{update.message.chat.id}.jpg"
        await file.download_to_drive(file_path)

        with open(file_path, "rb") as img_file:
            image_base64 = base64.b64encode(img_file.read()).decode("utf-8")

        payload = {
            "model": MODEL_NAME,
            "prompt": "Опиши це зображення максимально точно і з гумором.",
            "stream": False,
            "images": [image_base64]
        }

        response = requests.post(OLLAMA_URL, json=payload)
        response.raise_for_status()
        result = response.json().get("response", "Не вдалося отримати відповідь.")
        await update.message.reply_text(result)

    except Exception as e:
        logger.error(f"Помилка при обробці зображення: {e}")
        await update.message.reply_text("Сталася помилка при обробці зображення 🫤")

    finally:
        if os.path.exists(file_path):
            os.remove(file_path)

if __name__ == "__main__":
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    app.run_polling()
