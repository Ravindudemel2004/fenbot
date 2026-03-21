import os, re, requests
from urllib.parse import quote
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes, CommandHandler

# ✅ Use environment variable KEY (not the token itself)
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

def extract_fen(text):
    match = re.search(r'[rnbqkpRNBQKP1-8/]+(?:\s+[a-zA-Z0-9-]+)*', text)
    return match.group(0).strip() if match else None

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    fen = extract_fen(update.message.text)
    if not fen:
        await update.message.reply_text(
            "❌ Send a valid FEN.\nExample: `rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1`",
            parse_mode="Markdown"
        )
        return
    
    # ✅ URL encode + no extra spaces
    safe_fen = quote(fen, safe='')
    img_url = f"https://fen2image.chessvision.ai/{safe_fen}?pov=white"
    
    try:
        img_data = requests.get(img_url, timeout=15).content
        await update.message.reply_photo(photo=img_data, caption="♟️ Generated")
    except Exception as e:
        await update.message.reply_text(f"⚠️ Error: {str(e)[:200]}")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "♟️ **Chess FEN Bot**\n\nSend me any FEN string and I'll generate a board image!\n\nExample:\n`rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq e3 0 1`",
        parse_mode="Markdown"
    )

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_handler(CommandHandler("start", start))
    
    print("🤖 Bot starting with polling...")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()