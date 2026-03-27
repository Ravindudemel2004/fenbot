"""Random FEN Telegram Bot - Commands Only"""
import os
import random
import logging
import urllib.parse
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from dotenv import load_dotenv

# Load token from .env or use default
load_dotenv()
BOT_TOKEN = os.getenv("TELEGRAM_TOKEN", "8614554986:AAF0nbOIBu4OE6fEwA8jVvfgB4h1LA-kjVI")

# Logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ============ CONFIG ============
FEN_FILE = "fens.txt"

# ============ HELPERS ============

def load_fens(filename: str) -> list:
    """Load FENs from file (one per line, skip comments)"""
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            fens = [line.strip() for line in f if line.strip() and not line.startswith('#')]
        logger.info(f"✅ Loaded {len(fens)} FENs")
        return fens
    except FileNotFoundError:
        logger.error(f"❌ File not found: {filename}")
        return []

def get_random_fen(fens: list) -> str:
    """Pick random FEN"""
    return random.choice(fens) if fens else None

def fen_to_url(fen: str, pov: str = 'white') -> str:
    """Build ChessVision.ai image URL"""
    encoded = urllib.parse.quote(fen.strip(), safe='')
    return f"https://fen2image.chessvision.ai/{encoded}?pov={pov}"

# ============ COMMANDS ============

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Welcome message"""
    await update.message.reply_text(
        "♟️ *Random FEN Bot*\n\n"
        "🎲 Commands:\n"
        "/random - Random position (White view)\n"
        "/random_black - Random position (Black view)\n"
        "/help - Show this message\n\n"
        "Powered by ChessVision.ai",
        parse_mode="Markdown"
    )

async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Help message"""
    await update.message.reply_text(
        "*Available Commands:*\n"
        "• `/random` — Get random chess diagram (White POV)\n"
        "• `/random_black` — Get random diagram (Black POV)\n"
        "• `/start` — Welcome message\n"
        "• `/help` — This message\n\n"
        "📁 FENs loaded from: `fens.txt`",
        parse_mode="Markdown"
    )

async def send_random(update: Update, context: ContextTypes.DEFAULT_TYPE, pov: str = 'white'):
    """Send random FEN image"""
    fens = load_fens(FEN_FILE)
    
    if not fens:
        await update.message.reply_text(
            "❌ No positions found.\n"
            f"Please add FENs to `{FEN_FILE}` (one per line)."
        )
        return
    
    fen = get_random_fen(fens)
    url = fen_to_url(fen, pov=pov)
    
    # Get turn from FEN for caption
    parts = fen.split()
    turn = "White" if len(parts) > 1 and parts[1] == 'w' else "Black"
    piece = "♙" if turn == "White" else "♟"
    
    try:
        await update.message.reply_photo(
            photo=url,
            caption=f"🎲 Random Position ({pov.capitalize()} view)\n\n"
                   f"{piece} {turn} to play\n\n"
                   f"```\n{fen}\n```",
            parse_mode="Markdown"
        )
        logger.info(f"📤 Sent: {fen[:40]}...")
    except Exception as e:
        logger.error(f"❌ Error: {e}")
        await update.message.reply_text("❌ Failed to generate image. Try /random again!")

async def random_white(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await send_random(update, context, pov='white')

async def random_black(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await send_random(update, context, pov='black')

# ============ IGNORE NON-COMMAND MESSAGES ============

async def ignore_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Reply to non-command messages with hint"""
    await update.message.reply_text(
        "🤖 I only respond to commands!\n\n"
        "Try:\n"
        "/random — Get a random position\n"
        "/help — See all commands",
        parse_mode="Markdown"
    )

# ============ MAIN ============

def main():
    print("🤖 Random FEN Bot (Commands Only) starting...")
    logger.info("Bot initializing...")
    
    # Build app
    app = Application.builder().token(BOT_TOKEN).build()
    
    # Register ONLY command handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_cmd))
    app.add_handler(CommandHandler("random", random_white))
    app.add_handler(CommandHandler("random_black", random_black))
    
    # Optional: Reply to non-command messages
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, ignore_message))
    
    print("✅ Bot running! Use /random to get started ♟️")
    logger.info("Bot started")
    
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
