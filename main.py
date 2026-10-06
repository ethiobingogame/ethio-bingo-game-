from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# የጨዋታው አጠቃላይ ሁኔታ እና የክፍያ አካውንቶች (ንግድ ባንክ እና ቴሌብር)
game_state = {
    "players_count": 0,
    "prize_pool": 0,
    "stake": 10,  # የናሙና ስቴክ ዋጋ 
    "banned_users": [],
    "payment_accounts": {
        "cbe": {
            "bank_name": "የኢትዮጵያ ንግድ ባንክ (CBE)",
            "account_number": "1000XXXXXXXXXX",
            "account_holder": "እናቴ ቢንጎ"
        },
        "telebirr": {
            "service_name": "ቴሌብር (Telebirr)",
            "account_number": "09XXXXXXXX",
            "account_holder": "እናቴ ቢንጎ"
        }
    }
}

@app.route('/')
def index():
    return render_template('index.html')

# የባንክ እና የቴሌብር አካውንት መረጃዎችን ለተጠቃሚው ለማሳየት
@app.route('/api/accounts', methods=['GET'])
def get_accounts():
    return jsonify({
        "status": "success",
        "accounts": game_state["payment_accounts"]
    })

@app.route('/api/join', methods=['POST'])
def join_game():
    data = request.json or {}
    user_id = data.get('user_id', 'guest')
    transaction_ref = data.get('transaction_ref', '') # የባንክ ወይም የቴሌብር የትራንዛክሽን ቁጥር
    
    if user_id in game_state["banned_users"]:
        return jsonify({"status": "banned", "message": "በቀድሞ የተሳሳተ ቢንጎ ሙከራ ምክንያት በዚህ ጨዋታ ታግደዋል!"})
    
    # ተጫዋች ሲቀላቀል የሰዎች ብዛት እና የሽልማት መጠን (Prize Pool) በራስሰር ይጨምራል
    game_state["players_count"] += 1
    game_state["prize_pool"] = game_state["players_count"] * game_state["stake"]
    
    return jsonify({
        "status": "success",
        "players_count": game_state["players_count"],
        "prize_pool": game_state["prize_pool"],
        "message": "ክፍያዎ ተረጋግጦ ጨዋታውን ተቀላቅለዋል!"
    })

@app.route('/api/verify-bingo', methods=['POST'])
def verify_bingo():
    data = request.json or {}
    user_id = data.get('user_id', 'guest')
    marked_numbers = data.get('marked_numbers', [])
    
    # የቢንጎ ማረጋገጫ ሎጂክ
    is_winner = len(marked_numbers) >= 5 
    
    if is_winner:
        reward = game_state["prize_pool"]
        msg = f"🎉 ዊን! አሸንፈዋል! የተሰበሰበው ጠቅላላ ሽልማት ብር {reward} ወደ አካውንትዎ ተልኳል።"
        return jsonify({"status": "win", "message": msg, "reward": reward})
    else:
        # የተሳሳተ ቢንጎ ከሆነ ለአንድ ጨዋታ ማገድ
        if user_id not in game_state["banned_users"]:
            game_state["banned_users"].append(user_id)
        return jsonify({"status": "banned", "message": "❌ የተሳሳተ ቢንጎ! ለዚህ ጨዋታ ታግደዋል (Suspended for one game)።"})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
