from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from extensions import db
from models import Comment, Post

comment_bp = Blueprint("comment_bp", __name__)


# ==================== COMMENT CRUD OPERATIONS =============================

# READ: Fetch all comments
@comment_bp.route("/comments", methods=["GET"])
def fetch_comments():

    comments = Comment.query.all()

    results = []

    for comment in comments:
        results.append({
            "id": comment.id,
            "content": comment.content,
            "post_id": comment.post_id,
            "user_id": comment.user_id
        })

    return jsonify(results), 200


# CREATE: Add a new comment
@comment_bp.route("/comments", methods=["POST"])
@jwt_required()
def add_comment():

    data = request.get_json() or {}

    if not data.get("content") or not data.get("post_id"):
        return jsonify({
            "error": "Missing required fields"
        }), 400

    current_user_id = int(get_jwt_identity())

    post = db.session.get(Post, data["post_id"])

    if not post:
        return jsonify({
            "error": "Post does not exist"
        }), 404

    new_comment = Comment(
        content=data["content"],
        post_id=data["post_id"],
        user_id=current_user_id
    )

    db.session.add(new_comment)
    db.session.commit()

    return jsonify({
        "success": "Comment created successfully",
        "comment": {
            "id": new_comment.id,
            "content": new_comment.content,
            "post_id": new_comment.post_id,
            "user_id": new_comment.user_id
        }
    }), 201


# READ: Fetch single comment
@comment_bp.route("/comments/<int:id>", methods=["GET"])
def fetch_comment(id):

    comment = db.session.get(Comment, id)

    if not comment:
        return jsonify({
            "error": "Comment not found"
        }), 404

    return jsonify({
        "id": comment.id,
        "content": comment.content,
        "post_id": comment.post_id,
        "user_id": comment.user_id
    }), 200


# UPDATE COMMENT
@comment_bp.route("/comments/<int:id>", methods=["PUT", "PATCH"])
@jwt_required()
def update_comment(id):

    comment = db.session.get(Comment, id)

    if not comment:
        return jsonify({
            "error": "Comment not found"
        }), 404

    current_user_id = int(get_jwt_identity())

    if comment.user_id != current_user_id:
        return jsonify({
            "error": "Unauthorized"
        }), 403

    data = request.get_json() or {}

    comment.content = data.get(
        "content",
        comment.content
    )

    db.session.commit()

    return jsonify({
        "success": "Comment updated successfully"
    }), 200


# DELETE COMMENT
@comment_bp.route("/comments/<int:id>", methods=["DELETE"])
@jwt_required()
def delete_comment(id):

    comment = db.session.get(Comment, id)

    if not comment:
        return jsonify({
            "error": "Comment not found"
        }), 404

    current_user_id = int(get_jwt_identity())

    if comment.user_id != current_user_id:
        return jsonify({
            "error": "Unauthorized"
        }), 403

    db.session.delete(comment)
    db.session.commit()

    return jsonify({
        "success": "Comment deleted successfully"
    }), 200