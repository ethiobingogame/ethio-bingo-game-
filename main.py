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

# የጨዋታው መሠረታዊ መረጃዎች
game_state = {
    "game_id": 656,
    "players_count": 0,          # ከ 0 የሚጀምር የተጫዋቾች ብዛት
    "ticket_price": 10.0,        # የካርታ ዋጋ (Stake)
    "commission_rate": 0.20,     # የኮሚሽን ቅናሽ (20%)
    "prize_pool": 0.0,           # አጠቃላይ ደራሽ (Derash)
    "game_status": "Waiting",    # Waiting, Active, Finished
    "timer": 45,                 # የሚጠበቀው ሰዓት/ሰከንድ
    "drawn_numbers": [],         # የተጠሩ ቁጥሮች
}

# የተጠቃሚዎች መረጃ እና ኪስ ቦርሳ (Wallet / Database Simulation)
users_db = {}
user_states = {}  # ተጠቃሚው አሁን ምን እየሰራ እንደሆነ ለመቆጣጠር

# ትክክለኞቹ የድርጅቱ አካውንቶች መረጃዎች
COMPANY_ACCOUNTS = {
    "telebirr": "📱 **ቴሌብር (Telebirr)**\nቁጥር: `0944123180`\nስም: Enyachew Amerga",
    "cbe": "🏦 **የንግድ ባንክ (CBE)**\nቁጥር: `1000682528641`\nስም: Enyachew Amerga"
}

# ----------------------------------------------------
# 2. የቴሌግራም ቦት ትዕዛዞች እና መስተጋብሮች
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
            "balance": 50.0,  # ለአዲስ ተጠቃሚ የናሙና ቦነስ
            "invited": 0
        }

    user_states[user_id] = None # ስቴቱን ማጽዳት

    markup = types.InlineKeyboardMarkup(row_width=2)
    btn_play = types.InlineKeyboardButton("🎮 ፕሌይ (Play)", callback_data="play_game")
    btn_balance = types.InlineKeyboardButton("💳 ቼክ ባላንስ", callback_data="check_balance")
    btn_deposit = types.InlineKeyboardButton("💰 ዲፖዚት", callback_data="deposit")
    btn_withdraw = types.InlineKeyboardButton("💸 ዊዝድሮው", callback_data="withdraw")
    btn_invite = types.InlineKeyboardButton("👥 ጓደኛ ጋበዝ", callback_data="invite_friend")
    
    markup.add(btn_play, btn_balance, btn_deposit, btn_withdraw, btn_invite)
    
    welcome_text = (
        f"🇪🇹 ሰላም **{first_name}**! እንኳን ወደ **Ethio Bingo Game** በደህና መጡ።\n\n"
        "የቴሌግራም አካውንትዎ በትክክል ተመዝግቧል!\n"
        "እባክዎ ከታች ከሚገኙት አማራጮች የሚፈልጉትን ይጫኑ፦"
    )
    bot.send_message(message.chat.id, welcome_text, parse_mode="Markdown", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    user_id = call.from_user.id
    if user_id not in users_db:
        users_db[user_id] = {"balance": 0.0, "invited": 0}

    if call.data == "play_game":
        bot.answer_callback_query(call.id)
        bot.send_message(call.message.chat.id, "🎮 ጨዋታውን ለመጀመር ከዚህ በታች ያለውን ሊንክ ይጠቀሙ ወይም አብሮ የተሰራውን Mini-App ይክፈቱ!")
    
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
    
    elif call.data == "invite_friend":
        bot.answer_callback_query(call.id)
        bot_username = bot.get_me().username
        ref_link = f"https://t.me/{bot_username}?start=ref_{user_id}"
        bot.send_message(call.message.chat.id, f"👥 ጓደኛዎን ለመጋበዝ ይጠቀሙበት:\n\n{ref_link}\n\nእያንዳንዱ ጓደኛ ሲገባ 5 ብር ቦነስ ያግኙ!")

# ----------------------------------------------------
# 3. ቴክስት እና የፎቶ (ስክሪንሻት) መልዕክቶችን ማስተናገጃ
# ----------------------------------------------------
@bot.message_handler(content_types=['text'])
def handle_text_messages(message):
    user_id = message.from_user.id
    if user_id not in users_db:
        users_db[user_id] = {"balance": 0.0, "invited": 0}

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
            elif amount < 50:
                bot.send_message(message.chat.id, "⚠️ ዝቅተኛው የማውጫ መጠን 50 ብር ነው። እባክዎ እንደገና ይሞክሩ:")
            else:
                bot.send_message(
                    message.chat.id, 
                    f"❌ **ባላንስ የለህም!**\n"
                    f"የጠየቁት መጠን ({amount} ብር) ካለዎት ቀሪ ባላንስ ({current_balance} ብር) ይበልጣል። እባክዎ በቂ ባላንስ ይኑርዎት።", 
                    parse_mode="Markdown"
                )
                user_states[user_id] = None
        except ValueError:
            bot.send_message(message.chat.id, "⚠️ እባክዎ ትክክለኛ የብር መጠን በቁጥር ብቻ ይጻፉ:")

@bot.message_handler(content_types=['photo'])
def handle_photo_messages(message):
    user_id = message.from_user.id
    if user_id not in users_db:
        users_db[user_id] = {"balance": 0.0, "invited": 0}

    state = user_states.get(user_id)

    if state == "waiting_for_screenshot":
        # ስክሪንሻቱ እንደገባ በሲሙሌሽን የተጠቃሚው አካውንት ላይ ብር ይጨምራል
        deposit_amount_simulated = 100.0 
        users_db[user_id]["balance"] += deposit_amount_simulated
        user_states[user_id] = None

        bot.send_message(
            message.chat.id,
            f"✅ **ስክሪንሻቱ በትክክል ተረጋግጧል!**\n"
            f"አካውንትዎ ላይ **{deposit_amount_simulated} ብር** ተጨምሯል።\n"
            f"አጠቃላይ ቀሪ ባላንስዎ: **{users_db[user_id]['balance']} ብር**",
            parse_mode="Markdown"
        )
    else:
        bot.send_message(message.chat.id, "📸 ፎቶ ደርሶናል፤ ነገር ግን አሁን የዲፖዚት ማረጋገጫ ሂደት ውስጥ አይደሉም። እባክዎ መጀመሪያ 'ዲፖዚት' የሚለውን ይጫኑ።")

# ----------------------------------------------------
# 4. የዌብ ጨዋታ ገጽታ (HTML & Mini-App Interface)
# ----------------------------------------------------
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="am">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Ethio Bingo Game</title>
    <style>
        body { font-family: Arial, sans-serif; background-color: #3b2a59; color: white; text-align: center; margin: 0; padding: 10px; }
        .container { background: #513682; padding: 15px; border-radius: 12px; box-shadow: 0px 4px 15px rgba(0,0,0,0.3); max-width: 450px; margin: auto; }
        h1 { font-size: 22px; margin-bottom: 10px; }
        .info-box { display: flex; justify-content: space-around; background: #422d6d; padding: 10px; border-radius: 8px; font-size: 14px; margin-bottom: 15px; }
        .grid-container { display: grid; grid-template-columns: repeat(10, 1fr); gap: 3px; margin-bottom: 15px; }
        .cell { background: #9c7bc2; padding: 8px 2px; font-size: 12px; border-radius: 4px; font-weight: bold; }
        .cell.called { background: #e94560; color: white; }
        .actions button { padding: 10px 15px; font-size: 14px; margin: 5px; cursor: pointer; border: none; border-radius: 6px; font-weight: bold; }
        .btn-join { background-color: #28a745; color: white; width: 45%; }
        .btn-start { background-color: #007bff; color: white; width: 45%; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🎮 Ethio Bingo Game</h1>
        
        <div class="info-box">
            <div>ግጥሚያ ID: <span id="game-id">{{ game.game_id }}</span></div>
            <div>ደራሽ: <span id="prize-pool">{{ game.prize_pool }}</span> ብር</div>
            <div>ተጫዋቾች: <span id="players-count">{{ game.players_count }}</span></div>
        </div>

        <div class="info-box">
            <div>ስታክ: {{ game.ticket_price }} ብር</div>
            <div>ሁኔታ: <span id="game-status">{{ game.game_status }}</span></div>
            <div>ሰዓት: <span id="timer">{{ game.timer }}</span> ሰ</div>
        </div>

        <div class="grid-container" id="bingo-board"></div>

        <div class="actions">
            <button class="btn-join" onclick="joinGame()">ይቀላቀሉ</button>
            <button class="btn-start" onclick="startGame()">ጨዋታ ጀምር</button>
        </div>
    </div>

    <script>
        const board = document.getElementById('bingo-board');
        for (let i = 1; i <= 100; i++) {
            const cell = document.createElement('div');
            cell.className = 'cell';
            cell.id = 'cell-' + i;
            cell.innerText = i;
            board.appendChild(cell);
        }

        function updateStatus() {
            fetch('/api/status')
                .then(res => res.json())
                .then(data => {
                    document.getElementById('players-count').innerText = data.players_count;
                    document.getElementById('prize-pool').innerText = data.prize_pool;
                    document.getElementById('game-status').innerText = data.game_status;
                    document.getElementById('timer').innerText = data.timer;
                    document.getElementById('game-id').innerText = data.game_id;

                    document.querySelectorAll('.cell').forEach(c => c.classList.remove('called'));
                    data.drawn_numbers.forEach(num => {
                        const cell = document.getElementById('cell-' + num);
                        if(cell) cell.classList.add('called');
                    });
                });
        }

        function joinGame() {
            fetch('/api/join', { method: 'POST', headers: { 'Content-Type': 'application/json' } })
            .then(res => res.json())
            .then(data => {
                alert(data.message);
                updateStatus();
            });
        }

        function startGame() {
            fetch('/api/start', { method: 'POST' })
            .then(res => res.json())
            .then(data => {
                alert(data.message);
                updateStatus();
            });
        }

        setInterval(updateStatus, 2000);
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE, game=game_state)

@app.route('/api/status', methods=['GET'])
def get_status():
    return jsonify(game_state)

@app.route('/api/join', methods=['POST'])
def join_game():
    game_state['players_count'] += 1
    total_collected = game_state['players_count'] * game_state['ticket_price']
    commission = total_collected * game_state['commission_rate']
    game_state['prize_pool'] = total_collected - commission
    
    return jsonify({
        "status": "success",
        "message": "ጨዋታውን በተሳካ ሁኔታ ተቀላቅለዋል!",
        "players_count": game_state['players_count']
    })

@app.route('/api/start', methods=['POST'])
def start_number_game():
    if game_state['players_count'] > 0:
        game_state['game_status'] = "Active"
        game_state['drawn_numbers'] = [8, 50, 14, 26, 41]
        return jsonify({"status": "success", "message": "Ethio Bingo ጨዋታ ተጀምሯል!"})
    return jsonify({"status": "error", "message": "እባክዎ መጀመሪያ ተጫዋቾች ይግቡ!"}), 400

# ----------------------------------------------------
# 5. አፕሊኬሽኑን ማስኬጃ (Background Bot + Flask Server)
# ----------------------------------------------------
def run_telegram_bot():
    try:
        bot.infinity_polling(none_stop=True)
    except Exception as e:
        print(f"Bot polling error: {e}")

if __name__ == '__main__':
    bot_thread = threading.Thread(target=run_telegram_bot)
    bot_thread.daemon = True
    bot_thread.start()

    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
