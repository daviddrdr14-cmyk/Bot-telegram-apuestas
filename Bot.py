import os, requests
from datetime import datetime
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes

TOKEN = os.getenv("TELEGRAM_TOKEN")
API_KEY = os.getenv("API_FOOTBALL_KEY")
HOST = "v3.football.api-sports.io"

def get_fixtures():
    url = f"https://{HOST}/fixtures"
    params = {"date": datetime.now().strftime("%Y-%m-%d"), "timezone": "America/Mexico_City"}
    headers = {"x-apisports-key": API_KEY}
    r = requests.get(url, headers=headers, params=params, timeout=20)
    return r.json().get("response", [])

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    kb = [[InlineKeyboardButton("⚽ Partidos Hoy", callback_data="today")],[InlineKeyboardButton("🔥 Top 5 Picks", callback_data="top5")]]
    await update.message.reply_text("🔥 BOT APUESTAS PRO - SOLO TELEGRAM\nListo para Brasil, Colombia, Ecuador...", reply_markup=InlineKeyboardMarkup(kb))

async def handle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    await q.edit_message_text("⏳ Consultando API-Football...")
    games = get_fixtures()
    if not games:
        await q.edit_message_text("No hay partidos hoy o se acabaron los 100 req.")
        return
    txt = f"📅 HOY {datetime.now().strftime('%d/%m')}\n\n"
    for f in games[:12]:
        home = f['teams']['home']['name']
        away = f['teams']['away']['name']
        hour = f['fixture']['date'][11:16]
        txt += f"{hour} {home} vs {away}\n"
    await q.edit_message_text(txt)

def main():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(handle))
    app.run_polling()

if __name__ == "__main__":
    main()
