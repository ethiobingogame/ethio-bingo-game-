import os
import random
import threading
import telebot
from flask import Flask, render_template_string, request, jsonify
from telebot import types

# ------------------------------------------------
TOKEN = '8981866243:AAGFL3eNKbWaP5a0ZXtiyXoscJhX168HDrI'
bot = telebot.TeleBot(TOKEN)

app = Flask(__name__)

users_db = {}
active_players_count = 1
current_derash = 168.0

ADMIN_USERNAME = "Enyachew-19"

COMPANY_ACCOUNTS = {
    "telebirr": "📱 **ቴሌብር (Telebirr)**\nቁጥር: `0944123180`\nስም: Enyachew Amerga",
    "cbe": "🏦 **የንግድ ባንክ (CBE)**\nቁጥር: `1000682528641`\nስም: Enyachew Amerga"
}

# ----------------------------------------------------
# 2. የቴሌግራም ቦት ትዕዛዞች እና ምናሌዎች
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
            "balance": 0.0,
            "invited": 0,
            "step": "registered"
        }

    # እባክዎ የራሳቸውን የ Render/Railway ሊንክ እዚህ ጋር ያስገቡ
    webapp_url = "https://ethio-bingo-game.onrender.com"
    
    markup = types.InlineKeyboardMarkup(row_width=1)
    btn_play = types.InlineKeyboardButton("🎮 Play game (/play)", web_app=types.WebAppInfo(url=webapp_url))
    btn_deposit = types.InlineKeyboardButton("💰 Deposit funds (/deposit)", callback_data="deposit")
    btn_withdraw = types.InlineKeyboardButton("💸 Withdraw funds (/withdraw)", callback_data="withdraw")
    btn_balance = types.InlineKeyboardButton("💳 Check balance (/balance)", callback_data="check_balance")
    btn_invite = types.InlineKeyboardButton("👥 Invite friends (/invite)", callback_data="invite_friend")
    btn_contact = types.InlineKeyboardButton("📞 Contact us (/contact)", callback_data="contact_us")
    
    markup.add(btn_play, btn_deposit, btn_withdraw, btn_balance, btn_invite, btn_contact)
    
    welcome_text = (
        f"🇪🇹 ሰላም **{first_name}**! እንኳን ወደ **ኢትዮ ቢንጎ ጌም (Ethio Bingo)** በደህና መጡ።\n\n"
        "እባክዎ ጨዋታውን ለመጀመር ወይም አካውንትዎን ለማስተዳደር ከታች ያሉትን ቁልፎች ይጠቀሙ፦"
    )
    bot.send_message(message.chat.id, welcome_text, parse_mode="Markdown", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    user_id = call.from_user.id
    if user_id not in users_db:
        users_db[user_id] = {"balance": 0.0, "invited": 0, "step": "registered"}

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
        bot.send_message(call.message.chat.id, "💰 ገንዘብ ለማስገባት የክፍያ አማራጭ ይምረጡ፦", parse_mode="Markdown")
        
    elif call.data == "dep_telebirr":
        bot.answer_callback_query(call.id)
        users_db[user_id]["step"] = "awaiting_deposit_screenshot"
        bot.send_message(call.message.chat.id, f"{COMPANY_ACCOUNTS['telebirr']}\n\nገንዘብ ካስተላለፉ በኋላ እባክዎ **የስክሪንሻት ፎቶ (Screenshot)** ይላኩ!", parse_mode="Markdown")
        
    elif call.data == "dep_cbe":
        bot.answer_callback_query(call.id)
        users_db[user_id]["step"] = "awaiting_deposit_screenshot"
        bot.send_message(call.message.chat.id, f"{COMPANY_ACCOUNTS['cbe']}\n\nገንዘብ ካስተላለፉ በኋላ እባክዎ **የስክሪንሻት ፎቶ (Screenshot)** ይላኩ!", parse_mode="Markdown")
        
    elif call.data == "withdraw":
        bot.answer_callback_query(call.id)
        markup = types.InlineKeyboardMarkup(row_width=2)
        markup.add(
            types.InlineKeyboardButton("📱 ቴሌብር", callback_data="wd_telebirr"),
            types.InlineKeyboardButton("🏦 ንግድ ባንክ", callback_data="wd_cbe")
        )
        bot.send_message(call.message.chat.id, "💸 ገንዘብ ለማውጣት (Withdraw) የባንክ/ቴሌብር አማራጭ ይምረጡ፦", parse_mode="Markdown")

    elif call.data == "wd_telebirr" or call.data == "wd_cbe":
        bot.answer_callback_query(call.id)
        users_db[user_id]["step"] = "awaiting_withdraw_amount"
        users_db[user_id]["wd_method"] = "ቴሌብር" if "telebirr" in call.data else "ንግድ ባንክ"
        bot.send_message(call.message.chat.id, f"ሊያወጡት የሚፈልጉትን የገንዘብ መጠን (Amount) እና የሂሳብ ቁጥርዎን ይጻፉ፦", parse_mode="Markdown")
        
    elif call.data == "invite_friend":
        bot.answer_callback_query(call.id)
        bot_username = bot.get_me().username
        invite_link = f"https://t.me/{bot_username}?start={user_id}"
        msg = f"👥 **ጓደኞ በመጋበዝ ሽልማት ያግኙ!**\n\nጓደኞችዎን በዚህ ሊንክ ይጋብዙ፦\n`{invite_link}`"
        bot.send_message(call.message.chat.id, msg, parse_mode="Markdown")
        
    elif call.data == "contact_us":
        bot.answer_callback_query(call.id)
        bot.send_message(call.message.chat.id, f"📞 **እኛን ያግኙን (Support)**\n\nአስተዳዳሪን ለማግኘት፦ @{ADMIN_USERNAME}", parse_mode="Markdown")

@bot.message_handler(content_types=['photo'])
def handle_docs_photo(message):
    user_id = message.from_user.id
    if user_id in users_db and users_db[user_id].get("step") == "awaiting_deposit_screenshot":
        users_db[user_id]["step"] = "registered"
        added_amount = 100.0
        users_db[user_id]["balance"] += added_amount
        
        bot.reply_to(message, f"✅ **Deposit Successful!**\n\nክፍያው ተረጋግጧል! 💰 **{added_amount} ብር** ወደ አካውንትዎ ገብቷል።", parse_mode="Markdown")
        
        admin_msg = f"🔔 **አዲስ ዲፖዚት ገብቷል!**\nተጠቃሚ: @{message.from_user.username or user_id}\nመጠን: {added_amount} ብር"
        try:
            bot.send_message(f"@{ADMIN_USERNAME}", admin_msg, parse_mode="Markdown")
        except Exception:
            pass
    else:
        bot.reply_to(message, "📸 የስክሪንሻት ፎቶ ተቀብለናል እናመሰግናለን!")

@bot.message_handler(func=lambda message: True)
def handle_text_messages(message):
    user_id = message.from_user.id
    if user_id in users_db and users_db[user_id].get("step") == "awaiting_withdraw_amount":
        text = message.text
        current_bal = users_db[user_id]["balance"]
        
        try:
            amount = float(text.split()[0])
        except ValueError:
            bot.reply_to(message, "❌ እባክዎ ትክክለኛ የቁጥር መጠን ይጻፉ (ለምሳሌ: 200)")
            return

        if current_bal >= amount:
            users_db[user_id]["balance"] -= amount
            users_db[user_id]["step"] = "registered"
            bot.reply_to(message, f"✅ **Withdrawal Request Successful!**\n\nየጠየቁት መጠን ({amount} ብር) ወደ ውጭ ለመላክ ወደ አስተዳዳሪ ተላልፏል።", parse_mode="Markdown")
            
            admin_msg = f"💸 **አዲስ የዊዝድሮ ጥያቄ!**\n\n👤 ተጠቃሚ: @{message.from_user.username or user_id}\n💵 መጠን: {amount} ብር\n🏦 አማራጭ: {users_db[user_id].get('wd_method')}"
            try:
                bot.send_message(f"@{ADMIN_USERNAME}", admin_msg, parse_mode="Markdown")
            except Exception:
                pass
        else:
            bot.reply_to(message, f"❌ በቂ ባላንስ የለዎትም! የእርስዎ አካውንት ባላንስ: **{current_bal} ብር** ብቻ ነው.", parse_mode="Markdown")

# ----------------------------------------------------
# 3. የኢትዮ ቢንጎ ሚኒ-አፕ (የተስተካከለ ስክሪፕት እና ቆጣሪ)
# ----------------------------------------------------
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="am">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Ethio Bingo Mini App</title>
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background-color: #3b2a59; color: white; margin: 0; padding: 10px; text-align: center; }
        .container { background: #513682; padding: 12px; border-radius: 12px; max-width: 420px; margin: auto; box-shadow: 0px 4px 15px rgba(0,0,0,0.3); }
        .header { display: flex; justify-content: space-between; align-items: center; background: #422d6d; padding: 10px 12px; border-radius: 8px; margin-bottom: 12px; font-size: 14px; }
        .wallet-badge { background: #e94560; padding: 4px 10px; border-radius: 6px; font-weight: bold; }
        .game-card { background: #422d6d; padding: 10px; border-radius: 8px; margin-bottom: 8px; display: flex; justify-content: space-between; align-items: center; font-size: 13px; }
        .btn-play { background-color: #f39c12; color: white; border: none; padding: 6px 14px; border-radius: 5px; font-weight: bold; cursor: pointer; }
        
        .lobby-header { display: flex; justify-content: space-between; padding: 0 5px 8px 5px; font-size: 12px; font-weight: bold; color: #dcd6f7; border-bottom: 1px solid #6c5ce7; margin-bottom: 8px; }

        .picker-grid { display: grid; grid-template-columns: repeat(10, 1fr); gap: 3px; margin: 8px 0; max-height: 220px; overflow-y: auto; padding: 5px; background: #422d6d; border-radius: 8px; }
        .num-cell { background: #6c5ce7; padding: 6px 0; border-radius: 3px; font-size: 11px; cursor: pointer; font-weight: bold; text-align: center; }
        .num-cell.selected { background: #e94560; color: white; }
        
        .bingo-board { display: grid; grid-template-columns: repeat(5, 1fr); gap: 3px; background: #2c1e4a; padding: 6px; border-radius: 8px; margin-top: 8px; border: 2px solid #1abc9c; }
        .board-header-cell { background: #1abc9c; color: white; padding: 6px 0; border-radius: 3px; font-weight: bold; font-size: 13px; text-align: center; }
        .board-cell { background: #f1f2f6; color: #333; padding: 8px 2px; border-radius: 3px; font-weight: bold; font-size: 13px; text-align: center; cursor: pointer; }
        .board-cell.marked { background: #2ecc71; color: white; }
        .board-cell.free-cell { background: #e74c3c; color: white; font-size: 11px; }
        
        .btn-action { background: #2ecc71; color: white; border: none; padding: 10px; border-radius: 6px; font-weight: bold; cursor: pointer; margin-top: 8px; width: 100%; font-size: 14px; }
        .btn-secondary { background: #718093; color: white; border: none; padding: 6px 12px; border-radius: 5px; cursor: pointer; font-size: 12px; margin-top: 5px; width: 100%; }
        
        .top-info-bar { display: flex; justify-content: space-between; background: #422d6d; padding: 6px 10px; border-radius: 6px; font-size: 11px; margin-bottom: 8px; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <span style="font-weight: bold; font-size: 15px;">ኢትዮ ቢንጎ (Ethio Bingo)</span>
            <div class="wallet-badge">💰 <span id="user-balance">0.00</span> ETB</div>
        </div>

        <!-- ሎቢ (Lobby View) -->
        <div id="view-lobby">
            <div class="lobby-header">
                <span style="width: 50px; text-align: left;">Stake</span>
                <span style="width: 60px;">Timer</span>
                <span style="width: 50px;">Players</span>
                <span style="width: 60px;">Derash</span>
                <span style="width: 50px; text-align: right;">Action</span>
            </div>
            <div id="games-list-container"></div>
        </div>

        <!-- 200 ቦርዶች መምረጫ (Picker View) -->
        <div id="view-picker" style="display: none;">
            <div class="top-info-bar">
                <span>Stake: <b id="picker-stake">10</b> ETB</span>
                <span>ቆጣሪ: <b id="countdown-timer" style="color: #f1c40f; font-size: 14px;">45</b> ሰከንድ</span>
            </div>
            <div style="font-size: 12px; margin-bottom: 5px; color: #f1c40f;">ከ 1 እስከ 200 ቦርዶች አንዱን ይምረጡ</div>
            <div class="picker-grid" id="picker-grid"></div>
            <button class="btn-secondary" id="toggle-range-btn" onclick="toggleRange()">Show 100-200</button>
            <button class="btn-action" onclick="startBingoGame()">ቦርዱን አስጀምር (Start)</button>
            <button class="btn-secondary" onclick="showLobby()" style="margin-top: 5px;">ተመለስ (Back)</button>
        </div>

        <!-- የቢንጎ ጨዋታ ሰሌዳ (Board View) -->
        <div id="view-board" style="display: none;">
            <div class="top-info-bar">
                <span>ቦርድ #: <b id="board-selected-num" style="color: #f1c40f;">1</b></span>
                <span>ዕድል (Derash): <b style="color: #2ecc71;" id="board-derash-val">168 ETB</b></span>
            </div>
            <div style="background: #422d6d; padding: 6px 10px; border-radius: 6px; margin-bottom: 6px; display: flex; justify-content: space-between; align-items: center;">
                <span style="font-size: 12px;">የተጠራ ቁጥር (Call)</span>
                <b id="current-call" style="font-size: 15px; color: #f1c40f; background: #2c1e4a; padding: 3px 10px; border-radius: 4px;">መጠባበቂያ...</b>
            </div>
            
            <div class="bingo-board" id="user-bingo-board"></div>
            
            <button class="btn-action" style="background: #e94560;" onclick="checkBingoWin()">BINGO! (ቢንጎ በል)</button>
            <button class="btn-secondary" onclick="showLobby()" style="margin-top: 6px;">ተመለስ / Leave</button>
        </div>
    </div>

    <script>
        let chosenBoardId = 1;
        let showingSecondHalf = false;
        let timerInterval = null;
        let timeLeft = 45;
        let callingInterval = null;

        const games = [
            { stake: 10.0, players: 1, derash: 168.0 },
            { stake: 20.0, players: 1, derash: 336.0 },
            { stake: 50.0, players: 1, derash: 840.0 }
        ];

        function loadLobby() {
            const container = document.getElementById('games-list-container');
            container.innerHTML = '';
            games.forEach((g, index) => {
                let card = document.createElement('div');
                card.className = 'game-card';
                card.innerHTML = `
                    <span style="font-weight:bold; width: 50px; text-align: left;">${g.stake} ETB</span>
                    <span style="color: #f1c40f; width: 60px;">45 ሰከንድ</span>
                    <span style="width: 50px; text-align: center;">${g.players}</span>
                    <span style="color: #2ecc71; font-weight:bold; width: 60px;">${g.derash} ETB</span>
                    <button class="btn-play" style="width: 50px;" onclick="openPicker(${index})">Play</button>
                `;
                container.appendChild(card);
            });
        }

        function openPicker(index) {
            chosenBoardId = 1;
            showingSecondHalf = false;
            timeLeft = 45;
            
            document.getElementById('picker-stake').innerText = games[index].stake;
            document.getElementById('board-derash-val').innerText = games[index].derash + " ETB";
            
            document.getElementById('view-lobby').style.display = 'none';
            document.getElementById('view-picker').style.display = 'block';
            document.getElementById('view-board').style.display = 'none';
            
            renderBoardPicker(1, 100);
            
            if (timerInterval) clearInterval(timerInterval);
            let timerEl = document.getElementById('countdown-timer');
            if (timerEl) timerEl.innerText = timeLeft;

            timerInterval = setInterval(() => {
                timeLeft--;
                if (timerEl) {
                    timerEl.innerText = timeLeft;
                }
                if (timeLeft <= 0) {
                    clearInterval(timerInterval);
                    startBingoGame();
                }
            }, 1000);
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
                cell.onclick = (function(boardId) {
                    return function() {
                        chosenBoardId = boardId;
                        renderBoardPicker(showingSecondHalf ? 101 : 1, showingSecondHalf ? 200 : 100);
                    };
                })(i);
                grid.appendChild(cell);
            }
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

        function generateUniqueBoard(id) {
            let s = (n) => Math.abs(Math.sin(id * 99 + n * 33) * 10000);
            let b = [], i = [], n = [], g = [], o = [];
            while(b.length < 5) { let val = Math.floor(s(b.length) % 15) + 1; if(!b.includes(val)) b.push(val); }
            while(i.length < 5) { let val = Math.floor(s(i.length + 10) % 15) + 16; if(!i.includes(val)) i.push(val); }
            while(n.length < 4) { let val = Math.floor(s(n.length + 20) % 15) + 31; if(!n.includes(val)) n.push(val); }
            while(g.length < 5) { let val = Math.floor(s(g.length + 30) % 15) + 46; if(!g.includes(val)) g.push(val); }
            while(o.length < 5) { let val = Math.floor(s(o.length + 40) % 15) + 61; if(!o.includes(val)) o.push(val); }
            n.splice(2, 0, 'FREE');
            let board = [];
            for(let r = 0; r < 5; r++) board.push(b[r], i[r], n[r], g[r], o[r]);
            return board;
        }

        function startBingoGame() {
            if (timerInterval) clearInterval(timerInterval);
            document.getElementById('view-lobby').style.display = 'none';
            document.getElementById('view-picker').style.display = 'none';
            document.getElementById('view-board').style.display = 'block';
            
            document.getElementById('board-selected-num').innerText = chosenBoardId;
            
            const boardContainer = document.getElementById('user-bingo-board');
            boardContainer.innerHTML = '';
            
            ['B', 'I', 'N', 'G', 'O'].forEach(h => {
                let hc = document.createElement('div');
                hc.className = 'board-header-cell';
                hc.innerText = h;
                boardContainer.appendChild(hc);
            });

            let boardValues = generateUniqueBoard(chosenBoardId);
            boardValues.forEach(val => {
                let cell = document.createElement('div');
                cell.className = 'board-cell';
                if (val === 'FREE') {
                    cell.innerText = '★ FREE';
                    cell.classList.add('free-cell', 'marked');
                } else {
                    cell.innerText = val;
                    cell.onclick = function() {
                        this.classList.toggle('marked');
                    };
                }
                boardContainer.appendChild(cell);
            });

            let letters = ['B', 'I', 'N', 'G', 'O'];
            if (callingInterval) clearInterval(callingInterval);
            callingInterval = setInterval(() => {
                let lIdx = Math.floor(Math.random() * 5);
                let num = Math.floor(Math.random() * 15) + (lIdx * 15 + 1);
                let callEl = document.getElementById('current-call');
                if (callEl) {
                    callEl.innerText = `${letters[lIdx]}-${num}`;
                }
            }, 3000);
        }

        function checkBingoWin() {
            if (callingInterval) clearInterval(callingInterval);
            let marked = document.querySelectorAll('.board-cell.marked').length;
            if (marked >= 5) {
                alert('🎉 እንኳን ደስ አለዎት! ትክክለኛ ቢንጎ ነው!');
            } else {
                alert('❌ የተሳሳተ ቢንጎ (Bogus)!');
            }
            showLobby();
        }

        function showLobby() {
            if (timerInterval) clearInterval(timerInterval);
            if (callingInterval) clearInterval(callingInterval);
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
    return jsonify({"games": [{"stake": 10.0, "players": active_players_count, "derash": current_derash}]})

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
