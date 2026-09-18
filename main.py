import os
import threading
from flask import Flask, render_template
import telebot

TOKEN = os.environ.get('BOT_TOKEN', '')
bot = telebot.TeleBot(TOKEN) if TOKEN else None

app = Flask(__name__)

@app.route('/')
def home():
    try:
        return render_template('index.html')
    except Exception as e:
        return f"Template Error: {str(e)}", 500

if bot:
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
            "ሰላም! ወደ **ኢትዮ ቢንጎ ጌም** እንኳን ደህና መጡ።\n\nጨዋታውን ለመጀመር ከታች ያለውን ቁልፍ ይጫኑ!", 
            reply_markup=markup, 
            parse_mode='Markdown'
        )

    def run_bot():
        try:
            bot.remove_webhook()
            bot.infinity_polling(none_stop=True)
        except Exception as e:
            print(f"Bot error: {e}")

if __name__ == '__main__':
    if bot:
        t = threading.Thread(target=run_bot)
        t.daemon = True
        t.start()
    
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
