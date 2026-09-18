import requests
from flask import Flask, jsonify, request

app = Flask(__name__)

# የቴሌግራም ቦት ቶከን
TELEGRAM_BOT_TOKEN = "8970903838:AAHe0aHlIWVc94wAOB0lml8fM6BmVIEhaDM"

# የፈተና/ማሳያ ተጠቃሚዎች የውሂብ ማከማቻ
users_db = {
    "123456789": {"username": "ተጫዋች", "balance": 5.0} # ዝቅተኛ ባላንስ ለሙከራ
}

# ትክክለኛው የባንክ መረጃዎች (በእንያቸው አመርጋ ስም)
BANK_DETAILS = {
    "account_holder": "እንያቸው አመርጋ (Enyachew Amerga)",
    "cbe": "1000682528641",
    "telebirr": "0944123180"
}

HOUSE_COMMISSION_PERCENT = 20  # ለቤቱ የሚቆረጥ 20% ኮሚሽን

@app.route('/')
def index():
    return "Ethio Bingo Mini App Backend is Running Successfully!"

# የቴሌግራም ዌብሆክ (Webhook) መቀበያ
@app.route(f'/webhook/{TELEGRAM_BOT_TOKEN}', methods=['POST'])
def telegram_webhook():
    update = request.json
    if not update:
        return jsonify({"status": "ok"})
    
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    answer_callback_url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/answerCallbackQuery"

    # 1. ጽሁፍ ሲላክ (/start)
    if "message" in update:
        chat_id = update["message"]["chat"]["id"]
        text = update["message"].get("text", "")
        
        if text == "/start":
            bot_message = "እንኳን ወደ Ethio Bingo Game በደህና መጡ! ከታች ያሉትን አማራጮች በመጠቀም መጫወት እና አካውንትዎን ማስተዳደር ይችላሉ።"
            
            keyboard = {
                "inline_keyboard": [
                    [{"text": "🎮 ቢንጎ ጨዋታ (Play Bingo)", "callback_data": "play_bingo"}],
                    [{"text": "💰 ዲፖዚት (Deposit)", "callback_data": "deposit_menu"}, {"text": "💳 ዊዝድሮ (Withdraw)", "callback_data": "withdraw"}],
                    [{"text": "👥 ጓደኛ ጋብዝ (Invite Friend)", "callback_data": "invite"}],
                    [{"text": "📞 አግኙን (Contact Us)", "callback_data": "contact"}, {"text": "📝 ማመልከቻ (Apply)", "callback_data": "apply"}]
                ]
            }
            
            payload = {
                "chat_id": chat_id, 
                "text": bot_message,
                "reply_markup": keyboard
            }
            requests.post(url, json=payload)

    # 2. አዝራሮች ሲጫኑ (Callback Query)
    elif "callback_query" in update:
        callback_query = update["callback_query"]
        callback_id = callback_query["id"]
        chat_id = callback_query["message"]["chat"]["id"]
        user_id = str(callback_query["from"]["id"])
        data = callback_query.get("data", "")
        
        # የናፍቆት ምልክት ማጥፊያ
        requests.post(answer_callback_url, json={"callback_query_id": callback_id})
        
        response_text = ""
        reply_markup = None
        
        if data == "play_bingo":
            # ተጠቃሚው ወደ ጨዋታው ገብቶ ቁጥር መርጠው ሊጫወት ሲል ብቻ ባላንሱን እንፈትሻለን
            if user_id not in users_db:
                users_db[user_id] = {"balance": 0.0}
            
            current_balance = users_db[user_id]["balance"]
            ticket_price = 10.0 # የቲኬት ዋጋ
            
            if current_balance < ticket_price:
                # ባላንሱ ካነሰ ወደ ዲፖዚት እንዲሄድ አማራጭ እንሰጠዋለን
                response_text = f"⚠️ ቀሪ ሂሳብዎ ({current_balance} ብር) ለዚህ ጨዋታ በቂ አይደለም። እባክዎ መጀመሪያ ዲፖዚት ያድርጉ።"
                reply_markup = {
                    "inline_keyboard": [
                        [{"text": "💰 አሁን ዲፖዚት አድርግ (Deposit)", "callback_data": "deposit_menu"}]
                    ]
                }
            else:
                response_text = "🎮 ወደ ቢንጎ ጨዋታው ገብተዋል! ቲኬትዎን ይምረጡና ቁጥሮችን መጫወት ይጀምሩ።"
                
        elif data == "deposit_menu":
            # ተጠቃሚው የትኛውን ባንክ መምረጥ እንደሚፈልግ የሚጠይቅ ንዑስ ምናሌ
            response_text = "💰 እባክዎ ገንዘብ ለማስገባት የሚፈልጉትን የክፍያ አማራጭ ይምረጡ፦"
            reply_markup = {
                "inline_keyboard": [
                    [{"text": "ንግድ ባንክ (CBE)", "callback_data": "dep_cbe"}, {"text": "ቴሌብር (Telebirr)", "callback_data": "dep_telebirr"}]
                ]
            }
            
        elif data == "dep_cbe":
            response_text = f"🏦 **የንግድ ባንክ (CBE) አካውንት**\n\n• ስም: {BANK_DETAILS['account_holder']}\n• የሂሳብ ቁጥር: `{BANK_DETAILS['cbe']}`\n\nገንዘቡን ካስተላለፉ በኋላ የክፍያውን ስክሪንሾት ይላኩ።ኮንፊርም ይደረጋል።"
            
        elif data == "dep_telebirr":
            response_text = f"📱 **ቴሌብር (Telebirr) አካውንት**\n\n• ስም: {BANK_DETAILS['account_holder']}\n• ስልክ ቁጥር: `{BANK_DETAILS['telebirr']}`\n\nገንዘቡን ካስተላለፉ በኋላ የክፍያውን ስክሪንሾት ይላኩ።"
            
        elif data == "withdraw":
            response_text = "💳 **ዊዝድሮ (Withdraw)**\n\nገንዘብ ለማውጣት የሚፈልጉትን መጠን እና የባንክ አካውንት ቁጥር ይላኩ።"
        elif data == "invite":
            response_text = "👥 ጓደኛ በመጋበዝ ቦነሶችን ይሰብስቡ! የእርስዎን ሊንክ ለጓደኞችዎ ያጋሩ።"
        elif data == "contact":
            response_text = "📞 ማንኛውም ጥያቄ ካሎት አድሚኑን ማግኘት ይችላሉ።"
        elif data == "apply":
            response_text = "📝 ለማመልከት የሚፈልጉትን መረጃ እዚህ ይሙሉ ወይም አድሚኑን ያግኙ።"
        else:
            response_text = "አገልግሎቱ በሂደት ላይ ነው።"
            
        payload = {
            "chat_id": chat_id,
            "text": response_text,
            "parse_mode": "Markdown"
        }
        if reply_markup:
            payload["reply_markup"] = reply_markup
            
        requests.post(url, json=payload)
            
    return jsonify({"status": "ok"})

# ኤፒአይዎች
@app.route('/api/get_balance', methods=['POST'])
def get_balance():
    data = request.json or {}
    user_id = str(data.get("user_id"))
    if user_id not in users_db:
        users_db[user_id] = {"balance": 0.0}
    return jsonify({"status": "success", "balance": users_db[user_id]["balance"]})

@app.route('/api/deposit_info', methods=['GET'])
def deposit_info():
    return jsonify({
        "status": "success",
        "account_holder": BANK_DETAILS["account_holder"],
        "accounts": {"cbe": BANK_DETAILS["cbe"], "telebirr": BANK_DETAILS["telebirr"]}
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

