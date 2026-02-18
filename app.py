from flask import Flask, request, jsonify
from config import Config
from models import db, User
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
import datetime
from functools import wraps
from routes import routes
from auth import token_required

app = Flask(__name__)   # ⚡ Create app FIRST

app.config.from_object(Config)
CORS(app)

db.init_app(app)

app.register_blueprint(routes)   # ⚡ Register AFTER app created

with app.app_context():
    db.create_all()
# HOME
# ==========================================
@app.route("/")
def home():
    return jsonify({
        "status": "success",
        "message": "Masfo Ultra Backend Running 🚀"
    })


# ==========================================
# REGISTER
# ==========================================
@app.route("/api/register", methods=["POST"])
def register():
    data = request.get_json()

    if User.query.filter_by(username=data["username"]).first():
        return jsonify({"error": "Username already exists"}), 400

    if User.query.filter_by(email=data["email"]).first():
        return jsonify({"error": "Email already exists"}), 400

    hashed = generate_password_hash(data["password"])

    user = User(
        username=data["username"],
        email=data["email"],
        password=hashed,
        full_name=data.get("full_name"),
        phone=data.get("phone"),
        country=data.get("country"),
        state=data.get("state"),
        city=data.get("city"),
        role="user"
    )

    db.session.add(user)
    db.session.commit()

    return jsonify({"message": "User registered successfully"}), 201


# ==========================================
# LOGIN
# ==========================================
@app.route("/api/login", methods=["POST"])
def login():
    try:
        data = request.get_json()

        user = User.query.filter_by(username=data["username"]).first()

        if not user:
            return jsonify({"error": "User not found"}), 404

        if not check_password_hash(user.password, data["password"]):
            return jsonify({"error": "Wrong password"}), 401

        token = jwt.encode({
            "user_id": user.id,
            "role": user.role,
            "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=1)
        }, app.config["SECRET_KEY"], algorithm="HS256")

        return jsonify({
            "access_token": token,
            "role": user.role
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500
# ==========================================
# GET ALL USERS (ADMIN ONLY)
# ==========================================
@app.route("/api/users", methods=["GET"])
@token_required
def get_users(decoded):

    if decoded["role"] != "admin":
        return jsonify({"error": "Admin only"}), 403

    users = User.query.all()

    return jsonify([
        {
            "id": u.id,
            "username": u.username,
            "email": u.email,
            "role": u.role
        }
        for u in users
    ])


# ==========================================
# DELETE USER (ADMIN ONLY)
# ==========================================
@app.route("/api/users/<int:user_id>", methods=["DELETE"])
@token_required
def delete_user(decoded, user_id):

    if decoded["role"] != "admin":
        return jsonify({"error": "Admin only"}), 403

    user = User.query.get(user_id)

    if not user:
        return jsonify({"error": "User not found"}), 404

    db.session.delete(user)
    db.session.commit()

    return jsonify({"message": "User deleted"})


# ==========================================
# USER PROFILE
# ==========================================
@app.route("/api/profile", methods=["GET"])
@token_required
def profile(decoded):

    user = User.query.get(decoded["user_id"])

    if not user:
        return jsonify({"error": "User not found"}), 404

    return jsonify({
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "role": user.role,
        "full_name": user.full_name,
        "phone": user.phone,
        "country": user.country,
        "state": user.state,
        "city": user.city
    })


# ==========================================
# CHANGE PASSWORD
# ==========================================
@app.route("/api/change-password", methods=["PUT"])
@token_required
def change_password(decoded):

    user = User.query.get(decoded["user_id"])
    data = request.get_json()

    user.password = generate_password_hash(data["password"])
    db.session.commit()

    return jsonify({"message": "Password updated successfully"})


# ==========================================
# CREATE FIRST ADMIN (RUN ONCE)
# ==========================================
@app.route("/setup-admin")
def setup_admin():

    existing = User.query.filter_by(username="admin").first()
    if existing:
        return "Admin already exists"

    admin = User(
        full_name="Super Admin",
        username="admin",
        email="admin@masfo.com",
        password=generate_password_hash("admin123"),
        role="admin"
    )

    db.session.add(admin)
    db.session.commit()

    return "Admin created successfully"


# ==========================================
# RUN APP (VERY LAST)
# ==========================================
import os

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)