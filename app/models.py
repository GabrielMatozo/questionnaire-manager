import json
from datetime import datetime

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)

    def __init__(self, username, password_hash):
        self.username = username
        self.password_hash = password_hash

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return str(self.id)


class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.Text, nullable=False)
    order = db.Column(db.Integer, nullable=False, default=0)
    options = db.relationship(
        "Option", backref="question", cascade="all, delete-orphan", lazy=True
    )

    def __init__(self, text, order=0):
        self.text = text
        self.order = order


class Option(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(100), nullable=False)
    weight = db.Column(db.Float, nullable=False, default=0.0)
    question_id = db.Column(db.Integer, db.ForeignKey("question.id"), nullable=False)

    def __init__(self, text, weight, question_id):
        self.text = text
        self.weight = weight
        self.question_id = question_id


class Resultado(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    respostas = db.Column(db.Text, nullable=False)
    pontuacao_total = db.Column(db.Float, nullable=False, default=0.0)
    data = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __init__(self, nome, respostas, pontuacao_total=0.0):
        self.nome = nome
        self.respostas = respostas
        self.pontuacao_total = pontuacao_total

    def get_respostas_dict(self):
        try:
            return json.loads(self.respostas)
        except Exception:
            return {}
