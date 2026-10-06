import requests
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# የቴሌግራም ቦት ማዋቀሪያ (የእርስዎን የቦት ቶከን እና የአድሚን Chat ID እዚህ ያስገቡ)
BOT_TOKEN = "YOUR_TELEGRAM_BOT_TOKEN"
ADMIN_CHAT_ID = "YOUR_ADMIN_CHAT_ID"  # የአድሚን ቴሌግራም ID ቁጥር
ADMIN_USERNAME = "@enyachew_19"        # የእርስዎ ትክክለኛ ዩዘርኔም (በሲስተም ሆነው ለማወቅ)

# የጨዋታው አጠቃላይ ሁኔታ እና ትክክለኛ የባንክ/ቴሌብር አካውንቶች
game_state = {
    "players_count": 0,
    "prize_pool": 0,
    "stake": 10,
    "commission_rate": 0.20, # 20% ኮሚሽን
    "banned_users": [],
    "user_balances": {}, # የተጠቃሚዎች ባላንስ ማከማቻ
    "used_ft_numbers": [], # ድግግሞሽ (Double FT) ለመከላከል
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
        return f"Template Error: {str(e)}", 500

# አካውንቶቹን ለማሳየት
@app.route('/api/accounts', methods=['GET'])
def get_accounts():
    return jsonify({
        "status": "success",
        "accounts": game_state["payment_accounts"]
    })

# 1. ዲፖዚት (በቦቱ በራሱ የሚረጋገጥ - አድሚን አያስፈልገውም)
@app.route('/api/deposit', methods=['POST'])
def deposit():
    data = request.get_json(silent=True) or {}
    user_id = data.get('user_id', 'guest')
    amount = float(data.get('amount', 0))
    ft_number = data.get('ft_number', '').strip()
    
    if not ft_number:
        return jsonify({"status": "error", "message": "እባክዎ ትክክለኛ የትራንዛክሽን (FT) ቁጥር ያስገቡ!"})
    
    # ድግግሞሽ (Double / Duplicate FT) ማረጋገጫ
    if ft_number in game_state["used_ft_numbers"]:
        return jsonify({"status": "error", "message": "ይህ የ FT ቁጥር ከዚህ በፊት ጥቅም ላይ ውሏል! እባክዎ ትክክለኛ ቁጥር ያስገቡ።"})
    
    # 20% ኮሚሽን ከተቀነሰ በኋላ የሚቀረው ሂሳብ
    net_amount = amount - (amount * game_state["commission_rate"])
    
    game_state["used_ft_numbers"].append(ft_number)
    
    if user_id not in game_state["user_balances"]:
        game_state["user_balances"][user_id] = 0
    game_state["user_balances"][user_id] += net_amount

    return jsonify({
        "status": "success",
        "message": f"ዲፖዚትዎ በራስ-ሰር ተረጋግጧል! ብር {net_amount} ወደ አካውንትዎ ገብቷል (20% ኮሚሽን ተቆርጧል)።",
        "balance": game_state["user_balances"][user_id]
    })

# 2. ዊዝድሮ (Withdrawal) ጥያቄ - ወደ አድሚን ብቻ የሚልክ
@app.route('/api/withdraw', methods=['POST'])
def withdraw():
    data = request.get_json(silent=True) or {}
    user_id = data.get('user_id', 'guest')
    amount = float(data.get('amount', 0))
    payment_method = data.get('payment_method', '') # cbe ወይም telebirr
    account_number = data.get('account_number', '') # የተጠቃሚው የባንክ/ቴሌብር ቁጥር
    account_holder = data.get('account_holder', '') # የተጠቃሚው ስም
    
    current_balance = game_state["user_balances"].get(user_id, 0)
    
    if current_balance < amount:
        return jsonify({"status": "error", "message": f"በቂ ባላንስ የለዎትም! ያሎት ባላንስ: ብር {current_balance} ነው።"})
    
    # ከባላንስ መቀነስ
    game_state["user_balances"][user_id] -= amount
    
    # ጥያቄውን በቀጥታ ወደ አድሚን ቴሌግራም መላክ
    admin_msg = (
        f"⚠️ **አዲስ የገንዘብ ማውጣት (Withdraw) ጥያቄ!**\n\n"
        f"👤 ተጠቃሚ ID: `{user_id}`\n"
        f"💰 የሚወጣው መጠን: ብር **{amount}**\n"
        f"💳 የባንክ/ቴሌብር አማራጭ: **{payment_method.upper()}**\n"
        f"🔢 አካውንት ቁጥር: `{account_number}`\n"
        f"👤 የሂሳብ ባለቤት ስም: **{account_holder}**\n"
        f"🛠️ አድሚን ዩዘርኔም: `{ADMIN_USERNAME}`"
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
        "message": "የዊዝድሮ ጥያቄዎ ለአድሚን ተልኳል። አድሚኑ አረጋግጦ ብሩን ይልክልዎታል!",
        "remaining_balance": game_state["user_balances"][user_id]
    })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
