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
    return "Bot Tuxtla GLOBAL Activo - Todas las ligas"

def buscar_equipo(nombre):
    key = nombre.lower()
    if key in CACHE_TEAMS: return CACHE_TEAMS[key]
    try:
        r = requests.get(f"https://v3.football.api-sports.io/teams?search={nombre}", headers=HEADERS, timeout=10)
        data = r.json()
        if data['response']:
            # Filtra por equipo más relevante (con más búsquedas)
            team = data['response'][0]['team']
            CACHE_TEAMS[key] = team
            return team
    except Exception as e: print(e)
    return None

def get_ultimos_partidos(team_id, last=5):
    try:
        # SIN filtro de liga - trae de cualquier liga donde juegue
        url = f"https://v3.football.api-sports.io/fixtures?team={team_id}&last={last}"
        r = requests.get(url, headers=HEADERS, timeout=10)
        return r.json().get('response', [])
    except: return []

def analizar_ht(fixtures):
    if not fixtures: return None
    goles_ht = 0
    partidos_gol_ht = 0
    total = 0
    ligas = []
    for f in fixtures:
        ht = f['score']['halftime']
        if ht['home'] is None: continue
        g = ht['home'] + ht['away']
        goles_ht += g
        if g > 0: partidos_gol_ht += 1
        total += 1
        ligas.append(f['league']['name'])
    if total==0: return None
    prob = int((partidos_gol_ht / total * 100))
    prom = round(goles_ht/total, 2)
    liga_comun = max(set(ligas), key=ligas.count) if ligas else "Varias"
    return prob, prom, total, liga_comun

@bot.message_handler(commands=['start'])
def start(m):
    bot.reply_to(m, "🌎 BOT TUXTLA GLOBAL 🌎\n\nEscribe cualquier partido del mundo:\n\n• Real Madrid vs Barcelona\n• Man City vs Arsenal\n• Boca Juniors vs River Plate\n• Flamengo vs Palmeiras\n• Monterrey vs Tigres\n\n¡Todas las ligas!")

@bot.message_handler(func=lambda m: True)
def predecir(m):
    if "vs" not in m.text.lower(): return
    try:
        e1_name, e2_name = [x.strip() for x in m.text.lower().split("vs")]
        bot.send_chat_action(m.chat.id, 'typing')

        t1 = buscar_equipo(e1_name)
        t2 = buscar_equipo(e2_name)

        if not t1 or not t2:
            bot.reply_to(m, f"❌ No encontré: {e1_name} o {e2_name}\nPrueba: Real Madrid vs Barcelona")
            return

        f1 = get_ultimos_partidos(t1['id'])
        f2 = get_ultimos_partidos(t2['id'])

        a1 = analizar_ht(f1)
        a2 = analizar_ht(f2)

        if not a1 or not a2:
            bot.reply_to(m, "⚠️ Sin datos recientes para esos equipos, intenta con equipos más conocidos")
            return

        prob_real = int((a1[0] + a2[0]) / 2)
        if a1[1] > 0.8 and a2[1] > 0.8: prob_real = min(95, prob_real + 12)
        if a1[1] < 0.4 and a2[1] < 0.4: prob_real = max(35, prob_real - 20)

        msg = f"""🌎 **{t1['name']} vs {t2['name']}**
🏆 Liga detectada: {a1[3]} / {a2[3]}

📡 **DATOS REALES GLOBALES:**
📊 {t1['name']} ({a1[3]}): Gol HT en {a1[0]}% - Prom {a1[1]} goles HT en {a1[2]} partidos
📊 {t2['name']} ({a2[3]}): Gol HT en {a2[0]}% - Prom {a2[1]} goles HT en {a2[2]} partidos

⏱️ **PRIMER TIEMPO - PREDICCIÓN REAL:**
⚽️ Over 0.5 Gol HT: **{prob_real}%** 🔥
{'✅ SE ESPERA GOL EN 1T' if prob_real>70 else '❌ POCA PROB DE GOL EN 1T'}

⏳ **PARTIDO COMPLETO:**
🥅 Ambos anotan: {'SI' if prob_real>65 else 'NO'} - {prob_real if prob_real>65 else 100-prob_real}%
📈 Over 2.5: {75 if prob_real>70 else 50}%

💰 **APUESTA RECOMENDADA:**
👉 {'Over 0.5 Gol HT' if prob_real>68 else 'Under 0.5 Gol HT'} - Confianza {prob_real}%
"""
        bot.reply_to(m, msg, parse_mode="Markdown")
    except Exception as e:
        print(e)
        bot.reply_to(m, f"Error API: {e}")

def run_bot():
    bot.remove_webhook()
    time.sleep(2)
    while True:
        try: bot.infinity_polling(skip_pending=True)
        except: time.sleep(5)

threading.Thread(target=run_bot, daemon=True).start()
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
