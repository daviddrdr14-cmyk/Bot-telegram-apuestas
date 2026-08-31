import os, time, threading
from flask import Flask
import telebot

TOKEN = os.getenv("TELEGRAM_TOKEN")
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot Tuxtla Activo 2026"

@bot.message_handler(commands=['start'])
def start(m):
    bot.reply_to(m, "🔥 Bot Tuxtla Activo!\nYa jala! Escribe un partido")

@bot.message_handler(func=lambda x: True)
def echo(m):
    bot.reply_to(m, f"Recibi: {m.text} ✅")

def run_bot():
    bot.remove_webhook()
    time.sleep(1)
    print("Bot iniciado correctamente - sin conflicto")
    while True:
        try:
            bot.infinity_polling(timeout=20, long_polling_timeout=20, skip_pending=True)
        except Exception as e:
            print(f"Error polling: {e} - reintentando en 5s")
            time.sleep(5)

threading.Thread(target=run_bot, daemon=True).start()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
