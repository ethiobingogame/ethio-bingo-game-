import requests
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# የቴሌግራም ቦት ማዋቀሪያ (የእርስዎን የቦት ቶከን እና የአድሚን Chat ID እዚህ ያስገቡ)
BOT_TOKEN = "YOUR_TELEGRAM_BOT_TOKEN"
ADMIN_CHAT_ID = "YOUR_ADMIN_CHAT_ID"  
ADMIN_USERNAME = "@enyachew_19"        

# የጨዋታው አጠቃላይ ሁኔታ (Ethio Bingo Game)
game_state = {
    "bot_name": "Ethio Bingo Game",
    "players_count": 0,
    "prize_pool": 0,
    "stake": 10,
    "commission_rate": 0.20, 
    "banned_users": [],
    "user_balances": {}, 
    "used_ft_numbers": [], 
    "payment_accounts": {
        "cbe": {
            "bank_name": "የኢትዮጵያ ንግድ ባንክ (CBE)",
            "account_number": "1000682528641",
            "account_holder": "Enyachew Amerga"
        },
        "telebirr": {
            "service_name": "ቴሌብር (Telebirr)",
            "account_number": "0944123180",
            "account_holder": "Enyachew Amerga"
        }
    }
}

@app.route('/')
def index():
    try:
        return render_template('index.html')
    except Exception as e:
        return f"Template Error: index.html - {str(e)}", 500

@app.route('/api/status', methods=['GET'])
def get_status():
    return jsonify({
        "status": "success",
        "bot_name": game_state["bot_name"],
        "players_count": game_state["players_count"],
        "prize_pool": game_state["prize_pool"],
        "stakes": [10, 20, 50]
    })

@app.route('/api/accounts', methods=['GET'])
def get_accounts():
    return jsonify({
        "status": "success",
        "accounts": game_state["payment_accounts"]
    })

@app.route('/api/deposit', methods=['POST'])
def deposit():
    data = request.get_json(silent=True) or {}
    user_id = data.get('user_id', 'guest')
    amount = float(data.get('amount', 0))
    ft_number = data.get('ft_number', '').strip()
    
    if not ft_number:
        return jsonify({"status": "error", "message": "እባክዎ ትክክለኛ የትራንዛክሽን (FT) ቁጥር ያስገቡ!"})
    
    if ft_number in game_state["used_ft_numbers"]:
        return jsonify({"status": "error", "message": "ይህ የ FT ቁጥር ከዚህ በፊት ጥቅም ላይ ውሏል!"})
    
    net_amount = amount - (amount * game_state["commission_rate"])
    game_state["used_ft_numbers"].append(ft_number)
    
    if user_id not in game_state["user_balances"]:
        game_state["user_balances"][user_id] = 0
    game_state["user_balances"][user_id] += net_amount

    return jsonify({
        "status": "success",
        "message": f"ዲፖዚትዎ ተረጋግጧል! ብር {net_amount} ወደ አካውንትዎ ገብቷልም።",
        "balance": game_state["user_balances"][user_id]
    })

@app.route('/api/withdraw', methods=['POST'])
def withdraw():
    data = request.get_json(silent=True) or {}
    user_id = data.get('user_id', 'guest')
    amount = float(data.get('amount', 0))
    payment_method = data.get('payment_method', '') 
    account_number = data.get('account_number', '') 
    account_holder = data.get('account_holder', '') 
    
    current_balance = game_state["user_balances"].get(user_id, 0)
    
    if current_balance < amount:
        return jsonify({"status": "error", "message": f"በቂ ባላንስ የለዎትም! ያሎት ባላንስ: ብር {current_balance} ነው።"})
    
    game_state["user_balances"][user_id] -= amount
    
    admin_msg = (
        f"⚠️ **አዲስ የገንዘብ ማውጣት (Withdraw) ጥያቄ!**\n\n"
        f"👤 ተጠቃሚ ID: `{user_id}`\n"
        f"💰 የሚወጣው መጠን: ብር **{amount}**\n"
        f"💳 የባንክ አማራጭ: **{payment_method.upper()}**\n"
        f"🔢 አካውንት ቁጥር: `{account_number}`\n"
        f"👤 ስም: **{account_holder}**\n"
        f"🛠️ አድሚን: `{ADMIN_USERNAME}`"
    )
    
    try:
        requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage", json={
            "chat_id": ADMIN_CHAT_ID,
            "text": admin_msg,
            "parse_mode": "Markdown"
        })
    except Exception as e:
        print("Admin notification error:", e)
    
    return jsonify({
        "status": "success",
        "message": "የዊዝድሮ ጥያቄዎ ለአድሚን ተልኳል!",
        "remaining_balance": game_state["user_balances"][user_id]
    })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
