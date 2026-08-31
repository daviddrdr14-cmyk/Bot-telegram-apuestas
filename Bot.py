import os, time, threading, requests
from flask import Flask
import telebot

TOKEN = os.getenv("TELEGRAM_TOKEN")
API_KEY = os.getenv("API_FOOTBALL_KEY")
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)
HEADERS = {"x-apisports-key": API_KEY}
CACHE_TEAMS = {}

@app.route('/')
def home():
    return "Bot GLOBAL V2 Activo"

def buscar_equipo(nombre):
    key = nombre.lower().strip()
    if key in CACHE_TEAMS: return CACHE_TEAMS[key]
    try:
        r = requests.get(f"https://v3.football.api-sports.io/teams?search={nombre}", headers=HEADERS, timeout=15)
        js = r.json()
        if js['response']:
            team = js['response'][0]['team']
            CACHE_TEAMS[key] = team
            return team
    except Exception as e: print("buscar error", e)
    return None

def get_ultimos_partidos(team_id):
    try:
        # TRAEMOS SIN FILTRO DE TEMPORADA - trae lo más reciente automáticamente
        url = f"https://v3.football.api-sports.io/fixtures?team={team_id}&last=10&status=FT"
        r = requests.get(url, headers=HEADERS, timeout=15)
        data = r.json()
        # Si la API te dice que excediste límite, avisa
        if 'errors' in data and data['errors']:
            print("ERROR API:", data['errors'])
        return data.get('response', [])
    except Exception as e:
        print("fixtures error", e)
        return []

def analizar_ht(fixtures):
    if not fixtures: return None
    goles_ht = 0
    partidos_gol_ht = 0
    total = 0
    ligas = []
    for f in fixtures[:5]: # solo últimos 5 con HT válido
        ht = f['score']['halftime']
        if not ht or ht['home'] is None: continue
        g = (ht['home'] or 0) + (ht['away'] or 0)
        goles_ht += g
        if g > 0: partidos_gol_ht += 1
        total += 1
        ligas.append(f['league']['name'])
    if total==0: return None
    prob = int((partidos_gol_ht / total * 100))
    prom = round(goles_ht/total, 2)
    liga_comun = max(set(ligas), key=ligas.count) if ligas else "Internacional"
    return prob, prom, total, liga_comun

@bot.message_handler(commands=['start'])
def start(m):
    bot.reply_to(m, "🌎 BOT GLOBAL V2 🌎\nPrueba: Real Madrid vs Barcelona")

@bot.message_handler(func=lambda m: True)
def predecir(m):
    if "vs" not in m.text.lower(): return
    try:
        e1_name, e2_name = [x.strip() for x in m.text.lower().split("vs")]
        bot.send_chat_action(m.chat.id, 'typing')
        t1 = buscar_equipo(e1_name)
        t2 = buscar_equipo(e2_name)
        if not t1 or not t2:
            bot.reply_to(m, f"❌ No encontré {e1_name} o {e2_name}. Prueba nombres en inglés: Manchester City vs Arsenal")
            return
        f1 = get_ultimos_partidos(t1['id'])
        f2 = get_ultimos_partidos(t2['id'])

        # DEBUG para ver qué pasa
        if not f1 and not f2:
            bot.reply_to(m, "⚠️ API-Football sin datos o se acabaron los 100 requests gratis de hoy. Se resetea a medianoche. Prueba mañana o verifica tu API KEY en Render.")
            return

        a1 = analizar_ht(f1)
        a2 = analizar_ht(f2)
        if not a1 or not a2:
            bot.reply_to(m, f"⚠️ {t1['name']} tiene {len(f1)} partidos pero sin HT. {t2['name']} {len(f2)}. Intenta con equipos TOP de Europa.")
            return

        prob_real = int((a1[0] + a2[0]) / 2)
        msg = f"""🌎 **{t1['name']} vs {t2['name']}**
🏆 {a1[3]} / {a2[3]}

📡 REAL (Últimos {a1[2]} partidos):
{t1['name']}: Gol HT {a1[0]}% (prom {a1[1]})
{t2['name']}: Gol HT {a2[0]}% (prom {a2[1]})

⏱️ **Over 0.5 Gol HT: {prob_real}%**
{'✅ SE ESPERA GOL HT' if prob_real>65 else '❌ POCA PROB HT'}

💰 Apuesta: {'Over 0.5 HT' if prob_real>65 else 'Under 0.5 HT'} {prob_real}%
"""
        bot.reply_to(m, msg, parse_mode="Markdown")
    except Exception as e:
        print(e)
        bot.reply_to(m, f"Error: {e}")

def run_bot():
    bot.remove_webhook(); time.sleep(2)
    while True:
        try: bot.infinity_polling(skip_pending=True)
        except: time.sleep(5)

threading.Thread(target=run_bot, daemon=True).start()
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
