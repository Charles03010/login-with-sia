from flask import Flask, request, jsonify, render_template, redirect
from sia_actions import login_and_extract_data
import os
import asyncio

app = Flask(__name__)

@app.route("/", methods=["GET"])
def index():
    if request.args.get("error") == "failed":
        return render_template("index.html", response='failed')
    return render_template("index.html")

@app.route("/test", methods=["GET"])
def test_route():
    return redirect("/?error=failed")

@app.route("/", methods=["POST"])
def get_sia_data_route():
    if request.content_type == "application/x-www-form-urlencoded":
        data = request.form
    elif request.is_json:
        data = request.get_json()
    else:
        return jsonify({"error": "Unsupported content type"}), 400
    username = data.get("loginNipNim")
    password = data.get("loginPsw")
    if not username or not password:
        return jsonify({"error": "Username and password are required"}), 400
    print(f"Received request for username: {username}")
    return asyncio.run(login_and_extract_data(username, password))


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="127.0.0.1", port=port, debug=True)