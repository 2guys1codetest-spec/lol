from flask import Flask, jsonify, request

app = Flask(__name__)

# 1. Ping-Endpunkt für die Live-Statusanzeige im Launcher
@app.route('/ping', methods=['GET'])
def ping():
    return jsonify({"status": "online"}), 200

# 2. Login-Endpunkt
@app.route('/login', methods=['POST'])
def login():
    data = request.json or {}
    username = data.get("username")
    password = data.get("password")
    
    # Hier kannst du später deine Datenbank-Prüfung einbauen
    # Aktuell senden wir eine erfolgreiche JSON-Antwort zurück:
    return jsonify({"success": True, "message": f"Willkommen zurück, {username}!"}), 200

# 3. Registrierungs-Endpunkt
@app.route('/register', methods=['POST'])
def register():
    data = request.json or {}
    username = data.get("username")
    password = data.get("password")
    
    # Hier kannst du den User in der Datenbank speichern
    return jsonify({"success": True, "message": f"Account für {username} erfolgreich erstellt!"}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
