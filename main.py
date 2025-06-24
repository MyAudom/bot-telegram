import os
import pytesseract
from PIL import Image
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, CommandHandler, ContextTypes, filters

# Set this only if you're on Windows
# pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# Configure languages (English and Khmer)
OCR_LANGUAGES = 'eng+khm'

# Start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("📷 Please send me an image, and I will extract the text (English/Khmer).")

# Handle image
async def handle_image(update: Update, context: ContextTypes.DEFAULT_TYPE):
    photo = update.message.photo[-1]
    file = await photo.get_file()
    image_path = f"{file.file_id}.jpg"
    await file.download_to_drive(image_path)

    # OCR
    try:
        text = pytesseract.image_to_string(Image.open(image_path), lang=OCR_LANGUAGES)
        if text.strip():
            await update.message.reply_text(f"📝 Extracted Text:\n\n{text}")
        else:
            await update.message.reply_text("❌ No text found.")
    except Exception as e:
        await update.message.reply_text(f"⚠️ Error: {str(e)}")
    finally:
        os.remove(image_path)

# Main
def main():
    BOT_TOKEN = "7963297442:AAGmHvFOGekXBhGeSzFPscjCOvo0f3K7XG8"

    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.PHOTO, handle_image))

    print("✅ Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
