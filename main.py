from flask import Flask, render_template, request, jsonify
import random

app = Flask(__name__)

# የማሳያ (Mock) የውሂብ መዋቅር (Database ምትክ)
# እዚህ ጋር የተጠቃሚዎችን መረጃ፣ ዩዘርኔም እና የኪስ ቦርሳ (Wallet Balance) እንይዛለን
users_db = {}

# የቢንጎ ስቴኮች እና የተለዋዋጭ (Dynamic) ተጫዋቾች እና ድራሽ መረጃ
stakes_data = {
    10: {"players": 14, "derash": 140},
    20: {"players": 8, "derash": 160},
    50: {"players": 22, "derash": 1100}
}

@app.route('/')
def index():
    return render_template('index.html')

# 1. ዩዘርኔም እና ባላንስ ማስጀመር / ማረጋገጥ
@app.route('/api/user', methods=['POST'])
def handle_user():
    data = request.json
    telegram_id = str(data.get('telegram_id'))
    username = data.get('username', 'ተጠቃሚ')
    
    if telegram_id not in users_db:
        # አዲስ ተጠቃሚ ሲመዘገብ የሚሰጠው የመጀመሪያ ባላንስ
        users_db[telegram_id] = {
            "username": username,
            "balance": 100.0,  # ዜሮ እንዳይሆን የመነሻ ባላንስ ተሰጥቷል
            "boards": []
        }
    
    return jsonify({
        "status": "success",
        "user": users_db[telegram_id]
    })

# 2. የስቴኮች እና የተጫዋቾች ብዛት መረጃ (Dynamic Update)
@app.route('/api/stakes', methods=['GET'])
def get_stakes():
    # በየሰዓቱ ወይም ሲጠየቅ ተጫዋቾች በራንደም እንዲቀያየሩ ማድረግ ይቻላል
    for stake in stakes_data:
        change = random.choice([-1, 0, 1, 2])
        stakes_data[stake]["players"] = max(2, stakes_data[stake]["players"] + change)
        stakes_data[stake]["derash"] = stakes_data[stake]["players"] * stake
        
    return jsonify(stakes_data)

# 3. ከ 1 እስከ 200 ያሉ ቦርዶች ውስጥ ቦርድ መምረጥ
@app.route('/api/select_board', methods=['POST'])
def select_board():
    data = request.json
    telegram_id = str(data.get('telegram_id'))
    stake = int(data.get('stake', 10))
    board_number = int(data.get('board_number', 1)) # ከ 1 እስከ 200 ያለው ምርጫ
    
    if telegram_id not in users_db:
        return jsonify({"status": "error", "message": "ተጠቃሚው አልተገኘም"})
    
    user = users_db[telegram_id]
    
    # የባላንስ በቂ መሆን አለመሆኑን ማረጋገጥ
    if user["balance"] < stake:
        return jsonify({"status": "error", "message": "የሂሳብ ሚዛንዎ በቂ አይደለም!"})
    
    # ስቴኩን ከባላንስ መቀነስ
    user["balance"] -= stake
    
    # የቢንጎ ቦርድ ቁጥሮችን ማመንጨት (5x5 ራንደም ቁጥሮች)
    board_numbers = random.sample(range(1, 76), 25)
    
    selected_board = {
        "board_number": board_number,
        "stake": stake,
        "numbers": board_numbers,
        "marked": [False] * 25
    }
    
    user["boards"].append(selected_board)
    
    return jsonify({
        "status": "success",
        "message": f"ቦርድ ቁጥር {board_number} በተሳካ ሁኔታ ተመርጧል!",
        "balance": user["balance"],
        "board": selected_board
    })

# 4. የቢንጎ ማረጋገጫ (Bingo Verification & Notification)
@app.route('/api/check_win', methods=['POST'])
def check_win():
    data = request.json
    telegram_id = str(data.get('telegram_id'))
    board_index = int(data.get('board_index', 0))
    
    if telegram_id not in users_db:
        return jsonify({"status": "error", "message": "ተጠቃሚው አልተገኘም"})
    
    user = users_db[telegram_id]
    try:
        board = user["boards"][board_index]
    except IndexError:
        return jsonify({"status": "error", "message": "ቦርዱ አልተገኘም"})
    
    # እዚህጋ የቢንጎ መስመር መሞላቱን ይረጋገጣል (ለማሳያ ያህል በዕድል 50 በመቶ አሸናፊነት)
    is_winner = random.choice([True, False])
    
    if is_winner:
        reward = board["stake"] * 8 # የድል ሽልማት ሂሳብ
        user["balance"] += reward
        return jsonify({
            "status": "win",
            "message": f"እንኳን ደስ አለዎት! {user['username']} ጨዋታውን አሸንፈዋል! ሽልማትዎ: {reward} ETB",
            "new_balance": user["balance"]
        })
    else:
        return jsonify({
            "status": "lose",
            "message": "ተሸንፈዋል! ቀጣይ ሰሌዳ ላይ ዕድልዎን ይሞክሩ።"
        })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)

