# Questionnaire Manager

Aplicação web Flask para criação e gerenciamento de questionários com autenticação, painel admin, importação em lote, exportação CSV/Excel, API REST, múltiplos questionários, compartilhamento via link, webhooks e modo escuro.

## Funcionalidades

- Autenticação com Flask-Login + Flask-Bcrypt
- CRUD de perguntas com opções e pesos
- Múltiplos questionários
- Importação em lote via texto formatado
- Exportação CSV e Excel (.xlsx)
- Painel admin com paginação, filtros (nome, data, pontuação) e dashboard com gráficos (Chart.js)
- Drag-and-drop para reordenar perguntas (SortableJS)
- Dark mode
- Preview do questionário antes de publicar
- Link compartilhável com token e expiração
- Webhooks disparados ao completar questionário
- Templates de perguntas pré-definidos
- API REST documentada (flask-restx em `/api/docs`)
- Rate limiting em submissão e login
- Validação com Marshmallow
- CSRF protection
- Auto logout por inatividade
- Bandeja de sistema (pystray)
- Suporte a PyInstaller (app desktop)
- Testes automatizados (pytest)
- Docker

## Estrutura

```
questionnaire-manager/
├── app/
│   ├── __init__.py          # Inicialização Flask, Flask-Migrate, CSRF, Limiter
│   ├── models.py            # User, Questionnaire, Question, Option, Resultado,
│   │                        # ShareLink, Webhook, QuestionTemplate
│   ├── schemas.py           # Marshmallow schemas
│   ├── auth/
│   │   ├── routes.py        # Login/register/logout
│   ├── main/
│   │   ├── routes.py        # Submissão, admin, export, webhooks, etc.
│   │   ├── api.py           # API REST (flask-restx)
│   ├── static/
│   │   ├── admin.js         # Dark mode, drag-drop, toasts, auto logout
│   │   ├── style.css        # Tema claro/escuro
│   ├── templates/
│       ├── admin.html       # Painel admin completo
│       ├── index.html       # Formulário do questionário
│       ├── login.html / register.html / submitted.html
├── tests/                   # 23 testes (auth, questions, submission, API, security)
├── config.py
├── requirements.txt
├── pyproject.toml           # ruff + black + pytest config
├── Dockerfile / docker-compose.yml
├── run.py / build_exe.py
```

## Como Executar

```bash
pip install -r requirements.txt
python run.py
```

Acesse `http://127.0.0.1:5000`.

## Docker

```bash
docker compose up --build
```

## Testes

```bash
pytest --cov=app
```

## API

Documentação automática disponível em `/api/docs` (requer login).

## Licença

MIT
