import os, time, threading, requests
from flask import Flask
import telebot
from datetime import datetime

TOKEN = os.getenv("TELEGRAM_TOKEN")
API_KEY = os.getenv("API_FOOTBALL_KEY")
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)
HEADERS = {"x-apisports-key": API_KEY}

EQUIPOS = {
    "monterrey": 1400, "rayados": 1400,
    "san luis": 1403, "atletico san luis": 1403, "atl san luis": 1403,
    "america": 1404, "cruz azul": 1406, "tigres": 1405, "chivas": 1399, "pumas": 1402,
    "barcelona": 529, "real madrid": 541, "rayo vallecano": 728, "rayo": 728,
    "manchester city": 50, "man city": 50, "arsenal": 42, "liverpool": 40, "chelsea": 49, "manchester united": 33,
    "boca": 451, "river": 435, "flamengo": 127, "palmeiras": 121
}

@app.route('/')
def home(): return "Bot V5 FREE PLAN OK"

def get_id(nombre):
    n=nombre.lower().strip()
    if n in EQUIPOS: return EQUIPOS[n]
    for k,v in EQUIPOS.items():
        if k in n or n in k: return v
    return None

def get_fixtures_free(team_id):
    # PLAN GRATIS: no se puede usar 'last', hay que usar season
    current_year = datetime.now().year
    for season in [current_year, current_year-1, 2024, 2023]:
        try:
            url = f"https://v3.football.api-sports.io/fixtures?team={team_id}&season={season}"
            r = requests.get(url, headers=HEADERS, timeout=15)
            js = r.json()
            data = js.get('response', [])
            # filtra solo terminados y con halftime
            filtrados = [x for x in data if x['score']['halftime']['home'] is not None]
            # ordena por fecha más reciente
            filtrados = sorted(filtrados, key=lambda x: x['fixture']['date'], reverse=True)[:5]
            if filtrados:
                print(f"Team {team_id} season {season} -> {len(filtrados)}")
                return filtrados, None
        except Exception as e:
            print(e)
    return [], "Sin partidos"

def analizar(fixtures):
    if not fixtures: return None
    g=0; con=0; tot=0
    liga = fixtures[0]['league']['name'] if fixtures else ""
    for f in fixtures:
        ht=f['score']['halftime']
        gol=(ht['home'] or 0)+(ht['away'] or 0)
        g+=gol
        if gol>0: con+=1
        tot+=1
    return int(con/tot*100), round(g/tot,2), tot, liga

@bot.message_handler(func=lambda m: True)
def predecir(m):
    txt = m.text.lower()
    if "vs" not in txt:
        if "san luis" in txt and "monterrey" in txt:
            txt = txt.replace("monterrey san luis", "monterrey vs san luis")
        else:
            return
    try:
        e1, e2 = [x.strip() for x in txt.split("vs")]
        id1=get_id(e1); id2=get_id(e2)
        if not id1 or not id2:
            bot.reply_to(m, f"❌ Agrega más equipos al código. Prueba: Barcelona vs Real Madrid")
            return
        bot.send_chat_action(m.chat.id, 'typing')
        f1, err1 = get_fixtures_free(id1)
        f2, err2 = get_fixtures_free(id2)
        if not f1 or not f2:
            bot.reply_to(m, f"⚠️ Aún sin datos {e1}:{len(f1)} {e2}:{len(f2)}")
            return
        a1=analizar(f1); a2=analizar(f2)
        prob=int((a1[0]+a2[0])/2)
        msg=f"""🌎 **{e1.upper()} vs {e2.upper()}**
🏆 {a1[3]}

📡 REAL - Últimos {a1[2]} partidos (PLAN GRATIS):
{e1}: Gol HT {a1[0]}% prom {a1[1]}
{e2}: Gol HT {a2[0]}% prom {a2[1]}

⏱️ **Over 0.5 Gol HT: {prob}%**
{'✅ SI SE ESPERA GOL EN 1T' if prob>=65 else '❌ POCA PROB'}
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
