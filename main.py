import os
import threading
import random
from flask import Flask, render_template_string, jsonify, request
import telebot
from telebot import types

# ----------------------------------------------------
# 1. ማዋቀሪያ እና አዲሱ ቶከን (Configuration & Token)
# ----------------------------------------------------
TOKEN = '8806795454:AAESXX0GARmzthQ0FkcJRoMREN1SbcKSEZQ'
bot = telebot.TeleBot(TOKEN)

app = Flask(__name__)

# ----------------------------------------------------
# 2. የቴሌግራም ቦት ትዕዛዞች እና የዲፖዚት ፍሰት (Telegram Bot Handlers)
# ----------------------------------------------------
@bot.message_handler(commands=['start'])
def send_welcome(message):
    markup = types.InlineKeyboardMarkup(row_width=1)
    
    # ዌብ አፕ (Mini App) መክፈቻ ቁልፍ
    web_app = types.WebAppInfo(url="https://ethio-bingo-game.up.railway.app")
    btn_play = types.InlineKeyboardButton("🎮 Play game (/play)", web_app=web_app)
    
    btn_deposit = types.InlineKeyboardButton("💰 Deposit funds (/deposit)", callback_data="deposit_menu")
    btn_withdraw = types.InlineKeyboardButton("💸 Withdraw funds (/withdraw)", callback_data="withdraw")
    btn_balance = types.InlineKeyboardButton("💳 Check balance (/balance)", callback_data="balance")
    btn_invite = types.InlineKeyboardButton("👥 Invite friends (/invite)", callback_data="invite")
    btn_contact = types.InlineKeyboardButton("📞 Contact us (/contact)", callback_data="contact")
    
    markup.add(btn_play, btn_deposit, btn_withdraw, btn_balance, btn_invite, btn_contact)
    
    welcome_text = (
        "🇪🇹 ሰላም! እንኳን ወደ እኛ የቢንጎ ጨዋታ (Ethio Bingo) በደህና መጡ።\n\n"
        "ከዚህ በታች ያሉትን አማራጮች በመጠቀም ጨዋታውን ይጀምሩ፣ አካውንትዎትን ያስተዳድሩ እና ቦነሶችን ያግኙ!"
    )
    bot.send_message(message.chat.id, welcome_text, reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    if call.data == "deposit_menu":
        bot.answer_callback_query(call.id)
        markup = types.InlineKeyboardMarkup(row_width=1)
        btn_telebirr = types.InlineKeyboardButton("📱 Telebirr", callback_data="pay_telebirr")
        btn_cbe = types.InlineKeyboardButton("🏦 Commercial Bank of Ethiopia (CBE)", callback_data="pay_cbe")
        markup.add(btn_telebirr, btn_cbe)
        
        bot.send_message(
            call.message.chat.id, 
            "💰 **የገንዘብ ማስገቢያ (Deposit)**\n\nእባክዎ ገንዘብ ለማስገባት የሚፈልጉበትን የባንክ አማራጭ ይምረጡ፡", 
            reply_markup=markup
        )
        
    elif call.data == "pay_telebirr":
        bot.answer_callback_query(call.id)
        bot.send_message(
            call.message.chat.id, 
            "📱 **Telebirr አካውንት መረጃ፦**\n\n"
            "ስም: እያቸው (Enyachew)\n"
            "ስልክ ቁጥር: `0944123180`\n\n"
            "እባክዎ ከላይ ባለው ቁጥር ገንዘቡን ካስተላለፉ በኋላ የክፍያውን ደረሰኝ (Screenshot) ፎቶ በመላክ ለአስተዳዳሪው @Enyachew-19 ያረጋግጡ።"
        )
        
    elif call.data == "pay_cbe":
        bot.answer_callback_query(call.id)
        bot.send_message(
            call.message.chat.id, 
            "🏦 **የኢትዮጵያ ንግድ ባንክ (CBE) አካውንት መረጃ፦**\n\n"
            "ስም: እያቸው (Enyachew)\n"
            "አካውንት ቁጥር: `1000682528641`\n\n"
            "እባክዎ ገንዘቡን ከላኩ በኋላ የክፍያውን ደረሰኝ (Screenshot) ፎቶ በመላክ ለአስተዳዳሪው @Enyachew-19 ያረጋግጡ።"
        )
        
    elif call.data == "withdraw":
        bot.answer_callback_query(call.id)
        bot.send_message(
            call.message.chat.id, 
            "💸 **ገንዘብ ማውጣት (Withdrawal)**\n\n"
            "ገንዘብ ለማውጣት የሚፈልጉትን መጠን እና የባንክ/ቴሌብር አካውንት ቁጥርዎን በመጻፍ ለአስተዳዳሪው @Enyachew-19 ይላኩ።"
        )
        
    elif call.data == "balance":
        bot.answer_callback_query(call.id)
        bot.send_message(call.message.chat.id, "💳 የአካውንትዎ ቀሪ ሂሳብ: 0.00 ETB")
        
    elif call.data == "invite":
        bot.answer_callback_query(call.id)
        bot.send_message(call.message.chat.id, "👥 ጓደኞችዎን በመጋበዝ ቦነስ ያግኙ!")
        
    elif call.data == "contact":
        bot.answer_callback_query(call.id)
        bot.send_message(call.message.chat.id, "📞 ለማንኛውም እርዳታ አስተዳዳሪውን ያነጋግሩ: @Enyachew-19")

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
