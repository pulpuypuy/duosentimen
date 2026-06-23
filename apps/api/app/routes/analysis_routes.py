from flask import Blueprint, request
from flask_jwt_extended import jwt_required

from app.services import analysis_service
from app.utils.responses import ok

analysis_bp = Blueprint('analysis', __name__)


@analysis_bp.get('/summary')
@jwt_required()
def summary():
    return ok(analysis_service.get_summary())


@analysis_bp.get('/distribution')
@jwt_required()
def distribution():
    return ok(analysis_service.get_distribution())


@analysis_bp.get('/trends')
@jwt_required()
def trends():
    period = request.args.get('period', 'monthly')
    return ok(analysis_service.get_trends(period))


@analysis_bp.get('/by-version')
@jwt_required()
def by_version():
    return ok(analysis_service.get_by_version())


@analysis_bp.get('/top-terms')
@jwt_required()
def top_terms():
    n = int(request.args.get('n', 15))
    return ok(analysis_service.get_top_terms(n))


@analysis_bp.get('/reviews')
@jwt_required()
def reviews():
    page     = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 20))
    pag = analysis_service.get_reviews(
        q          = request.args.get('q'),
        sentiment  = request.args.get('sentiment'),
        version    = request.args.get('version'),
        date_from  = request.args.get('from'),
        date_to    = request.args.get('to'),
        page       = page,
        per_page   = per_page,
    )
    return ok({
        'items':    [r.to_dict() for r in pag.items],
        'total':    pag.total,
        'pages':    pag.pages,
        'page':     page,
        'per_page': per_page,
    })


@analysis_bp.post('/rebuild-trends')
@jwt_required()
def rebuild_trends():
    analysis_service.rebuild_trends()
    return ok(None, 'Trends diperbarui')
