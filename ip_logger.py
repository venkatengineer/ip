from flask import Flask, request, jsonify, send_from_directory, send_file
import sqlite3
from datetime import datetime
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app)  # allow frontend to call backend

DB_NAME = "ips.db"

# ---------- Database Setup ----------
def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS visitors (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ip TEXT,
            timestamp TEXT
        )
    ''')
    conn.commit()
    conn.close()

init_db()

# ---------- Helper ----------
def save_ip(ip):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("INSERT INTO visitors (ip, timestamp) VALUES (?, ?)", (ip, datetime.now().isoformat()))
    conn.commit()
    conn.close()

# ---------- Routes ----------

@app.route("/download_db")
def download_db():
    if not os.path.exists(DB_NAME):
        return jsonify({"error": "Database file not found"}), 404
    return send_file(DB_NAME, as_attachment=True)

@app.route("/log", methods=["GET"])
def log_ip():
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        ip = forwarded.split(",")[0]
    else:
        ip = request.remote_addr

    save_ip(ip)
    return jsonify({"status": "success", "message": "IP logged"})

@app.route("/")
def serve_frontend():
    return send_from_directory(".", "index.html")

@app.route("/logs")
def show_logs():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT ip, timestamp FROM visitors")
    rows = c.fetchall()
    conn.close()
    return jsonify(rows)

# ---- Debug helper (optional)
@app.route("/files")
def list_files():
    return jsonify(os.listdir("."))

if __name__ == "__main__":
    # Render requires host 0.0.0.0
    app.run(host="0.0.0.0", port=5000)
