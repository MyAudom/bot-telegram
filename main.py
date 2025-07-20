import logging
from telegram.ext import Updater, MessageHandler, Filters
from telegram import Update
from telegram.ext.callbackcontext import CallbackContext
from PIL import Image
import pytesseract
import os

# Telegram bot token
TOKEN = '7580165032:AAHh1nT4CR_N7dW_FaqBDIAGMXmhFE_62QU'

logging.basicConfig(level=logging.INFO)

def start_bot():
    updater = Updater(token=TOKEN, use_context=True)
    dp = updater.dispatcher
    dp.add_handler(MessageHandler(Filters.photo, handle_image))
    updater.start_polling()
    updater.idle()

def handle_image(update: Update, context: CallbackContext):
    photo_file = update.message.photo[-1].get_file()
    image_path = f"image_{update.message.message_id}.jpg"
    photo_file.download(image_path)

    try:
        img = Image.open(image_path)
        text = pytesseract.image_to_string(img, lang='khm+eng')
        if text.strip():
            update.message.reply_text("📝 OCR Text Detected:\n\n" + text)
        else:
            update.message.reply_text("⚠️ Sorry, I couldn't detect any text.")
    except Exception as e:
        update.message.reply_text(f"❌ Error: {e}")
    finally:
        if os.path.exists(image_path):
            os.remove(image_path)

if __name__ == '__main__':
    start_bot()
