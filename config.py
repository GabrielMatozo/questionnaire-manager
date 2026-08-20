import os


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-only-change-secret-key")

    USER_DOCUMENTS = os.path.join(os.path.expanduser("~"), "Documents")
    DB_FOLDER = os.path.join(USER_DOCUMENTS, "questionnaire-manager")

    os.makedirs(DB_FOLDER, exist_ok=True)

    SQLALCHEMY_DATABASE_URI = f"sqlite:///{os.path.join(DB_FOLDER, 'questionnaire.db')}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    WTF_CSRF_ENABLED = True

    RATELIMIT_DEFAULT = "100/hour"
    RATELIMIT_STORAGE_URI = "memory://"

    UPLOAD_FOLDER = os.path.join(DB_FOLDER, "uploads")
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
