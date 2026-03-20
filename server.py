from flask import Flask, request, render_template_string, redirect, session
import sqlite3
import os
import random
import string

app = Flask(__name__)
app.secret_key = "nyxo_secret"

USERNAME = "admin"
PASSWORD = "nyxo"

# 📦 DB
def init_db():
    conn = sqlite3.connect("keys.db")
    c = conn.cursor()
    c.execute("CREATE TABLE IF NOT EXISTS keys (key TEXT PRIMARY KEY)")
    conn.commit()
    conn.close()

init_db()

# 🔑 KEY GENERATOR
def generate_key(length=12):
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))

# 🔐 LOGIN
@app.route("/login", methods=["GET","POST"])
def login():
    if request.method == "POST":
        if request.form.get("user") == USERNAME and request.form.get("pw") == PASSWORD:
            session["logged_in"] = True
            return redirect("/")
        return "Wrong Login ❌"

    return """
    <body style="background:#0b0b0b;color:white;text-align:center;">
    <h2>Login</h2>
    <form method="POST">
    <input name="user"><br><br>
    <input name="pw" type="password"><br><br>
    <button>Login</button>
    </form>
    </body>
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
    conn.close()

    html = """
    <html>
    <head>
    <style>
    body {background:#0b0b0b;color:white;text-align:center;font-family:Arial;}
    .box {background:#111;margin:20px auto;padding:15px;border-radius:10px;width:300px;}
    button {padding:10px;border:none;border-radius:8px;background:#1f1f1f;color:white;}
    input {padding:10px;border-radius:8px;border:none;background:#1a1a1a;color:white;}
    a {color:red;text-decoration:none;}
    </style>
    </head>
    <body>

    <h1>NYXO PANEL</h1>

    <div class="box">
        <form method="POST" action="/generate">
            <button>Generate Key</button>
        </form>
    </div>

    <div class="box">
        <form method="POST" action="/add">
            <input name="key" placeholder="Custom Key">
            <button>Add Key</button>
        </form>
    </div>

    {% for k in keys %}
    <div class="box">
        <p>{{k[0]}}</p>
        <a href="/delete/{{k[0]}}">Delete</a>
    </div>
    {% endfor %}

    <br>
    <a href="/logout">Logout</a>

    </body>
    </html>
    """

    return render_template_string(html, keys=keys)

# ➕ ADD KEY
@app.route("/add", methods=["POST"])
def add():
    if not session.get("logged_in"):
        return redirect("/login")

    key = request.form.get("key")

    conn = sqlite3.connect("keys.db")
    c = conn.cursor()
    try:
        c.execute("INSERT INTO keys (key) VALUES (?)", (key,))
        conn.commit()
    except:
        pass
    conn.close()

    return redirect("/")

# 🔑 GENERATE KEY
@app.route("/generate", methods=["POST"])
def generate():
    if not session.get("logged_in"):
        return redirect("/login")

    key = generate_key()

    conn = sqlite3.connect("keys.db")
    c = conn.cursor()
    c.execute("INSERT INTO keys (key) VALUES (?)", (key,))
    conn.commit()
    conn.close()

    return redirect("/")

# ❌ DELETE
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

# 🔓 LOGOUT
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")

# 🚀 START
port = int(os.environ.get("PORT", 10000))
app.run(host="0.0.0.0", port=port)
