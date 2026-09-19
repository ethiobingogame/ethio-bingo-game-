import os
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

BOT_TOKEN = "8970903838:AAHe0aHlIWVc94wAOB0lml8fM6BmVIEhaDM"
TELEGRAM_API_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"
RAILWAY_URL = "https://Ethio-bingo-game-production.up.railway.app"

user_balances = {}
house_commission_balance = 0

# 1. የ index.html ፋይልን በትክክል ከዋናው ማህደር ማንበቢያ
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
INDEX_PATH = os.path.join(BASE_DIR, 'index.html')

@app.route('/')
def serve_index():
    if os.path.exists(INDEX_PATH):
        with open(INDEX_PATH, 'r', encoding='utf-8') as f:
            return f.read()
    return "index.html file not found in root directory!", 404

# 2. ቴሌግራም ቦቱን ከ Railway ሰርቨር ጋር ማያያዣ (Webhook Setup)
@app.route('/setup')
def setup_webhook():
    webhook_url = f"{RAILWAY_URL}/{BOT_TOKEN}"
    response = requests.get(f"{TELEGRAM_API_URL}/setWebhook?url={webhook_url}")
    return response.json()

# 3. ቴሌግራም ቦቱ /start ሲባል ምላሽ እንዲሰጥ ማድረግ
@app.route(f"/{BOT_TOKEN}", methods=["POST"])
def telegram_webhook():
    update = request.get_json()
    if update and "message" in update:
        chat_id = update["message"]["chat"]["id"]
        text = update["message"].get("text", "")
        
        if text.startswith("/start"):
            welcome_message = (
                "ሰላም! ወደ ኢትዮ ቢንጎ (Ethio Bingo) እንኳን በደህና መጡ።\n\n"
                "ከዚህ በታች ያለውን የጨዋታ አገናኝ በመጠቀም ቦርዶችን በመምረጥ መጫወት ይጀምሩ!"
            )
            requests.post(f"{TELEGRAM_API_URL}/sendMessage", json={
                "chat_id": chat_id,
                "text": welcome_message
            })
            
    return jsonify({"status": "ok"})

# ዲፖዚት
@app.route("/api/deposit", methods=["POST"])
def verify_deposit():
    data = request.get_json()
    user_id = data.get("user_id")
    amount = data.get("amount")
    
    if user_id and amount:
        user_balances[user_id] = user_balances.get(user_id, 0) + float(amount)
        return jsonify({"success": True, "message": "ቀሪ ሒሳብዎ ተሞልቷል!"})
    
    return jsonify({"success": False, "message": "ትክክለኛ ያልሆነ መረጃ።"}), 400

# ዊዝድሮ
@app.route("/api/withdraw", methods=["POST"])
def request_withdraw():
    data = request.get_json()
    user_id = data.get("user_id")
    amount = data.get("amount")
    
    if user_id and amount:
        return jsonify({"success": True, "message": "የገንዘብ ማውጣት ጥያቄዎ ወደ አድሚን ተልኳል።"})
        
    return jsonify({"success": False, "message": "ክዋኔው አልተሳካም።"}), 400

# ቢንጎ እና 20% ኮሚሽን
@app.route("/api/check-bingo", methods=["POST"])
def check_bingo():
    global house_commission_balance
    data = request.get_json()
    is_valid_bingo = data.get("is_valid", False)
    stake_amount = float(data.get("stake", 10))
    user_id = data.get("user_id")

    if is_valid_bingo:
        commission = stake_amount * 0.20
        player_prize = stake_amount * 0.80
        house_commission_balance += commission
        
        if user_id:
            user_balances[user_id] = user_balances.get(user_id, 0) + player_prize

        return jsonify({
            "isBingo": True, 
            "message": "ቢንጎ! ትክክለኛ ማረጋገጫ።",
            "prize": player_prize,
            "commission": commission
        })
    else:
        return jsonify({"isBingo": False, "message": "የተሳሳተ ቢንጎ! ከዚህ ዙር ውጪ ሆናለ።"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
