from marshmallow import Schema, fields, validate


class OptionSchema(Schema):
    id = fields.Int(dump_only=True)
    text = fields.Str(required=True, validate=validate.Length(min=1, max=100))
    weight = fields.Float(required=True, validate=validate.Range(min=0.0, max=999.0))


class QuestionSchema(Schema):
    id = fields.Int(dump_only=True)
    text = fields.Str(required=True, validate=validate.Length(min=1))
    order = fields.Int(dump_only=True)
    options = fields.List(fields.Nested(OptionSchema), dump_only=True)


class QuestionInputSchema(Schema):
    text = fields.Str(required=True, validate=validate.Length(min=1))
    options = fields.List(fields.Dict(), required=True)


class ResultadoSchema(Schema):
    id = fields.Int(dump_only=True)
    nome = fields.Str(required=True, validate=validate.Length(min=1, max=100))
    pontuacao_total = fields.Float(dump_only=True)
    data = fields.DateTime(dump_only=True)
    respostas = fields.Dict(dump_only=True)


class SubmissionSchema(Schema):
    nome = fields.Str(required=True, validate=validate.Length(min=1, max=100))
    respostas = fields.Dict(required=True)


class QuestionnaireSchema(Schema):
    id = fields.Int(dump_only=True)
    title = fields.Str(required=True, validate=validate.Length(min=1, max=200))
    description = fields.Str(allow_none=True)
    active = fields.Bool(dump_only=True)
    created_at = fields.DateTime(dump_only=True)
    questions = fields.List(fields.Nested(QuestionSchema), dump_only=True)


class LoginSchema(Schema):
    username = fields.Str(required=True, validate=validate.Length(min=3, max=80))
    password = fields.Str(required=True, validate=validate.Length(min=4))


class RegisterSchema(Schema):
    username = fields.Str(required=True, validate=validate.Length(min=3, max=80))
    password = fields.Str(required=True, validate=validate.Length(min=4))


question_schema = QuestionSchema()
questions_schema = QuestionSchema(many=True)
resultado_schema = ResultadoSchema()
resultados_schema = ResultadoSchema(many=True)
submission_schema = SubmissionSchema()
questionnaire_schema = QuestionnaireSchema()
questionnaires_schema = QuestionnaireSchema(many=True)
login_schema = LoginSchema()
register_schema = RegisterSchema()
option_schema = OptionSchema()
question_input_schema = QuestionInputSchema()
