# luna.py
# ⚙ Luna Bot

from dotenv import load_dotenv
load_dotenv()

import os
import logging
from pathlib import Path
from flask import Flask, request
from telebot import TeleBot, types
from openai import OpenAI

# 🧠 Agents
from core.tina_agent import TinaAgent

# =============================
# ⏱ Scheduler (Optional)
# =============================
try:
    from scheduler import start_scheduler
    SCHED_AVAILABLE = True
except ImportError:
    SCHED_AVAILABLE = False
    print("⚠ Scheduler module not found — continuing without scheduler.")

# =============================
# Logging Setup
# =============================
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(message)s'
)
log = logging.getLogger(__name__)

# =============================
# Environment Variables
# =============================
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")
RUN_MODE = os.getenv("WEBHOOK_MODE", "true").lower() == "true"

if not TELEGRAM_TOKEN or not OPENAI_API_KEY:
    log.error("Required environment variables missing!")
    raise ValueError("TELEGRAM_TOKEN and OPENAI_API_KEY are required")

# =============================
# Initialize Bot & Client
# =============================
bot = TeleBot(TELEGRAM_TOKEN)
DEFAULT_MODEL = "gpt-4o-mini"

client = OpenAI(api_key=OPENAI_API_KEY)
user_state = {}
IMG_PATH = Path("images")

# =============================
# ⚡ Agent Selector
# =============================
def get_active_agent(chat_id):
    agent = user_state.get(chat_id, "lala")
    if agent == "tina":
        return TinaAgent()
    return TinaAgent()  # فعلاً فقط tina فعاله

# =====================
# Keyboard
# =====================
def main_menu():
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add("🌙 About Luna")
    kb.add("💬 Talk to Tina")
    kb.add("🎨 ثبت سفارش نقاشی")
    return kb

# =============================
# 🚀 Command Handlers
# =============================
@bot.message_handler(commands=["start"])
def start(msg):
    try:
        with open(IMG_PATH / "start.jpg", "rb") as photo:
            bot.send_photo(
                msg.chat.id,
                photo,
                caption=(
                    "🌙 به Luna خوش اومدی\n\n"
                    "من دستیار هوشمند و خلاق تو هستم ✨"
                )
            )

        # ⬅️ کیبورد حتماً با پیام جدا
        bot.send_message(
            msg.chat.id,
            "از منو یکی رو انتخاب کن 👇",
            reply_markup=main_menu()
        )

    except Exception as e:
        log.error(f"[Start Error] {e}")
        bot.send_message(msg.chat.id, "⚠ مشکلی پیش اومد.")

@bot.message_handler(func=lambda m: m.text == "🌙 About Luna")
def about(msg):
    try:
        with open(IMG_PATH / "about.jpg", "rb") as photo:
            bot.send_photo(
                msg.chat.id,
                photo,
                caption=(
                    "🌙 Luna\n\n"
                    "ربات همراه خلاق، هنری و هوشمند ✨\n"
                    "اینجام که کمک کنم، الهام بدم و بسازم 🌌"
                )
            )
    except Exception as e:
        log.error(f"[About Error] {e}")

@bot.message_handler(func=lambda m: m.text == "💬 Talk to Tina")
def talk_to_tina(msg):
    user_state[msg.chat.id] = "tina"
    try:
        with open(IMG_PATH / "tina.jpg", "rb") as photo:
            bot.send_photo(
                msg.chat.id,
                photo,
                caption=(
                    "💬 حالت گفت‌وگو با Tina فعال شد\n"
                    "هرچی دوست داری بنویس 🌸"
                )
            )
    except Exception as e:
        log.error(f"[Tina Error] {e}")

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

# =============================
# 💬 AI Chat
# =============================
@bot.message_handler(func=lambda m: True)
def chat(msg):
    agent = get_active_agent(msg.chat.id)
    try:
        reply = agent.generate_response(msg.text, client)
        bot.send_message(msg.chat.id, reply)
    except Exception as e:
        log.error(f"[Chat Error] {e}")
        bot.send_message(msg.chat.id, "⚠ مشکلی پیش اومد — دوباره امتحان کن 🌙")

# =============================
# 🌐 Flask Webhook
# =============================
app = Flask(__name__)

@app.route(f"/{TELEGRAM_TOKEN}", methods=["POST"])
def webhook():
    update = types.Update.de_json(request.data.decode("UTF-8"))
    bot.process_new_updates([update])
    return "ok", 200

@app.route("/")
def home():
    return "✅ Luna Bot Online"

# =============================
# 🚀 Main Entry
# =============================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))

    if RUN_MODE and SCHED_AVAILABLE:
        log.info("🌀 Scheduler started...")
        start_scheduler(interval_seconds=300)
    else:
        log.info("⏱ Scheduler disabled or not found.")

    log.info("✅ Bot is running...")
    app.run(host="0.0.0.0", port=port)


