from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity

from app.services import prediction_service
from app.utils.responses import ok, error

prediction_bp = Blueprint('prediction', __name__)


@prediction_bp.post('/predict')
@jwt_required()
def predict():
    body = request.get_json(silent=True) or {}
    text = body.get('text', '').strip()

    if not text:
        return error('Teks tidak boleh kosong')

    user_id = int(get_jwt_identity())
    result  = prediction_service.predict(text, user_id)
    return ok(result)


@prediction_bp.get('/history')
@jwt_required()
def history():
    user_id = int(get_jwt_identity())
    limit   = int(request.args.get('limit', 10))
    data    = prediction_service.get_history(user_id, limit)
    return ok(data)
