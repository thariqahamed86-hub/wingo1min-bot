import telebot
import datetime
import pytz
import random
import threading
import time
from flask import Flask

# --- CONFIGURATION ---
API_TOKEN = '8750268784:AAFiMexKhIRK1NidWa1KVUitkIMiJ337rOA'
WIN_STICKER_ID = 'CAACAgUAAxkBAAER4h1qo_aDagqTDFeZsvVfXRWkHL1gMQACxiAAAlKt-FSX-5IBfGtcPz0E'   
LOSS_STICKER_ID = 'CAACAgUAAxkBAAER4h9qo_aX3jMiUFY5WnP-YiWldp1WOgACJg8AAhRQUVTAisD_A8dpDz0E' 

# Target Telegram Group ID
TARGET_GROUP_ID = 6842709265

bot = telebot.TeleBot(API_TOKEN)
app = Flask(__name__)

# --- GLOBAL GAME VARIABLES ---
current_level = 1
total_rounds_played = 0
current_prediction = {}
bot_start_time = time.time()

def get_current_period_info():
    """Calculates the exact Wingo 1-Min Period Number for India (IST)."""
    tz = pytz.timezone('Asia/Kolkata')
    now = datetime.datetime.now(tz)
    total_minutes = now.hour * 60 + now.minute
    sequence = total_minutes + 1
    date_str = now.strftime("%Y%m%d")
    return f"{date_str}100{sequence:04d}"

def generate_prediction_data():
    """Generates a pseudo-random prediction framework for size/color metrics."""
    predicted_number = random.choice([0, 1, 2, 3, 4, 5, 6, 7, 8, 9])
    
    if predicted_number in:
        pred_color = "🔴 RED"
        color_emoji = "🔴"
    elif predicted_number in:
        pred_color = "🟢 GREEN"
        color_emoji = "🟢"
    elif predicted_number == 0:
        pred_color = "🔴🟣 RED+VIOLET"
        color_emoji = "🔴"
    else:  # Number 5
        pred_color = "🟢🟣 GREEN+VIOLET"
        color_emoji = "🟢"
        
    if predicted_number >= 5:
        pred_size = "📈 BIG"
    else:
        pred_size = "📉 SMALL"
        
    return predicted_number, pred_color, pred_size, color_emoji

# --- TELEGRAM BOT ROUTING ENGINE ---

@bot.message_handler(commands=['start'])
def send_welcome(message):
    # Works in the group or in private chat
    welcome_text = (
        "🇮🇳 **Wingo 1-Min Prediction Engine Active**\n\n"
        "Welcome to the ultimate tracking matrix bot! I am configured to broadcast analytics directly into my target group.\n\n"
        "✨ **Type `/help` to see all available commands!**"
    )
    bot.reply_to(message, welcome_text, parse_mode='Markdown')

@bot.message_handler(commands=['help'])
def send_help(message):
    help_text = (
        "❓ **Wingo Bot Help & Commands Menu** ❓\n\n"
        "⚙️ **General Commands:**\n"
        "➡️ `/start` - Wake up the bot and view setup status.\n"
        "➡️ `/help` - Show this commands explanation directory.\n"
        "➡️ `/status` - Check active Martingale levels, uptime, and system health.\n\n"
        "🎮 **Group Analysis Commands (Admins Only):**\n"
        "➡️ `/predict` - Process and broadcast the next Wingo matrix calculation.\n"
        "➡️ `/result [0-9]` - Input the final winning digit to resolve stats (e.g., `/result 7`)."
    )
    bot.reply_to(message, help_text, parse_mode='Markdown')

@bot.message_handler(commands=['status'])
def send_status(message):
    # Calculate bot uptime
    uptime_seconds = int(time.time() - bot_start_time)
    uptime_hours = uptime_seconds // 3600
    uptime_minutes = (uptime_seconds % 3600) // 60
    
    status_text = (
        "📊 **SYSTEM STATUS REPORT** 📊\n\n"
        f"🟢 **Bot Health:** `Optimal` (Running 24/7)\n"
        f"⏳ **Uptime:** `{uptime_hours}h {uptime_minutes}m`\n"
        f"📈 **Current Martingale Level:** `Level {current_level}`\n"
        f"🔄 **Total Rounds Analyzed:** `{total_rounds_played}`\n"
        f"👥 **Linked Target Group ID:** `{TARGET_GROUP_ID}`"
    )
    bot.reply_to(message, status_text, parse_mode='Markdown')

@bot.message_handler(commands=['predict'])
def send_prediction(message):
    global current_prediction
    
    # Restrict group operations strictly to your specific Group ID
    if message.chat.id != TARGET_GROUP_ID:
        bot.reply_to(message, "❌ Prediction tools are locked outside the verified main target group.")
        return

    period_id = get_current_period_info()
    num, color, size, emoji = generate_prediction_data()
    
    current_prediction = {
        "period": period_id,
        "number": num,
        "color": color,
        "size": size
    }
    
    msg = (
        f"🔥 **WINGO 1 MIN** 🔥\n\n"
        f"📅 **Period No:** `{period_id}`\n"
        f"📊 **BIG/SMALL:** {size}\n"
        f"🎨 **COLOR:** {color}\n"
        f"🔢 **NUMBER:** {emoji} {num} {emoji}\n\n"
        f"💰 **Level:** {current_level} (Maint: X{current_level})"
    )
    
    bot.send_message(TARGET_GROUP_ID, msg, parse_mode='Markdown')

@bot.message_handler(commands=['result'])
def check_result(message):
    global current_level, current_prediction, total_rounds_played
    
    if message.chat.id != TARGET_GROUP_ID:
        return
        
    try:
        winning_number = int(message.text.split()[1])
        
        if winning_number < 0 or winning_number > 9:
            bot.send_message(TARGET_GROUP_ID, "❌ Number must be between 0 and 9.")
            return
            
        winning_size = "📈 BIG" if winning_number >= 5 else "📉 SMALL"
        is_win = (current_prediction.get('size') == winning_size)
        
        total_rounds_played += 1  # Increment total history count
        
        if is_win:
            result_text = f"✅ **WIN ROUND!** \nOutcome: Number {winning_number} was {winning_size}"
            sticker_to_send = WIN_STICKER_ID
            current_level = 1 
        else:
            result_text = f"❌ **LOSS ROUND** \nOutcome: Number {winning_number} was {winning_size}"
            sticker_to_send = LOSS_STICKER_ID
            current_level += 1 
            
        bot.send_message(TARGET_GROUP_ID, result_text, parse_mode='Markdown')
        bot.send_sticker(TARGET_GROUP_ID, sticker_to_send)
        bot.send_message(TARGET_GROUP_ID, f"🔄 **Next Investment Scale:** Level {current_level}\nUse `/predict` for upcoming matrix.")
        
    except (IndexError, ValueError):
        bot.send_message(TARGET_GROUP_ID, "❌ Please type the trailing winning value. Example: `/result 3`")
    except Exception as e:
        print(f"Operational error encountered: {e}")

# --- INTERNAL RENDER KEEP-ALIVE SERVER CONFIGURATION ---
@app.route('/')
def home():
    return "Wingo Target Group Engine Online."

def run_bot_polling():
    while True:
        try:
            bot.infinity_polling(skip_pending=True)
        except Exception as err:
            print(f"Polling loop reset due to network variation: {err}")
            time.sleep(5)

if __name__ == "__main__":
    polling_worker = threading.Thread(target=run_bot_polling)
    polling_worker.daemon = True
    polling_worker.start()

    app.run(host="0.0.0.0", port=10000)
