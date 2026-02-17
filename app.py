from flask import Flask, request, jsonify
from config import Config
from models import db, User
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
import datetime
from functools import wraps

app = Flask(__name__)
app.config.from_object(Config)
CORS(app)
db.init_app(app)

with app.app_context():
    db.create_all()

# ===============================
# TOKEN DECORATOR
# ===============================
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):

        auth_header = request.headers.get("Authorization")

        if not auth_header:
            return jsonify({"error": "Token missing"}), 401

        try:
            # cire Bearer idan yana nan
            if auth_header.startswith("Bearer "):
                token = auth_header.split(" ")[1]
            else:
                token = auth_header

            decoded = jwt.decode(
                token,
                app.config["SECRET_KEY"],
                algorithms=["HS256"]
            )

        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Token expired"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"error": "Invalid token"}), 401

        return f(decoded, *args, **kwargs)

    return decorated
# ===============================
# HOME
# ===============================
@app.route("/")
def home():
    return jsonify({
        "status": "success",
        "message": "Masfo Ultra Backend Running 🚀"
    })

# ===============================
# REGISTER
# ===============================
@app.route("/api/register", methods=["POST"])
def register():
    data = request.json

    hashed = generate_password_hash(data["password"])
    user = User(
        username=data["username"],
        password=hashed,
        role="admin"   # 👈 wannan layin muhimmi ne
    )

    db.session.add(user)
    db.session.commit()

    return jsonify({"message": "User registered"}), 201

# ===============================
# LOGIN
# ===============================
@app.route("/api/login", methods=["POST"])
def login():

    data = request.json
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
# =====================
# ADMIN ROUTE - GET USERS
# =====================
@app.route("/api/users")
@token_required
def get_users(decoded):
    if decoded["role"] != "admin":
        return jsonify({"error": "Admin only"}), 403

    users = User.query.all()
    return jsonify([
        {"id": u.id, "username": u.username, "role": u.role}
        for u in users
    ])

# ===============================
# PROTECTED
# ===============================
@app.route("/api/protected")
@token_required
def protected(decoded):
    return jsonify({
        "message": "Access granted",
        "user_id": decoded["user_id"],
        "role": decoded["role"]
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
# =====================
# DELETE USER
# =====================
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
# ===============================
# USER PROFILE
# ===============================
@app.route("/api/profile", methods=["GET"])
@token_required
def profile(decoded):

    user = User.query.get(decoded["user_id"])

    if not user:
        return jsonify({"error": "User not found"}), 404

    return jsonify({
        "id": user.id,
        "username": user.username,
        "role": user.role,
        "full_name": user.full_name,
        "phone": user.phone,
        "country": user.country,
        "state": user.state,
        "city": user.city
    })
@app.route("/api/create-admin")
def create_admin():
    from models import User
    from werkzeug.security import generate_password_hash
    
    existing = User.query.filter_by(username="admin").first()
    if existing:
        return "Admin already exists"

    user = User(
        username="admin",
        email="admin@masfo.com",
        password=generate_password_hash("123456"),
        role="user"
    )

    db.session.add(user)
    db.session.commit()

    return "Admin created successfully"
@app.route("/api/change-password", methods=["PUT"])
@token_required
def change_password(decoded):
    user = User.query.get(decoded["user_id"])

    data = request.get_json()
    user.password = generate_password_hash(data["password"])

    db.session.commit()

    return jsonify({"message":"Password updated"})
@app.route("/setup-admin")
def setup_admin():
    from werkzeug.security import generate_password_hash
    
    existing = User.query.filter_by(username="admin").first()
    if existing:
        return "Admin already exists"

    admin = User(
        full_name="Super Admin",
        username="admin",
        password=generate_password_hash("admin123"),
        role="admin"
    )

    db.session.add(admin)
    db.session.commit()

    return "Admin created"