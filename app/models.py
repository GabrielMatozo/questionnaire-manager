import json
import uuid
from datetime import datetime

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_active = db.Column(db.DateTime, default=datetime.utcnow)

    resultados = db.relationship("Resultado", backref="user", lazy=True)

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


class Questionnaire(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False, default="Questionário de Avaliação")
    description = db.Column(db.Text, default="")
    active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    questions = db.relationship(
        "Question", backref="questionnaire", cascade="all, delete-orphan", lazy=True
    )
    resultados = db.relationship("Resultado", backref="questionnaire", lazy=True)

    def __init__(self, title="Questionário de Avaliação", description=""):
        self.title = title
        self.description = description


class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.Text, nullable=False)
    order = db.Column(db.Integer, nullable=False, default=0)
    questionnaire_id = db.Column(db.Integer, db.ForeignKey("questionnaire.id"), nullable=True)

    options = db.relationship("Option", backref="question", cascade="all, delete-orphan", lazy=True)

    def __init__(self, text, order=0, questionnaire_id=None):
        self.text = text
        self.order = order
        self.questionnaire_id = questionnaire_id


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
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=True)
    questionnaire_id = db.Column(db.Integer, db.ForeignKey("questionnaire.id"), nullable=True)

    def __init__(self, nome, respostas, pontuacao_total=0.0, user_id=None, questionnaire_id=None):
        self.nome = nome
        self.respostas = respostas
        self.pontuacao_total = pontuacao_total
        self.user_id = user_id
        self.questionnaire_id = questionnaire_id

    def get_respostas_dict(self):
        try:
            return json.loads(self.respostas)
        except Exception:
            return {}


class QuestionTemplate(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    question_text = db.Column(db.Text, nullable=False)
    options_json = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __init__(self, name, question_text, options_json):
        self.name = name
        self.question_text = question_text
        self.options_json = options_json

    def get_options(self):
        try:
            return json.loads(self.options_json)
        except Exception:
            return []


class ShareLink(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    token = db.Column(db.String(64), unique=True, nullable=False, default=lambda: uuid.uuid4().hex)
    questionnaire_id = db.Column(db.Integer, db.ForeignKey("questionnaire.id"), nullable=True)
    active = db.Column(db.Boolean, default=True)
    expires_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __init__(self, questionnaire_id=None, expires_at=None):
        self.questionnaire_id = questionnaire_id
        self.expires_at = expires_at


class Webhook(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String(500), nullable=False)
    event = db.Column(db.String(50), nullable=False, default="questionario_completo")
    active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __init__(self, url, event="questionario_completo"):
        self.url = url
        self.event = event
