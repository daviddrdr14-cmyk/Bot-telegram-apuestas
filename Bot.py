import os
import logging
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

TOKEN = os.getenv("TELEGRAM_TOKEN")

logging.basicConfig(level=logging.INFO)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [["⚽ Partidos Hoy"]]
    markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text("🔥 Bot de Apuestas Activo ✅\nPresiona ⚽ Partidos Hoy", reply_markup=markup)

async def partidos(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Cargando partidos de hoy... pronto aquí irán las cuotas.")

def main():
    print("Bot iniciado correctamente...")
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.Regex("^⚽ Partidos Hoy$"), partidos))
    app.run_polling()

if __name__ == "__main__":
    main()
