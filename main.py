import os
from flask import Flask, request
import telebot
from telebot import types

# የቦቱን ቶከን እዚህ ያስገቡ
TOKEN = os.getenv('BOT_TOKEN', 'YOUR_BOT_TOKEN_HERE')
bot = telebot.TeleBot(TOKEN)

# የአድሚን እና የባንክ መረጃዎች
ADMIN_USERNAME = "@enyachew_19"
ADMIN_CHAT_ID = os.getenv('ADMIN_CHAT_ID', '123456789')
ACCOUNT_NAME = "እነያቸዉ አመርጋ"
TELEBIRR_ACCOUNT = "0944123180"
CBE_ACCOUNT = "1000682528641"

# የተጠቃሚዎች መረጃ መያዣ
users_db = {}
user_states = {}

app = Flask(__name__)

# ዋናው ሜኑ
def main_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    play_btn = types.KeyboardButton("🎮 Play (ኢትዮ ቢንጎ ጨዋታ)")
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
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        reg_btn = types.KeyboardButton("📝 ይመዝገቡ (Register)")
        markup.add(reg_btn)
        
        bot.send_message(
            message.chat.id,
            f"ሰላም <b>{message.from_user.first_name}</b>! ወደ <b>ኢትዮ ቢንጎ (Ethio Bingo)</b> እንኳን በደህና መጡ።\n\n"
            "ቦቱን ለመጠቀም መጀመሪያ መመዝገብ አለብዎት። ከታች ያለውን በመጫን ይመዝገቡ!",
            parse_mode='HTML',
            reply_markup=markup
        )
        user_states[user_id] = "waiting_registration"
    else:
        bot.send_message(
            message.chat.id,
            "እንኳን ደህና መጡ! ከታች ካሉት አማራጮች የሚፈልጉትን መምረጥ ይችላሉ።",
            reply_markup=main_menu()
        )

@bot.message_handler(func=lambda message: True)
def handle_messages(message):
    user_id = message.from_user.id
    text = message.text
    chat_id = message.chat.id

    if text == "📝 ይመዝገቡ (Register)" or user_states.get(user_id) == "waiting_registration":
        users_db[user_id] = {"balance": 0.0, "name": message.from_user.first_name}
        user_states[user_id] = "registered"
        bot.send_message(
            chat_id,
            "✅ በስኬት ተመዝግበዋል! አሁን የኢትዮ ቢንጎ ጨዋታዎችን መጫወት ይችላሉ።",
            reply_markup=main_menu()
        )
        return

    if "Play" in text or "ጨዋታ" in text:
        # ልክ እንደ ኦሪጅናሉ አቀማመጥ (Active Game, Stake, Start in waiting እና የቦርድ ምርጫዎች)
        game_markup = types.InlineKeyboardMarkup(row_width=1)
        game_markup.add(
            types.InlineKeyboardButton("🟢 10 ETB | Active: playing | Players: 77 | 616 ETB", callback_data="play_10"),
            types.InlineKeyboardButton("🔵 20 ETB | Active: Low balance | Players: 10 | 160 ETB", callback_data="play_20"),
            types.InlineKeyboardButton("🟣 50 ETB | Active: Low balance | Players: 65 | 2640 ETB", callback_data="play_50"),
            types.InlineKeyboardButton("🎲 ሰሌዳ ቁጥር መርጠው ለመጀመር (Select Board)", callback_data="select_board")
        )
        bot.send_message(
            chat_id, 
            "🎮 <b>Ethio Bingo Mini App</b>\n\n"
            "ማስተካከያ: አሁን የሚፈልጉትን የETB አማራጭ በመምረጥ ጨዋታውን ይጀምሩ! ሰዓቱ ሲደርስ ቁጥሮች በራሳቸው ይጠራሉ::", 
            parse_mode='HTML', 
            reply_markup=game_markup
        )

    elif "Deposit" in text or "ብር አጫውት" in text:
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
                user_states[user_id] = "waiting_withdraw_account"
                
                acc_markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
                acc_markup.add(types.KeyboardButton("📱 ቴሌብር (Telebirr) ቁጥሬን"), types.KeyboardButton("🏦 የንግድ ባንክ (CBE) አካውንቴን"))
                bot.send_message(chat_id, "አካውንትዎ የሚላክበትን የባንክ ዓይነት ይምረጡ ወይም የባንክ/ቴሌብር ቁጥርዎን ይጻፉ:", reply_markup=acc_markup)
        except ValueError:
            bot.send_message(chat_id, "❌ እባክዎ ትክክለኛ ቁጥር ብቻ ያስገቡ (ለምሳሌ: 150)።")

    elif user_states.get(user_id) == "waiting_withdraw_account":
        account_details = text
        amount = user_states.get(f"withdraw_amt_{user_id}", 0)
        
        admin_msg = (
            f"🚨 <b>አዲስ የገንዘብ ማውጣት (Withdraw) ጥያቄ!</b>\n\n"
            f"👤 <b>ተጠቃሚ:</b> {message.from_user.first_name} (ID: <code>{user_id}</code>)\n"
            f"💰 <b>መጠን:</b> {amount} ብር\n"
            f"🏦 <b>የአካውንት መረጃ:</b> {account_details}\n\n"
            f"እባክዎ አረጋግጠው ገንዘቡን ያስተላልፉ። አድሚን: {ADMIN_USERNAME}"
        )
        
        try:
            bot.send_message(ADMIN_CHAT_ID, admin_msg, parse_mode='HTML')
        except Exception as e:
            print(f"Error sending to admin: {e}")

        user_states[user_id] = "registered"
        bot.send_message(chat_id, f"✅ የብር ማውጣት ጥያቄዎ በአስተዳዳሪው ({ADMIN_USERNAME}) ዘንድ ደርሷል። አድሚኑ አረጋግጦ ይለቅልዎታል!", reply_markup=main_menu())

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    chat_id = call.message.chat.id
    
    if call.data.startswith("play_"):
        stake = call.data.split("_")[1]
        bot.answer_callback_query(call.id, f"የ {stake} ብር ጨዋታ ተመረጠ!")
        
        # ልክ እንደ ኦሪጅናሉ ቦርድ ምርጫ (ለምሳሌ Board 38 እና ቁጥሮች አወጣጥ ሎጂክ)
        board_markup = types.InlineKeyboardMarkup(row_width=3)
        board_markup.add(
            types.InlineKeyboardButton("🎲 Board 38 (ይምረጡ)", callback_data="select_board_38"),
            types.InlineKeyboardButton("🔄 Refresh", callback_data="refresh_game"),
            types.InlineKeyboardButton("🚪 Leave", callback_data="leave_game")
        )
        bot.send_message(
            chat_id, 
            f"🎯 <b>Ethio Bingo - Stake: {stake} ETB</b>\n\n"
            "ሰዓቱ እየቆጠረ ነው (Start in waiting...) ቁጥሮች በድምፅ እና በጽሁፍ በቅደም ተከተል ይጠራሉ። "
            "ካርድዎ ላይ ቁጥሩ ሲመጣ የሚለውን ተጭነው 'ቢንጎ (BINGO)' ይበሉ!",
            parse_mode='HTML',
            reply_markup=board_markup
        )

    elif call.data == "select_board":
        bot.send_message(chat_id, "📋 እባክዎ ከ 1 እስከ 100 ካሉት ሰሌዳዎች (Boards) የሚፈልጉትን ይምረጡ።")

    elif call.data == "select_board_38":
        bot.send_message(chat_id, "✅ ሰሌዳ ቁጥር 38 ተመርጧል። ጨዋታው ተጀምሯል! አሸናፊው ከፍ ያለ ሽልማት (ደራሽ) ይወስዳል።")

    elif call.data == "refresh_game":
        bot.answer_callback_query(call.id, "መረጃው ታድሷል (Refreshed)!")

    elif call.data == "leave_game":
        bot.answer_callback_query(call.id, "ከጨዋታው ወጥተዋል!")
        bot.send_message(chat_id, "ከጨዋታው ወጥተዋል፣ ዋናውን ሜኑ መጠቀም ይችላሉ።", reply_markup=main_menu())

    elif call.data == "dep_telebirr":
        bot.send_message(
            chat_id,
            f"📱 <b>በቴሌብር ለማስገባት:</b>\n\n"
            f"👤 <b>ስም:</b> {ACCOUNT_NAME}\n"
            f"📱 <b>ቁጥር:</b> <code>{TELEBIRR_ACCOUNT}</code>\n\n"
            "ብር ከላኩ በኋላ የትራንዛክሽን ማረጋገጫ (Screenshot ወይም Receipt) እዚህ ይላኩ። አድሚኑ አረጋግጦ ወደ ባላንስዎ ይጨምራል!",
            parse_mode='HTML'
        )

    elif call.data == "dep_cbe":
        bot.send_message(
            chat_id,
            f"🏦 <b>በንግድ ባንክ (CBE) ለማስገባት:</b>\n\n"
            f"👤 <b>ስም:</b> {ACCOUNT_NAME}\n"
            f"🏦 <b>አካውንት:</b> <code>{CBE_ACCOUNT}</code>\n\n"
            "ብር ከላኩ በኋላ የትራንዛክሽን ማረጋገጫ (Screenshot ወይም Receipt) እዚህ ይላኩ። አድሚኑ አረጋግጦ ወደ ባላንስዎ ይጨምራል!",
            parse_mode='HTML'
        )

@bot.message_handler(content_types=['photo'])
def handle_docs_photo(message):
    user_id = message.from_user.id
    chat_id = message.chat.id
    
    bot.send_message(
        chat_id, 
        f"📥 የክፍያ ማረጋገጫ ፎቶዎ ደርሷል! አድሚኑ ({ADMIN_USERNAME}) እያረጋገጠው ነው። ትክክለኛ ከሆነ ወዲያውኑ ወደ ባላንስዎ ይጨመራል።", 
        parse_mode='HTML',
        reply_markup=main_menu()
    )
    
    try:
        bot.forward_message(ADMIN_CHAT_ID, chat_id, message.message_id)
        bot.send_message(ADMIN_CHAT_ID, f"💳 ከ <b>{message.from_user.first_name}</b> (ID: <code>{user_id}</code>) የመጣ የዲፖዚት ማረጋገጫ ፎቶ ነው።", parse_mode='HTML')
    except Exception as e:
        print(f"Admin forward error: {e}")

@app.route('/' + TOKEN, methods=['POST'])
def getMessage():
    json_string = request.get_data().decode('utf-8')
    update = telebot.types.Update.de_json(json_string)
    bot.process_new_updates([update])
    return "!", 200

@app.route("/")
def webhook():
    bot.remove_webhook()
    bot.set_webhook(url='https://YOUR_RENDER_APP_URL.onrender.com/' + TOKEN)
    return "Ethio Bingo Mini App is running!", 200

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=int(os.environ.get('PORT', 5000)))
