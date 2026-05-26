import os

from flask import Flask
from flask_cors import CORS
from datetime import timedelta

from extensions import db, migrate, jwt


def create_app():
    app = Flask(__name__)

    # =========================
    # APP CONFIGURATION
    # =========================
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"

    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    app.config["SECRET_KEY"] = os.environ.get(
        "SECRET_KEY",
        "super-secret-key"
    )

    # JWT CONFIG
    app.config["JWT_SECRET_KEY"] = os.environ.get(
        "JWT_SECRET_KEY",
        "jwt-super-secret-key"
    )

    app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=1)

    # =========================
    # INITIALIZE EXTENSIONS
    # =========================
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)

    CORS(app)

    # =========================
    # IMPORT MODELS
    # =========================
    from models import TokenBlocklist

    # =========================
    # IMPORT BLUEPRINTS
    # =========================
    from views.user import user_bp
    from views.post import post_bp
    from views.comment import comment_bp
    from views.auth import auth_bp

    # =========================
    # REGISTER BLUEPRINTS
    # =========================
    app.register_blueprint(user_bp)
    app.register_blueprint(post_bp)
    app.register_blueprint(comment_bp)
    app.register_blueprint(auth_bp)

    # =========================
    # JWT BLOCKLIST CHECKER
    # =========================
    @jwt.token_in_blocklist_loader
    def check_if_token_revoked(jwt_header, jwt_payload):

        jti = jwt_payload["jti"]

        token = db.session.query(
            TokenBlocklist.id
        ).filter_by(
            jti=jti
        ).scalar()

        return token is not None

    # =========================
    # HOME ROUTE
    # =========================
    @app.route("/")
    def home():
        return {
            "message": "Flask API is running successfully"
        }

    return app


# =========================
# CREATE APP INSTANCE
# =========================
app = create_app()


# =========================
# RUN SERVER
# =========================
if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )