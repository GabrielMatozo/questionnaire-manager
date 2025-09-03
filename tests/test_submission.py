def test_submit_questionnaire(client, sample_question):
    resp = client.post(
        "/submit_questionario",
        data={
            "nome": "João",
            f"question_{sample_question.id}": sample_question.options[0].id,
        },
        follow_redirects=True,
    )
    assert resp.status_code == 200
    assert b"enviado com sucesso" in resp.data


def test_submit_without_name(client):
    resp = client.post("/submit_questionario", data={}, follow_redirects=True)
    assert resp.status_code == 200
    assert b"obrigat" in resp.data or b"Nome" in resp.data


def test_submit_no_responses(client, sample_question):
    resp = client.post("/submit_questionario", data={"nome": "João"}, follow_redirects=True)
    assert resp.status_code == 200
    from app.models import Resultado

    assert Resultado.query.count() == 0


def test_resultado_saved(client, sample_question):
    option_id = sample_question.options[0].id
    client.post(
        "/submit_questionario",
        data={
            "nome": "Maria",
            f"question_{sample_question.id}": option_id,
        },
    )
    from app.models import Resultado

    r = Resultado.query.first()
    assert r is not None
    assert r.nome == "Maria"
    assert r.pontuacao_total == 1.0
