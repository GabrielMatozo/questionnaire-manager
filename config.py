import os


class Config:
    SECRET_KEY = "questionario-secret-key-2025"

    # Pasta Documentos do usuário atual logado no Windows
    USER_DOCUMENTS = os.path.join(os.path.expanduser("~"), "Documents")
    DB_FOLDER = os.path.join(USER_DOCUMENTS, "questionario-manager")

    # Cria a pasta se não existir
    os.makedirs(DB_FOLDER, exist_ok=True)

    SQLALCHEMY_DATABASE_URI = f"sqlite:///{os.path.join(DB_FOLDER, 'questionario.db')}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
