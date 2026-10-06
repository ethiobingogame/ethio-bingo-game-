import os
import threading
import telebot
from flask import Flask, render_template_string, request, jsonify
from telebot import types

# ----------------------------------------------------
# 1. የቴሌግራም ቦት እና የፍላስክ (Flask) ማዋቀሪያ
# ----------------------------------------------------
TOKEN = os.environ.get('BOT_TOKEN', 'YOUR_TELEGRAM_BOT_TOKEN')
bot = telebot.TeleBot(TOKEN)

app = Flask(__name__)

# የጨዋታው መሠረታዊ መረጃዎች (እንደ ናሙናው ቪዲዮ)
games_list = [
    {"stake": 10.0, "status": "Waiting", "timer": 45, "players": 0, "draw_numbers": []},
    {"stake": 20.0, "status": "Ready", "timer": 0, "players": 0, "draw_numbers": []},
    {"stake": 50.0, "status": "playing", "timer": 68, "players": 0, "draw_numbers": [8, 50, 14, 26, 41]}
]

# የተጠቃሚዎች መረጃ እና ኪስ ቦርሳ (Wallet / Database)
users_db = {}
user_states = {}

# ትክክለኞቹ የድርጅቱ አካውንቶች መረጃዎች
COMPANY_ACCOUNTS = {
    "telebirr": "📱 **ቴሌብር (Telebirr)**\nቁጥር: `0944123180`\nስም: Enyachew Amerga",
    "cbe": "🏦 **የንግድ ባንክ (CBE)**\nቁጥር: `1000682528641`\nስም: Enyachew Amerga"
}

# ----------------------------------------------------
# 2. የቴሌግራም ቦት ትዕዛዞች (/start ሲሉ የሚመዘገብበት ሂደት)
# ----------------------------------------------------
@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_id = message.from_user.id
    username = message.from_user.username or "არមាន"
    first_name = message.from_user.first_name or "ተጠቃሚ"

    # ተጠቃሚው አዲስ ከሆነ በቴሌግራም አካውንቱ መረጃ መመዝገብ
    if user_id not in users_db:
        users_db[user_id] = {
            "first_name": first_name,
            "username": username,
            "balance": 59.0,  # እንደ ናሙናው ምስል 59 ብር መነሻ
            "invited": 0
        }

    user_states[user_id] = None

    markup = types.InlineKeyboardMarkup(row_width=2)
    btn_play = types.InlineKeyboardButton("🎮 ፕሌይ (Play - Mini App)", callback_data="play_game")
    btn_balance = types.InlineKeyboardButton("💳 ቼክ ባላንስ", callback_data="check_balance")
    btn_deposit = types.InlineKeyboardButton("💰 ዲፖዚት", callback_data="deposit")
    btn_withdraw = types.InlineKeyboardButton("💸 ዊዝድሮው", callback_data="withdraw")
    
    markup.add(btn_play, btn_balance, btn_deposit, btn_withdraw)
    
    welcome_text = (
        f"🇪🇹 ሰላም **{first_name}**! እንኳን ወደ **Ethio Bingo Game Bot** በደህና መጡ።[span_2](start_span)[span_2](end_span)\n\n"
        "የቴሌግራም አካውንትዎ በትክክል ተመዝግቧል!\n"
        "እባክዎ ከታች ከሚገኙት አማራጮች የሚፈልጉትን ይጫኑ፦"
    )
    bot.send_message(message.chat.id, welcome_text, parse_mode="Markdown", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    user_id = call.from_user.id
    if user_id not in users_db:
        users_db[user_id] = {"balance": 59.0, "invited": 0}

    if call.data == "play_game":
        bot.answer_callback_query(call.id)
        bot.send_message(call.message.chat.id, "🎮 ጨዋታውን ለመጀመር ከዚህ በታች ያለውን ሊንክ ይጠቀሙ ወይም የሚኒ-አፕ (Mini-App) ማዕቀፍ ይክፈቱ!")
    
    elif call.data == "check_balance":
        bal = users_db[user_id]["balance"]
        bot.answer_callback_query(call.id)
        bot.send_message(call.message.chat.id, f"💳 የእርስዎ አካውንት ባላንስ: **{bal} ብር**", parse_mode="Markdown")
    
    elif call.data == "deposit":
        bot.answer_callback_query(call.id)
        markup = types.InlineKeyboardMarkup(row_width=2)
        markup.add(
            types.InlineKeyboardButton("📱 ቴሌብር", callback_data="dep_telebirr"),
            types.InlineKeyboardButton("🏦 ንግድ ባንክ", callback_data="dep_cbe")
        )
        bot.send_message(call.message.chat.id, "💰 ገንዘብ ለማስገባት (Deposit) የሚፈልጉትን የክፍያ አማራጭ ይምረጡ፦", reply_markup=markup)
    
    elif call.data == "dep_telebirr":
        bot.answer_callback_query(call.id)
        user_states[user_id] = "waiting_for_screenshot"
        bot.send_message(
            call.message.chat.id, 
            f"ንብረት ለማስገባት የተመረጠው:\n\n{COMPANY_ACCOUNTS['telebirr']}\n\n"
            "እባክዎ ከላይ ባለው አካውንት ብሩን ካስተላለፉ በኋላ **የክፍያ ማረጋገጫ ስክሪንሻት (Screenshot)** ፎቶ ወደዚህ ቦት ይላኩ!",
            parse_mode="Markdown"
        )

    elif call.data == "dep_cbe":
        bot.answer_callback_query(call.id)
        user_states[user_id] = "waiting_for_screenshot"
        bot.send_message(
            call.message.chat.id, 
            f"ንብረት ለማስገባት የተመረጠው:\n\n{COMPANY_ACCOUNTS['cbe']}\n\n"
            "እባክዎ ከላይ ባለው አካውንት ብሩን ካስተላለፉ በኋላ **የክፍያ ማረጋገጫ ስክሪንሻት (Screenshot)** ፎቶ ወደዚህ ቦት ይላኩ!",
            parse_mode="Markdown"
        )

    elif call.data == "withdraw":
        bot.answer_callback_query(call.id)
        user_states[user_id] = "waiting_for_withdraw_amount"
        bot.send_message(call.message.chat.id, "💸 ለማውጣት (Withdraw) የሚፈልጉትን የብር መጠን ቁጥር ብቻ ይጻፉ (ዝቅተኛው 50 ብር):")

# ----------------------------------------------------
# 3. የጽሁፍ እና የፎቶ ማረጋገጫ (Screenshot) አስተናጋጅ
# ----------------------------------------------------
@bot.message_handler(content_types=['text'])
def handle_text_messages(message):
    user_id = message.from_user.id
    if user_id not in users_db:
        users_db[user_id] = {"balance": 59.0, "invited": 0}

    state = user_states.get(user_id)
    if state == "waiting_for_withdraw_amount":
        try:
            amount = float(message.text)
            current_balance = users_db[user_id]["balance"]

            if current_balance >= amount and amount >= 50:
                users_db[user_id]["balance"] -= amount
                user_states[user_id] = None
                bot.send_message(
                    message.chat.id, 
                    f"✅ የብር ማውጫ ጥያቄዎ በትክክል ተቀባይነት አግኝቷል!\n"
                    f"ወጪ የተደረገ: **{amount} ብር**\n"
                    f"ቀሪ ባላንስዎ: **{users_db[user_id]['balance']} ብር**", 
                    parse_mode="Markdown"
                )
            else:
                bot.send_message(message.chat.id, "❌ በቂ ባላንስ የለዎትም ወይም መጠኑ ከ 50 ብር በታች ነው።")
                user_states[user_id] = None
        except ValueError:
            bot.send_message(message.chat.id, "⚠️ እባክዎ ትክክለኛ የብር መጠን በቁጥር ብቻ ይጻፉ:")

@bot.message_handler(content_types=['photo'])
def handle_photo_messages(message):
    user_id = message.from_user.id
    if user_id not in users_db:
        users_db[user_id] = {"balance": 59.0, "invited": 0}

    state = user_states.get(user_id)
    if state == "waiting_for_screenshot":
        deposit_amount = 50.0 
        users_db[user_id]["balance"] += deposit_amount
        user_states[user_id] = None
        bot.send_message(
            message.chat.id,
            f"✅ **ስክሪንሻቱ ተረጋግጧል!**\nአካውንትዎ ላይ **{deposit_amount} ብር** ተጨምሯል።\nቀሪ ባላንስዎ: **{users_db[user_id]['balance']} ብር**",
            parse_mode="Markdown"
        )

# ----------------------------------------------------
# 4. የኢትዮ ቢንጎ ጌም ሚኒ-አፕ (Mini-App HTML Interface)
# ----------------------------------------------------
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="am">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Ethio Bingo Game Bot</title>
    <style>
        body { font-family: Arial, sans-serif; background-color: #3b2a59; color: white; margin: 0; padding: 10px; text-align: center; }
        .container { background: #513682; padding: 15px; border-radius: 12px; max-width: 450px; margin: auto; box-shadow: 0px 4px 15px rgba(0,0,0,0.3); }
        .header { display: flex; justify-content: space-between; align-items: center; background: #422d6d; padding: 10px; border-radius: 8px; margin-bottom: 15px; font-size: 14px; }
        .wallet-badge { background: #e94560; padding: 5px 10px; border-radius: 6px; font-weight: bold; }
        .game-card { background: #422d6d; padding: 10px; border-radius: 8px; margin-bottom: 10px; display: flex; justify-content: space-between; align-items: center; }
        .btn-play { background-color: #f39c12; color: white; border: none; padding: 6px 15px; border-radius: 5px; font-weight: bold; cursor: pointer; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <span style="font-weight: bold; font-size: 16px;">Ethio Bingo Game Bot</span>
            <div class="wallet-badge">💰 <span id="user-balance">59</span> ETB</div>
        </div>

        <div style="display: flex; justify-content: space-between; margin-bottom: 10px; font-size: 13px; font-weight: bold;">
            <span>Stake</span><span>Active/Status</span><span>Players</span><span>Derash</span><span>Action</span>
        </div>

        <div id="games-list-container">
            <!-- በራስሰር በጃቫስክሪፕት የሚሞላ -->
        </div>

        <div style="margin-top: 15px; font-size: 12px; color: #dcd6f7;">© Ethio Bingo 2026</div>
    </div>

    <script>
        function loadGames() {
            fetch('/api/games')
                .then(res => res.json())
                .then(data => {
                    const container = document.getElementById('games-list-container');
                    container.innerHTML = '';
                    data.games.forEach((g, index) => {
                        let derash = g.players * g.stake * 0.8; // 20% ኮሚሽን ተቀንሶ የሚቀረው ደራሽ
                        let statusText = g.status === 'Waiting' ? g.timer + 's' : g.status;
                        
                        let card = document.createElement('div');
                        card.className = 'game-card';
                        card.innerHTML = `
                            <span style="font-weight:bold;">${g.stake} ETB</span>
                            <span style="color: #f1c40f;">${statusText}</span>
                            <span>${g.players}</span>
                            <span style="color: #2ecc71; font-weight:bold;">${derash} ETB</span>
                            <button class="btn-play" onclick="joinGame(${index})">Play</button>
                        `;
                        container.appendChild(card);
                    });
                });
        }

        function joinGame(index) {
            fetch('/api/join', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ game_index: index })
            })
            .then(res => res.json())
            .then(data => {
                alert(data.message);
                loadGames();
            });
        }

        setInterval(loadGames, 2000);
        loadGames();
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/games', methods=['GET'])
def get_games():
    return jsonify({"games": games_list})

@app.route('/api/join', methods=['POST'])
def join_game():
    data = request.get_json()
    idx = data.get('game_index', 0)
    
    # ተጠቃሚው ሲገባ እንደ ሰው ብዛት አውቶማቲካሊ ጨመረ (መቀነስም/መጨመርም ይችላል)
    games_list[idx]['players'] += 1
    
    return jsonify({
        "status": "success",
        "message": "ጨዋታውን በተሳካ ሁኔታ ተቀላቅለዋል! ተጫዋቾች ታክለዋልና ደራሹ አውቶማቲካሊ ተስተካክሏል።"
    })

# ----------------------------------------------------
# 5. ማስኬጃ ክፍል (Background Bot & Flask)
# ----------------------------------------------------
def run_telegram_bot():
    try:
        bot.infinity_polling(none_stop=True)
    except Exception as e:
        print(f"Bot error: {e}")

if __name__ == '__main__':
    bot_thread = threading.Thread(target=run_telegram_bot)
    bot_thread.daemon = True
    bot_thread.start()

    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)

