import json


def test_api_questions_empty(client, auth_headers):
    resp = client.get("/api/questions_json")
    assert resp.status_code == 200
    data = json.loads(resp.data)
    assert data["total"] == 0


def test_api_questions_with_data(client, auth_headers, sample_question):
    resp = client.get("/api/questions_json")
    data = json.loads(resp.data)
    assert data["total"] == 1
    assert len(data["questions"]) == 1
    assert data["questions"][0]["text"] == "Qual sua cor favorita?"


def test_api_questions_search(client, auth_headers, sample_question):
    resp = client.get("/api/questions_json?search=favorita")
    data = json.loads(resp.data)
    assert data["total"] == 1


def test_api_questions_pagination(client, auth_headers, sample_question):
    resp = client.get("/api/questions_json?page=1&per_page=10")
    data = json.loads(resp.data)
    assert data["page"] == 1
    assert data["per_page"] == 10


def test_api_restx_questions_endpoint(client, auth_headers, sample_question):
    resp = client.get("/api/questions/")
    assert resp.status_code == 200


def test_api_restx_question_detail(client, auth_headers, sample_question):
    resp = client.get(f"/api/questions/{sample_question.id}")
    assert resp.status_code == 200
