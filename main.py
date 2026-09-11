import telebot
import requests
import time
import threading
import random
from flask import Flask

# --- USER CONFIGURATION ---
# 1. Your Bot Token
API_TOKEN = '8750268784:AAFiMexKhIRK1NidWa1KVUitkIMiJ337rOA'

# 2. Your Sticker IDs
WIN_STICKER_ID = 'CAACAgUAAxkBAAER4h1qo_aDagqTDFeZsvVfXRWkHL1gMQACxiAAAlKt-FSX-5IBfGtcPz0E'
LOSS_STICKER_ID = 'CAACAgUAAxkBAAER4h9qo_aX3jMiUFY5WnP-YiWldp1WOgACJg8AAhRQUVTAisD_A8dpDz0E'

# 3. YOUR GAME API URL (The most important part)
# Example: "https://91clubapi.com"
GAME_API_URL = "https://draw.ar-lottery01.com/WinGo/WinGo_1M/GetHistoryIssuePage.json?ts=1789133040660" 

bot = telebot.TeleBot(API_TOKEN)
app = Flask(__name__)

# --- VARIABLES ---
last_processed_period = None
current_level = 1
current_prediction = {"period": None, "size": None}

def fetch_latest_result():
    """Fetches the latest result from the real game API."""
    try:
        # Standard Wingo API Headers (Mimics a real phone)
        headers = {
            'User-Agent': 'Mozilla/5.0 (Linux; Android 10; Mobile)',
            'Content-Type': 'application/json'
        }
        # Common Payload for Wingo History (Page 1)
        payload = {"pageSize": 10, "pageNo": 1, "typeId": 1, "language": 0}
        
        # We use POST because 99% of Wingo sites use POST for this
        response = requests.post(GAME_API_URL, json=payload, headers=headers, timeout=5)
        data = response.json()
        
        # Extract the latest item (usually index 0)
        latest_item = data['data']['list'][0]
        return {
            "period": str(latest_item['issueNumber']),
            "number": int(latest_item['number']),
            "size": "📈 BIG" if int(latest_item['number']) >= 5 else "📉 SMALL",
            "color": "🟢 GREEN" if int(latest_item['number']) in [1,3,7,9,5] else "🔴 RED"
        }
    except Exception as e:
        print(f"API Error: {e}")
        return None

def generate_prediction(next_period):
    """Generates a forecast for the NEXT period."""
    # (Here you can add complex logic based on history if you want)
    pred_num = random.choice([0,1,2,3,4,5,6,7,8,9])
    size = "📈 BIG" if pred_num >= 5 else "📉 SMALL"
    color = "🔴 RED" if pred_num in [0,2,4,6,8] else "🟢 GREEN"
    emoji = "🔴" if color == "🔴 RED" else "🟢"
    if pred_num == 0: color = "🔴🟣 VIOLET"
    if pred_num == 5: color = "🟢🟣 VIOLET"
    
    return {"period": next_period, "size": size, "color": color, "emoji": emoji, "number": pred_num}

def send_message_to_channel(msg):
    # Replace with your Channel ID or just reply to users
    # For now, this prints to console. In a real bot, you'd broadcast or wait for user.
    pass

# --- AUTOMATED GAME LOOP ---
def game_loop():
    global last_processed_period, current_level, current_prediction
    print("Background Game Monitor Started...")
    
    while True:
        try:
            # 1. Get Real Data
            result = fetch_latest_result()
            
            if result:
                latest_period = result['period']
                
                # If we found a NEW result we haven't seen yet
                if latest_period != last_processed_period:
                    print(f"New Result Detected: {latest_period} -> {result['number']}")
                    
                    # A. CHECK WIN/LOSS (If we made a prediction for this period)
                    if current_prediction['period'] == latest_period:
                        won = (current_prediction['size'] == result['size'])
                        
                        if won:
                            status = f"✅ **WIN!** Result: {result['number']} ({result['size']})"
                            current_level = 1 # Reset
                            # Send Win Sticker (You need to implement broadcast here if using channel)
                        else:
                            status = f"❌ **LOSS** Result: {result['number']} ({result['size']})"
                            current_level += 1 # Martingale
                            
                        # Here you would typically bot.send_message(CHANNEL_ID, status)
                        print(status)

                    # B. PREDICT NEXT ROUND
                    # Calculate next period ID (Simple +1 logic)
                    next_period_int = int(latest_period) + 1
                    next_period = str(next_period_int)
                    
                    pred = generate_prediction(next_period)
                    current_prediction = pred
                    
                    msg = (
                        f"🔥 **NEW PERIOD: {next_period}**\n"
                        f"📊 Prediction: {pred['size']}\n"
                        f"🎨 Color: {pred['color']}\n"
                        f"💰 Level: {current_level}"
                    )
                    # For demo: just printing. 
                    # To auto-send to a group, use: bot.send_message(CHAT_ID, msg)
                    print(msg) 
                    
                    last_processed_period = latest_period
                    
            time.sleep(5) # Check every 5 seconds
            
        except Exception as e:
            print(f"Loop Error: {e}")
            time.sleep(10)

# --- WEB SERVER ---
@app.route('/')
def index():
    return "Bot is watching the game..."

def run_flask():
    app.run(host="0.0.0.0", port=10000)

if __name__ == "__main__":
    # 1. Start Game Monitor
    threading.Thread(target=game_loop).start()
    
    # 2. Start Web Server
    threading.Thread(target=run_flask).start()
    
    # 3. Start Bot
    bot.infinity_polling(skip_pending=True)
