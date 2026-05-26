
from flask import  request, jsonify, Blueprint
from extensions import db
from models import Post, User
from flask_jwt_extended import jwt_required, get_jwt_identity


post_bp = Blueprint('post_bp', __name__)


def post_to_dict(post):
    return {
        "id": post.id,
        "title": post.title,
        "content": post.content,
        "user": {
            "id": post.user.id,
            "email": post.user.email,
            "username": post.user.username
        } if post.user else None
    }


# READ
@post_bp.route("/posts")
@jwt_required()
def fetch_posts():
    # fetching data in sqlalchemy
    posts = Post.query.all()
    results = [post_to_dict(post) for post in posts]
    return jsonify(results), 200

# ADD
@post_bp.route("/posts", methods=["POST"])
@jwt_required()
def add_post():
    data = request.get_json()

    current_user_id = get_jwt_identity()
    if not current_user_id:
        return jsonify({"error": "Unauthorized as user do not exist"}), 404
    
    new_post = Post(
        title=data["title"],
        content=data["content"],
        user_id=int(current_user_id)
    )

    db.session.add(new_post)
    db.session.commit()

    return jsonify({"success": "Post created successfully"}), 201


# read one post
@post_bp.route("/posts/<int:post_id>")
@jwt_required()
def fetch_post(post_id):
    post = Post.query.get(post_id)
    if not post:
        return jsonify({"error": "Post does not exists"}), 404
    
    return jsonify(post_to_dict(post)), 200


# -0--UPDATE
@post_bp.route("/posts/<int:id>", methods=["PUT"])
@jwt_required()
def update_post(id):
    current_user_id = int(get_jwt_identity())
    # fetch the post
    post = Post.query.get(id)

    # if post doesn't exists give an error
    if not post:
        return jsonify({"error": "Post does not exists"}), 404

    if post.user_id != current_user_id:
        return jsonify({"error": "Not authorized to update this post"}), 401
    
    data = request.get_json()

    post.title = data.get("title", post.title)
    post.content = data.get("content", post.content)

    db.session.commit()

    return jsonify({"success": "Post updated successfully"}), 200


# DELETE
@post_bp.route("/posts/<int:id>", methods=["DELETE"])
@jwt_required()
def delete_post(id):
    current_user_id = int(get_jwt_identity())
    # fetch the post
    post = Post.query.get(id)

    # if post doesn't exists give an error
    if not post:
        return jsonify({"error": "The post you want to delete does not exists"}), 404

    if post.user_id != current_user_id:
        return jsonify({"error": "Not authorized to delete this post"}), 401

    db.session.delete(post)
    db.session.commit()

    return jsonify({"success": "Post deleted successfully"}), 200


