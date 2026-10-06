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

# የጨዋታው መሠረታዊ ዝርዝሮች
games_list = [
    {"stake": 10.0, "status": "Waiting", "timer": 45, "players": 18, "draw_numbers": []},
    {"stake": 20.0, "status": "Ready", "timer": 0, "players": 3, "draw_numbers": []},
    {"stake": 50.0, "status": "playing", "timer": 68, "players": 68, "draw_numbers": [8, 50, 14, 26, 41]}
]

users_db = {}
user_states = {}

COMPANY_ACCOUNTS = {
    "telebirr": "📱 **ቴሌብር (Telebirr)**\nቁጥር: `0944123180`\nስም: Enyachew Amerga",
    "cbe": "🏦 **የንግድ ባንክ (CBE)**\nቁጥር: `1000682528641`\nስም: Enyachew Amerga"
}

# ----------------------------------------------------
# 2. የቴሌግራም ቦት ትዕዛዞች
# ----------------------------------------------------
@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_id = message.from_user.id
    username = message.from_user.username or "არមាន"
    first_name = message.from_user.first_name or "ተጠቃሚ"

    if user_id not in users_db:
        users_db[user_id] = {
            "first_name": first_name,
            "username": username,
            "balance": 59.0,
            "invited": 0
        }

    markup = types.InlineKeyboardMarkup(row_width=2)
    btn_play = types.InlineKeyboardButton("🎮 Ethio Bingo ፕሌይ (Mini App)", callback_data="play_game")
    btn_balance = types.InlineKeyboardButton("💳 ቼክ ባላንስ", callback_data="check_balance")
    btn_deposit = types.InlineKeyboardButton("💰 ዲፖዚት", callback_data="deposit")
    btn_withdraw = types.InlineKeyboardButton("💸 ዊዝድሮው", callback_data="withdraw")
    
    markup.add(btn_play, btn_balance, btn_deposit, btn_withdraw)
    
    welcome_text = (
        f"🇪🇹 ሰላም **{first_name}**! እንኳን ወደ **Ethio Bingo Game Bot** በደህና መጡ።[span_0](start_span)[span_0](end_span)\n\n"
        "እባክዎ ጨዋታውን ለመጀመር ከታች ያለውን ሊንክ ወይም ቁልፍ ይጫኑ፦"
    )
    bot.send_message(message.chat.id, welcome_text, parse_mode="Markdown", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    user_id = call.from_user.id
    if user_id not in users_db:
        users_db[user_id] = {"balance": 59.0, "invited": 0}

    if call.data == "play_game":
        bot.answer_callback_query(call.id)
        bot.send_message(call.message.chat.id, "🎮 ጨዋታውን ለመጀመር ሚኒ-አፑን (Mini-App) ይክፈቱ።")
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
        bot.send_message(call.message.chat.id, "💰 ገንዘብ ለማስገባት የክፍያ አማራጭ ይምረጡ፦", reply_markup=markup)
    elif call.data == "dep_telebirr":
        bot.answer_callback_query(call.id)
        bot.send_message(call.message.chat.id, f"{COMPANY_ACCOUNTS['telebirr']}\n\nገንዘብ ካስተላለፉ በኋላ **የስክሪንሻት ፎቶ** ይላኩ!", parse_mode="Markdown")
    elif call.data == "dep_cbe":
        bot.answer_callback_query(call.id)
        bot.send_message(call.message.chat.id, f"{COMPANY_ACCOUNTS['cbe']}\n\nገንዘብ ካስተላለፉ በኋላ **የስክሪንሻት ፎቶ** ይላኩ!", parse_mode="Markdown")

# ----------------------------------------------------
# 3. ሙሉ የተስተካከለ የኢትዮ ቢንጎ ሚኒ-አፕ (ቁጥር መምረጫ እና ሰሌዳ)
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
        
        /* ቁጥር መምረጫ ግሪድ (Number Picker Grid) */
        .picker-grid { display: grid; grid-template-columns: repeat(10, 1fr); gap: 4px; margin-top: 10px; max-height: 250px; overflow-y: auto; padding: 5px; background: #422d6d; border-radius: 8px; }
        .num-cell { background: #6c5ce7; padding: 6px 0; border-radius: 4px; font-size: 12px; cursor: pointer; font-weight: bold; }
        .num-cell.selected { background: #e94560; color: white; }
        
        /* የጨዋታ ቦርድ ገጽታ */
        .bingo-board { display: grid; grid-template-columns: repeat(5, 1fr); gap: 5px; background: #2c1e4a; padding: 10px; border-radius: 8px; margin-top: 10px; }
        .board-cell { background: #f1f2f6; color: #333; padding: 8px; border-radius: 4px; font-weight: bold; font-size: 13px; }
        .board-cell.marked { background: #e94560; color: white; }
        
        .btn-action { background: #2ecc71; color: white; border: none; padding: 10px 20px; border-radius: 6px; font-weight: bold; cursor: pointer; margin-top: 10px; width: 100%; }
        .back-btn { background: #718093; color: white; border: none; padding: 6px 12px; border-radius: 5px; cursor: pointer; margin-top: 5px; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <span style="font-weight: bold; font-size: 16px;">Ethio Bingo Game Bot</span>
            <div class="wallet-badge">💰 <span id="user-balance">59</span> ETB</div>
        </div>

        <!-- 1. የጨዋታዎች ዝርዝር ማሳያ -->
        <div id="view-lobby">
            <div style="display: flex; justify-content: space-between; margin-bottom: 10px; font-size: 13px; font-weight: bold;">
                <span>Stake</span><span>Active/Status</span><span>Players</span><span>Derash</span><span>Action</span>
            </div>
            <div id="games-list-container"></div>
        </div>

        <!-- 2. ቁጥር መምረጫ (Number Selection View) -->
        <div id="view-picker" style="display: none;">
            <h3 style="margin: 5px 0; font-size: 15px;">ዕድለኛ ቁጥሮችዎን ይምረጡ (እስከ 15)</h3>
            <div style="font-size: 12px; color: #f1c40f; margin-bottom: 5px;">የተመረጡ: <span id="selected-count">0</span>/15</div>
            <div class="picker-grid" id="picker-grid"></div>
            <button class="btn-action" onclick="startGameWithNumbers()">Start Game & Continue ➔</button>
            <button class="back-btn" onclick="showLobby()">Back</button>
        </div>

        <!-- 3. ንቁ የቢንጎ ቦርድ (Active Playing Board View) -->
        <div id="view-board" style="display: none;">
            <h3 style="margin: 5px 0; font-size: 14px; color: #2ecc71;" id="game-status-title">ጨዋታ በመካሄድ ላይ...</h3>
            <div style="font-size: 13px; background: #422d6d; padding: 8px; border-radius: 6px; margin-bottom: 5px;">
                Current Call: <b id="current-call" style="font-size: 18px; color: #f1c40f;">B-8</b>
            </div>
            <div class="bingo-board" id="user-bingo-board"></div>
            <button class="btn-action" style="background: #e94560;" onclick="alert('BINGO! ተጫዋች አሸንፏል!')">🎯 BINGO!</button>
            <button class="back-btn" onclick="showLobby()">Leave Game</button>
        </div>

        <div style="margin-top: 15px; font-size: 12px; color: #dcd6f7;">© Ethio Bingo 2026</div>
    </div>

    <script>
        let selectedNumbers = [];
        let currentStakeIndex = 0;

        const games = [
            { stake: 10.0, status: "Waiting", timer: 45, players: 18, derash: 144 },
            { stake: 20.0, status: "Ready", timer: 0, players: 3, derash: 48 },
            { stake: 50.0, status: "playing", timer: 68, players: 68, derash: 2720 }
        ];

        function loadLobby() {
            const container = document.getElementById('games-list-container');
            container.innerHTML = '';
            games.forEach((g, index) => {
                let statusText = g.status === 'Waiting' ? g.timer + 's' : g.status;
                let card = document.createElement('div');
                card.className = 'game-card';
                card.innerHTML = `
                    <span style="font-weight:bold;">${g.stake} ETB</span>
                    <span style="color: #f1c40f;">${statusText}</span>
                    <span>${g.players}</span>
                    <span style="color: #2ecc71; font-weight:bold;">${g.derash} ETB</span>
                    <button class="btn-play" onclick="openPicker(${index})">Play</button>
                `;
                container.appendChild(card);
            });
        }

        function openPicker(index) {
            currentStakeIndex = index;
            selectedNumbers = [];
            document.getElementById('view-lobby').style.display = 'none';
            document.getElementById('view-picker').style.display = 'block';
            
            const grid = document.getElementById('picker-grid');
            grid.innerHTML = '';
            for (let i = 1; i <= 100; i++) {
                let cell = document.createElement('div');
                cell.className = 'num-cell';
                cell.innerText = i;
                cell.onclick = () => toggleNumber(i, cell);
                grid.appendChild(cell);
            }
            document.getElementById('selected-count').innerText = '0';
        }

        function toggleNumber(num, element) {
            const idx = selectedNumbers.indexOf(num);
            if (idx > -1) {
                selectedNumbers.splice(idx, 1);
                element.classList.remove('selected');
            } else {
                if (selectedNumbers.length < 15) {
                    selectedNumbers.push(num);
                    element.classList.add('selected');
                } else {
                    alert('እስከ 15 ቁጥሮች ብቻ መምረጥ ይችላሉ!');
                }
            }
            document.getElementById('selected-count').innerText = selectedNumbers.length;
        }

        function startGameWithNumbers() {
            if (selectedNumbers.length < 5) {
                alert('እባክዎ ቢያንስ 5 ቁጥሮችን ይምረጡ!');
                return;
            }
            document.getElementById('view-picker').style.display = 'none';
            document.getElementById('view-board').style.display = 'block';
            
            // የቢንጎ ሰሌዳውን ማቀናበር
            const boardContainer = document.getElementById('user-bingo-board');
            boardContainer.innerHTML = '';
            for (let i = 0; i < 25; i++) {
                let bCell = document.createElement('div');
                bCell.className = 'board-cell';
                if (i === 12) {
                    bCell.innerText = '★';
                    bCell.classList.add('marked');
                } else {
                    let randNum = selectedNumbers[i % selectedNumbers.length] || (i + 1);
                    bCell.innerText = randNum;
                    if (i % 3 === 0) bCell.classList.add('marked');
                }
                boardContainer.appendChild(bCell);
            }
        }

        function showLobby() {
            document.getElementById('view-picker').style.display = 'none';
            document.getElementById('view-board').style.display = 'none';
            document.getElementById('view-lobby').style.display = 'block';
            loadLobby();
        }

        loadLobby();
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

# ----------------------------------------------------
# 4. ማስኬጃ ክፍል
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
