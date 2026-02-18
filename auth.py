from functools import wraps
from flask import request, jsonify, current_app
import jwt
from models import User

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get("Authorization")

        if not auth_header:
            return jsonify({"error": "Token missing"}), 401

        try:
            if auth_header.startswith("Bearer "):
                token = auth_header.split(" ")[1]
            else:
                return jsonify({"error": "Invalid token format"}), 401

            data = jwt.decode(
                token,
                current_app.config["SECRET_KEY"],
                algorithms=["HS256"]
            )

            # ✅ WANNAN KA MANTA
            current_user = User.query.get(data["user_id"])

            if not current_user:
                return jsonify({"error": "User not found"}), 401

        except Exception:
            return jsonify({"error": "Token invalid"}), 401

        return f(current_user, *args, **kwargs)

    return decorated