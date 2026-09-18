import requests
from flask import Flask, jsonify, request

app = Flask(__name__)

# የቴሌግራም ቦት ቶከን
TELEGRAM_BOT_TOKEN = "8970903838:AAHe0aHlIWVc94wAOB0lml8fM6BmVIEhaDM"

# 👑 የአድሚን ቻት አይዲ
ADMIN_CHAT_ID = "Enyachew19"

# የተጠቃሚዎች የውሂብ ማከማቻ (የምዝገባ ሁኔታን ለመያዝ)
users_db = {}

# 💯 የባንክ መረጃዎች (የእርስዎ አካውንት)
BANK_DETAILS = {
    "account_holder": "እንያቸው አመርጋ (Enyachew Amerga)",
    "cbe": "10006825286441",
    "telebirr": "0944123180"
}

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

    # 1. ጽሁፍ ወይም ምዝገባ ሲላክ
    if "message" in update:
        message = update["message"]
        chat_id = message["chat"]["id"]
        user_id = str(message["from"]["id"])
        text = message.get("text", "").strip()
        
        # ተጠቃሚው መመዝገቡን ማረጋገጥ
        if user_id not in users_db:
            users_db[user_id] = {"registered": False, "balance": 10.0, "name": ""}
            
        user_data = users_db[user_id]
        
        if text.startswith("/start"):
            if not user_data["registered"]:
                # ገና ካልተመዘገበ የምዝገባ ጥያቄ እናቀርብለታለን
                bot_message = "እንኳን ወደ Ethio Bingo Game በደህና መጡ! 🎮\n\nእባክዎ ለመመዝገብ **ስምዎን** (Full Name) በዚህ ቻት ውስጥ ጽፈው ይላኩን።"
                requests.post(url, json={"chat_id": chat_id, "text": bot_message})
                return jsonify({"status": "ok"})
            else:
                # ከተመዘገበ ቀጥታ ዋናውን ምናሌ እናሳያለን
                show_main_menu(chat_id, url, user_data)
                
        elif not user_data["registered"]:
            # ተጠቃሚው የላከውን ስም እንደ ምዝገባ እንወስደዋለን
            user_data["name"] = text
            user_data["registered"] = True
            
            bot_message = f"✅ የተከበሩ/ቺ {text} በሰላም ተመዝግበዋል! ጀማሪ ቦነስ 10 ብር ተሰጥቶዎታል።\n\nአሁን ከታች ያሉትን አማራጮች መጠቀም ይችላሉ፦"
            requests.post(url, json={"chat_id": chat_id, "text": bot_message})
            show_main_menu(chat_id, url, user_data)
            
        elif "photo" in message:
            # ስክሪንሾት ሲልክ
            bot_message = "✅ የክፍያ ስክሪንሾትዎ በእንያቸው አመርጋ አካውንት ተቀብሏል! አድሚኑ አረጋግጦ ሒሳብዎን ይጨምርልዎታል።"
            requests.post(url, json={"chat_id": chat_id, "text": bot_message})
            
            admin_notification = f"🔔 አዲስ የዲፖዚት ስክሪንሾት ከተጠቃሚ (ስም: {user_data.get('name')}, ID: {user_id}) ደርሷል!"
            requests.post(url, json={"chat_id": ADMIN_CHAT_ID, "text": admin_notification})

    # 2. አዝራሮች ሲጫኑ (Callback Query)
    elif "callback_query" in update:
        callback_query = update["callback_query"]
        callback_id = callback_query["id"]
        chat_id = callback_query["message"]["chat"]["id"]
        user_id = str(callback_query["from"]["id"])
        data = callback_query.get("data", "")
        
        requests.post(answer_callback_url, json={"callback_query_id": callback_id})
        
        if user_id not in users_db:
            users_db[user_id] = {"registered": False, "balance": 10.0, "name": ""}
            
        user_data = users_db[user_id]
        response_text = ""
        reply_markup = None
        
        if data == "play_bingo":
            response_text = "🎮 **ወደ ቢንጎ ጨዋታው በሰላም መጡ!**\n\nእባክዎ መጫወት የሚፈልጉትን የቲኬት ዋጋ ይምረጡ፦"
            reply_markup = {
                "inline_keyboard": [
                    [{"text": "🎫 ቲኬት 10 ብር", "callback_data": "bet_10"}, {"text": "🎫 ቲኬት 20 ብር", "callback_data": "bet_20"}],
                    [{"text": "🎫 ቲኬት 50 ብር", "callback_data": "bet_50"}, {"text": "🎫 ቲኬት 100 ብር", "callback_data": "bet_100"}],
                    [{"text": "🔙 ወደ ዋናው ምናሌ", "callback_data": "main_menu"}]
                ]
            }
            
        elif data.startswith("bet_"):
            bet_amount = float(data.split("_")[1])
            current_balance = user_data["balance"]
            
            if current_balance < bet_amount:
                response_text = f"⚠️ **Insufficient Balance!**\n\nየኪስ ቦርሳዎ ቀሪ ሂሳብ ({current_balance} ብር) ለዚህ ጨዋታ በቂ አይደለም።\n\nእባክዎ መጀመሪያ ዲፖዚት ያድርጉ።"
                reply_markup = {
                    "inline_keyboard": [
                        [{"text": "💰 አሁን ዲፖዚት አድርግ", "callback_data": "deposit_menu"}],
                        [{"text": "🔙 ተመለስ", "callback_data": "play_bingo"}]
                    ]
                }
            else:
                user_data["balance"] -= bet_amount
                response_text = f"🎉 ቲኬትዎ ተቆርጧል! ጨዋታው ተጀምሯል መልካም እድል!\n\nቀሪ ሂሳብዎ: {user_data['balance']} ብር"
                
        elif data == "deposit_menu":
            response_text = "💰 እባክዎ ገንዘብ ለማስገባት የሚፈልጉትን የክፍያ አማራጭ ይምረጡ (ገንዘቡ በቀጥታ ወደ እንያቸው አመርጋ አካውንት ይገባል)፦"
            reply_markup = {
                "inline_keyboard": [
                    [{"text": "ንግድ ባንክ (CBE)", "callback_data": "dep_cbe"}, {"text": "ቴሌብር (Telebirr)", "callback_data": "dep_telebirr"}],
                    [{"text": "🔙 ተመለስ", "callback_data": "main_menu"}]
                ]
            }
            
        elif data == "dep_cbe":
            response_text = f"🏦 **የንግድ ባንክ (CBE) አካውንት**\n\n• ስም: {BANK_DETAILS['account_holder']}\n• የሂሳብ ቁጥር: `{BANK_DETAILS['cbe']}`\n\nገንዘቡን ካስተላለፉ በኋላ ስክሪንሾት ይላኩ።"
            
        elif data == "dep_telebirr":
            response_text = f"📱 **ቴሌብር (Telebirr) አካውንት**\n\n• ስም: {BANK_DETAILS['account_holder']}\n• ስልክ ቁጥር: `{BANK_DETAILS['telebirr']}`\n\nገንዘቡን ካስተላለፉ በኋላ ስክሪንሾት ይላኩ።"
            
        elif data == "withdraw_menu":
            current_balance = user_data["balance"]
            response_text = f"💳 **ዊዝድሮ (Withdrawal)**\n\nአሁን ያለዎት ቀሪ ሂሳብ: **{current_balance} ብር**\n\nገንዘብ ለማውጣት ሲፈልጉ የባንክ አካውንትዎን እና መጠኑን በመጻፍ ይላኩ።"
            
        elif data == "invite_friend":
            bot_username = "Ethio_Bingo_Game_Bot"
            invite_link = f"https://t.me/{bot_username}?start=ref_{user_id}"
            response_text = f"👥 **ጓደኛ በመጋበዝ ሽልማት ያግኙ!**\n\nይህንን የእርስዎን ልዩ ሊንክ ያጋሩ፦\n\n`{invite_link}`"
            
        elif data == "contact":
            response_text = "📞 ማንኛውም ጥያቄ ካሎት አድሚኑን ማግኘት ይችላሉ።"
        elif data == "apply":
            response_text = "📝 ለማመልከት የሚፈልጉትን መረጃ እዚህ ይሙሉ ወይም ያግኙን።"
        elif data == "main_menu":
            response_text = "እንኳን ወደ ዋናው ገጽ በደህና መጡ!"
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

def get_main_keyboard():
    return {
        "inline_keyboard": [
            [{"text": "🎮 ቢንጎ ጨዋታ (Play Bingo)", "callback_data": "play_bingo"}],
            [{"text": "💰 ዲፖዚት (Deposit)", "callback_data": "deposit_menu"}, {"text": "💳 ዊዝድሮ (Withdraw)", "callback_data": "withdraw_menu"}],
            [{"text": "👥 ጓደኛ ጋብዝ (Invite Friend)", "callback_data": "invite_friend"}],
            [{"text": "📞 አግኙን (Contact Us)", "callback_data": "contact"}, {"text": "📝 ማመልከቻ (Apply)", "callback_data": "apply"}]
        ]
    }

def show_main_menu(chat_id, url, user_data):
    bot_message = f"👤 መለያ ስም: {user_data['name']}\n💰 ቀሪ ሂሳብ: {user_data['balance']} ብር\n\nየሚፈልጉትን አማራጭ ከታች ይምረጡ፦"
    payload = {
        "chat_id": chat_id,
        "text": bot_message,
        "reply_markup": get_main_keyboard()
    }
    requests.post(url, json=payload)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
