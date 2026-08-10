from flask import Flask, request, jsonify
from db.mongo import users
import jwt
import datetime

app = Flask(__name__)

SECRET_KEY = "supersecret"


@app.route("/login", methods=["POST"])
def login():
    try:
        data = request.get_json()

        if not data:
            return jsonify({"error": "JSON mancante"}), 400

        username = data.get("username")
        password = data.get("password")

        if not username or not password:
            return jsonify({"error": "Username o password mancanti"}), 400

        user = users.find_one({
            "username": username,
            "password": password
        })

        if not user:
            return jsonify({"error": "Credenziali non valide"}), 401

        token = jwt.encode(
            {
                "username": username,
                "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=1)
            },
            SECRET_KEY,
            algorithm="HS256"
        )

        return jsonify({"token": token})

    except Exception as e:
        print("ERRORE /login:", e)
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(host="::", port=5000, debug=True)