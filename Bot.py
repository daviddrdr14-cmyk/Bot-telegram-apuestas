import os, time, threading, random, hashlib
from flask import Flask
import telebot

TOKEN = os.getenv("TELEGRAM_TOKEN")
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot Tuxtla HT+FT Activo"

def generar_stats(e1, e2):
    seed = int(hashlib.md5((e1+e2).encode()).hexdigest(), 16) % 100000
    random.seed(seed)

    # MERCADOS HT
    over05_ht = random.randint(68, 90)
    corners1_ht = random.randint(1, 4)
    corners2_ht = random.randint(1, 4)
    total_corners_ht = corners1_ht + corners2_ht

    # MERCADOS PARTIDO COMPLETO
    btts = random.choice(["SI ✅", "NO ❌"])
    gana_ft = random.choice([e1, e2, "EMPATE"])
    marcador_ft = random.choice(["1-0", "2-0", "2-1", "1-1", "0-1", "2-2", "3-1"])
    over25_ft = random.randint(55, 85)

    tarjetas1 = random.randint(1, 3)
    tarjetas2 = random.randint(1, 4)
    total_tarjetas = tarjetas1 + tarjetas2

    return {
        "over05_ht": over05_ht,
        "c1_ht": corners1_ht, "c2_ht": corners2_ht, "ct_ht": total_corners_ht,
        "btts": btts, "gana_ft": gana_ft, "marcador_ft": marcador_ft,
        "over25": over25_ft,
        "t1": tarjetas1, "t2": tarjetas2, "tt": total_tarjetas
    }

@bot.message_handler(commands=['start','help'])
def start(m):
    bot.reply_to(m,
        "🔥 BOT TUXTLA 2026 🔥\n\n"
        "Escribe: `America vs Cruz Azul`\n\n"
        "Te doy:\n"
        "1T -> Gol + Corners\n"
        "90 Min -> Gana + BTTS + Tarjetas"
    )

@bot.message_handler(func=lambda m: True)
def predecir(m):
    if "vs" not in m.text.lower():
        bot.reply_to(m, "Escribe: America vs Cruz Azul")
        return
    try:
        p = m.text.lower().split("vs")
        e1 = p[0].strip().title()
        e2 = p[1].strip().title()
        s = generar_stats(e1, e2)

        msg = f"""📊 **{e1} vs {e2}**

⏱️ **PRIMER TIEMPO (Solo HT):**
⚽️ Gol HT - Over 0.5: `{s['over05_ht']}%` PROB
🚩 Corners HT: {e1} {s['c1_ht']} - {e2} {s['c2_ht']} (Total HT: {s['ct_ht']})

⏳ **PARTIDO COMPLETO (90 min):**
🏆 Gana partido: **{s['gana_ft']}**
⚽️ Marcador probable: **{s['marcador_ft']}**
🥅 Ambos anotan: **{s['btts']}**
📈 Over 2.5 Goles: {s['over25']}%
🟨 Tarjetas: {e1} {s['t1']} - {e2} {s['t2']} (Total: {s['tt']})

💰 **COMBINADA RECOMENDADA:**
👉 Over 0.5 Gol HT ({s['over05_ht']}%) + Over {s['ct_ht']-0.5} Corners HT
"""
        bot.reply_to(m, msg, parse_mode="Markdown")
    except Exception as e:
        print(e)
        bot.reply_to(m, "Escribe: America vs Cruz Azul")

def run_bot():
    bot.remove_webhook()
    time.sleep(2)
    print("Bot Tuxtla HT/FT Iniciado")
    while True:
        try:
            bot.infinity_polling(skip_pending=True)
        except:
            time.sleep(5)

threading.Thread(target=run_bot, daemon=True).start()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
