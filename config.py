class Config:
    # Configuração da chave secreta para segurança
    SECRET_KEY = "questionario-secret-key-2025"
    # Caminho para o banco de dados SQLite
    SQLALCHEMY_DATABASE_URI = "sqlite:///questionario.db"
    # Desabilitar notificações de modificações no SQLAlchemy
    SQLALCHEMY_TRACK_MODIFICATIONS = False
