from flask import Blueprint, request, jsonify
from models import db
from models import Post

routes = Blueprint("routes", __name__)

@routes.route("/api/posts", methods=["GET"])
def get_posts():
    posts = Post.query.all()
    return jsonify([
        {
            "id": p.id,
            "title": p.title,
            "body": p.body
        } for p in posts
    ])
@routes.route("/api/posts", methods=["POST"])
@token_required
def create_post(current_user):
    
    if current_user.role != "admin":
        return jsonify({"error": "Admin access required"}), 403

    data = request.get_json()

    new_post = Post(
        title=data["title"],
        body=data["body"]
    )

    db.session.add(new_post)
    db.session.commit()

    return jsonify({"message": "Post created successfully"})