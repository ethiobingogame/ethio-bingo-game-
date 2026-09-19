import os
import threading
from flask import Flask, render_template
import telebot

# የቦት ቶክን እና አዲሱ የሬይልዌይ ሊንክ
TOKEN = "8970903838:AAHe0aHlIWVc94wAOB0lml8fM6BmVIEhaDM"
WEB_APP_URL = "https://ethio-bingo-game-production.up.railway.app"

bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

@app.route('/')
def home():
    try:
        return render_template('index.html')
    except Exception as e:
        return f"Template Error: {str(e)}", 500

@bot.message_handler(commands=['start'])
def send_welcome(message):
    markup = telebot.types.InlineKeyboardMarkup()
    mini_app_btn = telebot.types.InlineKeyboardButton(
        text="🎮 ኢትዮ ቢንጎ ክፈት", 
        web_app=telebot.types.WebAppInfo(url=WEB_APP_URL)
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

# ቦቱ ሰርቨሩ ሲጀመር አብሮ እንዲነቃ የሚደረግበት ትሬድ
bot_thread = threading.Thread(target=run_bot)
bot_thread.daemon = True
bot_thread.start()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
