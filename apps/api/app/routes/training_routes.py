import os
from flask import Blueprint, request, current_app, send_file
from flask_jwt_extended import jwt_required, get_jwt_identity

from app.services import training_service
from app.utils.responses import ok, created, error, not_found

training_bp = Blueprint('training', __name__)


@training_bp.post('/jobs')
@jwt_required()
def start_training():
    body    = request.get_json(silent=True) or {}
    user_id = int(get_jwt_identity())
    app     = current_app._get_current_object()
    model_dir = current_app.config['MODEL_DIR']

    mv = training_service.start_training(body, user_id, model_dir, app)
    return created(mv.to_dict(), 'Training dimulai')


@training_bp.get('/models')
@jwt_required()
def list_models():
    models = training_service.list_models()
    return ok([m.to_dict() for m in models])


@training_bp.get('/models/active')
@jwt_required()
def active_model():
    mv = training_service.get_active_model()
    if not mv:
        return not_found('Active model')
    return ok(mv.to_dict(include_matrix=True))


@training_bp.get('/models/<int:model_id>')
@jwt_required()
def get_model(model_id: int):
    mv = training_service.get_model(model_id)
    if not mv:
        return not_found('Model')
    return ok(mv.to_dict(include_matrix=True))


@training_bp.post('/models/<int:model_id>/deploy')
@jwt_required()
def deploy(model_id: int):
    mv = training_service.deploy_model(model_id)
    if not mv:
        return not_found('Model')
    return ok(mv.to_dict(), f'{mv.version_tag} berhasil di-deploy')


@training_bp.get('/models/<int:model_id>/download')
@jwt_required()
def download_model(model_id: int):
    mv = training_service.get_model(model_id)
    if not mv or not mv.model_file_path:
        return not_found('Model file')
    if not os.path.exists(mv.model_file_path):
        return error('File model tidak ditemukan di server', 404)
    return send_file(
        mv.model_file_path,
        as_attachment=True,
        download_name=f'model_{mv.version_tag}.pkl',
    )
