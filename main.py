import os
import requests
import telebot
from telebot import types
from flask import Flask, request

BOT_TOKEN = os.getenv("BOT_TOKEN", "").strip()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "").strip()

bot = telebot.TeleBot(BOT_TOKEN)
app = Flask(__name__)

def make_menu():
    markup = types.InlineKeyboardMarkup()
    markup.row(
        types.InlineKeyboardButton("🥗 Food", callback_data="Food"),
        types.InlineKeyboardButton("😴 Sleep", callback_data="Sleep")
    )
    markup.row(
        types.InlineKeyboardButton("🏃 Exercise", callback_data="Exercise"),
        types.InlineKeyboardButton("💧 Hydration", callback_data="Hydration")
    )
    markup.row(types.InlineKeyboardButton("🧠 Mental Wellness", callback_data="Mental Wellness"))
    markup.row(types.InlineKeyboardButton("❓ Ask Any Health Question", callback_data="Ask"))
    return markup

def ask_gemini(user_text):
    if not GEMINI_API_KEY:
        return "Gemini API key missing."

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"

    prompt = f"""
You are a friendly AI Health Coach.

Rules:
- Give general health and wellness knowledge only.
- Do not diagnose disease.
- Do not prescribe medicine or dosage.
- Keep answers short, simple, practical, and safe.
- If symptoms seem serious, tell the user to contact a qualified doctor.

User question: {user_text}
"""

    payload = {
        "contents": [
            {"parts": [{"text": prompt}]}
        ]
    }

    try:
        r = requests.post(url, json=payload, timeout=30)
        if r.status_code != 200:
            return f"Gemini API error {r.status_code}: {r.text[:250]}"

        data = r.json()
        return data["candidates"][0]["content"]["parts"][0]["text"][:4000]

    except Exception as e:
        return f"Error: {str(e)[:250]}"

@bot.message_handler(commands=["start"])
def start(message):
    bot.send_message(
        message.chat.id,
        "👋 Welcome to Free AI Health Coach\n\n"
        "Choose a topic or ask any health question anytime.\n\n"
        "Note: I provide general health knowledge only, not diagnosis or medicine prescription.",
        reply_markup=make_menu()
    )

@bot.callback_query_handler(func=lambda call: True)
def callback(call):
    bot.answer_callback_query(call.id)
    bot.send_message(call.message.chat.id, f"Ask me anything about {call.data}.")

@bot.message_handler(func=lambda message: True)
def chat(message):
    answer = ask_gemini(message.text)
    bot.reply_to(message, answer)

@app.route("/", methods=["GET"])
def home():
    return "AI Health Coach Bot is running."

@app.route("/webhook", methods=["GET", "POST"])
def webhook():
    if request.method == "GET":
        return "Webhook route is active."

    update = telebot.types.Update.de_json(request.get_data().decode("utf-8"))
    bot.process_new_updates([update])
    return "OK"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
