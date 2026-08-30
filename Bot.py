import os, requests
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes

TOKEN = os.getenv("TELEGRAM_TOKEN")
API_KEY = os.getenv("API_FOOTBALL_KEY")
HOST = "v3.football.api-sports.io"

def get_fixtures():
    url = f"https://{HOST}/fixtures"
    params = {"date": datetime.now().strftime("%Y-%m-%d")}
    headers = {"x-apisports-key": API_KEY, "x-rapidapi-host": HOST}
    try:
        r = requests.get(url, headers=headers, params=params, timeout=15)
        return r.json().get("response", [])
    except:
        return []

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    kb = [[InlineKeyboardButton("⚽ Partidos Hoy", callback_data="partidos")]]
    await update.message.reply_text(
        "🔥 Bot de Apuestas Activo ✅", 
        reply_markup=InlineKeyboardMarkup(kb)
    )

async def handle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    await q.edit_message_text("⏳ Consultando partidos...")
    games = get_fixtures()
    if not games:
        await q.edit_message_text("No hay partidos hoy o error de API.")
        return
    txt = f"📅 HOY {datetime.now().strftime('%Y-%m-%d')}\n\n"
    for f in games[:10]:
        txt += f"🏆 {f['league']['name']}\n{f['teams']['home']['name']} vs {f['teams']['away']['name']}\n\n"
    await q.edit_message_text(txt)

def main():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(handle))
    print("Bot iniciado...")
    app.run_polling()

if __name__ == "__main__":
    main()
