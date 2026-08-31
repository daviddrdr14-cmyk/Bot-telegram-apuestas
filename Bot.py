import os, time, threading, requests
from flask import Flask
import telebot

TOKEN = os.getenv("TELEGRAM_TOKEN")
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

# IDs de SofaScore - estos son los oficiales de ellos
EQUIPOS_SOFASCORE = {
    "monterrey": 1733, "rayados": 1733,
    "san luis": 40001, "atletico san luis": 40001,
    "barcelona": 2817, "real madrid": 2829, "rayo vallecano": 2824, "rayo": 2824,
    "america": 1738, "cruz azul": 1740, "tigres": 1734, "chivas": 1736, "pumas": 1737,
    "manchester city": 17, "man city": 17, "arsenal": 42, "liverpool": 44, "chelsea": 38
}

HEADERS_SOFA = {
    "User-Agent": "Mozilla/5.0",
    "Accept": "application/json"
}

@app.route('/')
def home(): return "Bot V7 SofaScore 2026 LIVE"

def get_id(nombre):
    n=nombre.lower().strip()
    if n in EQUIPOS_SOFASCORE: return EQUIPOS_SOFASCORE[n]
    for k,v in EQUIPOS_SOFASCORE.items():
        if k in n: return v
    return None

def get_ultimos_sofa(team_id):
    try:
        # API interna de SofaScore - últimos partidos
        url = f"https://api.sofascore.com/api/v1/team/{team_id}/events/last/0"
        r = requests.get(url, headers=HEADERS_SOFA, timeout=10)
        data = r.json()
        eventos = data.get('events', [])[:5]

        goles_ht = 0
        con_gol = 0
        for ev in eventos:
            # ht score
            ht = ev.get('time', {}).get('currentPeriodStartTimestamp', 0)
            # usamos el marcador al descanso si existe
            home_ht = ev.get('homeScore', {}).get('period1', 0)
            away_ht = ev.get('awayScore', {}).get('period1', 0)
            if home_ht is None: home_ht = 0
            if away_ht is None: away_ht = 0
            total = home_ht + away_ht
            goles_ht += total
            if total > 0: con_gol += 1

        if len(eventos) == 0: return None
        prob = int(con_gol/len(eventos)*100)
        prom = round(goles_ht/len(eventos), 2)
        print(f"Sofa {team_id} -> {prob}% {prom} con {len(eventos)}")
        return prob, prom, len(eventos)
    except Exception as e:
        print(f"Error Sofa {team_id}: {e}")
        return None

@bot.message_handler(func=lambda m: True)
def predecir(m):
    if "vs" not in m.text.lower(): return
    try:
        e1, e2 = [x.strip() for x in m.text.lower().split("vs")]
        id1=get_id(e1); id2=get_id(e2)
        if not id1 or not id2:
            bot.reply_to(m, "❌ Prueba: Barcelona vs Rayo o Monterrey vs San Luis")
            return

        bot.send_chat_action(m.chat.id, 'typing')
        a1=get_ultimos_sofa(id1)
        a2=get_ultimos_sofa(id2)

        if not a1 or not a2:
            bot.reply_to(m, f"⚠️ SofaScore no dio datos, prueba de nuevo")
            return

        prob=int((a1[0]+a2[0])/2)

        msg=f"""🌎 **{e1.upper()} vs {e2.upper()}**
📡 **SOFASCORE 2026 - DATOS REALES HOY**

📊 Últimos {a1[2]} partidos:
{e1}: Gol HT {a1[0]}% prom {a1[1]}
{e2}: Gol HT {a2[0]}% prom {a2[1]}

⏱️ **Over 0.5 Gol 1T: {prob}%**
{'✅ SE ESPERA GOL EN 1T' if prob>=65 else '❌ POCA PROB'}

✅ Fuente: SofaScore.com en vivo 2026
"""
        bot.reply_to(m, msg, parse_mode="Markdown")
    except Exception as e:
        bot.reply_to(m, f"Error: {e}")

def run_bot():
    bot.remove_webhook(); time.sleep(2)
    while True:
        try: bot.infinity_polling(skip_pending=True)
        except: time.sleep(5)

threading.Thread(target=run_bot, daemon=True).start()
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
