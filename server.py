import json
import os
import sqlite3
import time
from flask import Flask, jsonify, request
from werkzeug.security import check_password_hash, generate_password_hash

app = Flask(__name__)
DB_FILE = "aethelia_secure.db"

# Zentraler Speicher im Arbeitsspeicher für Echtzeit-Multiplayer (Heartbeats & PvP)
ACTIVE_SESSIONS = {}


def init_db():
    """Initialisiert die SQLite-Datenbank mit sicheren Tabellenstrukturen."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            password_hash TEXT NOT NULL,
            player_data TEXT NOT NULL
        )
    """
    )
    conn.commit()
    conn.close()


init_db()


def cleanup_inactive_sessions():
    """Entfernt inaktive Spieler automatisch nach 10 Sekunden (verhindert Ghost-Spieler)."""
    now = time.time()
    to_delete = [
        user
        for user, data in ACTIVE_SESSIONS.items()
        if now - data.get("last_seen", 0) > 10
    ]
    for user in to_delete:
        del ACTIVE_SESSIONS[user]


@app.route("/ping", methods=["GET"])
def ping():
    cleanup_inactive_sessions()
    return (
        jsonify(
            {
                "status": "online",
                "online_players_count": len(ACTIVE_SESSIONS),
            }
        ),
        200,
    )


@app.route("/register", methods=["POST"])
def register():
    data = request.json
    username = data.get("username")
    password = data.get("password")
    player_data = data.get("player_data")

    if not username or not password or not player_data:
        return (
            jsonify({"success": False, "message": "Unvollständige Daten."}),
            400,
        )

    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    # Schutz vor SQL-Injection durch Prepared Statements (?)
    cursor.execute("SELECT username FROM users WHERE username = ?", (username,))
    if cursor.fetchone():
        conn.close()
        return (
            jsonify(
                {"success": False, "message": "Benutzername bereits vergeben."}
            ),
            400,
        )

    # Sicheres Passwort-Hashing (kein Klartext!)
    pwd_hash = generate_password_hash(password)
    cursor.execute(
        "INSERT INTO users (username, password_hash, player_data) VALUES (?, ?, ?)",
        (username, pwd_hash, json.dumps(player_data)),
    )
    conn.commit()
    conn.close()

    return (
        jsonify({"success": True, "message": "Account erfolgreich erstellt!"}),
        201,
    )


@app.route("/login", methods=["POST"])
def login():
    cleanup_inactive_sessions()
    data = request.json
    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return jsonify({"success": False, "message": "Fehlende Anmeldedaten."}), 400

    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT password_hash, player_data FROM users WHERE username = ?",
        (username,),
    )
    row = cursor.fetchone()
    conn.close()

    if row and check_password_hash(row[0], password):
        p_data = json.loads(row[1])
        ACTIVE_SESSIONS[username] = {
            "level": p_data.get("level", 1),
            "coords": [0, 0],
            "last_seen": time.time(),
        }
        return (
            jsonify(
                {
                    "success": True,
                    "message": "Login erfolgreich",
                    "player_data": p_data,
                }
            ),
            200,
        )

    return (
        jsonify(
            {"success": False, "message": "Ungültiger Benutzername oder Passwort."}
        ),
        401,
    )


@app.route("/heartbeat", methods=["POST"])
def heartbeat():
    cleanup_inactive_sessions()
    data = request.json
    username = data.get("username")
    coords = data.get("coords", [0, 0])

    if username in ACTIVE_SESSIONS:
        ACTIVE_SESSIONS[username]["last_seen"] = time.time()
        ACTIVE_SESSIONS[username]["coords"] = coords
        return jsonify({"success": True}), 200
    return jsonify({"success": False}), 404


@app.route("/save", methods=["POST"])
def save_progress():
    data = request.json
    username = data.get("username")
    player_data = data.get("player_data")

    if not username or not player_data:
        return jsonify({"success": False}), 400

    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE users SET player_data = ? WHERE username = ?",
        (json.dumps(player_data), username),
    )
    conn.commit()
    conn.close()

    if username in ACTIVE_SESSIONS:
        ACTIVE_SESSIONS[username]["last_seen"] = time.time()

    return jsonify({"success": True}), 200


@app.route("/online-players", methods=["GET"])
def online_players():
    cleanup_inactive_sessions()
    return jsonify({"players": ACTIVE_SESSIONS}), 200


@app.route("/logout", methods=["POST"])
def logout():
    data = request.json
    username = data.get("username")
    if username in ACTIVE_SESSIONS:
        del ACTIVE_SESSIONS[username]
    return jsonify({"success": True}), 200


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)