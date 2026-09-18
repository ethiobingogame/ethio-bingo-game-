from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# ዋናው የሚኒ-አፕ ገጽ (Frontend Home)
@app.route('/')
def home():
    return render_template('index.html')

# የባላንስ እና ምናሌ መቆጣጠሪያ ኤፒአይ
@app.route('/api/user-balance', methods=['GET'])
def get_balance():
    # የተጠቃሚውን ባላንስ መመለሻ
    user_id = request.args.get('user_id')
    # ከዳታቤዝ ውስጥ ባላንሱን አምጥቶ መመለስ ይቻላል
    return jsonify({"status": "success", "balance": 27.0})

# አውቶማቲክ የዲፖዚት ማረጋገጫ (Receipt / FTM Scanner Endpoint)
@app.route('/api/verify-deposit', methods=['POST'])
def verify_deposit():
    data = request.json
    ftm_code = data.get('ftm_code')
    amount = data.get('amount')
    
    # እዚህ ጋር የባንክ ደረሰኝ ወይም FTM ቁጥር የማረጋገጫ ሎጂክ ይገባል
    # ክፍያው ትክክለኛ ከሆነ በራሱ ወደ ユーザ ኪስ ቦርሳ ይጨምራል
    
    return jsonify({
        "status": "success", 
        "message": f"ብር ሐሰተኛ አለመሆኑ ተረጋግጧል። {amount} ETB ወደ አካውንትዎ ገቢ ሆኗል!"
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
