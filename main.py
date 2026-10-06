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
    {"stake": 10.0, "status": "Waiting", "timer": 42, "players": 21, "derash": 168},
    {"stake": 20.0, "status": "Ready", "timer": 45, "players": 6, "derash": 96},
    {"stake": 50.0, "status": "playing", "timer": 68, "players": 68, "derash": 2720}
]

users_db = {}

COMPANY_ACCOUNTS = {
    "telebirr": "📱 **ቴሌብር (Telebirr)**\nቁጥር: `0944123180`\nስም: Enyachew Amerga",
    "cbe": "🏦 **የንግድ ባንክ (CBE)**\nቁጥር: `1000682528641`\nስም: Enyachew Amerga"
}

# ----------------------------------------------------
# 2. የቴሌግራም ቦት ትዕዛዞች እና ሙሉ አማራጮች
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

    webapp_url = "https://your-app-name.onrender.com"
    
    markup = types.InlineKeyboardMarkup(row_width=2)
    btn_play = types.InlineKeyboardButton("🎮 Ethio Bingo ፕሌይ (Mini App)", web_app=types.WebAppInfo(url=webapp_url))
    btn_balance = types.InlineKeyboardButton("💳 ቼክ ባላንስ", callback_data="check_balance")
    btn_deposit = types.InlineKeyboardButton("💰 ዲፖዚት", callback_data="deposit")
    btn_withdraw = types.InlineKeyboardButton("💸 ዊዝድሮው", callback_data="withdraw")
    btn_invite = types.InlineKeyboardButton("👥 ጓደኛ ጋብዝ (Invite)", callback_data="invite_friend")
    btn_contact = types.InlineKeyboardButton("📞 እኛን ያግኙን", callback_data="contact_us")
    
    markup.add(btn_play, btn_balance, btn_deposit, btn_withdraw, btn_invite, btn_contact)
    
    welcome_text = (
        f"🇪🇹 ሰላም **{first_name}**! እንኳን ወደ **Ethio Bingo Game Bot** በደህና መጡ[span_0](start_span)[span_0](end_span)።\n\n"
        "እባክዎ ጨዋታውን ለመጀመር ወይም አካውንትዎን ለማስተዳደር ከታች ያሉትን ቁልፎች ይጠቀሙ፦"
    )
    bot.send_message(message.chat.id, welcome_text, parse_mode="Markdown", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    user_id = call.from_user.id
    if user_id not in users_db:
        users_db[user_id] = {"balance": 59.0, "invited": 0}

    if call.data == "check_balance":
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
        
    elif call.data == "withdraw":
        bot.answer_callback_query(call.id)
        bot.send_message(call.message.chat.id, "💸 ገንዘብ ለማውጣት (Withdraw) የሚፈልጉትን መጠን እና የባንክ/ቴሌብር ቁጥርዎን ይጻፉ።", parse_mode="Markdown")
        
    elif call.data == "invite_friend":
        bot.answer_callback_query(call.id)
        bot_username = bot.get_me().username
        invite_link = f"https://t.me/{bot_username}?start={user_id}"
        msg = f"👥 **ጓደኞ በመጋበዝ ሽልማት ያግኙ!**\n\nጓደኞችዎን በዚህ ሊንክ ይጋብዙ፦\n`{invite_link}`\n\nእያንዳንዱ የጋበዙት ሰው ሲመዘገብ ጉርሻ ያገኛሉ!"
        bot.send_message(call.message.chat.id, msg, parse_mode="Markdown")
        
    elif call.data == "contact_us":
        bot.answer_callback_query(call.id)
        bot.send_message(call.message.chat.id, "📞 **እኛን ያግኙን (Support)**\n\nማንኛውም ጥያቄ ወይም አስተያየት ካሎት በቦት አስተዳዳሪው በኩል ማግኘት ይችላሉ፦\n👉 @SupportUsername", parse_mode="Markdown")

# ----------------------------------------------------
# 3. የኢትዮ ቢንጎ ሚኒ-አፕ (1-200 ቦርዶች ምርጫ እና ትክክለኛ የቢንጎ ሰሌዳ)
# ----------------------------------------------------
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="am">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Ethio Bingo Mini App</title>
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; background-color: #3b2a59; color: white; margin: 0; padding: 10px; text-align: center; }
        .container { background: #513682; padding: 12px; border-radius: 12px; max-width: 420px; margin: auto; box-shadow: 0px 4px 15px rgba(0,0,0,0.3); }
        .header { display: flex; justify-content: space-between; align-items: center; background: #422d6d; padding: 10px 12px; border-radius: 8px; margin-bottom: 12px; font-size: 14px; }
        .wallet-badge { background: #e94560; padding: 4px 10px; border-radius: 6px; font-weight: bold; }
        .game-card { background: #422d6d; padding: 10px; border-radius: 8px; margin-bottom: 8px; display: flex; justify-content: space-between; align-items: center; font-size: 13px; }
        .btn-play { background-color: #f39c12; color: white; border: none; padding: 6px 14px; border-radius: 5px; font-weight: bold; cursor: pointer; }
        
        .lobby-header { display: flex; justify-content: space-between; padding: 0 5px 8px 5px; font-size: 12px; font-weight: bold; color: #dcd6f7; border-bottom: 1px solid #6c5ce7; margin-bottom: 8px; }

        /* 1 እስከ 200 ቦርዶች መምረጫ ግሪድ */
        .picker-grid { display: grid; grid-template-columns: repeat(10, 1fr); gap: 3px; margin: 8px 0; max-height: 260px; overflow-y: auto; padding: 5px; background: #422d6d; border-radius: 8px; }
        .num-cell { background: #6c5ce7; padding: 5px 0; border-radius: 3px; font-size: 11px; cursor: pointer; font-weight: bold; }
        .num-cell.selected { background: #e94560; color: white; }
        
        /* 5x5 የቢንጎ ቦርድ ገጽታ (ልክ እንደ ናሙናው) */
        .bingo-board { display: grid; grid-template-columns: repeat(5, 1fr); gap: 3px; background: #2c1e4a; padding: 6px; border-radius: 8px; margin-top: 8px; border: 2px solid #1abc9c; }
        .board-header-cell { background: #1abc9c; color: white; padding: 6px 0; border-radius: 3px; font-weight: bold; font-size: 13px; text-align: center; }
        .board-cell { background: #f1f2f6; color: #333; padding: 8px 2px; border-radius: 3px; font-weight: bold; font-size: 13px; text-align: center; cursor: pointer; }
        .board-cell.marked { background: #2ecc71; color: white; }
        .board-cell.free-cell { background: #e74c3c; color: white; font-size: 11px; }
        
        .btn-action { background: #2ecc71; color: white; border: none; padding: 10px; border-radius: 6px; font-weight: bold; cursor: pointer; margin-top: 8px; width: 100%; font-size: 14px; }
        .btn-secondary { background: #718093; color: white; border: none; padding: 6px 12px; border-radius: 5px; cursor: pointer; font-size: 12px; margin-top: 5px; }
        
        .top-info-bar { display: flex; justify-content: space-between; background: #422d6d; padding: 6px 10px; border-radius: 6px; font-size: 11px; margin-bottom: 8px; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <span style="font-weight: bold; font-size: 15px;">Ethio Bingo</span>
            <div class="wallet-badge">💰 <span id="user-balance">59</span> ETB</div>
        </div>

        <!-- የጨዋታዎች ዝርዝር (Lobby) -->
        <div id="view-lobby">
            <div class="lobby-header">
                <span style="width: 50px; text-align: left;">Stake</span>
                <span style="width: 60px;">Status</span>
                <span style="width: 50px;">Players</span>
                <span style="width: 60px;">Derash</span>
                <span style="width: 50px; text-align: right;">Action</span>
            </div>
            <div id="games-list-container"></div>
        </div>

        <!-- 1 እስከ 200 ቦርዶች መምረጫ ገጽ -->
        <div id="view-picker" style="display: none;">
            <div class="top-info-bar">
                <span>Stake: <b id="picker-stake">10</b> ETB</span>
                <span>ቦርድ ይምረጡ (ከ 1 እስከ 200)</span>
            </div>
            <div class="picker-grid" id="picker-grid"></div>
            <button class="btn-secondary" id="toggle-range-btn" onclick="toggleRange()">Show 100-200</button>
            <button class="btn-action" onclick="startBingoGame()">ቦርዱን አስጀምር (Start)</button>
            <button class="btn-secondary" onclick="showLobby()">ተመለስ</button>
        </div>

        <!-- የቢንጎ ጨዋታ ሰሌዳ (Board View) -->
        <div id="view-board" style="display: none;">
            <div class="top-info-bar">
                <span>ቦርድ #: <b id="board-selected-num" style="color: #f1c40f;">1</b></span>
                <span>ዕድል (Derash): <b style="color: #2ecc71;" id="board-derash-val">168 ETB</b></span>
            </div>
            <div style="background: #422d6d; padding: 6px 10px; border-radius: 6px; margin-bottom: 6px; display: flex; justify-content: space-between; align-items: center;">
                <span style="font-size: 12px;">የተጠራ ቁጥር (Current Call)</span>
                <b id="current-call" style="font-size: 15px; color: #f1c40f; background: #2c1e4a; padding: 3px 10px; border-radius: 4px;">B-12</b>
            </div>
            
            <div class="bingo-board" id="user-bingo-board"></div>
            
            <button class="btn-action" style="background: #e94560;" onclick="checkBingoWin()">BINGO! (ቢንጎ በል)</button>
            <button class="btn-secondary" onclick="showLobby()" style="width: 100%; margin-top: 6px;">ጨዋታውንተው (Leave)</button>
        </div>

        <div style="margin-top: 10px; font-size: 11px; color: #dcd6f7;">Ethio Bingo 2026</div>
    </div>

    <script>
        let chosenBoardId = 1;
        let showingSecondHalf = false;
        let boardNumbers = [];

        const games = [
            { stake: 10.0, status: "42s", players: 21, derash: 168 },
            { stake: 20.0, status: "Ready", players: 6, derash: 96 },
            { stake: 50.0, status: "playing", players: 68, derash: 2720 }
        ];

        function loadLobby() {
            const container = document.getElementById('games-list-container');
            container.innerHTML = '';
            games.forEach((g, index) => {
                let card = document.createElement('div');
                card.className = 'game-card';
                card.innerHTML = `
                    <span style="font-weight:bold; width: 50px; text-align: left;">${g.stake} ETB</span>
                    <span style="color: #f1c40f; width: 60px;">${g.status}</span>
                    <span style="width: 50px; text-align: center;">${g.players}</span>
                    <span style="color: #2ecc71; font-weight:bold; width: 60px;">${g.derash} ETB</span>
                    <button class="btn-play" style="width: 50px;" onclick="openPicker(${index})">Play</button>
                `;
                container.appendChild(card);
            });
        }

        function openPicker(index) {
            let g = games[index];
            chosenBoardId = 1;
            showingSecondHalf = false;
            
            document.getElementById('picker-stake').innerText = g.stake;
            document.getElementById('view-lobby').style.display = 'none';
            document.getElementById('view-picker').style.display = 'block';
            
            renderBoardPicker(1, 100);
        }

        function renderBoardPicker(startNum, endNum) {
            const grid = document.getElementById('picker-grid');
            grid.innerHTML = '';
            for (let i = startNum; i <= endNum; i++) {
                let cell = document.createElement('div');
                cell.className = 'num-cell';
                if (chosenBoardId === i) {
                    cell.classList.add('selected');
                }
                cell.innerText = i;
                cell.onclick = () => selectBoardId(i);
                grid.appendChild(cell);
            }
        }

        function selectBoardId(id) {
            chosenBoardId = id;
            renderBoardPicker(showingSecondHalf ? 101 : 1, showingSecondHalf ? 200 : 100);
        }

        function toggleRange() {
            showingSecondHalf = !showingSecondHalf;
            const btn = document.getElementById('toggle-range-btn');
            if (showingSecondHalf) {
                renderBoardPicker(101, 200);
                btn.innerText = "Show 1-100";
            } else {
                renderBoardPicker(1, 100);
                btn.innerText = "Show 100-200";
            }
        }

        function startBingoGame() {
            document.getElementById('view-picker').style.display = 'none';
            document.getElementById('view-board').style.display = 'block';
            document.getElementById('board-selected-num').innerText = chosenBoardId;
            
            const boardContainer = document.getElementById('user-bingo-board');
            boardContainer.innerHTML = '';
            
            // የ B-I-N-G-O አምድ ራሶች
            const headers = ['B', 'I', 'N', 'G', 'O'];
            headers.forEach(h => {
                let hCell = document.createElement('div');
                hCell.className = 'board-header-cell';
                hCell.innerText = h;
                boardContainer.appendChild(hCell);
            });

            // ናሙና ቁጥሮች (በቦርዱ መሠረት የሚሞሉ)
            boardNumbers = [
                6, 20, 39, 50, 71,
                12, 23, 34, 47, 72,
                11, 25, 'FREE', 49, 63,
                1, 27, 38, 60, 70,
                5, 26, 44, 53, 68
            ];

            boardNumbers.forEach((val, idx) => {
                let bCell = document.createElement('div');
                bCell.className = 'board-cell';
                if (val === 'FREE') {
                    bCell.innerText = '★ FREE';
                    bCell.classList.add('free-cell');
                    bCell.classList.add('marked');
                } else {
                    bCell.innerText = val;
                    bCell.onclick = () => {
                        bCell.classList.toggle('marked');
                    };
                }
                boardContainer.appendChild(bCell);
            });
        }

        function checkBingoWin() {
            // ሲስተሙ ቦርዱን አረጋግጦ ትክክለኛ አሸናፊ መሆን አለመሆኑን ያሳያል
            let markedCount = document.querySelectorAll('.board-cell.marked').length;
            if (markedCount >= 5) {
                alert('🎉 እንኳን ደስ አለዎት! ትክክለኛ ቢንጎ (BINGO) ነው! አሸናፊ ሆናለ።');
                showLobby();
            } else {
                alert('❌ የተሳሳተ ቢንጎ (Bogus)! ገና በቂ መስመር አልሞሉም፤ ከጨዋታው ተሰናብተዋል።');
                showLobby();
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
