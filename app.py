from flask import Flask, request, jsonify
from sia_actions import login_and_extract_data
import os

app = Flask(__name__)

@app.route("/", methods=["POST"])
def get_sia_data_route():
    """
    Flask endpoint to trigger SIA login and data extraction.
    Expects JSON payload with 'username' and 'password'.
    """
    if not request.is_json:
        return jsonify({"error": "Missing JSON in request"}), 400
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")
    if not username or not password:
        return jsonify({"error": "Username and password are required"}), 400
    print(f"Received request for username: {username}")
    extracted_data = login_and_extract_data(username, password)
    if extracted_data is not None:
        return (
            jsonify({"message": "Data extracted successfully", "data": extracted_data}),
            200,
        )
    else:
        return (
            jsonify(
                {
                    "error": "Failed to login or extract data. Check server logs for details."
                }
            ),
            500,
        )
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="127.0.0.1", port=port, debug=True)