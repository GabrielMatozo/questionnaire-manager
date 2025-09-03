from app.models import Question


def test_add_question(client, auth_headers):
    resp = client.post(
        "/admin/add_question",
        data={
            "question_text": "Teste?",
            "option_text": ["Sim", "Nao"],
            "option_weight": ["1", "0"],
        },
        follow_redirects=True,
    )
    assert resp.status_code == 200


def test_list_questions_empty(client, auth_headers):
    resp = client.get("/admin")
    assert resp.status_code == 200
    assert b"Nenhuma pergunta" in resp.data


def test_edit_question(client, auth_headers, sample_question):
    resp = client.post(
        f"/admin/edit_question/{sample_question.id}",
        data={
            "question_text": "Editada?",
        },
        follow_redirects=True,
    )
    assert resp.status_code == 200
    q = Question.query.with_entities(Question.text).filter_by(id=sample_question.id).first()
    assert q.text == "Editada?"


def test_delete_question(client, auth_headers, sample_question):
    resp = client.post(f"/admin/delete_question/{sample_question.id}", follow_redirects=True)
    assert resp.status_code == 200
    assert Question.query.filter_by(id=sample_question.id).count() == 0


def test_import_questions(client, auth_headers):
    data = (
        'pergunta: "Gosta de Python?"\n'
        'opcoes e peso: "sim:1","nao:0"\n'
        'pergunta: "Usa Flask?"\n'
        'opcoes e peso: "sim:1","nao:0"'
    )
    resp = client.post(
        "/admin/import_questions", data={"questions_data": data}, follow_redirects=True
    )
    assert resp.status_code == 200
    assert Question.query.count() == 2
