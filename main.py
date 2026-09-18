import requests
from flask import Flask, jsonify, request

app = Flask(__name__)

# የቴሌግራም ቦት ቶከን
TELEGRAM_BOT_TOKEN = "8970903838:AAHe0aHlIWVc94wAOB0lml8fM6BmVIEhaDM"

# የፈተና/ማሳያ ተጠቃሚዎች የውሂብ ማከማቻ
users_db = {
    "123456789": {"username": "ተጫዋች", "balance": 50.0}
}

# ትክክለኛው የባንክ መረጃዎች (በእንያቸው አመርጋ ስም)
BANK_DETAILS = {
    "account_holder": "እንያቸው አመርጋ (Enyachew Amerga)",
    "cbe": "10006825286441",
    "telebirr": "0944123180"
}

HOUSE_COMMISSION_PERCENT = 20  # ለቤቱ የሚቆረጥ 20% ኮሚሽን

@app.route('/')
def index():
    return "Ethio Bingo Mini App Backend with Telegram Buttons is Running Successfully!"

# የቴሌግራም ዌብሆክ (Webhook) እና /start መልስ መስጫ ከአዝራሮች ጋር
@app.route(f'/webhook/{TELEGRAM_BOT_TOKEN}', methods=['POST'])
def telegram_webhook():
    update = request.json
    if update and "message" in update:
        chat_id = update["message"]["chat"]["id"]
        text = update["message"].get("text", "")
        
        if text == "/start":
            bot_message = "እንኳን ወደ Ethio Bingo Game በደህና መጡ! ከታች ያሉትን አማራጮች በመጠቀም መጫወት እና አካውንትዎን ማስተዳደር ይችላሉ።"
            
            # ተጠቃሚው የሚጫናቸው ቆንጆ አዝራሮች (Inline Keyboards)
            keyboard = {
                "inline_keyboard": [
                    [{"text": "🎮 ቢንጎ ጨዋታ (Play Bingo)", "callback_data": "play_bingo"}],
                    [{"text": "💰 ዲፖዚት (Deposit)", "callback_data": "deposit"}, {"text": "💳 ዊዝድሮ (Withdraw)", "callback_data": "withdraw"}],
                    [{"text": "👥 ጓደኛ ጋብዝ (Invite Friend)", "callback_data": "invite"}],
                    [{"text": "📞 አግኙን (Contact Us)", "callback_data": "contact"}, {"text": "📝 ማመልከቻ (Apply)", "callback_data": "apply"}]
                ]
            }
            
            url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
            payload = {
                "chat_id": chat_id, 
                "text": bot_message,
                "reply_markup": keyboard
            }
            requests.post(url, json=payload)
            
    return jsonify({"status": "ok"})

# 1. የባላንስ ማረጋገጫ ኤፒአይ
@app.route('/api/get_balance', methods=['POST'])
def get_balance():
    data = request.json or {}
    user_id = str(data.get("user_id"))
    
    if user_id not in users_db:
        users_db[user_id] = {"username": data.get("username", "Guest"), "balance": 0.0}
    
    return jsonify({
        "status": "success",
        "balance": users_db[user_id]["balance"]
    })

# 2. የዲፖዚት (Deposit) መረጃ ማግኛ
@app.route('/api/deposit_info', methods=['GET'])
def deposit_info():
    return jsonify({
        "status": "success",
        "account_holder": BANK_DETAILS["account_holder"],
        "accounts": {
            "cbe": BANK_DETAILS["cbe"],
            "telebirr": BANK_DETAILS["telebirr"]
        },
        "instructions": f"እባክዎ ገንዘቡን በእንያቸው አመርጋ (Enyachew Amerga) ስም ባሉት አካውንቶች (CBE: {BANK_DETAILS['cbe']} ወይም Telebirr: {BANK_DETAILS['telebirr']}) ካስተላለፉ በኋላ የክፍያውን ስክሪንሾት ይላኩ።"
    })

# 3. የጨዋታ መክፈቻ እና የባላንስ ማረጋገጫ (Low Balance Check)
@app.route('/api/play_game', methods=['POST'])
def play_game():
    data = request.json or {}
    user_id = str(data.get("user_id"))
    ticket_price = float(data.get("ticket_price", 10.0))
    
    if user_id not in users_db:
        return jsonify({"status": "error", "message": "ተጠቃሚው አልተመዘገበም"})
    
    current_balance = users_db[user_id]["balance"]
    
    if current_balance < ticket_price:
        return jsonify({
            "status": "low_balance",
            "message": "Low Balance! የኪስ ቦርሳዎ ቀሪ ሂሳብ በቂ አይደለም።",
            "balance": current_balance,
            "required": ticket_price
        })
    
    users_db[user_id]["balance"] -= ticket_price
    
    return jsonify({
        "status": "success",
        "message": "ጨዋታው ተጀምሯል መልካም እድል!",
        "remaining_balance": users_db[user_id]["balance"]
    })

# 4. የድል ስሌት እና የ 20% ኮሚሽን ማስተካከያ (ቤት ኮሚሽን)
@app.route('/api/calculate_win', methods=['POST'])
def calculate_win():
    data = request.json or {}
    total_players = int(data.get("total_players", 10))
    ticket_price = float(data.get("ticket_price", 40.0))
    
    total_pool = total_players * ticket_price
    house_commission = total_pool * (HOUSE_COMMISSION_PERCENT / 100)
    winner_prize = total_pool - house_commission
    
    return jsonify({
        "total_pool": total_pool,
        "house_commission": house_commission,
        "winner_prize": winner_prize
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
