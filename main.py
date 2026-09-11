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

# ... (Keep your existing bot commands above this line) ...

# --- KEEP ALIVE SERVER ---
@app.route('/')
def home():
    return "I am alive!"

def run_bot():
    # skip_pending=True prevents old messages from flooding in
    bot.infinity_polling(skip_pending=True)

if __name__ == "__main__":
    # Start the Bot in a background thread
    t = threading.Thread(target=run_bot)
    t.start()

    # Start the Web Server on Port 10000 (Required for Render)
    app.run(host="0.0.0.0", port=10000)
