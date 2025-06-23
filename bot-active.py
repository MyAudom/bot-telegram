import os
import yt_dlp
import logging
import asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
from datetime import datetime

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
BOT_TOKEN = "8100671655:AAFd7yq0UE3nrxxhSnx0fhfMqwzrBBX2HJo"
DOWNLOAD_DIR = "downloads"

# Function: Download with yt-dlp
def download_video(url: str):
    if not os.path.exists(DOWNLOAD_DIR):
        os.makedirs(DOWNLOAD_DIR)

    ydl_opts = {
        'format': 'bestvideo[height<=1080][ext=mp4]+bestaudio[ext=m4a]/best[height<=1080][ext=mp4]',
        'outtmpl': 'downloads/%(title)s.%(ext)s',
        'noplaylist': True,
        'merge_output_format': 'mp4',
        'ffmpeg_location': 'ffmpeg',
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        filename = ydl.prepare_filename(info)
        if not filename.endswith(".mp4"):
            filename = filename.rsplit(".", 1)[0] + ".mp4"
        return filename, info

# /start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 សួស្តី! សូមផ្ញើ Link YouTube ឬ Facebook មកខ្ញុំ ដើម្បីទាញយកវីដេអូ។")

# Message handler
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text.strip()
    status_msg = await update.message.reply_text("⏳ កំពុងទាញយកវីដេអូ...")

    try:
        original_path, info = download_video(url)
        file_size = os.path.getsize(original_path)

        # Prepare metadata
        title = info.get('title', 'N/A')
        video_id = info.get('id', 'N/A')
        uploader = info.get('uploader', 'N/A')
        account_name = update.message.from_user.full_name
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        caption = (
            f"*🧾Tittle* : {title}\n"
            f"*🆔ID* : {video_id}\n"
            f"*📛Page Name* : {uploader}\n"
            f"*⬇️Download By* : Telegram Bot\n"
            f"*🕰Time* : {current_time}\n"
            f"*✅Account Name* : {account_name}"
        )

        if file_size > 50 * 1024 * 1024:
            error_msg = await update.message.reply_text("❌ មិនអាចទាញយកឬបញ្ចូនវីដេអូបានទេ។")
            try:
                await context.bot.delete_message(chat_id=status_msg.chat_id, message_id=status_msg.message_id)
                await context.bot.delete_message(chat_id=error_msg.chat_id, message_id=error_msg.message_id)
            except Exception as e:
                logger.warning(f"Could not delete message: {e}")
            return
        else:
            sending_msg = await update.message.reply_text("⏳ កំពុងផ្ញើវីដេអូ...")

            with open(original_path, "rb") as video_file:
                sent_msg = await update.message.reply_video(video=video_file, caption=caption, parse_mode='Markdown')

            # Give some time before deleting the messages
            await asyncio.sleep(1)

            try:
                await context.bot.delete_message(chat_id=status_msg.chat_id, message_id=status_msg.message_id)
                await context.bot.delete_message(chat_id=sending_msg.chat_id, message_id=sending_msg.message_id)
            except Exception as e:
                logger.warning(f"Could not delete message: {e}")

            await update.message.reply_text("✅ ទាញយក និងផ្ញើវីដេអូបានជោគជ័យ!")

            try:
                os.remove(original_path)
            except Exception as e:
                logger.warning(f"Could not delete video file: {e}")

    except Exception as e:
        logger.error(f"Error: {e}")
        error_msg = await update.message.reply_text("❌ មិនអាចទាញយកឬបញ្ចូនវីដេអូបានទេ។")
        try:
            await context.bot.delete_message(chat_id=status_msg.chat_id, message_id=status_msg.message_id)
            await context.bot.delete_message(chat_id=error_msg.chat_id, message_id=error_msg.message_id)
        except Exception as e:
            logger.warning(f"Could not delete message: {e}")
          

# Main function
def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print("✅ Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
