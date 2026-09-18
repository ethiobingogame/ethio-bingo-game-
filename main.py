import os
from flask import Flask, render_template, request, jsonify
import telebot

TOKEN = os.environ.get('BOT_TOKEN', 'YOUR_BOT_TOKEN')
bot = telebot.TeleBot(TOKEN)

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@bot.message_handler(commands=['start'])
def send_welcome(message):
    markup = telebot.types.InlineKeyboardMarkup()
    web_app_url = "https://ethio-bingo-game-production.up.railway.app"
    mini_app_btn = telebot.types.InlineKeyboardButton(
        text="🎮 ኢትዮ ቢንጎ ክፈት", 
        web_app=telebot.types.WebAppInfo(url=web_app_url)
    )
    markup.add(mini_app_btn)
    
    bot.reply_to(
        message, 
        "ሰላም! ወደ **ኢትዮ ቢንጎ ጌም** እንኳን ደህና መጡ።\n\n ጨዋታውን ለመጀመር እና የኪስ ቦርሳዎን ለማስተዳደር ከታች ያለውን ቁልፍ ይጫኑ!", 
        reply_markup=markup, 
        parse_mode='Markdown'
    )

@app.route(f'/{TOKEN}', methods=['POST'])
def webhook():
    json_str = request.get_data().decode('utf-8')
    update = telebot.types.Update.de_json(json_str)
    bot.process_new_updates([update])
    return "OK", 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
