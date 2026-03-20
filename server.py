from flask import Flask, request, jsonify

app = Flask(__name__)

VALID_KEYS = [
    "Nyxo",
    "Nyxo123456",
    "NyxoPRO999"
]

USED = {}

@app.route("/auth", methods=["POST"])
def auth():
    data = request.json
    key = data.get("key")
    hwid = data.get("hwid")

    if key not in VALID_KEYS:
        return jsonify({"status": "invalid"})

    if key in USED:
        if USED[key] != hwid:
            return jsonify({"status": "hwid_mismatch"})
    else:
        USED[key] = hwid

    return jsonify({"status": "success"})

app.run(host="0.0.0.0", port=10000)