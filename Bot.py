import os
import threading
from flask import Flask
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

TOKEN = os.environ.get("TELEGRAM_TOKEN")

# Servidor falso para que Render no lo apague
flask_app = Flask(__name__)
@flask_app.route('/')
def home():
    return "Bot Activo"

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    flask_app.run(host="0.0.0.0", port=port)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🔥 Bot de Apuestas Activo\n\nUsa /apuesta para empezar")

async def apuesta(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("⚽️ Análisis listo")

def main():
    if not TOKEN:
        print("ERROR: No hay TELEGRAM_TOKEN")
        return
    print("Bot iniciado correctamente...")
    threading.Thread(target=run_flask).start()
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("apuesta", apuesta))
    app.run_polling()

if __name__ == "__main__":
    main()
