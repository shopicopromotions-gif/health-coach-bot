import os
import threading
from flask import Flask
import telebot
from telebot import types
import google.generativeai as genai

BOT_TOKEN = os.getenv("BOT_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
PORT = int(os.getenv("PORT", 10000))

bot = telebot.TeleBot(BOT_TOKEN)
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-1.5-flash")

web = Flask(__name__)

@web.route("/")
def home():
    return "AI Health Coach Bot is running."

def run_web():
    web.run(host="0.0.0.0", port=PORT)

def menu():
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

@bot.message_handler(commands=["start"])
def start(message):
    bot.send_message(
        message.chat.id,
        "👋 Welcome to Free AI Health Coach\n\nChoose a topic or ask any health question anytime.\n\nNote: I provide general health knowledge only, not diagnosis or medicine prescription.",
        reply_markup=menu()
    )

@bot.callback_query_handler(func=lambda call: True)
def callback(call):
    bot.answer_callback_query(call.id)
    bot.send_message(call.message.chat.id, f"Ask me anything about {call.data}.")

@bot.message_handler(func=lambda message: True)
def chat(message):
    prompt = f"""
You are a friendly AI Health Coach.
Give general health and wellness knowledge only.
Do not diagnose disease.
Do not prescribe medicine or dosage.
Keep answers short, simple, practical, and safe.
If symptoms seem serious, tell the user to contact a qualified doctor.

User question: {message.text}
"""
    try:
        response = model.generate_content(prompt)
        bot.reply_to(message, response.text[:4000])
    except Exception:
        bot.reply_to(message, "Sorry, something went wrong. Please try again later.")

if __name__ == "__main__":
    threading.Thread(target=run_web, daemon=True).start()
    bot.infinity_polling()
