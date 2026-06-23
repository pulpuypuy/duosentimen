from flask import Blueprint, request, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity

from app.services import scraping_service
from app.utils.responses import ok, created, error, not_found

scraping_bp = Blueprint('scraping', __name__)


@scraping_bp.post('/jobs')
@jwt_required()
def start_job():
    body    = request.get_json(silent=True) or {}
    user_id = int(get_jwt_identity())

    if not body.get('target_app_id'):
        return error('target_app_id diperlukan')

    app = current_app._get_current_object()
    job = scraping_service.start_job(body, user_id, app)
    return created(job.to_dict(), 'Scraping job dimulai')


@scraping_bp.get('/jobs')
@jwt_required()
def list_jobs():
    page     = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 10))
    pag      = scraping_service.list_jobs(page, per_page)
    return ok({
        'items':    [j.to_dict() for j in pag.items],
        'total':    pag.total,
        'pages':    pag.pages,
        'page':     page,
        'per_page': per_page,
    })


@scraping_bp.get('/jobs/<int:job_id>')
@jwt_required()
def get_job(job_id: int):
    job = scraping_service.get_job(job_id)
    if not job:
        return not_found('Scraping job')
    return ok(job.to_dict())


@scraping_bp.delete('/jobs/<int:job_id>')
@jwt_required()
def delete_job(job_id: int):
    ok_flag = scraping_service.delete_job(job_id)
    if not ok_flag:
        return not_found('Scraping job')
    return ok(None, 'Job berhasil dihapus')


@scraping_bp.post('/jobs/<int:job_id>/stop')
@jwt_required()
def stop_job(job_id: int):
    scraping_service.stop_job(job_id)
    return ok(None, 'Signal stop terkirim')


@scraping_bp.get('/stats')
@jwt_required()
def stats():
    return ok(scraping_service.get_dataset_stats())
