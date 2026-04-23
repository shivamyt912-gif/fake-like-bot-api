from flask import Flask, request, jsonify
import requests
import random

app = Flask(__name__)

@app.route('/like', methods=['GET'])
def like_api():
    uid = request.args.get('uid')
    region = request.args.get('server_name', 'NA')
    
    if not uid:
        return jsonify({"error": "UID required"}), 400
    
    # Default values
    before_like = 0
    player_name = "N/A"
    player_level = "N/A"
    player_region = region
    player_uid = uid
    
    try:
        # Real API call to mafuuu
        response = requests.get(
            f"https://shiv-m-elite-info-bot-all-server.vercel.app/player-info?uid={uid}",
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            basic = data.get('basicInfo', {})
            account_info = data.get('AccountInfo', {})
            
            # Extract real player data
            before_like = basic.get('liked', 0)
            player_name = basic.get('nickname', 'N/A')
            player_level = basic.get('level', 'N/A')
            player_region = basic.get('region', region)
            player_uid = account_info.get('UID', uid)
            
    except Exception as e:
        print(f"Error fetching real data: {e}")
    
    # Generate fake likes (1-220)
    like_given = random.randint(1, 220)
    after_like = before_like + like_given
    
    # Build response
    result = {
        "LikesGivenByAPI": like_given,
        "LikesafterCommand": after_like,
        "LikesbeforeCommand": before_like,
        "PlayerNickname": str(player_name),
        "Region": str(player_region),
        "Level": player_level,
        "UID": int(player_uid) if str(player_uid).isdigit() else int(uid) if str(uid).isdigit() else 0,
        "status": 1
    }
    
    return jsonify(result)


@app.route('/', methods=['GET'])
def home():
    return jsonify({
        "message": "Fake Like API",
        "usage": "/like?uid={uid}&server_name={region}",
        "example": "/like?uid=123456789&server_name=NA"
    })


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)