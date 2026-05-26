from datetime import datetime, timezone
from flask import Blueprint, request, jsonify
from extensions import db
from models import User, TokenBlocklist
from werkzeug.security import check_password_hash
from flask_jwt_extended import (
    create_access_token, 
    create_refresh_token, 
    jwt_required, 
    get_jwt_identity, 
    get_jwt
)

auth_bp = Blueprint('auth_bp', __name__)

# ==================== AUTHENTICATION OPERATIONS =============================

# POST: Authenticate user and return JWT tokens
@auth_bp.route("/login", methods=["POST"])
def login_user():
    data = request.get_json() or {}
    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return jsonify({"error": "Email and password are required"}), 400

    # Locate user by email
    user = User.query.filter_by(email=email).first()

    # Verify password hash match
    if user and check_password_hash(user.password, password):
        access_token = create_access_token(identity=str(user.id))
        refresh_token = create_refresh_token(identity=str(user.id))
        
        return jsonify({
            "access_token": access_token, 
            "refresh_token": refresh_token,
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email
            }
        }), 200
    
    return jsonify({"error": "Invalid email or password"}), 401


# POST: Generate a new access token using a valid refresh token
@auth_bp.route("/refresh", methods=["POST"])
@jwt_required(refresh=True)
def refresh():
    current_user_id = get_jwt_identity()
    access_token = create_access_token(identity=str(current_user_id))
    return jsonify({"access_token": access_token}), 200


# GET: Fetch authenticated user's profile details
@auth_bp.route("/current_user", methods=["GET"])
@jwt_required()
def loggedin_user():
    current_user_id = get_jwt_identity()

    # Modernized SQLAlchemy 2.0 query structure
    user = db.session.get(User, int(current_user_id))

    if not user:
        return jsonify({"error": "User does not exist"}), 404
    
    return jsonify({
        "id": user.id,
        "email": user.email,
        "username": user.username
    }), 200


# DELETE: Revoke the current access token (Logout)
@auth_bp.route("/logout", methods=["DELETE"])
@jwt_required()
def logout():
    jti = get_jwt()["jti"]
    now = datetime.now(timezone.utc)
    
    # Store token identity identifier inside the blocklist
    db.session.add(TokenBlocklist(jti=jti, created_at=now))
    db.session.commit()
    
    # FIX: Changed status code from 401 (Unauthorized error) to 200 (Success)
    return jsonify({"success": "Successfully logged out. Token revoked."}), 200