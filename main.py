import os
import random
import time
import threading
from flask import Flask, render_template_string, request, jsonify
import telebot
from telebot import types

# 1. ቦት ማስጀመሪያ እና አወቃቀር
TOKEN = '8970903838:AAHe0aHlIWVc94wAOB0lml8fM6BmVIEhaDM'
bot = telebot.TeleBot(TOKEN)

ADMIN_USERNAME = "@enyachew_19"
ADMIN_CHAT_ID = os.getenv('ADMIN_CHAT_ID', '123456789')
ACCOUNT_NAME = "እነያቸዉ አመርጋ"
TELEBIRR_ACCOUNT = "0944123180"
CBE_ACCOUNT = "1000682528641"

# ዳታቤዝ እና የጨዋታ ሁኔታዎች ማከማቻ
users_db = {}
user_states = {}
current_game_state = {
    "status": "waiting", # waiting, playing, finished
    "countdown": 30,
    "called_numbers": [],
    "current_number": None,
    "active_stake": 10,
    "players": 0
}

app = Flask(__name__)

# 2. የቴሌግራም ሚኒ አፕ (Frontend) ኤችቲኤምኤል ንድፍ
MINI_APP_HTML = """
<!DOCTYPE html>
<html lang="am">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ኢትዮ ቢንጎ (Ethio Bingo)</title>
    <style>
        body { font-family: Arial, sans-serif; background-color: #121212; color: #ffffff; text-align: center; margin: 0; padding: 20px; }
        .header { background: #1e1e1e; padding: 15px; border-radius: 10px; margin-bottom: 20px; box-shadow: 0 4px 10px rgba(0,0,0,0.5); }
        .board { display: grid; grid-template-columns: repeat(5, 1fr); gap: 8px; max-width: 350px; margin: 0 auto; background: #1e1e1e; padding: 15px; border-radius: 10px; }
        .cell { background: #2c2c2c; padding: 15px 5px; font-size: 18px; font-weight: bold; border-radius: 5px; cursor: pointer; transition: 0.3s; }
        .cell.marked { background: #ff9800; color: #000; }
        .number-display { font-size: 32px; color: #4CAF50; margin: 15px 0; font-weight: bold; }
        .btn { background: #4CAF50; color: white; border: none; padding: 12px 25px; font-size: 16px; border-radius: 5px; cursor: pointer; margin-top: 15px; }
        .btn:active { background: #45a049; }
    </style>
</head>
<body>
    <div class="header">
        <h2>🎮 ኢትዮ ቢንጎ (Ethio Bingo)</h2>
        <p>ቀሪ ቁጥር/ሰዓት: <span id="timer">30</span> ሰኮንድ</p>
        <div class="number-display" id="currentNumber">--</div>
    </div>

    <h3>የእርስዎ የቢንጎ ሰሌዳ (Board 38)</h3>
    <div class="board" id="bingoBoard">
        <!-- ጂኤስ (JS) በመጠቀም በራሱ ይሞላል -->
    </div>

    <button class="btn" onclick="declareBingo()">🎉 ቢንጎ (BINGO)!</button>

    <script>
        const boardElement = document.getElementById('bingoBoard');
        const currentNumEl = document.getElementById('currentNumber');
        const timerEl = document.getElementById('timer');

        // የናሙና ቢንጎ ካርድ ቁጥሮች መሙላት
        const numbers = [5, 12, 23, 34, 45, 3, 19, 28, 30, 50, 7, 15, "FREE", 33, 41, 2, 11, 25, 39, 48, 9, 18, 22, 37, 44];
        
        numbers.forEach((num, index) => {
            const cell = document.createElement('div');
            cell.className = 'cell' + (num === 'FREE' ? ' marked' : '');
            cell.innerText = num;
            if(num !== 'FREE') {
                cell.onclick = () => cell.classList.toggle('marked');
            }
            boardElement.appendChild(cell);
        });

        // የሰርቨር መረጃዎችን በየሰኮንዱ ማሳደስ (Polling state)
        setInterval(async () => {
            try {
                const response = await fetch('/game_status');
                const data = await response.json();
                currentNumEl.innerText = data.current_number || '--';
                timerEl.innerText = data.countdown;
            } catch (e) {
                console.error("Error fetching state");
            }
        }, 1000);

        function declareBingo() {
            alert("🎉 የእርስዎ የቢንጎ ጥያቄ ለአድሚን ተልኳል! እባክዎ ይጠብቁ።");
        }
    </script>
</body>
</html>
"""

# 3. የባክግራውንድ ዎርከር (Background Game Engine & Random Call Logic)
def background_game_engine():
    global current_game_state
    while True:
        if current_game_state["status"] == "waiting":
            while current_game_state["countdown"] > 0:
                time.sleep(1)
                current_game_state["countdown"] -= 1
            current_game_state["status"] = "playing"
            current_game_state["called_numbers"] = []
            
        elif current_game_state["status"] == "playing":
            # 1 ರಿಂದ 75 ያሉ ቁጥሮች ውስጥ ገና ያልተጠሩትን በዘፈቀደ (Random) መምረጥ
            all_nums = list(range(1, 76))
            available = [n for n in all_nums if n not in current_game_state["called_numbers"]]
            
            if available:
                chosen = random.choice(available)
                current_game_state["called_numbers"].append(chosen)
                current_game_state["current_number"] = chosen
            
            time.sleep(3) # በየ 3 ሰኮንዱ አንድ ቁጥር ይጠራል
            
            # ጨዋታው ሲያልቅ (ለምሳሌ 25 ቁጥሮች ከተጠሩ በኋላ) እንደገና ወደ waiting ይመለሳል
            if len(current_game_state["called_numbers"]) >= 25:
                current_game_state["status"] = "waiting"
                current_game_state["countdown"] = 30

# ሰርቨሩ ሲጀምር ባክግራውንድ ሰራተኛውን ማቀጣጠል
threading.Thread(target=background_game_engine, daemon=True).start()

@app.route('/')
def mini_app():
    return render_template_string(MINI_APP_HTML)

@app.route('/game_status')
def game_status():
    return jsonify(current_game_state)

# 4. የቴሌግራም ቦት ትዕዛዞች እና መቆጣጠሪያ
def main_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    
    # ቴሌግራም ሚኒ አፕ (WebApp) መክፈቻ ቁልፍ
    web_app_url = "https://ethio-bingo-game-production.up.railway.app/"
    play_btn = types.KeyboardButton("🎮 Play (ኢትዮ ቢንጎ ጨዋታ)", web_app=types.WebAppInfo(url=web_app_url))
    
    deposit_btn = types.KeyboardButton("💳 Deposit (ብር አጫውት)")
    withdraw_btn = types.KeyboardButton("💸 Withdraw (ብር አውጣ)")
    balance_btn = types.KeyboardButton("💰 Check Balance (ባላንስ)")
    invite_btn = types.KeyboardButton("👥 Invite (ጋብዝ)")
    contact_btn = types.KeyboardButton("📞 Contact Us (አድሚን)")
    
    markup.add(play_btn, deposit_btn, withdraw_btn, balance_btn, invite_btn, contact_btn)
    return markup

@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_id = message.from_user.id
    if user_id not in users_db:
        users_db[user_id] = {"balance": 0.0, "name": message.from_user.first_name}
    
    bot.send_message(
        message.chat.id,
        f"ሰላም <b>{message.from_user.first_name}</b>! ወደ <b>ኢትዮ ቢንጎ (Ethio Bingo)</b> እንኳን በደህና መጡ።\n\n"
        "ከታች ያለውን የጨዋታ አዝራር በመጫን ቦርዶችን በመምረጥ መጫወት ይጀምሩ!",
        parse_mode='HTML',
        reply_markup=main_menu()
    )

@bot.message_handler(func=lambda message: True)
def handle_messages(message):
    user_id = message.from_user.id
    text = message.text
    chat_id = message.chat.id

    if "Deposit" in text or "ብር አጫውት" in text:
        dep_markup = types.InlineKeyboardMarkup(row_width=2)
        dep_markup.add(
            types.InlineKeyboardButton("📱 ቴሌብር (Telebirr)", callback_data="dep_telebirr"),
            types.InlineKeyboardButton("🏦 ንግድ ባንክ (CBE)", callback_data="dep_cbe")
        )
        bot.send_message(
            chat_id,
            "💳 <b>የሂሳብ መሙያ (Deposit)</b>\n\nእባክዎ ገንዘብ ልከው ለማስገባት የሚፈልጉትን የባንክ አማራጭ ይምረጡ:",
            parse_mode='HTML',
            reply_markup=dep_markup
        )
    elif "Withdraw" in text or "ብር አውጣ" in text:
        user_states[user_id] = "waiting_withdraw_amount"
        bot.send_message(chat_id, "💸 <b>ብር ማውጣት (Withdraw)</b>\n\nእባክዎ ማውጣት የሚፈልጉትን የገንዘብ መጠን (ብር) ብቻ ይጻፉ (ለምሳሌ: 200):", parse_mode='HTML')
    elif "Check Balance" in text or "ባላንስ" in text:
        balance = users_db.get(user_id, {}).get("balance", 0.0)
        bot.send_message(chat_id, f"💰 የእርስዎ ቀሪ ሂሳብ: <b>{balance} ብር</b>", parse_mode='HTML')
    elif "Invite" in text or "ጋብዝ" in text:
        bot.send_message(chat_id, f"👥 ጓደኞችዎን በመጋበዝ ቦነስ ያግኙ!\n\nየእርስዎ መጋበዣ ሊንክ:\nhttps://t.me/Ethio_Bingo_Bot?start=ref_{user_id}")
    elif "Contact Us" in text or "አድሚን" in text:
        bot.send_message(chat_id, f"📞 ማንኛውም ጥያቄ ወይም ክፍያ በሚመለከት ሲኖርዎ በቀጥታ ዋናውን አድሚን ማግኘት ይችላሉ:\n\nአድሚን: <b>{ADMIN_USERNAME}</b>", parse_mode='HTML')

    elif user_states.get(user_id) == "waiting_withdraw_amount":
        try:
            amount = float(text)
            current_balance = users_db.get(user_id, {}).get("balance", 0.0)
            if amount > current_balance:
                bot.send_message(chat_id, "❌ በቂ ቀሪ ሂሳብ የለዎትም! እባክዎ ትክክለኛ መጠን ያስገቡ።")
            else:
                user_states[f"withdraw_amt_{user_id}"] = amount
                user_states[user_id] = "registered"
                admin_msg = (
                    f"🚨 <b>አዲስ የገንዘብ ማውጣት ጥያቄ!</b>\n\n"
                    f"👤 <b>ተጠቃሚ:</b> {message.from_user.first_name} (ID: <code>{user_id}</code>)\n"
                    f"💰 <b>መጠን:</b> {amount} ብር\n"
                    f"አድሚን: {ADMIN_USERNAME}"
                )
                bot.send_message(ADMIN_CHAT_ID, admin_msg, parse_mode='HTML')
                bot.send_message(chat_id, f"✅ የብር ማውጣት ጥያቄዎ ለአድሚኑ ({ADMIN_USERNAME}) ደርሷል!", reply_markup=main_menu())
        except ValueError:
            bot.send_message(chat_id, "❌ እባክዎ ትክክለኛ ቁጥር ብቻ ያስገቡ።")

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    chat_id = call.message.chat.id
    if call.data == "dep_telebirr":
        bot.send_message(
            chat_id,
            f"📱 <b>በቴሌብር ለማስገባት:</b>\n👤 <b>ስም:</b> {ACCOUNT_NAME}\n📱 <b>ቁጥር:</b> <code>{TELEBIRR_ACCOUNT}</code>\n\nብር ከላኩ በኋላ ስክሪንሾት (Screenshot) እዚህ ይላኩ።",
            parse_mode='HTML'
        )
    elif call.data == "dep_cbe":
        bot.send_message(
            chat_id,
            f"🏦 <b>በንግድ ባንክ (CBE) ለማስገባት:</b>\n👤 <b>ስም:</b> {ACCOUNT_NAME}\n🏦 <b>አካውንት:</b> <code>{CBE_ACCOUNT}</code>\n\nብር ከላኩ በኋላ ስክሪንሾት እዚህ ይላኩ።",
            parse_mode='HTML'
        )

@bot.message_handler(content_types=['photo'])
def handle_docs_photo(message):
    user_id = message.from_user.id
    chat_id = message.chat.id
    bot.send_message(chat_id, f"📥 የክፍያ ማረጋገጫዎ ደርሷል! አድሚኑ ({ADMIN_USERNAME}) እያረጋገጠው ነው።", reply_markup=main_menu())
    try:
        bot.forward_message(ADMIN_CHAT_ID, chat_id, message.message_id)
        bot.send_message(ADMIN_CHAT_ID, f"💳 ከ <b>{message.from_user.first_name}</b> (ID: <code>{user_id}</code>) የመጣ ዲፖዚት ማረጋገጫ ነው።", parse_mode='HTML')
    except Exception as e:
        print(f"Admin forward error: {e}")

# 5. የዌብሁክ እና የፍላስክ (Flask) ማስተንገጃ 
@app.route('/' + TOKEN, methods=['POST'])
def getMessage():
    json_string = request.get_data().decode('utf-8')
    update = types.Update.de_json(json_string)
    bot.process_new_updates([update])
    return "!", 200

@app.route("/set_webhook_route")
def webhook():
    bot.remove_webhook()
    app_url = "ethio-bingo-game-production.up.railway.app"
    bot.set_webhook(url=f"https://{app_url}/{TOKEN}")
    return "Webhook set successfully!", 200

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=int(os.environ.get('PORT', 5000)))
