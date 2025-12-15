import os
from dotenv import load_dotenv
from flask import Flask, request
import telebot
from telebot import types
from openai import OpenAI

# =====================
# Load env
# =====================
load_dotenv()
TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")

bot = telebot.TeleBot(TOKEN)
client = OpenAI(api_key=OPENAI_API_KEY)

app = Flask(__name__)

# =====================
# Keyboard
# =====================
def main_menu():
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add("🌙 درباره Luna")
    kb.add("💬 صحبت با تینا")
    kb.add("🎨 ثبت سفارش نقاشی")
    return kb

# =====================
# START
# =====================
@bot.message_handler(commands=["start"])
def start(msg):
    bot.send_message(
        msg.chat.id,
        "🌙 به Luna خوش اومدی\n\n"
        "من دستیار هوشمند و خلاق تو هستم ✨\n"
        "از منو یکی رو انتخاب کن 👇",
        reply_markup=main_menu()
    )

# =====================
# ABOUT
# =====================
@bot.message_handler(func=lambda m: m.text == "🌙 درباره Luna")
def about(msg):
    bot.send_message(
        msg.chat.id,
        "🌙 **Luna**\n\n"
        "ربات همراه خلاق، هنری و هوشمند ✨\n"
        "اینجام که کمک کنم، الهام بدم و بسازم 🌌",
        parse_mode="Markdown"
    )

# =====================
# TALK TO TINA (AI)
# =====================
@bot.message_handler(func=lambda m: m.text == "💬 صحبت با تینا")
def talk_tina(msg):
    bot.send_message(
        msg.chat.id,
        "💬 حالت گفت‌وگو با **تینا** فعال شد\n"
        "هرچی دوست داری بنویس 🌸"
    )
    bot.register_next_step_handler(msg, tina_chat)

def tina_chat(msg):
    try:
        response = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[
                {
                    "role": "system",
                    "content": "تو تینا هستی، یک همراه مهربان، آرام و الهام‌بخش 🌸"
                },
                {
                    "role": "user",
                    "content": msg.text
                }
            ]
        )
        reply = response.choices[0].message.content
        bot.send_message(msg.chat.id, reply)
    except Exception:
        bot.send_message(msg.chat.id, "🌙 الان کمی خسته‌ام… دوباره امتحان کن ✨")

# =====================
# ART ORDER
# =====================
@bot.message_handler(func=lambda m: m.text == "🎨 ثبت سفارش نقاشی")
def art_order(msg):
    bot.send_message(
        msg.chat.id,
        "🎨 ثبت سفارش نقاشی\n\n"
        "لطفاً بنویس:\n"
        "1️⃣ سبک نقاشی\n"
        "2️⃣ موضوع\n"
        "3️⃣ اندازه\n"
        "4️⃣ توضیحات خاص\n\n"
        "✍️ بعد از ارسال، بررسی میشه 🌙"
    )

# =====================
# WEBHOOK
# =====================
@app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    update = telebot.types.Update.de_json(request.data.decode("utf-8"))
    bot.process_new_updates([update])
    return "ok", 200

@app.route("/")
def home():
    return "🌙 Luna Bot is Online"

# =====================
# MAIN
# =====================
if __name__ == "__main__":
    bot.remove_webhook()
    bot.set_webhook(url=f"{WEBHOOK_URL}/{TOKEN}")
    app.run(host="0.0.0.0", port=5000)