from datetime import datetime

from flask_jwt_extended import create_access_token

from app.extensions import db
from app.models.user import User


def login(email: str, password: str) -> dict:
    """Validate credentials and return a JWT access token."""
    user = User.query.filter_by(email=email).first()
    if not user or not user.check_password(password):
        return None, 'Email atau password salah'

    user.last_login = datetime.utcnow()
    db.session.commit()

    token = create_access_token(identity=str(user.id))
    return {'token': token, 'user': user.to_dict()}, None


def get_user_by_id(user_id: int) -> User:
    return User.query.get(user_id)
