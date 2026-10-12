from flask import Flask, jsonify, request

app = Flask(__name__)

# Der wichtigste Ping-Endpunkt für den Launcher-Status
@app.route('/ping', methods=['GET'])
def ping():
    return jsonify({"status": "online"}), 200

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    # Hier deine Login-Logik
    return jsonify({"success": True, "message": "Erfolgreich angemeldet!"})

@app.route('/register', methods=['POST'])
def register():
    data = request.json
    # Hier deine Register-Logik
    return jsonify({"success": True, "message": "Erfolgreich registriert!"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
