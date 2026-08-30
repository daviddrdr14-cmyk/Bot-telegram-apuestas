import os, threading
from flask import Flask
import telebot

TOKEN = os.getenv("TELEGRAM_TOKEN")
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot Activo"

@bot.message_handler(commands=['start'])
def start(m):
    bot.reply_to(m, "🔥 Bot de Apuestas Activo Tuxtla 2026\n\nYa funciono! Escribe un partido:\nReal Madrid vs Barcelona")

@bot.message_handler(func=lambda m: True)
def all_msg(m):
    bot.reply_to(m, f"Recibi: {m.text}\n✅ Ya estoy funcionando")

def run_bot():
    print("Bot iniciado correctamente")
    bot.infinity_polling()

threading.Thread(target=run_bot).start()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
