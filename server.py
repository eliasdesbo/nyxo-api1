from flask import Flask, request, jsonify, render_template_string, redirect, session
import sqlite3
import os
import datetime

app = Flask(__name__)
app.secret_key = "nyxo_secret_key"

# 🔐 PANEL LOGIN DATEN
USERNAME = "admin"
PASSWORD = "nyxo"

# 📦 DATABASE
def init_db():
    conn = sqlite3.connect("keys.db")
    c = conn.cursor()
    c.execute("CREATE TABLE IF NOT EXISTS keys (key TEXT PRIMARY KEY, hwid TEXT)")
    c.execute("CREATE TABLE IF NOT EXISTS logs (key TEXT, hwid TEXT, time TEXT)")
    conn.commit()
    conn.close()

init_db()

# 🔐 AUTH API
@app.route("/auth", methods=["POST"])
def auth():
    data = request.json
    key = data.get("key")
    hwid = data.get("hwid")

    if key.lower() == "nyxo":
        return jsonify({"status": "success"})

    conn = sqlite3.connect("keys.db")
    c = conn.cursor()

    c.execute("SELECT hwid FROM keys WHERE key=?", (key,))
    result = c.fetchone()

    if not result:
        conn.close()
        return jsonify({"status": "invalid"})

    saved = result[0]

    if saved is None:
        c.execute("UPDATE keys SET hwid=? WHERE key=?", (hwid, key))
        conn.commit()
    elif saved != hwid:
        conn.close()
        return jsonify({"status": "hwid_mismatch"})

    # 📊 LOG SPEICHERN
    c.execute("INSERT INTO logs (key, hwid, time) VALUES (?, ?, ?)", 
              (key, hwid, str(datetime.datetime.now())))
    conn.commit()

    conn.close()
    return jsonify({"status": "success"})

# 🔐 LOGIN PAGE
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        user = request.form.get("user")
        pw = request.form.get("pw")

        if user == USERNAME and pw == PASSWORD:
            session["logged_in"] = True
            return redirect("/")
        else:
            return "Wrong Login"

    return """
    <h2>NYXO LOGIN</h2>
    <form method="POST">
        <input name="user" placeholder="Username"><br><br>
        <input name="pw" type="password" placeholder="Password"><br><br>
        <button>Login</button>
    </form>
    """

# 🖥 PANEL
@app.route("/")
def panel():
    if not session.get("logged_in"):
        return redirect("/login")

    conn = sqlite3.connect("keys.db")
    c = conn.cursor()

    c.execute("SELECT * FROM keys")
    keys = c.fetchall()

    c.execute("SELECT * FROM logs ORDER BY time DESC LIMIT 20")
    logs = c.fetchall()

    conn.close()

    html = """
    <html>
    <head>
    <title>NYXO ULTRA PANEL</title>
    <style>
    body {background:#0f0f0f;color:#00ffcc;font-family:Arial;text-align:center;}
    .box {background:#141414;margin:20px auto;padding:15px;border-radius:12px;width:320px;}
    input {padding:10px;border-radius:8px;border:none;background:#1a1a1a;color:#00ffcc;}
    button {padding:10px;border:none;border-radius:8px;background:#1f1f1f;color:#00ffcc;}
    a {color:red;text-decoration:none;}
    </style>
    </head>
    <body>

    <h1>NYXO ULTRA PANEL</h1>

    <div class="box">
        <form method="POST" action="/add">
            <input name="key" placeholder="New Key">
            <button>Add</button>
        </form>
    </div>

    <h2>KEYS</h2>
    {% for k in keys %}
    <div class="box">
        <p><b>{{k[0]}}</b></p>
        <p>HWID: {{k[1]}}</p>
        <a href="/delete/{{k[0]}}">Delete</a>
    </div>
    {% endfor %}

    <h2>LAST LOGS</h2>
    {% for log in logs %}
    <div class="box">
        <p>Key: {{log[0]}}</p>
        <p>HWID: {{log[1]}}</p>
        <p>{{log[2]}}</p>
    </div>
    {% endfor %}

    </body>
    </html>
    """

    return render_template_string(html, keys=keys, logs=logs)

# ➕ ADD KEY
@app.route("/add", methods=["POST"])
def add():
    if not session.get("logged_in"):
        return redirect("/login")

    key = request.form.get("key")

    conn = sqlite3.connect("keys.db")
    c = conn.cursor()
    try:
        c.execute("INSERT INTO keys (key, hwid) VALUES (?, NULL)", (key,))
        conn.commit()
    except:
        pass
    conn.close()

    return redirect("/")

# ❌ DELETE KEY
@app.route("/delete/<key>")
def delete(key):
    if not session.get("logged_in"):
        return redirect("/login")

    conn = sqlite3.connect("keys.db")
    c = conn.cursor()
    c.execute("DELETE FROM keys WHERE key=?", (key,))
    conn.commit()
    conn.close()

    return redirect("/")

# 🚀 START
port = int(os.environ.get("PORT", 10000))
app.run(host="0.0.0.0", port=port)
