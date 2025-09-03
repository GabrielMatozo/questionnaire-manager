from flask import Blueprint, jsonify, request
from flask_login import login_required
from flask_restx import Api, Namespace, Resource, fields

from ..models import Option, Question, Questionnaire, QuestionTemplate, Resultado, db

api_bp = Blueprint("api", __name__, url_prefix="/api")

api = Api(
    api_bp,
    version="1.0",
    title="Questionnaire Manager API",
    description="API REST para gerenciamento de questionários",
    doc="/docs",
)

ns = Namespace("questions", description="Operações com perguntas")
api.add_namespace(ns)

question_model = api.model(
    "Question",
    {
        "id": fields.Integer(readonly=True),
        "text": fields.String(required=True),
        "order": fields.Integer,
        "options": fields.List(
            fields.Nested(
                api.model(
                    "Option",
                    {
                        "id": fields.Integer(readonly=True),
                        "text": fields.String,
                        "weight": fields.Float,
                    },
                )
            )
        ),
    },
)

question_input = api.model(
    "QuestionInput",
    {
        "text": fields.String(required=True),
        "questionnaire_id": fields.Integer,
        "options": fields.List(
            fields.Nested(
                api.model(
                    "OptionInput",
                    {
                        "text": fields.String(required=True),
                        "weight": fields.Float(required=True),
                    },
                )
            )
        ),
    },
)


@ns.route("/")
class QuestionList(Resource):
    @login_required
    @ns.marshal_list_with(question_model)
    @ns.param("search", "Filtrar por texto")
    @ns.param("page", "Número da página", type=int, default=1)
    @ns.param("per_page", "Itens por página", type=int, default=20)
    def get(self):
        search = request.args.get("search", "", type=str).strip()
        page = request.args.get("page", 1, type=int)
        per_page = request.args.get("per_page", 20, type=int)
        query = Question.query
        if search:
            query = query.filter(Question.text.ilike(f"%{search}%"))
        questions = (
            query.order_by(Question.id)
            .paginate(page=page, per_page=per_page, error_out=False)
            .items
        )
        return questions

    @login_required
    @ns.expect(question_input)
    @ns.marshal_with(question_model, code=201)
    def post(self):
        data = request.json
        question = Question(text=data["text"], questionnaire_id=data.get("questionnaire_id"))
        db.session.add(question)
        db.session.flush()
        for opt in data.get("options", []):
            option = Option(text=opt["text"], weight=float(opt["weight"]), question_id=question.id)
            db.session.add(option)
        db.session.commit()
        return question, 201


@ns.route("/<int:qid>")
class QuestionResource(Resource):
    @login_required
    @ns.marshal_with(question_model)
    def get(self, qid):
        return Question.query.get_or_404(qid)

    @login_required
    @ns.expect(question_input)
    @ns.marshal_with(question_model)
    def put(self, qid):
        question = Question.query.get_or_404(qid)
        data = request.json
        if "text" in data:
            question.text = data["text"]
        db.session.commit()
        return question

    @login_required
    def delete(self, qid):
        question = Question.query.get_or_404(qid)
        db.session.delete(question)
        db.session.commit()
        return {"message": "Pergunta excluída"}, 200


resultado_ns = api.namespace("resultados", description="Resultados")

resultado_model = api.model(
    "Resultado",
    {
        "id": fields.Integer(readonly=True),
        "nome": fields.String,
        "pontuacao_total": fields.Float,
        "data": fields.DateTime,
    },
)


@resultado_ns.route("/")
class ResultadoList(Resource):
    @login_required
    @ns.param("page", type=int, default=1)
    @ns.param("per_page", type=int, default=20)
    @ns.param("search_nome", type=str)
    def get(self):
        page = request.args.get("page", 1, type=int)
        per_page = request.args.get("per_page", 20, type=int)
        search = request.args.get("search_nome", "", type=str).strip()

        query = Resultado.query
        if search:
            query = query.filter(Resultado.nome.ilike(f"%{search}%"))

        total = query.count()
        resultados = (
            query.order_by(Resultado.data.desc())
            .paginate(page=page, per_page=per_page, error_out=False)
            .items
        )

        return jsonify(
            {
                "resultados": [
                    {
                        "id": r.id,
                        "nome": r.nome,
                        "pontuacao_total": r.pontuacao_total,
                        "data": r.data.isoformat(),
                    }
                    for r in resultados
                ],
                "total": total,
                "page": page,
                "per_page": per_page,
            }
        )


questionnaire_ns = api.namespace("questionnaires", description="Questionários")

questionnaire_model = api.model(
    "Questionnaire",
    {
        "id": fields.Integer(readonly=True),
        "title": fields.String,
        "description": fields.String,
        "active": fields.Boolean,
        "created_at": fields.DateTime,
    },
)


@questionnaire_ns.route("/")
class QuestionnaireList(Resource):
    @login_required
    def get(self):
        qs = Questionnaire.query.all()
        return jsonify(
            [
                {
                    "id": q.id,
                    "title": q.title,
                    "description": q.description,
                    "active": q.active,
                    "created_at": q.created_at.isoformat(),
                }
                for q in qs
            ]
        )

    @login_required
    def post(self):
        data = request.json
        q = Questionnaire(
            title=data.get("title", "Questionário"),
            description=data.get("description", ""),
        )
        db.session.add(q)
        db.session.commit()
        return {"id": q.id, "message": "Questionário criado"}, 201


templates_ns = api.namespace("templates", description="Templates de perguntas")

template_model = api.model(
    "Template",
    {
        "id": fields.Integer(readonly=True),
        "name": fields.String,
        "question_text": fields.String,
    },
)


@templates_ns.route("/")
class TemplateList(Resource):
    @login_required
    def get(self):
        ts = QuestionTemplate.query.all()
        return jsonify(
            [
                {
                    "id": t.id,
                    "name": t.name,
                    "question_text": t.question_text,
                    "options": t.get_options(),
                }
                for t in ts
            ]
        )


webhook_ns = api.namespace("webhooks", description="Webhooks")

webhook_model = api.model(
    "Webhook",
    {
        "id": fields.Integer(readonly=True),
        "url": fields.String,
        "event": fields.String,
        "active": fields.Boolean,
    },
)


@webhook_ns.route("/")
class WebhookList(Resource):
    @login_required
    def get(self):
        from ..models import Webhook

        whs = Webhook.query.all()
        return jsonify(
            [
                {
                    "id": w.id,
                    "url": w.url,
                    "event": w.event,
                    "active": w.active,
                }
                for w in whs
            ]
        )


@api_bp.route("/questions_json")
@login_required
def questions_json():
    search = request.args.get("search", "", type=str).strip()
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 10, type=int)
    query = Question.query
    if search:
        query = query.filter(Question.text.ilike(f"%{search}%"))
    total = query.count()
    questions = (
        query.order_by(Question.id).paginate(page=page, per_page=per_page, error_out=False).items
    )
    data = []
    for q in questions:
        data.append(
            {
                "id": q.id,
                "text": q.text,
                "options": [{"id": o.id, "text": o.text, "weight": o.weight} for o in q.options],
            }
        )
    return jsonify({"questions": data, "total": total, "page": page, "per_page": per_page})
