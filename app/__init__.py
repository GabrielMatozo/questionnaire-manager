from flask import Flask
from flask_login import LoginManager

# Importação dos modelos e banco de dados
from .models import User, db


# Função para criar e configurar a aplicação Flask
def create_app():
    app = Flask(__name__)
    app.config.from_object("config.Config")

    # Inicializar o banco de dados
    db.init_app(app)

    # Configurar o gerenciador de login
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = "auth.login"  # type: ignore
    login_manager.login_message = "Por favor, faça login para acessar esta página."

    @login_manager.user_loader
    def load_user(user_id):
        # Carregar usuário pelo ID
        return User.query.get(int(user_id))

    # Registrar blueprints para rotas de autenticação e principais
    from .auth.routes import auth_bp
    from .main.routes import main_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)

    return app
