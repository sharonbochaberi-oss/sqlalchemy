from flask import Blueprint, request, jsonify

from extensions import db
from models import User
from werkzeug.security import generate_password_hash

user_bp = Blueprint("user_bp", __name__)


# GET ALL USERS
@user_bp.route("/users", methods=["GET"])
def get_users():

    users = User.query.all()

    return jsonify([
        user.to_dict() for user in users
    ]), 200


# GET SINGLE USER
@user_bp.route("/users/<int:id>", methods=["GET"])
def get_user(id):

    user = User.query.get(id)

    if not user:
        return jsonify({
            "error": "User not found"
        }), 404

    return jsonify(user.to_dict()), 200


# CREATE USER
@user_bp.route("/users", methods=["POST"])
def create_user():

    data = request.get_json()

    new_user = User(
        username=data["username"],
        email=data["email"],
        password=data["password"]
    )

    db.session.add(new_user)
    db.session.commit()

    return jsonify({
        "message": "User created successfully"
    }), 201


# UPDATE USER
@user_bp.route("/users/<int:id>", methods=["PATCH"])
def update_user(id):

    user = User.query.get(id)

    if not user:
        return jsonify({
            "error": "User not found"
        }), 404

    data = request.get_json()

    user.username = data.get(
        "username",
        user.username
    )

    user.email = data.get(
        "email",
        user.email
    )

    db.session.commit()

    return jsonify({
        "message": "User updated successfully"
    }), 200


# DELETE USER
@user_bp.route("/users/<int:id>", methods=["DELETE"])
def delete_user(id):

    user = User.query.get(id)

    if not user:
        return jsonify({
            "error": "User not found"
        }), 404

    db.session.delete(user)
    db.session.commit()

    return jsonify({
        "message": "User deleted successfully"
    }), 200