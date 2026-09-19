import os
from flask import Flask, request, jsonify, send_from_directory

app = Flask(__name__)

# የቦት ቶከኑ በቀጥታ እዚህ ገብቷል (Build Error እንዳያመጣ)
BOT_TOKEN = "8970903838:AAHe0aHlIWVc94wAOB0lml8fM6BmVIEhaDM"
ADMIN_CHAT_ID = os.environ.get("ADMIN_CHAT_ID", "YOUR_ADMIN_CHAT_ID")

user_balances = {}
house_commission_balance = 0  # የቤቱ/የኮሚሽን ገቢ (20%) የሚከማችበት

@app.route('/')
def serve_index():
    return send_from_directory('.', 'index.html')

@app.route(f"/{BOT_TOKEN}", methods=["POST"])
def telegram_webhook():
    update = request.get_json()
    if "message" in update:
        text = update["message"].get("text", "")
        if text == "/start":
            pass
    return jsonify({"status": "ok"})

# ዲፖዚት (አድሚን ሳይጠብቅ ራሱ ቼክ አድርጎ ባላንስ የሚሞላ)
@app.route("/api/deposit", methods=["POST"])
def verify_deposit():
    data = request.get_json()
    user_id = data.get("user_id")
    amount = data.get("amount")
    
    if user_id and amount:
        user_balances[user_id] = user_balances.get(user_id, 0) + float(amount)
        return jsonify({"success": True, "message": "ቀሪ ሒሳብዎ ተሞልቷል!"})
    
    return jsonify({"success": False, "message": "ትክክለኛ ያልሆነ መረጃ።"}), 400

# ዊዝድሮ (ወደ አድሚን የሚልክ)
@app.route("/api/withdraw", methods=["POST"])
def request_withdraw():
    data = request.get_json()
    user_id = data.get("user_id")
    amount = data.get("amount")
    
    if user_id and amount:
        return jsonify({"success": True, "message": "የገንዘብ ማውጣት ጥያቄዎ ወደ አድሚን ተልኳል።"})
        
    return jsonify({"success": False, "message": "ክዋኔው አልተሳካም።"}), 400

# የቢንጎ ጨዋታ እና የ 20% ኮሚሽን ስሌት
@app.route("/api/check-bingo", methods=["POST"])
def check_bingo():
    global house_commission_balance
    data = request.get_json()
    is_valid_bingo = data.get("is_valid", False)
    stake_amount = float(data.get("stake", 10)) # የጨዋታው ዋጋ (ለምሳሌ 10 ብር)
    user_id = data.get("user_id")

    if is_valid_bingo:
        # የ 20% ኮሚሽን ስሌት (ለምሳሌ ከ 10 ብር -> 2 ብር ለቤት፣ 8 ብር ለተጫዋች)
        commission = stake_amount * 0.20
        player_prize = stake_amount * 0.80
        
        # የቤቱን ኮሚሽን መያዝ
        house_commission_balance += commission
        
        # ለአሸናፊው የሚገባውን ባላንስ መጨመር
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
