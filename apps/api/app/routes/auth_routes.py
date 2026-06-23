from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity

from app.services import auth_service
from app.utils.responses import ok, error, unauthorized

auth_bp = Blueprint('auth', __name__)


@auth_bp.post('/login')
def login():
    body = request.get_json(silent=True) or {}
    email    = body.get('email', '').strip()
    password = body.get('password', '')

    if not email or not password:
        return error('Email dan password diperlukan')

    result, err = auth_service.login(email, password)
    if err:
        return unauthorized(err)
    return ok(result, 'Login berhasil')


@auth_bp.get('/me')
@jwt_required()
def me():
    user_id = int(get_jwt_identity())
    user    = auth_service.get_user_by_id(user_id)
    if not user:
        return error('User tidak ditemukan', 404)
    return ok(user.to_dict())


@auth_bp.post('/logout')
@jwt_required()
def logout():
    # stateless JWT — client simply discards token
    return ok(None, 'Logout berhasil')
