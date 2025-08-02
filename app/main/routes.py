import json

from flask import flash, redirect, render_template, request, url_for
from flask_bcrypt import Bcrypt
from flask_login import current_user, login_required

from ..models import Option, Question, Resultado, User, db
from . import main_bp

bcrypt = Bcrypt()


@main_bp.route("/")
def index():
    # Verificar se existe usuário cadastrado
    if not User.query.first():
        return redirect(url_for("auth.register"))

    questions = Question.query.order_by(Question.id).all()
    return render_template("index.html", questions=questions)


@main_bp.route("/questionario", methods=["POST"])
def submit_questionario():
    nome = request.form.get("nome")
    if not nome:
        flash("Por favor, informe seu nome!")
        return redirect(url_for("main.index"))

    questions = Question.query.order_by(Question.id).all()
    respostas = {}
    pontuacao_total = 0.0

    for question in questions:
        resposta_id = request.form.get(f"question_{question.id}")
        if resposta_id:
            option = Option.query.get(resposta_id)
            if option:
                respostas[question.id] = {
                    "pergunta": question.text,
                    "resposta": option.text,
                    "peso": option.weight,
                }
                pontuacao_total += option.weight

    resultado = Resultado(
        nome=nome, respostas=json.dumps(respostas), pontuacao_total=pontuacao_total
    )

    db.session.add(resultado)
    db.session.commit()

    return render_template("submitted.html")


@main_bp.route("/admin")
@login_required
def admin():
    questions = Question.query.order_by(Question.id).all()
    resultados = Resultado.query.order_by(Resultado.data.desc()).all()

    return render_template("admin.html", questions=questions, resultados=resultados)


@main_bp.route("/admin/add_question", methods=["POST"])
@login_required
def add_question():
    text = request.form.get("question_text")
    if not text:
        flash("Digite o texto da pergunta!")
        return redirect(url_for("main.admin"))

    # Obter próximo número de ordem
    last_question = Question.query.order_by(Question.id.desc()).first()
    order = (last_question.order + 1) if last_question else 1

    question = Question(text=text, order=order)
    db.session.add(question)
    db.session.flush()  # Para obter o ID

    # Adicionar opções
    option_texts = request.form.getlist("option_text")
    option_weights = request.form.getlist("option_weight")

    for text, weight in zip(option_texts, option_weights):
        if text and weight:
            option = Option(text=text, weight=float(weight), question_id=question.id)
            db.session.add(option)

    db.session.commit()
    flash("Pergunta adicionada com sucesso!")
    return redirect(url_for("main.admin"))


@main_bp.route("/admin/delete_question/<int:question_id>", methods=["POST"])
@login_required
def delete_question(question_id):
    question = Question.query.get_or_404(question_id)
    db.session.delete(question)
    db.session.commit()
    flash("Pergunta excluída com sucesso!")
    return redirect(url_for("main.admin"))


@main_bp.route("/admin/delete_resultado/<int:resultado_id>", methods=["POST"])
@login_required
def delete_resultado(resultado_id):
    resultado = Resultado.query.get_or_404(resultado_id)
    db.session.delete(resultado)
    db.session.commit()
    flash("Resultado excluído com sucesso!")
    return redirect(url_for("main.admin"))


@main_bp.route("/admin/change_password", methods=["POST"])
@login_required
def change_password():
    new_password = request.form.get("new_password")
    if not new_password:
        flash("Digite a nova senha!")
        return redirect(url_for("main.admin"))

    password_hash = bcrypt.generate_password_hash(new_password).decode("utf-8")
    current_user.password_hash = password_hash
    db.session.commit()

    flash("Senha alterada com sucesso!")
    return redirect(url_for("main.admin"))


@main_bp.route("/admin/edit_question/<int:question_id>", methods=["POST"])
@login_required
def edit_question(question_id):
    question = Question.query.get_or_404(question_id)

    # Verificar se é para excluir a pergunta
    if request.form.get("delete_question"):
        db.session.delete(question)
        db.session.commit()
        flash("Pergunta excluída com sucesso!")
        return redirect(url_for("main.admin"))

    # Verificar se é para excluir uma opção específica
    delete_option_id = request.form.get("delete_option")
    if delete_option_id:
        option = Option.query.get(delete_option_id)
        if option and option.question_id == question_id:
            db.session.delete(option)
            db.session.commit()
            flash("Opção excluída com sucesso!")
        return redirect(url_for("main.admin"))

    # Atualizar pergunta
    new_text = request.form.get("question_text")
    if new_text:
        question.text = new_text

    # Atualizar opções existentes
    for option in question.options:
        new_option_text = request.form.get(f"option_text_{option.id}")
        new_option_weight = request.form.get(f"option_weight_{option.id}")

        if new_option_text is not None:
            option.text = new_option_text
        if new_option_weight is not None:
            try:
                option.weight = float(new_option_weight)
            except ValueError:
                pass

    db.session.commit()
    flash("Pergunta atualizada com sucesso!")
    return redirect(url_for("main.admin"))


@main_bp.route("/admin/import_questions", methods=["POST"])
@login_required
def import_questions():
    questions_data = request.form.get("questions_data")
    if not questions_data:
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
                # Extrair texto da pergunta
                question_text = line.split("pergunta:", 1)[1].strip()
                # Remover aspas se existirem
                if question_text.startswith('"') and question_text.endswith('"'):
                    question_text = question_text[1:-1]

                # Obter próximo número de ordem
                last_question = Question.query.order_by(Question.id.desc()).first()
                order = (last_question.order + 1) if last_question else 1

                current_question = Question(text=question_text, order=order)
                db.session.add(current_question)
                db.session.flush()  # Para obter o ID

            elif line.startswith("opcoes e peso:") and current_question:
                # Extrair opções
                options_text = line.split("opcoes e peso:", 1)[1].strip()
                # Dividir por vírgulas e processar cada opção
                options_parts = options_text.split('","')

                for i, option_part in enumerate(options_parts):
                    option_part = option_part.strip()
                    # Remover aspas do início e fim
                    if i == 0 and option_part.startswith('"'):
                        option_part = option_part[1:]
                    if i == len(options_parts) - 1 and option_part.endswith('"'):
                        option_part = option_part[:-1]

                    # Dividir por : para obter texto e peso
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
        flash(f"{imported_count} pergunta(s) importada(s) com sucesso!")

    except Exception as e:
        db.session.rollback()
        flash(f"Erro ao importar perguntas: {str(e)}")

    return redirect(url_for("main.admin"))


@main_bp.route("/admin/delete_all_resultados", methods=["POST"])
@login_required
def delete_all_resultados():
    """Apagar todos os questionários respondidos"""
    try:
        # Contar quantos serão apagados
        count = Resultado.query.count()

        # Apagar todos os resultados
        Resultado.query.delete()
        db.session.commit()

        flash(f"{count} questionário(s) apagado(s) com sucesso!")

    except Exception as e:
        db.session.rollback()
        flash(f"Erro ao apagar questionários: {str(e)}")

    return redirect(url_for("main.admin"))


@main_bp.route("/admin/delete_all_questions", methods=["POST"])
@login_required
def delete_all_questions():
    """Apagar todas as perguntas cadastradas e suas opções"""
    try:
        # Contar quantas serão apagadas
        count = Question.query.count()

        # Apagar todas as opções primeiro (devido ao relacionamento)
        Option.query.delete()
        # Depois apagar todas as perguntas
        Question.query.delete()
        db.session.commit()

        flash(f"{count} pergunta(s) e suas opções apagadas com sucesso!")

    except Exception as e:
        db.session.rollback()
        flash(f"Erro ao apagar perguntas: {str(e)}")

    return redirect(url_for("main.admin"))
