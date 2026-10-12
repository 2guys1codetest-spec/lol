from flask import Flask, jsonify, request

app = Flask(__name__)

@app.route('/ping', methods=['GET'])
def ping():
    return jsonify({"status": "online"}), 200

@app.route('/login', methods=['POST'])
def login():
    data = request.json or {}
    username = data.get("username")
    return jsonify({"success": True, "message": f"Willkommen zurück, {username}!"}), 200

@app.route('/register', methods=['POST'])
def register():
    data = request.json or {}
    username = data.get("username")
    return jsonify({"success": True, "message": f"Account für {username} angelegt!"}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
