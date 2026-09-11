import telebot
import datetime
import pytz
import random
import threading
import time
from flask import Flask

# --- CONFIGURATION ---
# Ensure your token is inside 'quotes'
API_TOKEN = '8750268784:AAFiMexKhIRK1NidWa1KVUitkIMiJ337rOA'
WIN_STICKER_ID = 'CAACAgUAAxkBAAER4h1qo_aDagqTDFeZsvVfXRWkHL1gMQACxiAAAlKt-FSX-5IBfGtcPz0E'   
LOSS_STICKER_ID = 'CAACAgUAAxkBAAER4h9qo_aX3jMiUFY5WnP-YiWldp1WOgACJg8AAhRQUVTAisD_A8dpDz0E' 

bot = telebot.TeleBot(API_TOKEN)
app = Flask(__name__)

# --- GLOBAL VARIABLES ---
current_level = 1
current_prediction = {}

def get_current_period_info():
    """Calculates the exact Wingo 1-Min Period Number for India (IST)."""
    tz = pytz.timezone('Asia/Kolkata')
    now = datetime.datetime.now(tz)
    total_minutes = now.hour * 60 + now.minute
    sequence = total_minutes + 1
    date_str = now.strftime("%Y%m%d")
    return f"{date_str}100{sequence:04d}"

def generate_prediction_data():
    """Generates a complete prediction: Number, Color, Size"""
    predicted_number = random.choice([0, 1, 2, 3, 4, 5, 6, 7, 8, 9])
    
    if predicted_number in [1, 3, 7, 9]:
        pred_color = "🟢 GREEN"
        color_emoji = "🟢"
    elif predicted_number in [2, 4, 6, 8]:
        pred_color = "🔴 RED"
        color_emoji = "🔴"
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

# --- TELEGRAM BOT COMMAND HANDLERS ---

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "🇮🇳 **Wingo 1-Min Bot Ready!**\nUse /predict to start.")

@bot.message_handler(commands=['predict'])
def send_prediction(message):
    global current_prediction
    
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
    bot.reply_to(message, msg, parse_mode='Markdown')
    bot.send_message(message.chat.id, "⏳ Wait for result... \n\nType `/result [Winning Number]` (e.g., `/result 6`) to check win/loss.")

@bot.message_handler(commands=['result'])
def check_result(message):
    global current_level, current_prediction
    
    try:
        winning_number = int(message.text.split()[1])
        winning_size = "📈 BIG" if winning_number >= 5 else "📉 SMALL"
        
        is_win = (current_prediction.get('size') == winning_size)
        
        if is_win:
            result_text = f"✅ **WIN!** \nResult: {winning_number} was {winning_size}"
            sticker_to_send = WIN_STICKER_ID
            current_level = 1 
        else:
            result_text = f"❌ **LOSS** \nResult: {winning_number} was {winning_size}"
            sticker_to_send = LOSS_STICKER_ID
            current_level += 1 
            
        bot.reply_to(message, result_text, parse_mode='Markdown')
        
        if sticker_to_send:
            bot.send_sticker(message.chat.id, sticker_to_send)
            
        bot.send_message(message.chat.id, f"🔄 **New Level:** {current_level}\nUse /predict for next round.")
        
    except Exception:
        bot.reply_to(message, "❌ Please type the winning number. Example: `/result 5`")

# --- KEEP ALIVE WEB SERVER FOR RENDER ---
@app.route('/')
def home():
    return "Wingo Predictor Bot Is Online!"

def run_bot():
    # Loop indefinitely to restart polling if it crashes
    while True:
        try:
            bot.infinity_polling(skip_pending=True)
        except Exception as e:
            time.sleep(5)

if __name__ == "__main__":
    # 1. Start the Telegram Bot in a separate background thread
    t = threading.Thread(target=run_bot)
    t.start()

    # 2. Start the Flask Web Server on the main thread
    # This must be LAST because app.run() blocks the script
    app.run(host="0.0.0.0", port=10000)
