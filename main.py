import telebot
import datetime
import pytz
import random

# --- CONFIGURATION ---
API_TOKEN = '8750268784:AAFiMexKhIRK1NidWa1KVUitkIMiJ337rOA'
WIN_STICKER_ID = 'CAACAgUAAxkBAAER4h1qo_aDagqTDFeZsvVfXRWkHL1gMQACxiAAAlKt-FSX-5IBfGtcPz0E'   # Get from @idstickerbot
LOSS_STICKER_ID = 'CAACAgUAAxkBAAER4h9qo_aX3jMiUFY5WnP-YiWldp1WOgACJg8AAhRQUVTAisD_A8dpDz0E' # Get from @idstickerbot

bot = telebot.TeleBot(8750268784:AAFiMexKhIRK1NidWa1KVUitkIMiJ337rOA)

# --- GLOBAL VARIABLES ---
# Martingale Strategy Level
current_level = 1
# History: [Period, Number, Big/Small, Color, ResultStatus]
game_history = []

def get_current_period_info():
    """
    Calculates the exact Wingo 1-Min Period Number for India (IST).
    Resets daily at 00:00 IST.
    Format: YYYYMMDD + 100 + Sequence (0001 to 1440)
    """
    tz = pytz.timezone('Asia/Kolkata')
    now = datetime.datetime.now(tz)
    
    # Calculate how many minutes have passed since midnight
    total_minutes = now.hour * 60 + now.minute
    
    # Period sequence is minute + 1 (1st minute is period 1)
    sequence = total_minutes + 1
    
    # Wingo 1 Min Standard ID Format: YYYYMMDD100xxxx
    date_str = now.strftime("%Y%m%d")
    period_id = f"{date_str}100{sequence:04d}"
    
    return period_id

def generate_prediction_data():
    """Generates a complete prediction: Number, Color, Size"""
    # Simple logic: Randomly pick weighted by recent history (Simulated)
    # In a real scenario, you would analyze 'game_history' here
    
    predicted_number = random.choice([0, 1, 2, 3, 4, 5, 6, 7, 8, 9])
    
    # Determine attributes based on the number
    if predicted_number in [0, 2, 4, 6, 8]:
        pred_color = "🔴 RED"
        color_emoji = "🔴"
    else:
        pred_color = "🟢 GREEN"
        color_emoji = "🟢"
        
    # Handling Violet logic (0 and 5)
    if predicted_number == 0:
        pred_color = "🔴🟣 RED+VIOLET"
    elif predicted_number == 5:
        pred_color = "🟢🟣 GREEN+VIOLET"
        
    if predicted_number >= 5:
        pred_size = "📈 BIG"
    else:
        pred_size = "📉 SMALL"
        
    return predicted_number, pred_color, pred_size, color_emoji

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "🇮🇳 **Wingo 1-Min Bot Ready!**\nUse /predict to start.")

@bot.message_handler(commands=['predict'])
def send_prediction(message):
    global current_prediction, last_period_id
    
    period_id = get_current_period_info()
    num, color, size, emoji = generate_prediction_data()
    
    # Save prediction to verify later
    current_prediction = {
        "period": period_id,
        "number": num,
        "color": color,
        "size": size
    }
    
    # --- THE PREDICTION MESSAGE ---
    msg = (
        f"🔥 **WINGO 1 MIN** 🔥\n\n"
        f"📅 **Period No:** `{period_id}`\n"
        f"📊 **BIG/SMALL:** {size}\n"
        f"🎨 **COLOR:** {color}\n"
        f"🔢 **NUMBER:** {emoji} {num} {emoji}\n\n"
        f"💰 **Level:** {current_level} (Maint: X{current_level})"
    )
    
    bot.reply_to(message, msg, parse_mode='Markdown')
    
    # Instruction for the user to input result
    bot.send_message(message.chat.id, "⏳ Wait for result... \n\nType `/result [Winning Number]` (e.g., `/result 6`) to check win/loss.")

@bot.message_handler(commands=['result'])
def check_result(message):
    global current_level, current_prediction
    
    try:
        # User types: /result 6
        winning_number = int(message.text.split()[1])
        
        # Determine winning attributes
        winning_size = "📈 BIG" if winning_number >= 5 else "📉 SMALL"
        
        # Check if our prediction was correct (Checking Size as main bet)
        # You can change this to check Color or Number if you prefer
        is_win = (current_prediction['size'] == winning_size)
        
        if is_win:
            result_text = f"✅ **WIN!** \nResult: {winning_number} was {winning_size}"
            sticker_to_send = WIN_STICKER_ID
            current_level = 1 # Reset to Level 1
        else:
            result_text = f"❌ **LOSS** \nResult: {winning_number} was {winning_size}"
            sticker_to_send = LOSS_STICKER_ID
            current_level += 1 # Increase Level (Martingale)
            
        # 1. Send the Result Text
        bot.reply_to(message, result_text, parse_mode='Markdown')
        
        # 2. Send the Sticker
        if sticker_to_send != 'YOUR_WIN_STICKER_FILE_ID_HERE':
            bot.send_sticker(message.chat.id, sticker_to_send)
            
        bot.send_message(message.chat.id, f"🔄 **New Level:** {current_level}\nUse /predict for next round.")
        
    except IndexError:
        bot.reply_to(message, "❌ Please type the winning number. Example: `/result 5`")
    except Exception as e:
        bot.reply_to(message, f"⚠️ Error: {e}")

# Run the bot
bot.infinity_polling()
