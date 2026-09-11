import datetime
import os
import random
import threading
import time

from flask import Flask
import pytz
import telebot

# ============================================================
# CONFIGURATION
# ============================================================

# Read from environment variables, or fall back to your provided values
BOT_TOKEN = os.getenv("BOT_TOKEN", "8750268784:AAHRqnv0MebNMhfwuqetosJT3WvKWJ3oVPQ")
CHANNEL_ID = int(os.getenv("CHANNEL_ID", "-1002835568642"))

WIN_STICKER_ID = (
    "CAACAgUAAxkBAAER4h1qo_aDagqTDFeZsvVfXRWkHL1gMQACxiAAAlKt-FSX-5IBfGtcPz0E"
)
LOSS_STICKER_ID = (
    "CAACAgUAAxkBAAER4h9qo_aX3jMiUFY5WnP-YiWldp1WOgACJg8AAhRQUVTAisD_A8dpDz0E"
)

# ============================================================
# INITIALIZATION
# ============================================================

bot = telebot.TeleBot(BOT_TOKEN)
app = Flask(__name__)

current_level = 1
total_rounds_played = 0
predictions = {}
bot_start_time = time.time()
state_lock = threading.Lock()

# ============================================================
# PERIOD & PREDICTION GENERATION
# ============================================================

def get_current_period_info():
    tz = pytz.timezone("Asia/Kolkata")
    now = datetime.datetime.now(tz)
    total_minutes = now.hour * 60 + now.minute
    sequence = total_minutes + 1
    date_string = now.strftime("%Y%m%d")
    return f"{date_string}100{sequence:04d}"


def generate_prediction():
    number = random.randint(0, 9)

    if number in [2, 4, 6, 8]:
        color = "🔴 RED"
        emoji = "🔴"
    elif number in [1, 3, 7, 9]:
        color = "🟢 GREEN"
        emoji = "🟢"
    elif number == 0:
        color = "🔴🟣 RED + VIOLET"
        emoji = "🔴"
    else:
        color = "🟢🟣 GREEN + VIOLET"
        emoji = "🟢"

    size = "📈 BIG" if number >= 5 else "📉 SMALL"
    return number, color, size, emoji


def create_prediction():
    global total_rounds_played
    period = get_current_period_info()
    number, color, size, emoji = generate_prediction()

    prediction = {
        "period": period,
        "number": number,
        "color": color,
        "size": size,
        "emoji": emoji,
        "created_at": time.time(),
    }

    with state_lock:
        total_rounds_played += 1
        predictions[period] = prediction
        level = current_level

        if len(predictions) > 20:
            oldest_period = next(iter(predictions))
            del predictions[oldest_period]

    return prediction, level

# ============================================================
# TELEGRAM DISPATCH
# ============================================================

def send_prediction():
    try:
        prediction, level = create_prediction()

        period = prediction["period"]
        number = prediction["number"]
        color = prediction["color"]
        size = prediction["size"]
        emoji = prediction["emoji"]

        message = (
            "🔥 **WINGO 1 MIN** 🔥\n\n"
            f"📅 **PERIOD NUMBER:** `{period}`\n\n"
            f"📊 **BIG/SMALL:** {size}\n"
            f"🎨 **COLOR:** {color}\n"
            f"🔢 **NUMBER:** {emoji} `{number}` {emoji}\n\n"
            f"📈 **LEVEL:** `{level}`\n\n"
            "📩 **DM FOR MORE DETAILS:**\n"
            "@Maayan001\n"
            "@anonymoustele01\n"
            "@madexgurl\n\n"
            "⚠️ *Random game guess — not guaranteed.*"
        )

        bot.send_message(
            CHANNEL_ID,
            message,
            parse_mode="HTML"
        )
        print(f"Prediction sent: {period}")

    except Exception as error:
        print(f"Prediction error: {error}")


def automatic_prediction_loop():
    print("Automatic prediction system started.")
    last_period = None

    while True:
        try:
            current_period = get_current_period_info()

            if current_period != last_period:
                send_prediction()
                last_period = current_period

            time.sleep(2)

        except Exception as error:
            print(f"Automatic loop error: {error}")
            time.sleep(5)

# ============================================================
# BOT COMMAND HANDLERS
# ============================================================

@bot.message_handler(commands=["start"])
def start_command(message):
    text = (
        "🤖 **Wingo Channel Bot**\n\n"
        "🟢 Bot is online.\n\n"
        "The bot is configured to automatically post to the channel.\n\n"
        "Commands:\n"
        "/start - Start bot\n"
        "/help - Show help\n"
        "/status - Show status"
    )
    bot.reply_to(message, text, parse_mode="HTML")


@bot.message_handler(commands=["help"])
def help_command(message):
    text = (
        "❓ **BOT HELP**\n\n"
        "🤖 Automatic Mode:\n"
        "The bot creates one random game guess for each calculated period.\n\n"
        "⚙️ Commands:\n"
        "/start - Start bot\n"
        "/help - Show help\n"
        "/status - Show bot status"
    )
    bot.reply_to(message, text, parse_mode="HTML")


@bot.message_handler(commands=["status"])
def status_command(message):
    uptime = int(time.time() - bot_start_time)
    hours = uptime // 3600
    minutes = (uptime % 3600) // 60

    with state_lock:
        level = current_level
        rounds = total_rounds_played

    text = (
        "📊 **BOT STATUS**\n\n"
        "🟢 Status: `ONLINE`\n"
        f"⏳ Uptime: `{hours}h {minutes}m`\n"
        f"📈 Level: `{level}`\n"
        f"🔄 Rounds: `{rounds}`\n"
        f"📢 Channel ID: `{CHANNEL_ID}`"
    )
    bot.reply_to(message, text, parse_mode="HTML")

# ============================================================
# FLASK ROUTES
# ============================================================

@app.route("/")
def home():
    return "Telegram Channel Bot is online."


@app.route("/health")
def health():
    return {
        "status": "online",
        "uptime": int(time.time() - bot_start_time),
        "rounds": total_rounds_played,
    }

# ============================================================
# POLLING THREAD
# ============================================================

def run_bot():
    while True:
        try:
            print("Telegram polling started.")
            bot.infinity_polling(
                skip_pending=True,
                timeout=30,
                long_polling_timeout=30,
            )
        except Exception as error:
            print(f"Telegram polling error: {error}")
            time.sleep(5)

# ============================================================
# EXECUTION
# ============================================================

if __name__ == "__main__":
    # 1. Run Telegram polling daemon
    threading.Thread(target=run_bot, daemon=True).start()

    # 2. Run prediction publisher loop
    threading.Thread(target=automatic_prediction_loop, daemon=True).start()

    # 3. Run Flask server on main thread
    print("Starting Flask server...")
    app.run(host="0.0.0.0", port=10000)
