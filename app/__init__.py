import os
import sys

from flask import Flask
from flask_login import LoginManager

from .models import User, db


def resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller."""
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


def create_app():
    # Detecta se está rodando empacotado (PyInstaller) ou em desenvolvimento
    if hasattr(sys, "_MEIPASS"):
        template_folder = os.path.join(sys._MEIPASS, "app", "templates")
        static_folder = os.path.join(sys._MEIPASS, "static")
    else:
        base_dir = os.path.abspath(os.path.dirname(__file__))
        template_folder = os.path.join(base_dir, "templates")
        static_folder = os.path.join(base_dir, "static")

    app = Flask(
        __name__,
        template_folder=template_folder,
        static_folder=static_folder,
    )
    app.config.from_object("config.Config")

    db.init_app(app)
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = "auth.login"  # type: ignore
    login_manager.login_message = "Por favor, faça login para acessar esta página."

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    from .auth.routes import auth_bp
    from .main.api import api_bp
    from .main.routes import main_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(api_bp)

    return app
