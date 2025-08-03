import csv
import io

from flask import flash, redirect, render_template, request, url_for
from flask_bcrypt import Bcrypt
from flask_login import current_user, login_required

from ..models import Option, Question, Resultado, db
from . import main_bp

bcrypt = Bcrypt()


# Rota para submissão do questionário
@main_bp.route("/submit_questionario", methods=["POST"])
def submit_questionario():
    nome = request.form.get("nome")
    if not nome:
        flash("Nome é obrigatório!")
        return redirect("/")

    # Coletar respostas
    respostas = {}
    pontuacao_total = 0.0

    # Buscar todas as perguntas
    questions = Question.query.all()

    for question in questions:
        option_id = request.form.get(f"question_{question.id}")
        if option_id:
            option = Option.query.get(option_id)
            if option:
                respostas[str(question.id)] = {
                    "pergunta": question.text,
                    "resposta": option.text,
                    "peso": option.weight,
                }
                pontuacao_total += option.weight

    # Salvar resultado no banco
    if respostas:
        import json

        resultado = Resultado(
            nome=nome, respostas=json.dumps(respostas), pontuacao_total=pontuacao_total
        )
        db.session.add(resultado)
        db.session.commit()
        flash(f"Questionário enviado com sucesso por {nome}!")
    else:
        flash("Nenhuma resposta foi fornecida!")

    return redirect("/")


@main_bp.route("/")
def index():
    questions = Question.query.order_by(Question.order).all()
    return render_template("index.html", questions=questions)


@main_bp.route("/admin/export_resultados_csv", methods=["GET"])
@login_required
def export_resultados_csv():
    resultados = Resultado.query.order_by(Resultado.data.desc()).all()
    fieldnames = ["Nome", "Data/Hora", "Pontuação Total", "Média", "Respostas"]
    output = io.StringIO()
    writer = csv.DictWriter(
        output, fieldnames=fieldnames, delimiter=";", quoting=csv.QUOTE_MINIMAL
    )
    writer.writeheader()
    for r in resultados:
        respostas_dict = (
            r.get_respostas_dict() if hasattr(r, "get_respostas_dict") else {}
        )
        total_perguntas = len(respostas_dict)
        media = r.pontuacao_total / total_perguntas if total_perguntas > 0 else 0
        respostas_str = " | ".join(
            [
                f"{v['pergunta']} => {v['resposta']} (Peso: {v['peso']})"
                for v in respostas_dict.values()
            ]
        )
        writer.writerow(
            {
                "Nome": r.nome,
                "Data/Hora": r.data.strftime("%d/%m/%Y %H:%M"),
                "Pontuação Total": f"{r.pontuacao_total:.2f}",
                "Média": f"{media:.2f}",
                "Respostas": respostas_str,
            }
        )
    output.seek(0)
    return (
        output.getvalue(),
        200,
        {
            "Content-Type": "text/csv; charset=utf-8",
            "Content-Disposition": "attachment; filename=resultados.csv",
        },
    )


# Funções/rotas
# @main_bp.route("/admin/reorder_questions", methods=["POST"])
# @login_required
# def reorder_questions():
#     if not request.is_json:
#         return {"success": False, "message": "Requisição inválida."}, 400
#     data = request.get_json()
#     order_list = data.get("order")
#     if not order_list or not isinstance(order_list, list):
#         return {"success": False, "message": "Lista de ordem inválida."}, 400
#     try:
#         for idx, qid in enumerate(order_list):
#             question = Question.query.get(int(qid))
#             if question:
#                 question.order = idx + 1
#         db.session.commit()
#         return {"success": True}, 200
#     except Exception as e:
#         db.session.rollback()
#         return {"success": False, "message": f"Erro ao salvar ordem: {str(e)}"}, 500


@main_bp.route("/delete_option_ajax", methods=["POST"])
@login_required
def delete_option_ajax():
    if not request.is_json:
        return {"success": False, "message": "Requisição inválida."}, 400
    data = request.get_json()
    option_id = data.get("option_id")
    question_id = data.get("question_id")
    if not option_id or not question_id:
        return {"success": False, "message": "Dados insuficientes."}, 400

    option = Option.query.get(option_id)
    if not option or str(option.question_id) != str(question_id):
        return {"success": False, "message": "Opção não encontrada."}, 404

    # Verificar se não é a única opção da pergunta
    question = Question.query.get(question_id)
    if question and len(question.options) <= 1:
        return {
            "success": False,
            "message": "Não é possível excluir a única opção da pergunta!",
        }, 400

    db.session.delete(option)
    db.session.commit()
    return {"success": True, "message": "Opção excluída com sucesso!"}, 200


@main_bp.route("/admin")
@login_required
def admin():
    questions = Question.query.order_by(Question.order).all()
    resultados = Resultado.query.order_by(Resultado.data.desc()).all()
    return render_template("admin.html", questions=questions, resultados=resultados)


@main_bp.route("/admin/add_question", methods=["POST"])
@login_required
def add_question():
    def ajax_response(success, message=None):
        return {"success": success, "message": message or ""}, 200 if success else 400

    text = request.form.get("question_text")
    if not text:
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return ajax_response(False, "Digite o texto da pergunta!")
        flash("Digite o texto da pergunta!")
        return redirect(url_for("main.admin"))

    last_question = Question.query.order_by(Question.id.desc()).first()
    order = (last_question.order + 1) if last_question else 1

    question = Question(text=text, order=order)
    db.session.add(question)
    db.session.flush()

    option_texts = request.form.getlist("option_text")
    option_weights = request.form.getlist("option_weight")

    for text, weight in zip(option_texts, option_weights):
        if text and weight:
            # Normalizar decimal (trocar vírgula por ponto para ter um padrão)
            weight_normalized = str(weight).replace(",", ".")
            try:
                weight_float = float(weight_normalized)
                option = Option(text=text, weight=weight_float, question_id=question.id)
                db.session.add(option)
            except ValueError:
                continue

    db.session.commit()
    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return ajax_response(True, "Pergunta adicionada com sucesso!")
    flash("Pergunta adicionada com sucesso!")
    return redirect(url_for("main.admin"))


@main_bp.route("/admin/delete_question/<int:question_id>", methods=["POST"])
@login_required
def delete_question(question_id):
    def ajax_response(success, message=None):
        return {"success": success, "message": message or ""}, 200 if success else 400

    question = Question.query.get_or_404(question_id)
    db.session.delete(question)
    db.session.commit()
    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return ajax_response(True, "Pergunta excluída com sucesso!")
    flash("Pergunta excluída com sucesso!")
    return redirect(url_for("main.admin"))


@main_bp.route("/admin/delete_resultado/<int:resultado_id>", methods=["POST"])
@login_required
def delete_resultado(resultado_id):
    def ajax_response(success, message=None):
        return {"success": success, "message": message or ""}, 200 if success else 400

    resultado = Resultado.query.get_or_404(resultado_id)
    db.session.delete(resultado)
    db.session.commit()
    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return ajax_response(True, "Resultado excluído com sucesso!")
    flash("Resultado excluído com sucesso!")
    return redirect(url_for("main.admin"))


@main_bp.route("/admin/change_password", methods=["POST"])
@login_required
def change_password():
    def ajax_response(success, message=None):
        return {"success": success, "message": message or ""}, 200 if success else 400

    new_password = request.form.get("new_password")
    if not new_password:
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return ajax_response(False, "Digite a nova senha!")
        flash("Digite a nova senha!")
        return redirect(url_for("main.admin"))

    password_hash = bcrypt.generate_password_hash(new_password).decode("utf-8")
    current_user.password_hash = password_hash
    db.session.commit()

    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return ajax_response(True, "Senha alterada com sucesso!")
    flash("Senha alterada com sucesso!")
    return redirect(url_for("main.admin"))


@main_bp.route("/admin/edit_question/<int:question_id>", methods=["POST"])
@login_required
def edit_question(question_id):
    question = Question.query.get_or_404(question_id)

    # AJAX helper
    def ajax_response(success, message=None):
        return {"success": success, "message": message or ""}, 200 if success else 400

    # Excluir pergunta
    if request.form.get("delete_question"):
        db.session.delete(question)
        db.session.commit()
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return ajax_response(True, "Pergunta excluída com sucesso!")
        flash("Pergunta excluída com sucesso!")
        return redirect(url_for("main.admin"))

    # Excluir opção específica
    delete_option_id = request.form.get("delete_option")
    if delete_option_id:
        option = Option.query.get(delete_option_id)
        if option and option.question_id == question_id:
            db.session.delete(option)
            db.session.commit()
            if request.headers.get("X-Requested-With") == "XMLHttpRequest":
                return ajax_response(True, "Opção excluída com sucesso!")
            flash("Opção excluída com sucesso!")
        return redirect(url_for("main.admin"))

    # Atualizar pergunta
    new_text = request.form.get("question_text")
    if new_text:
        question.text = new_text

    # Adicionar nova opção se fornecida
    new_option_text = request.form.get("new_option_text")
    new_option_weight = request.form.get("new_option_weight")
    if new_option_text and new_option_weight:
        try:
            weight = float(new_option_weight.replace(",", "."))
            new_option = Option(
                text=new_option_text, weight=weight, question_id=question.id
            )
            db.session.add(new_option)
        except ValueError:
            if request.headers.get("X-Requested-With") == "XMLHttpRequest":
                return ajax_response(
                    False, "Peso da nova opção deve ser um número válido!"
                )

    # Atualizar opções existentes
    for option in question.options:
        new_option_text = request.form.get(f"option_text_{option.id}")
        new_option_weight = request.form.get(f"option_weight_{option.id}")

        if new_option_text is not None:
            option.text = new_option_text
        if new_option_weight is not None:
            try:
                # Normalizar vírgula para ponto
                weight_str = new_option_weight.replace(",", ".")
                option.weight = float(weight_str)
            except ValueError:
                pass

    db.session.commit()
    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return ajax_response(True, "Pergunta atualizada com sucesso!")
    flash("Pergunta atualizada com sucesso!")
    return redirect(url_for("main.admin"))


@main_bp.route("/admin/import_questions", methods=["POST"])
@login_required
def import_questions():
    def ajax_response(success, message=None):
        return {"success": success, "message": message or ""}, 200 if success else 400

    questions_data = request.form.get("questions_data")
    if not questions_data:
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return ajax_response(False, "Digite os dados das perguntas!")
        flash("Digite os dados das perguntas!")
        return redirect(url_for("main.admin"))

    try:
        lines = questions_data.strip().split("\n")
        current_question = None
        imported_count = 0

        for line in lines:
            line = line.strip()
            if not line:
                continue

            if line.startswith("pergunta:"):
                question_text = line.split("pergunta:", 1)[1].strip()
                if question_text.startswith('"') and question_text.endswith('"'):
                    question_text = question_text[1:-1]
                last_question = Question.query.order_by(Question.id.desc()).first()
                order = (last_question.order + 1) if last_question else 1
                current_question = Question(text=question_text, order=order)
                db.session.add(current_question)
                db.session.flush()
            elif line.startswith("opcoes e peso:") and current_question:
                options_text = line.split("opcoes e peso:", 1)[1].strip()
                options_parts = options_text.split('","')
                for i, option_part in enumerate(options_parts):
                    option_part = option_part.strip()
                    if i == 0 and option_part.startswith('"'):
                        option_part = option_part[1:]
                    if i == len(options_parts) - 1 and option_part.endswith('"'):
                        option_part = option_part[:-1]
                    if ":" in option_part:
                        text_part, weight_part = option_part.rsplit(":", 1)
                        try:
                            weight = float(weight_part)
                            option = Option(
                                text=text_part,
                                weight=weight,
                                question_id=current_question.id,
                            )
                            db.session.add(option)
                        except ValueError:
                            continue
                imported_count += 1
                current_question = None
        db.session.commit()
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return ajax_response(
                True, f"{imported_count} pergunta(s) importada(s) com sucesso!"
            )
        flash(f"{imported_count} pergunta(s) importada(s) com sucesso!")
    except Exception as e:
        db.session.rollback()
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return ajax_response(False, f"Erro ao importar perguntas: {str(e)}")
        flash(f"Erro ao importar perguntas: {str(e)}")
    return redirect(url_for("main.admin"))


@main_bp.route("/admin/delete_all_resultados", methods=["POST"])
@login_required
def delete_all_resultados():
    """Apagar todos os questionários respondidos"""

    def ajax_response(success, message=None):
        return {"success": success, "message": message or ""}, 200 if success else 400

    try:
        # Contar quantos serão apagados
        count = Resultado.query.count()

        # Apagar todos os resultados
        Resultado.query.delete()
        db.session.commit()

        message = f"{count} questionário(s) apagado(s) com sucesso!"
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return ajax_response(True, message)
        flash(message)

    except Exception as e:
        db.session.rollback()
        error_msg = f"Erro ao apagar questionários: {str(e)}"
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return ajax_response(False, error_msg)
        flash(error_msg)

    return redirect(url_for("main.admin"))


@main_bp.route("/admin/delete_all_questions", methods=["POST"])
@login_required
def delete_all_questions():
    """Apagar todas as perguntas cadastradas e suas opções"""

    def ajax_response(success, message=None):
        return {"success": success, "message": message or ""}, 200 if success else 400

    try:
        # Contar quantas serão apagadas
        count = Question.query.count()

        # Apagar todas as opções primeiro (devido ao relacionamento)
        Option.query.delete()
        # Depois apagar todas as perguntas
        Question.query.delete()
        db.session.commit()

        message = f"{count} pergunta(s) e suas opções apagadas com sucesso!"
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return ajax_response(True, message)
        flash(message)

    except Exception as e:
        db.session.rollback()
        error_msg = f"Erro ao apagar perguntas: {str(e)}"
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return ajax_response(False, error_msg)
        flash(error_msg)

    return redirect(url_for("main.admin"))


@main_bp.route("/clear_all_results_ajax", methods=["POST"])
@login_required
def clear_all_results_ajax():
    def ajax_response(success, message=None):
        if success:
            return {"success": True, "message": message}, 200
        else:
            return {"success": False, "message": message}, 400

    try:
        count = Resultado.query.count()
        Resultado.query.delete()
        db.session.commit()

        message = f"{count} resultado(s) apagado(s) com sucesso!"
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return ajax_response(True, message)
        flash(message)

    except Exception as e:
        db.session.rollback()
        error_msg = f"Erro ao apagar resultados: {str(e)}"
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return ajax_response(False, error_msg)
        flash(error_msg)

    return redirect(url_for("main.admin"))
