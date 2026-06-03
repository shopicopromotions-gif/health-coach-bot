import os
import threading
from flask import Flask
import google.generativeai as genai
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, ContextTypes, filters

BOT_TOKEN = os.getenv("BOT_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
PORT = int(os.getenv("PORT", 10000))

web = Flask(__name__)

@web.route("/")
def home():
    return "AI Health Coach Bot is running."

def run_web():
    web.run(host="0.0.0.0", port=PORT)

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-1.5-flash")

menu = [
    [InlineKeyboardButton("🥗 Food", callback_data="Food & Nutrition"),
     InlineKeyboardButton("😴 Sleep", callback_data="Sleep Health")],
    [InlineKeyboardButton("🏃 Exercise", callback_data="Exercise Basics"),
     InlineKeyboardButton("💧 Hydration", callback_data="Water & Hydration")],
    [InlineKeyboardButton("🧠 Mental Wellness", callback_data="Mental Wellness")],
    [InlineKeyboardButton("❓ Ask Any Health Question", callback_data="Ask")]
]

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Welcome to Free AI Health Coach\n\nChoose a topic or ask any health question anytime.",
        reply_markup=InlineKeyboardMarkup(menu)
    )

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.message.reply_text(f"Ask me anything about {query.data}.")

async def chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text

    prompt = f"""
You are a friendly AI Health Coach.
Give general health and wellness knowledge only.
Do not diagnose disease.
Do not prescribe medicine or dosage.
Do not give emergency treatment instructions.
Keep the answer simple, practical, and safe.
If symptoms seem serious, tell the user to contact a qualified doctor.

User question: {user_text}
"""

    try:
        response = model.generate_content(prompt)
        await update.message.reply_text(response.text[:4000])
    except Exception as e:
        await update.message.reply_text("Sorry, something went wrong. Please try again later.")

def run_bot():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chat))
    app.run_polling()

if __name__ == "__main__":
    threading.Thread(target=run_web).start()
    run_bot()
