import os, time, threading, requests
from flask import Flask
import telebot

TOKEN = os.getenv("TELEGRAM_TOKEN")
API_KEY = os.getenv("API_FOOTBALL_KEY")
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)
HEADERS = {"x-apisports-key": API_KEY}

# IDs FIJOS - no necesitamos buscar
EQUIPOS_FIJOS = {
    "monterrey": 1400, "rayados": 1400,
    "san luis": 1403, "atletico san luis": 1403,
    "america": 1404, "club america": 1404,
    "cruz azul": 1406, "tigres": 1405, "chivas": 1399, "guadalajara": 1399,
    "pumas": 1402, "toluca": 1411,
    "barcelona": 529, "real madrid": 541, "madrid": 541,
    "rayo vallecano": 728, "rayo": 728,
    "atletico madrid": 530, "sevilla": 536, "betis": 543,
    "manchester city": 50, "man city": 50, "arsenal": 42, "liverpool": 40, "chelsea": 49, "manchester united": 33, "man united": 33,
    "bayern": 157, "psg": 85, "inter": 505, "milan": 489, "juventus": 496,
    "boca": 451, "river": 435, "flamengo": 127, "palmeiras": 121
}

@app.route('/')
def home(): return "Bot V4 IDs FIJOS Activo"

def get_id(nombre):
    n = nombre.lower().strip()
    if n in EQUIPOS_FIJOS: return EQUIPOS_FIJOS[n], n
    # busca parcial
    for k,v in EQUIPOS_FIJOS.items():
        if k in n or n in k: return v, k
    return None, None

def get_ultimos(team_id):
    try:
        url = f"https://v3.football.api-sports.io/fixtures?team={team_id}&last=5"
        r = requests.get(url, headers=HEADERS, timeout=15)
        js = r.json()
        if 'errors' in js and js['errors']:
            return [], str(js['errors'])
        return js.get('response', []), None
    except Exception as e:
        return [], str(e)

def analizar(fixtures):
    if not fixtures: return None
    g_ht=0; con=0; tot=0; ligas=[]
    for f in fixtures:
        ht=f['score']['halftime']
        if not ht or ht['home'] is None: continue
        g=(ht['home'] or 0)+(ht['away'] or 0)
        g_ht+=g
        if g>0: con+=1
        tot+=1
        ligas.append(f['league']['name'])
    if tot==0: return None
    return int(con/tot*100), round(g_ht/tot,2), tot, ligas[0] if ligas else "Liga"

@bot.message_handler(func=lambda m: True)
def predecir(m):
    if "vs" not in m.text.lower(): return
    try:
        e1_name, e2_name = [x.strip() for x in m.text.lower().split("vs")]
        id1, key1 = get_id(e1_name)
        id2, key2 = get_id(e2_name)
        if not id1 or not id2:
            bot.reply_to(m, f"❌ No tengo ID para {e1_name} o {e2_name}\nPrueba: Barcelona vs Real Madrid, Monterrey vs Tigres, Man City vs Arsenal")
            return
        bot.send_chat_action(m.chat.id, 'typing')
        f1, err1 = get_ultimos(id1)
        f2, err2 = get_ultimos(id2)
        if err1 or err2:
            bot.reply_to(m, f"⚠️ Error API: {err1 or err2}\nVerifica tu API_FOOTBALL_KEY en Render")
            return
        if not f1 or not f2:
            bot.reply_to(m, f"Sin partidos para esos IDs. {e1_name}:{len(f1)} {e2_name}:{len(f2)}")
            return
        a1=analizar(f1); a2=analizar(f2)
        if not a1 or not a2:
            bot.reply_to(m, "Sin datos HT válidos")
            return
        prob=int((a1[0]+a2[0])/2)
        msg=f"""🌎 **{e1_name.upper()} vs {e2_name.upper()}**
🏆 {a1[3]}

📡 REAL {a1[2]} partidos:
{e1_name}: Gol HT {a1[0]}% (prom {a1[1]})
{e2_name}: Gol HT {a2[0]}% (prom {a2[1]})

⏱️ **Over 0.5 Gol HT: {prob}%**
{'✅ ESPERA GOL HT' if prob>=65 else '❌ POCA PROB'}
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
