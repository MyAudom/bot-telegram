import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, ContextTypes, filters
from PIL import Image
import pytesseract
import os

TOKEN = '7580165032:AAHh1nT4CR_N7dW_FaqBDIAGMXmhFE_62QU'

logging.basicConfig(level=logging.INFO)

async def handle_image(update: Update, context: ContextTypes.DEFAULT_TYPE):
    photo = update.message.photo[-1]
    file = await photo.get_file()
    file_path = f"image_{update.message.message_id}.jpg"
    await file.download_to_drive(file_path)

    try:
        img = Image.open(file_path)
        text = pytesseract.image_to_string(img, lang='khm+eng')
        if text.strip():
            await update.message.reply_text("📝 OCR Text Detected:\n\n" + text)
        else:
            await update.message.reply_text("⚠️ Sorry, I couldn't detect any text.")
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {e}")
    finally:
        if os.path.exists(file_path):
            os.remove(file_path)

app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(MessageHandler(filters.PHOTO, handle_image))

if __name__ == '__main__':
    app.run_polling()
