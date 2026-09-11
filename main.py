import os
import time
import datetime
import random
import threading

import pytz
import telebot
from flask import Flask


# ============================================================
# CONFIGURATION
# ============================================================

# Put your NEW Telegram bot token in the environment variable
BOT_TOKEN = os.getenv("8750268784:AAFiMexKhIRK1NidWa1KVUitkIMiJ337rOA")

# Example:
# CHANNEL_ID = -1001234567890
#
# For a public channel, you can alternatively use:
# CHANNEL_ID = "@YourChannelUsername"
CHANNEL_ID = os.getenv("-1002835568642")

WIN_STICKER_ID = os.getenv("CAACAgUAAxkBAAER4h1qo_aDagqTDFeZsvVfXRWkHL1gMQACxiAAAlKt-FSX-5IBfGtcPz0E", "")
LOSS_STICKER_ID = os.getenv("CAACAgUAAxkBAAER4h9qo_aX3jMiUFY5WnP-YiWldp1WOgACJg8AAhRQUVTAisD_A8dpDz0E", "")


if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN is missing.")

if not CHANNEL_ID:
    raise ValueError("CHANNEL_ID is missing.")


# Convert numeric channel ID from environment variable
try:
    CHANNEL_ID = int(CHANNEL_ID)
except ValueError:
    # Allows @ChannelUsername
    pass


bot = telebot.TeleBot(BOT_TOKEN)
app = Flask(__name__)


# ============================================================
# GLOBAL VARIABLES
# ============================================================

current_level = 1
total_rounds_played = 0

predictions = {}

bot_start_time = time.time()

state_lock = threading.Lock()


# ============================================================
# PERIOD CALCULATION
# ============================================================

def get_current_period_info():

    tz = pytz.timezone("Asia/Kolkata")

    now = datetime.datetime.now(tz)

    total_minutes = now.hour * 60 + now.minute

    sequence = total_minutes + 1

    date_string = now.strftime("%Y%m%d")

    period_id = f"{date_string}100{sequence:04d}"

    return period_id


# ============================================================
# GENERATE GAME GUESS
# ============================================================

def generate_prediction():

    number = random.randint(0, 9)

    # Color
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

        # Number 5
        color = "🟢🟣 GREEN + VIOLET"
        emoji = "🟢"


    # Big / Small
    if number >= 5:

        size = "📈 BIG"

    else:

        size = "📉 SMALL"


    return number, color, size, emoji


# ============================================================
# CREATE PREDICTION
# ============================================================

def create_prediction():

    period = get_current_period_info()

    number, color, size, emoji = generate_prediction()


    prediction = {
        "period": period,
        "number": number,
        "color": color,
        "size": size,
        "emoji": emoji,
        "created_at": time.time()
    }


    with state_lock:

        predictions[period] = prediction

        level = current_level


        # Keep only recent predictions
        if len(predictions) > 20:

            oldest = next(iter(predictions))

            del predictions[oldest]


    return prediction, level


# ============================================================
# SEND PREDICTION TO CHANNEL
# ============================================================

def send_prediction():

    try:

        prediction, level = create_prediction()

        period = prediction["period"]
        number = prediction["number"]
        color = prediction["color"]
        size = prediction["size"]
        emoji = prediction["emoji"]


        text = (
            "🔥 *WINGO 1 MIN* 🔥\n\n"

            f"📅 *PERIOD:* `{period}`\n\n"

            f"📊 *BIG/SMALL:* {size}\n"

            f"🎨 *COLOR:* {color}\n"

            f"🔢 *NUMBER:* {emoji} `{number}` {emoji}\n\n"

            f"📈 *LEVEL:* `{level}`\n\n"

            "⚠️ Random game guess — "
            "not guaranteed."
        )


        bot.send_message(
            CHANNEL_ID,
            text,
            parse_mode="Markdown"
        )


        print(
            f"Prediction sent successfully: {period}"
        )


    except Exception as error:

        print(
            f"Prediction sending error: {error}"
        )


# ============================================================
# AUTOMATIC 1-MINUTE SYSTEM
# ============================================================

def automatic_prediction_loop():

    print("Automatic prediction system started.")

    last_period = None


    while True:

        try:

            current_period = get_current_period_info()


            # Prevent duplicate posts
            if current_period != last_period:

                send_prediction()

                last_period = current_period


            # Check every 2 seconds
            time.sleep(2)


        except Exception as error:

            print(
                f"Automatic prediction error: {error}"
            )

            time.sleep(5)


# ============================================================
# START COMMAND
# ============================================================

@bot.message_handler(commands=["start"])
def start_command(message):

    text = (
        "🤖 *Wingo Channel Bot*\n\n"

        "🟢 Bot is online.\n\n"

        "This bot is configured to post "
        "automatically to the Telegram channel.\n\n"

        "Commands:\n"
        "/start\n"
        "/help\n"
        "/status"
    )


    bot.reply_to(
        message,
        text,
        parse_mode="Markdown"
    )


# ============================================================
# HELP COMMAND
# ============================================================

@bot.message_handler(commands=["help"])
def help_command(message):

    text = (
        "❓ *BOT HELP*\n\n"

        "🤖 Automatic Mode:\n"
        "The bot automatically creates one "
        "game guess for each calculated period.\n\n"

        "⚙️ Commands:\n"
        "/start - Start bot\n"
        "/help - Show help\n"
        "/status - Show bot status"
    )


    bot.reply_to(
        message,
        text,
        parse_mode="Markdown"
    )


# ============================================================
# STATUS COMMAND
# ============================================================

@bot.message_handler(commands=["status"])
def status_command(message):

    uptime = int(
        time.time() - bot_start_time
    )

    hours = uptime // 3600

    minutes = (
        uptime % 3600
    ) // 60


    with state_lock:

        level = current_level

        rounds = total_rounds_played


    text = (
        "📊 *BOT STATUS*\n\n"

        "🟢 Status: `ONLINE`\n"

        f"⏳ Uptime: `{hours}h {minutes}m`\n"

        f"📈 Level: `{level}`\n"

        f"🔄 Rounds: `{rounds}`\n"

        f"📢 Channel: `{CHANNEL_ID}`"
    )


    bot.reply_to(
        message,
        text,
        parse_mode="Markdown"
    )


# ============================================================
# FLASK SERVER
# ============================================================

@app.route("/")
def home():

    return "Telegram Channel Bot is online."


@app.route("/health")
def health():

    return {
        "status": "online",
        "uptime": int(
            time.time() - bot_start_time
        )
    }


# ============================================================
# TELEGRAM POLLING
# ============================================================

def run_bot():

    while True:

        try:

            print(
                "Telegram polling started."
            )


            bot.infinity_polling(
                skip_pending=True,
                timeout=30,
                long_polling_timeout=30
            )


        except Exception as error:

            print(
                f"Telegram polling error: {error}"
            )

            time.sleep(5)


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":


    # Telegram command thread
    telegram_thread = threading.Thread(
        target=run_bot,
        daemon=True
    )

    telegram_thread.start()


    # Automatic prediction thread
    prediction_thread = threading.Thread(
        target=automatic_prediction_loop,
        daemon=True
    )

    prediction_thread.start()


    # Web server
    port = int(
        os.getenv("PORT", "10000")
    )


    app.run(
        host="0.0.0.0",
        port=port
    )
