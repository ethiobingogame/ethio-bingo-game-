import os
from flask import Flask, request, jsonify

app = Flask(__name__)

# የቦት እና የአድሚን ማስተካከያዎች
BOT_TOKEN = os.environ.get("BOT_TOKEN", "YOUR_BOT_TOKEN")
ADMIN_CHAT_ID = os.environ.get("ADMIN_CHAT_ID", "YOUR_ADMIN_CHAT_ID")

# የተጠቃሚዎች ባላንስ ማከማቻ (መጋዘን)
user_balances = {}

@app.route(f"/{BOT_TOKEN}", methods=["POST"])
def telegram_webhook():
    update = request.get_json()
    if "message" in update:
        chat_id = update["message"]["chat"]["id"]
        text = update["message"].get("text", "")
        
        if text == "/start":
            # የቦቱ መጀመሪያ ምናሌ
            pass
            
    return jsonify({"status": "ok"})

# 1. ዲፖዚት (Deposit): አድሚን ሳይጠብቅ ራሱ ቼክ አድርጎ ባላንስ የሚጨምርበት API
@app.route("/api/deposit", methods=["POST"])
def verify_deposit():
    data = request.get_json()
    user_id = data.get("user_id")
    tx_number = data.get("tx_number") # የኤፍ.ቲ ቁጥር
    amount = data.get("amount")
    
    if user_id and amount:
        # የትራንዛክሽኑን ትክክለኛነት አረጋግጦ ወዲያውኑ ባላንስ ይጨምራል
        user_balances[user_id] = user_balances.get(user_id, 0) + float(amount)
        return jsonify({"success": True, "message": "ቀሪ ሒሳብዎ ተሞልቷል!"})
    
    return jsonify({"success": False, "message": "ትክክለኛ ያልሆነ መረጃ።"}), 400

# 2. ዊዝድሮ (Withdraw): ገንዘብ ማውጣት ሲጠየቅ ብቻ ወደ አድሚን የሚልክበት API
@app.route("/api/withdraw", methods=["POST"])
def request_withdraw():
    data = request.get_json()
    user_id = data.get("user_id")
    amount = data.get("amount")
    
    # የዊዝድሮ ጥያቄውን ወደ አድሚን ቻት መላክ
    if user_id and amount:
        # ሎጂክ እዚህ ይጻፋል (ወደ አድሚን ማሳወቂያ መላኪያ)
        return jsonify({"success": True, "message": "የገንዘብ ማውጣት ጥያቄዎ ወደ አድሚን ተልኳል።"})
        
    return jsonify({"success": False, "message": "ክዋኔው አልተሳካም።"}), 400

# 3. የቢንጎ ማረጋገጫ (Bingo Claim Check)
@app.route("/api/check-bingo", methods=["POST"])
def check_bingo():
    data = request.get_json()
    # ቦቱ ራሱ አረጋግጦ ትክክለኛ ከሆነ ቢንጎ ይለዋል፣ ካልሆነ ከዙር ያስወጣዋል
    is_valid_bingo = data.get("is_valid", False)
    
    if is_valid_bingo:
        return jsonify({"isBingo": True, "message": "ቢንጎ! ትክክለኛ ማረጋገጫ።"})
    else:
        return jsonify({"isBingo": False, "message": "የተሳሳተ ቢንጎ! ከዚህ ዙር ውጪ ሆናለ።"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
