import os
import requests
from flask import Flask, request

BOT_TOKEN = os.getenv("BOT_TOKEN", "").strip()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "").strip()

app = Flask(__name__)

TELEGRAM_API = f"https://api.telegram.org/bot{BOT_TOKEN}"


def send_message(chat_id, text, reply_markup=None):
    data = {
        "chat_id": chat_id,
        "text": text[:4000]
    }
    if reply_markup:
        data["reply_markup"] = reply_markup

    requests.post(f"{TELEGRAM_API}/sendMessage", json=data, timeout=20)


def menu():
    return {
        "inline_keyboard": [
            [
                {"text": "🥗 Food", "callback_data": "Food"},
                {"text": "😴 Sleep", "callback_data": "Sleep"}
            ],
            [
                {"text": "🏃 Exercise", "callback_data": "Exercise"},
                {"text": "💧 Hydration", "callback_data": "Hydration"}
            ],
            [
                {"text": "🧠 Mental Wellness", "callback_data": "Mental Wellness"}
            ],
            [
                {"text": "❓ Ask Any Health Question", "callback_data": "Ask"}
            ]
        ]
    }


def ask_gemini(user_text):
    if not GEMINI_API_KEY:
        return "Gemini API key missing in Render Environment Variables."

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


@app.route("/", methods=["GET"])
def home():
    return "AI Health Coach Bot is running."


@app.route("/webhook", methods=["GET", "POST"])
def webhook():
    if request.method == "GET":
        return "Webhook route active."

    data = request.get_json()

    if "message" in data:
        chat_id = data["message"]["chat"]["id"]
        text = data["message"].get("text", "")

        if text == "/start":
            send_message(
                chat_id,
                "👋 Welcome to Free AI Health Coach\n\nChoose a topic or ask any health question anytime.\n\nNote: I provide general health knowledge only, not diagnosis or medicine prescription.",
                menu()
            )
        else:
            answer = ask_gemini(text)
            send_message(chat_id, answer)

    elif "callback_query" in data:
        call = data["callback_query"]
        chat_id = call["message"]["chat"]["id"]
        topic = call["data"]

        requests.post(
            f"{TELEGRAM_API}/answerCallbackQuery",
            json={"callback_query_id": call["id"]},
            timeout=10
        )

        send_message(chat_id, f"Ask me anything about {topic}.")

    return "OK"


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
