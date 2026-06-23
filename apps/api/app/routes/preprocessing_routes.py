from flask import Blueprint, request, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity

from app.services import preprocessing_service
from app.utils.responses import ok, created, error, not_found

preprocessing_bp = Blueprint('preprocessing', __name__)


@preprocessing_bp.post('/jobs')
@jwt_required()
def start_job():
    body    = request.get_json(silent=True) or {}
    user_id = int(get_jwt_identity())

    scraping_job_id = body.get('scraping_job_id')
    if not scraping_job_id:
        return error('scraping_job_id diperlukan')

    app = current_app._get_current_object()
    job = preprocessing_service.start_job(int(scraping_job_id), user_id, app)
    return created(job.to_dict(), 'Preprocessing dimulai')


@preprocessing_bp.get('/jobs/<int:job_id>')
@jwt_required()
def get_job(job_id: int):
    job = preprocessing_service.get_job(job_id)
    if not job:
        return not_found('Preprocessing job')
    return ok(job.to_dict())


@preprocessing_bp.post('/jobs/<int:job_id>/stop')
@jwt_required()
def stop_job(job_id: int):
    preprocessing_service.stop_job(job_id)
    return ok(None, 'Signal stop terkirim')


@preprocessing_bp.get('/jobs/<int:job_id>/preview')
@jwt_required()
def preview(job_id: int):
    limit = int(request.args.get('limit', 10))
    data  = preprocessing_service.get_preview(job_id, limit)
    return ok(data)


@preprocessing_bp.get('/jobs/<int:job_id>/distribution')
@jwt_required()
def distribution(job_id: int):
    data = preprocessing_service.get_distribution(job_id)
    return ok(data)
