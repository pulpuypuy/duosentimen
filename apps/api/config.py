import os
from datetime import timedelta


class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key')
    SQLALCHEMY_DATABASE_URI = os.getenv(
        'DATABASE_URL', 'mysql+pymysql://root:@localhost/duosentimen'
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_recycle': 280,
        'pool_pre_ping': True,
    }
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'jwt-dev-secret')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=8)
    CORS_ORIGINS = os.getenv(
        'CORS_ORIGINS', '*'
    )
    if isinstance(CORS_ORIGINS, str) and CORS_ORIGINS != '*':
        CORS_ORIGINS = CORS_ORIGINS.split(',')
    MODEL_DIR = os.getenv('MODEL_DIR', 'models/')


class DevelopmentConfig(Config):
    DEBUG = True


class ProductionConfig(Config):
    DEBUG = False


config_map = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
}
