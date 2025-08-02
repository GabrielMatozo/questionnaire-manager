from flask import Blueprint

# Blueprint para rotas de autenticação
auth_bp = Blueprint("auth", __name__, url_prefix="/auth")
