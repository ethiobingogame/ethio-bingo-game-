from flask import Flask, render_template_string, request, jsonify
import os

app = Flask(__name__)

# የጨዋታው መሠረታዊ መረጃዎች (Game State)
game_state = {
    "players_count": 0,          # የተጫዋቾች ብዛት ከ 0 ይጀምራል
    "ticket_price": 50.0,        # የአንድ ካርታ ዋጋ (በብር)
    "commission_rate": 0.20,     # የኮሚሽን ቅናሽ (20%)
    "prize_pool": 0.0,           # ለደራሽ የሚቀመጠው አጠቃላይ ገንዘብ
    "game_status": "Waiting",    # Waiting, Active, Ready, Finished
    "drawn_numbers": [],         # የተጠሩ ቁጥሮች ዝርዝር
}

# የፊት ገጽታ (HTML Template በዚሁ ፋይል ውስጥ በአንድነት የተካተተ)
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="am">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Ethio Bingo Game</title>
    <style>
        body { font-family: Arial, sans-serif; background-color: #f4f4f9; text-align: center; padding: 50px; }
        .container { background: white; padding: 30px; border-radius: 10px; box-shadow: 0px 0px 10px rgba(0,0,0,0.1); display: inline-block; max-width: 400px; width: 100%; }
        h1 { color: #333; font-size: 24px; }
        .card-info { margin: 20px 0; font-size: 18px; text-align: left; background: #fafafa; padding: 15px; border-radius: 8px; }
        .card-info p { margin: 10px 0; }
        .actions button { padding: 12px 20px; font-size: 16px; margin: 5px; cursor: pointer; background-color: #28a745; color: white; border: none; border-radius: 5px; width: 100%; }
        .actions button:hover { background-color: #218838; }
        .start-btn { background-color: #007bff !important; }
        .start-btn:hover { background-color: #0056b3 !important; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🎮 Ethio Bingo Game</h1>
        <div class="card-info">
            <p><strong>የተጫዋቾች ብዛት:</strong> <span id="players-count">{{ game.players_count }}</span></p>
            <p><strong>አጠቃላይ ደራሽ (Prize):</strong> <span id="prize-pool">{{ game.prize_pool }}</span> ብር</p>
            <p><strong>የጨዋታ ሁኔታ:</strong> <span id="game-status">{{ game.game_status }}</span></p>
        </div>
        
        <div class="actions">
            <button onclick="joinGame()">ጨዋታውን ይቀላቀሉ</button>
            <button class="start-btn" onclick="startGame()">ጨዋታ ጀምር</button>
        </div>
    </div>

    <script>
        function joinGame() {
            fetch('/api/join', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ balance: 100.0 })
            })
            .then(res => res.json())
            .then(data => {
                if(data.status === 'success') {
                    alert(data.message);
                    location.reload();
                } else {
                    alert(data.message);
                }
            });
        }

        function startGame() {
            fetch('/api/start', { method: 'POST' })
            .then(res => res.json())
            .then(data => {
                alert(data.message);
                location.reload();
            });
        }
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE, game=game_state)

@app.route('/api/join', methods=['POST'])
def join_game():
    data = request.json or {}
    user_balance = data.get('balance', 0.0)
    
    # የባላንስ ማረጋገጫ (Balance Verification)
    if user_balance < game_state['ticket_price']:
        return jsonify({
            "status": "error",
            "message": "Low Balance! በቂ ሂሳብ የለዎትም እባክዎ አካውንትዎን ይሙሉን።"
        }), 400

    # ተጫዋች ሲገባ ቁጥሩን መጨመር እና ደራሹን ማሰላት (ከ20% ኮሚሽን ጋር)
    game_state['players_count'] += 1
    total_collected = game_state['players_count'] * game_state['ticket_price']
    commission = total_collected * game_state['commission_rate']
    game_state['prize_pool'] = total_collected - commission
    
    return jsonify({
        "status": "success",
        "message": "በተሳካ ሁኔታ ጨዋታውን ተቀላቅለዋል!",
        "game": game_state
    })

@app.route('/api/status', methods=['GET'])
def get_status():
    return jsonify(game_state)

@app.route('/api/start', methods=['POST'])
def start_game():
    if game_state['players_count'] > 0:
        game_state['game_status'] = "Active"
        return jsonify({"status": "success", "message": "Ethio Bingo ጨዋታ ተጀምሯል!"})
    return jsonify({"status": "error", "message": "በቂ ተጫዋቾች አልተገኙም!"}), 400

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
