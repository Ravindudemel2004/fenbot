from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters
import urllib.parse
import chess
import asyncio

BOT_TOKEN = '8614554986:AAF0nbOIBu4OE6fEwA8jVvfgB4h1LA-kjVI'

def fen_to_url(fen: str):
    encoded = urllib.parse.quote(fen)
    return f"https://fen2image.chessvision.ai/{encoded}"

async def start(update: Update, context):
    await update.message.reply_text(
        "Send me a FEN string and I will return a chessboard image."
    )

async def handle_fen(update: Update, context):
    fen = update.message.text.strip()

    try:
        url = fen_to_url(fen)

        # Send image directly via URL
        await update.message.reply_photo(photo=url)

    except Exception as e:
        await update.message.reply_text("Invalid FEN or error occurred.")

app = ApplicationBuilder().token(BOT_TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_fen))

app.run_polling()
def fen_to_url(fen):
    encoded = urllib.parse.quote(fen)
    return f"https://fen2image.chessvision.ai/{encoded}?turn=white&pov=white"

def is_valid_fen(fen):
    try:
        chess.Board(fen)
        return True
    except:
        return False
    


async def stop_bot(app):
    await asyncio.sleep(1200)  # 20 minutes
    await app.stop()

app = ApplicationBuilder().token(BOT_TOKEN).build()

# start stop timer
app.create_task(stop_bot(app))

app.run_polling()
