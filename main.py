import random
import requests
from flask import Flask, jsonify, request

app = Flask(__name__)

# የቴሌግራም ቦት ቶከን
TELEGRAM_BOT_TOKEN = "8970903838:AAHe0aHlIWVc94wAOB0lml8fM6BmVIEhaDM"

# 👑 የአድሚን ቻት አይዲ
ADMIN_CHAT_ID = "1219" 

# የተጠቃሚዎች መረጃ ማከማቻ
users_db = {}

# የባንክ መረጃዎች (የእርስዎ አካውንት)
BANK_DETAILS = {
    "account_holder": "እንያቸው አመርጋ (Enyachew Amerga)",
    "cbe": "10006825286441",
    "telebirr": "0944123180"
}

# ልክ እንደ ምስሉ በትክክል የቢንጎ ቦርድ የሚያመነጭ ፊርማ (Function)
def generate_bingo_board(board_number):
    b = random.sample(range(1, 16), 5)
    i = random.sample(range(16, 31), 5)
    n = random.sample(range(31, 46), 4)
    n.insert(2, "*") # መሃል ላይ ያለችው የ ነጻ (Free) ምልክት
    g = random.sample(range(46, 61), 5)
    o = random.sample(range(61, 76), 5)
    
    board_text = f"**Board No.{board_number}**\n"
    board_text += "B    I    N    G    0\n"
    board_text += "--------------------\n"
    for r in range(5):
        val_n = " * " if n[r] == "*" else f"{n[r]:2d}"
        board_text += f"{b[r]:2d} | {i[r]:2d} | {val_n} | {g[r]:2d} | {o[r]:2d}\n"
    return board_text

@app.route('/')
def index():
    return "Ethio Bingo Game is Running!"

@app.route(f'/webhook/{TELEGRAM_BOT_TOKEN}', methods=['POST'])
def telegram_webhook():
    update = request.json
    if not update:
        return jsonify({"status": "ok"})
    
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    answer_callback_url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/answerCallbackQuery"

    if "message" in update:
        message = update["message"]
        chat_id = message["chat"]["id"]
        user_id = str(message["from"]["id"])
        username = message["from"].get("username", f"User_{user_id}")
        text = message.get("text", "").strip()
        
        if user_id not in users_db:
            users_db[user_id] = {"registered": True, "balance": 10.0, "username": username}
            
        user_data = users_db[user_id]
        
        if text.startswith("/start"):
            show_main_menu(chat_id, url, user_data)
                
        elif "photo" in message:
            bot_message = "✅ የክፍያ ስክሪንሾትዎ በእንያቸው አመርጋ አካውንት ተቀብሏል! አድሚኑ አረጋግጦ ሒሳብዎን ይጨምርልዎታል።"
            requests.post(url, json={"chat_id": chat_id, "text": bot_message})
            
            admin_notification = f"🔔 አዲስ የዲፖዚት ስክሪንሾት ከኢትዮ ቢንጎ ተጠቃሚ (@{username}, ID: {user_id}) ደርሷል!"
            requests.post(url, json={"chat_id": ADMIN_CHAT_ID, "text": admin_notification})

    elif "callback_query" in update:
        callback_query = update["callback_query"]
        callback_id = callback_query["id"]
        chat_id = callback_query["message"]["chat"]["id"]
        user_id = str(callback_query["from"]["id"])
        username = callback_query["from"].get("username", f"User_{user_id}")
        data = callback_query.get("data", "")
        
        requests.post(answer_callback_url, json={"callback_query_id": callback_id})
        
        if user_id not in users_db:
            users_db[user_id] = {"registered": True, "balance": 10.0, "username": username}
            
        user_data = users_db[user_id]
        response_text = ""
        reply_markup = None
        
        if data == "play_menu":
            response_text = (
                "🎮 **ኢትዮ ቢንጎ - የጨዋታ አማራጮች**\n\n"
                "እባክዎ መጫወት የሚፈልጉትን የቲኬት ዋጋ ይምረጡ (ልክ እንደ አራዳ ቢንጎ)፦"
            )
            reply_markup = {
                "inline_keyboard": [
                    [{"text": "🟢 10 ETB (Active)", "callback_data": "bet_10"}, {"text": "🔵 20 ETB (Low Balance)", "callback_data": "bet_20"}],
                    [{"text": "🟠 50 ETB (Active)", "callback_data": "bet_50"}, {"text": "🟣 100 ETB", "callback_data": "bet_100"}],
                    [{"text": "🔙 ወደ ዋናው ምናሌ", "callback_data": "main_menu"}]
                ]
            }
            
        elif data.startswith("bet_"):
            bet_amount = float(data.split("_")[1])
            current_balance = user_data["balance"]
            
            if current_balance < bet_amount:
                response_text = f"⚠️ ቀሪ ሂሳብዎ ({current_balance} ETB) ለዚህ ጨዋታ በቂ አይደለም። እባክዎ መጀመሪያ ዲፖዚት ያድርጉ።"
                reply_markup = {
                    "inline_keyboard": [
                        [{"text": "💰 አሁን ዲፖዚት አድርግ", "callback_data": "deposit_menu"}],
                        [{"text": "🔙 ተመለስ", "callback_data": "play_menu"}]
                    ]
                }
            else:
                board_no = random.randint(1, 100)
                board_display = generate_bingo_board(board_no)
                
                response_text = (
                    f"🎫 **ቲኬትዎ ተቆርጧል!**\n\n"
                    f"```\n{board_display}\n```\n\n"
                    f"ማስታወሻ፦ አሸናፊ ነዎት! መልካም እድል!\n"
                    f"ቀሪ ሂሳብዎ: {bet_amount}.0 ETB"
                )
                reply_markup = {
                    "inline_keyboard": [
                        [{"text": "🔄 ሪፍሬሽ (Refresh)", "callback_data": play_menu_callback(data)}, {"text": "🚪 መውጫ (Leave)", "callback_data": "main_menu"}]
                    ]
                }
                
        elif data == "deposit_menu":
            response_text = (
                f"💰 **ኢትዮ ቢንጎ ጌም - ዲፖዚት**\n\n"
                f"ገንዘብ ለማስገባት የሚፈልጉትን የባንክ አማራጭ ይምረጡ (ገንዘቡ በቀጥታ ወደ **{BANK_DETAILS['account_holder']}** አካውንት ይገባል)፦"
            )
            reply_markup = {
                "inline_keyboard": [
                    [{"text": "ንግድ ባንክ (CBE)", "callback_data": "dep_cbe"}, {"text": "ቴሌብር (Telebirr)", "callback_data": "dep_telebirr"}],
                    [{"text": "🔙 ተመለስ", "callback_data": "main_menu"}]
                ]
            }
            
        elif data == "dep_cbe":
            response_text = f"🏦 **የንግድ ባንክ (CBE) አካውንት**\n\n• ስም: {BANK_DETAILS['account_holder']}\n• የሂሳብ ቁጥር: `{BANK_DETAILS['cbe']}`\n\nገንዘቡን ካስተላለፉ በኋላ ስክሪንሾት ቦቱ ላይ ይላኩ።"
            
        elif data == "dep_telebirr":
            response_text = f"📱 **ቴሌብር (Telebirr) አካውንት**\n\n• ስም: {BANK_DETAILS['account_holder']}\n• ስልክ ቁጥር: `{BANK_DETAILS['telebirr']}`\n\nገንዘቡን ካስተላለፉ በኋላ ስክሪንሾት ቦቱ ላይ ይላኩ።"
            
        elif data == "withdraw_menu":
            response_text = f"💳 **ዊዝድሮ (Withdrawal)**\n\nአሁን ያለዎት ቀሪ ሂሳብ: **{user_data['balance']} ETB**\n\nገንዘብ ለማውጣት የባንክ አካውንትዎን እና መጠኑን በመጻፍ ለአድሚን ይላኩ።"
            
        elif data == "check_balance":
            response_text = f"👛 **የኪስ ቦርሳ ቆጠራ (Check Balance)**\n\n• ተጠቃሚ: @{username}\n• ቀሪ ሂሳብ: **{user_data['balance']} ETB**"
            
        elif data == "invite_friend":
            bot_username = "Ethio_Bingo_Game_Bot"
            invite_link = f"https://t.me/{bot_username}?start=ref_{user_id}"
            response_text = f"👥 **ጓደኛ በመጋበዝ ሽልማት ያግኙ!**\n\nይህንን የእርስዎን ልዩ ሊንክ ለጓደኞችዎ ያጋሩ፦\n\n`{invite_link}`"
            
        elif data == "contact":
            response_text = f"📞 ማንኛውም ጥያቄ ወይም የቴክኒክ ችግር ካሎት **@{ADMIN_CHAT_ID}** በመጻፍ አድሚኑን ማግኘት ይችላሉ።"
            
        elif data == "main_menu":
            response_text = f"👤 ዩዘር: @{username}\n👛 ቀሪ ሂሳብ: {user_data['balance']} ETB\n\n© Ethio Bingo Game. የሚፈልጉትን አማራጭ ከታች ይምረጡ፦"
            reply_markup = get_main_keyboard()
            
        payload = {
            "chat_id": chat_id,
            "text": response_text,
            "parse_mode": "Markdown"
        }
        if reply_markup:
            payload["reply_markup"] = reply_markup
            
        requests.post(url, json=payload)
            
    return jsonify({"status": "ok"})

def play_menu_callback(current_bet):
    return current_bet

def get_main_keyboard():
    return {
        "inline_keyboard": [
            [{"text": "🎮 ፕሌይ ጨዋታ (Play Bingo)", "callback_data": "play_menu"}],
            [{"text": "💰 ዲፖዚት (Deposit)", "callback_data": "deposit_menu"}, {"text": "💳 ዊዝድሮ (Withdraw)", "callback_data": "withdraw_menu"}],
            [{"text": "👛 ቼክ ባላንስ (Check Balance)", "callback_data": "check_balance"}, {"text": "👥 ኢንቫይት ፍሬንድ (Invite)", "callback_data": "invite_friend"}],
            [{"text": "📞 አግኙን / እገዛ (Support)", "callback_data": "contact"}]
        ]
    }

def show_main_menu(chat_id, url, user_data):
    bot_message = f"👤 ዩዘር: @{user_data['username']}\n👛 ቀሪ ሂሳብ: {user_data['balance']} ETB\n\n© Ethio Bingo Game. የሚፈልጉትን አማራጭ ከታች ይምረጡ፦"
    payload = {
        "chat_id": chat_id,
        "text": bot_message,
        "reply_markup": get_main_keyboard()
    }
    requests.post(url, json=payload)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
