from flask import Blueprint, jsonify, request
from flask_login import login_required

from ..models import Question

api_bp = Blueprint("api", __name__)


@api_bp.route("/questions_json")
@login_required
def questions_json():
    search = request.args.get("search", "", type=str).strip()
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 10, type=int)
    query = Question.query
    if search:
        query = query.filter(Question.text.ilike(f"%{search}%"))  # type: ignore
    total = query.count()
    questions = (
        query.order_by(Question.id)
        .paginate(page=page, per_page=per_page, error_out=False)
        .items
    )
    data = []
    for q in questions:
        data.append(
            {
                "id": q.id,
                "text": q.text,
                "options": [
                    {"id": o.id, "text": o.text, "weight": o.weight} for o in q.options
                ],
            }
        )
    return jsonify(
        {"questions": data, "total": total, "page": page, "per_page": per_page}
    )
