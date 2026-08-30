import os
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

TOKEN = os.environ.get("TELEGRAM_TOKEN")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🔥 Bot de Apuestas Activo\n\nUsa /apuesta para empezar")

async def apuesta(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("⚽️ Próximamente: análisis de apuestas")

def main():
    if not TOKEN:
        print("ERROR: No hay TELEGRAM_TOKEN en Environment")
        return
    print("Bot iniciado correctamente...")
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("apuesta", apuesta))
    app.run_polling()

if __name__ == "__main__":
    main()
