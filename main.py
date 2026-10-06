import os
import threading
import random
from flask import Flask, render_template_string, jsonify, request
import telebot
from telebot import types

# ----------------------------------------------------
# 1. ማዋቀሪያ እና ቶከን (Configuration & Token)
# ----------------------------------------------------
TOKEN = '8806795454:AAESXX0GARmzthQ0FkcJRoMREN1SbcKSEZQ'
bot = telebot.TeleBot(TOKEN)

app = Flask(__name__)

# ለጊዜው የተጠቃሚዎች ባንክ ሂሳብ እና ሪፈራል መያዣ (Memory Database)
user_balances = {}  # {chat_id: balance}
user_states = {}    # ተጠቃሚው የትኛውን ሂደት ላይ እንዳለ ለማወቅ

# ----------------------------------------------------
# 2. የቴሌግራም ቦት ትዕዛዞች እና የባንክ ፍሰቶች (Telegram Bot Handlers)
# ----------------------------------------------------
@bot.message_handler(commands=['start'])
def send_welcome(message):
    chat_id = message.chat.id
    
    # ሪፈራል ወይም መጋበዣ ሊንክ የተጠቃሚውን ID ይዞ ይመጣል (ወይም በጽሁፍ ይረጋገጣል)
    markup = types.InlineKeyboardMarkup(row_width=1)
    
    # ዌብ አፕ (Mini App) መክፈቻ ቁልፍ
    web_app = types.WebAppInfo(url="https://ethio-bingo-game.up.railway.app/")
    btn_play = types.InlineKeyboardButton("🎮 Play game (/play)", web_app=web_app)
    
    btn_deposit = types.InlineKeyboardButton("💰 Deposit funds (/deposit)", callback_data="deposit_menu")
    btn_withdraw = types.InlineKeyboardButton("💸 Withdraw funds (/withdraw)", callback_data="withdraw_menu")
    btn_balance = types.InlineKeyboardButton("💳 Check balance (/balance)", callback_data="balance")
    btn_invite = types.InlineKeyboardButton("👥 Invite friends (/invite)", callback_data="invite")
    btn_contact = types.InlineKeyboardButton("📞 Contact us (/contact)", callback_data="contact")
    
    markup.add(btn_play, btn_deposit, btn_withdraw, btn_balance, btn_invite, btn_contact)
    
    welcome_text = (
        "🇪🇹 ሰላም! እንኳን ወደ እኛ የቢንጎ ጨዋታ (Ethio Bingo) በደህና መጡ።\n\n"
        "ከዚህ በታች ያሉትን አማራጮች በመጠቀም ጨዋታውን ይጀምሩ፣ አካውንትዎትን ያስተዳድሩ እና ቦነሶችን ያግኙ!"
    )
    bot.send_message(chat_id, welcome_text, reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    chat_id = call.message.chat.id
    
    if call.data == "deposit_menu":
        bot.answer_callback_query(call.id)
        markup = types.InlineKeyboardMarkup(row_width=1)
        btn_telebirr = types.InlineKeyboardButton("📱 Telebirr", callback_data="dep_telebirr")
        btn_cbe = types.InlineKeyboardButton("🏦 Commercial Bank of Ethiopia (CBE)", callback_data="dep_cbe")
        markup.add(btn_telebirr, btn_cbe)
        
        bot.send_message(
            chat_id, 
            "💰 **የገንዘብ ማስገቢያ (Deposit)**\n\nእባክዎ ገንዘብ ለማስገባት የሚፈልጉበትን የባንክ አማራጭ ይምረጡ፡", 
            reply_markup=markup
        )
        
    elif call.data in ["dep_telebirr", "dep_cbe"]:
        bot.answer_callback_query(call.id)
        bank_name = "Telebirr (0944123180)" if call.data == "dep_telebirr" else "CBE (1000682528641)"
        user_states[chat_id] = {"action": "waiting_deposit_amount", "bank": bank_name}
        bot.send_message(
            chat_id, 
            f"መረጡት ባንክ: {bank_name}\n\nእባክዎ ማስገባት የሚፈልጉትን የብር መጠን በቁጥር ብቻ ይጻፉልን (በቦቱ በቀጥታ ይረጋገጣል)፦"
        )

    elif call.data == "withdraw_menu":
        bot.answer_callback_query(call.id)
        markup = types.InlineKeyboardMarkup(row_width=1)
        btn_telebirr = types.InlineKeyboardButton("📱 Telebirr", callback_data="w_telebirr")
        btn_cbe = types.InlineKeyboardButton("🏦 Commercial Bank of Ethiopia (CBE)", callback_data="w_cbe")
        markup.add(btn_telebirr, btn_cbe)
        
        bot.send_message(
            chat_id, 
            "💸 **ገንዘብ ማውጣት (Withdrawal)**\n\nእባክዎ ገንዘብ ማውጣት የሚፈልጉበትን የባንክ ዓይነት ይምረጡ፡", 
            reply_markup=markup
        )

    elif call.data in ["w_telebirr", "w_cbe"]:
        bot.answer_callback_query(call.id)
        bank_type = "Telebirr" if call.data == "w_telebirr" else "CBE"
        user_states[chat_id] = {"action": "waiting_withdraw_account", "bank": bank_type}
        bot.send_message(
            chat_id, 
            f"መረጡት ባንክ: {bank_type}\n\nእባክዎ የባንክ/የቴሌብር አካውንት ቁጥርዎን ይጻፉልን፦"
        )

    elif call.data == "balance":
        bot.answer_callback_query(call.id)
        current_bal = user_balances.get(chat_id, 0.0)
        bot.send_message(chat_id, f"💳 የአካውንትዎ ቀሪ ሂሳብ: {current_bal} ETB")
        
    elif call.data == "invite":
        bot.answer_callback_query(call.id)
        # የቦቱን ዩዘርናም በማግኘት ለተጠቃሚው ልዩ መጋበዣ ሊንክ እንፈጥራለን
        bot_info = bot.get_me()
        bot_username = bot_info.username
        invite_link = f"https://t.me/{bot_username}?start=ref_{chat_id}"
        
        invite_text = (
            "👥 **ጓደኞችዎን በመጋበዝ ቦነስ ያግኙ!**\n\n"
            "እያንዳንዱን ጓደኛ ወደ ቦቱ ሲጋብዙ ተጨማሪ የጨዋታ ቦነስ ያገኛሉ።\n\n"
            "🔗 **የእርስዎ ልዩ መጋበዣ ሊንክ (Referral Link):**\n"
            f"`{invite_link}`\n\n"
            "ይህንን ሊንክ ለጓደኞችዎ በመላክ ይጋብዙ!"
        )
        bot.send_message(chat_id, invite_text, parse_mode="Markdown")
        
    elif call.data == "contact":
        bot.answer_callback_query(call.id)
        bot.send_message(chat_id, "📞 ለማንኛውም እርዳታ አስተዳዳሪውን ያነጋግሩ: @Enyachew-19")

@bot.message_handler(func=lambda message: True)
def handle_text_messages(message):
    chat_id = message.chat.id
    text = message.text.strip()
    
    if chat_id in user_states:
        state = user_states[chat_id]
        
        # የዲፖዚት መጠን መቀበያ እና በቦቱ ማረጋገጫ (አድሚን ጋር ሳይሄድ እዛው የሚያልቅ)
        if state["action"] == "waiting_deposit_amount":
            try:
                amount = float(text)
                if amount <= 0:
                    raise ValueError()
                
                current_bal = user_balances.get(chat_id, 0.0)
                user_balances[chat_id] = current_bal + amount
                
                bank = state["bank"]
                del user_states[chat_id]
                
                bot.send_message(
                    chat_id,
                    f"✅ **ክፍያው በቦቱ ተረጋግጧል!**\n\n"
                    f"ባንክ: {bank}\n"
                    f"የተቀመጠው ገንዘብ: {amount} ETB\n"
                    f"አዲስ የአካውንት ቀሪ ሂሳብዎ: {user_balances[chat_id]} ETB"
                )
            except ValueError:
                bot.send_message(chat_id, "❌ እባክዎ ትክክለኛ የብር መጠን በቁጥር ብቻ ይጻፉ (ለምሳሌ: 50)")

        # የዊዝድሮ አካውንት ቁጥር መቀበያ
        elif state["action"] == "waiting_withdraw_account":
            state["account_number"] = text
            state["action"] = "waiting_withdraw_amount"
            bot.send_message(chat_id, f"የሰጡት አካውንት: {text}\n\nአሁን ማውጣት የሚፈልጉትን የብር መጠን ይጻፉ፦")

        # የዊዝድሮ መጠን መቀበያ እና ባላንስ ማረጋገጫ (ቦቱ ባላንሱን አረጋግጦ ለአድሚን የሚልክበት)
        elif state["action"] == "waiting_withdraw_amount":
            try:
                withdraw_amount = float(text)
                current_bal = user_balances.get(chat_id, 0.0)
                
                if withdraw_amount > current_bal:
                    bot.send_message(chat_id, f"❌ በቂ ቀሪ ሂሳብ የለዎትም! የአሁን ቀሪ ሂሳብዎ {current_bal} ETB ብቻ ነው።")
                else:
                    bank = state["bank"]
                    acc_no = state["account_number"]
                    
                    # ከቀሪ ሂሳብ እንቀንሳለን
                    user_balances[chat_id] = current_bal - withdraw_amount
                    del user_states[chat_id]
                    
                    bot.send_message(
                        chat_id,
                        f"✅ የገንዘብ ማውጫ ጥያቄዎ በትክክል ተመዝግቦ ለአስተዳዳሪው ተልኳል!\n"
                        f"የተቀነሰው መጠን: {withdraw_amount} ETB\n"
                        f"ቀሪ ሂሳብዎ: {user_balances[chat_id]} ETB"
                    )
                    
                    # ለአድሚን የሚላክ መልክት (ቦቱ ራሱ በራስ ሰር ለአድሚን ይልካል)
                    admin_msg = (
                        f"🚨 **አዲስ የገንዘብ ማውጣት (Withdrawal) ጥያቄ!**\n\n"
                        f"ተጠቃሚ ID: `{chat_id}`\n"
                        f"ባንክ: {bank}\n"
                        f"አካውንት ቁጥር: `{acc_no}`\n"
                        f"መጠን: {withdraw_amount} ETB"
                    )
                    bot.send_message("@Enyachew-19", admin_msg, parse_mode="Markdown")
            except ValueError:
                bot.send_message(chat_id, "❌ እባክዎ ትክክለኛ የብር መጠን በቁጥር ብቻ ይጻፉ።")

# ----------------------------------------------------
# 3. የፍላስክ ዌብ መተግበሪያ (Flask Web Routes & Mini App UI)
# ----------------------------------------------------
@app.route('/')
def index():
    return render_template_string('''
    <!DOCTYPE html>
    <html lang="am">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Ethio Bingo</title>
        <script src="https://telegram.org/js/telegram-web-app.js"></script>
        <style>
            body { font-family: Arial, sans-serif; background-color: #121212; color: #fff; text-align: center; padding: 20px; }
            .card { background: #1e1e1e; padding: 15px; margin: 10px auto; border-radius: 10px; max-width: 400px; display: flex; justify-content: space-between; align-items: center; }
            button { background: #ff9800; border: none; padding: 10px 15px; color: white; border-radius: 5px; cursor: pointer; font-weight: bold; }
            button:hover { background: #e68900; }
            .header { display: flex; justify-content: space-between; align-items: center; background: #222; padding: 10px 20px; border-radius: 8px; margin-bottom: 20px; }
        </style>
    </head>
    <body>
        <div class="header">
            <h2>🇪🇹 ኢትዮ ቢንጎ (Ethio Bingo)</h2>
            <span style="background: #4caf50; padding: 5px 10px; border-radius: 5px;" id="balance">💰 0.00 ETB</span>
        </div>
        
        <div class="card">
            <div>
                <h3>10 ETB</h3>
                <p>ቆጣሪ: 45 ሰኮንድ | ሽልማት: 168 ETB</p>
            </div>
            <button onclick="startGame(10)">Play</button>
        </div>

        <div class="card">
            <div>
                <h3>20 ETB</h3>
                <p>ቆጣሪ: 45 ሰኮንድ | ሽልማት: 336 ETB</p>
            </div>
            <button onclick="startGame(20)">Play</button>
        </div>

        <div class="card">
            <div>
                <h3>50 ETB</h3>
                <p>ቆጣሪ: 45 ሰኮንድ | ሽልማት: 840 ETB</p>
            </div>
            <button onclick="startGame(50)">Play</button>
        </div>

        <script>
            let tg = window.Telegram.WebApp;
            tg.expand();

            function startGame(amount) {
                alert(amount + ' ETB ጨዋታ ተመርጧል! ሰሌዳው እየተዘጋጀ ነው...');
            }
        </script>
    </body>
    </html>
    ''')

@app.route('/api/status')
def api_status():
    return jsonify({"status": "running", "bot": "Ethio Bingo Game Bot"})

# ----------------------------------------------------
# 4. ማስኬጃ ክፍል (Bot & Server Runner)
# ----------------------------------------------------
def run_telegram_bot():
    try:
        bot.remove_webhook()
        bot.infinity_polling(none_stop=True, interval=0, timeout=20)
    except Exception as e:
        print(f"Bot polling error: {e}")

if __name__ == '__main__':
    bot_thread = threading.Thread(target=run_telegram_bot)
    bot_thread.daemon = True
    bot_thread.start()

    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
