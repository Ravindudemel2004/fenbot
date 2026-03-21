import os
import re
import requests
from urllib.parse import quote
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes

# 1. Load the token from .env file
load_dotenv()
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
API_URL = "https://fen2image.chessvision.ai/"

# 2. Function to extract FEN from user text
def extract_fen(text):
    # A FEN string usually has slashes '/' and spaces.
    # This regex looks for the chess board part (letters/numbers/slashes)
    match = re.search(r'[rnbqkpRNBQKP1-8/]+(?:\s+[a-zA-Z0-9-]+)*', text)
    if match:
        return match.group(0).strip()
    return None

# 3. The function that runs when someone sends a message
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    fen = extract_fen(user_text)

    # If no FEN found, tell the user
    if not fen:
        await update.message.reply_text(
            "❌ I couldn't find a valid FEN string.\n"
            "Please send something like:\n"
            "`rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1`",
            parse_mode="Markdown"
        )
        return

    # 4. Prepare the API URL
    # FEN contains slashes (/), which break URLs. We must encode them to %2F
    safe_fen = quote(fen, safe='')
    image_url = f"{API_URL}{safe_fen}?pov=white"

    try:
        # 5. Download the image from the chess engine
        response = requests.get(image_url, timeout=10)
        response.raise_for_status() # Check if download failed
        
        # 6. Send the image back to Telegram
        await update.message.reply_photo(
            photo=response.content, 
            caption=f"♟️ Position:\n`{fen}`",
            parse_mode="Markdown"
        )
    except Exception as e:
        await update.message.reply_text(f"⚠️ Error generating image: {str(e)}")

# 7. Start the Bot
def main():
    print("🤖 Bot is starting...")
    # Build the application with your token
    app = Application.builder().token(TOKEN).build()
    
    # Tell the bot: "When you get a text message, run handle_message"
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    # Start listening
    app.run_polling()

if __name__ == "__main__":
    main()