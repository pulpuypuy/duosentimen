import os
from flask import Flask
from dotenv import load_dotenv

from .extensions import db, migrate, jwt, bcrypt, cors
from config import config_map

load_dotenv()


def create_app(env: str = None) -> Flask:
    env = env or os.getenv('FLASK_ENV', 'development')
    app = Flask(__name__)
    app.config.from_object(config_map.get(env, config_map['development']))

    # Ensure model storage dir exists
    os.makedirs(app.config['MODEL_DIR'], exist_ok=True)

    # ── Extensions ──────────────────────────────────────────────────────────
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    bcrypt.init_app(app)
    cors.init_app(
        app,
        resources={r'/api/*': {'origins': app.config['CORS_ORIGINS']}},
        supports_credentials=True,
    )

    # ── Import models so Flask-Migrate can detect them ───────────────────────
    from .models import user, review, scraping_job, preprocessing_job  # noqa
    from .models import model_version, prediction_log, sentiment_trend  # noqa

    # ── Register Blueprints ──────────────────────────────────────────────────
    from .routes.auth_routes import auth_bp
    from .routes.scraping_routes import scraping_bp
    from .routes.preprocessing_routes import preprocessing_bp
    from .routes.training_routes import training_bp
    from .routes.analysis_routes import analysis_bp
    from .routes.prediction_routes import prediction_bp

    app.register_blueprint(auth_bp,           url_prefix='/api/auth')
    app.register_blueprint(scraping_bp,       url_prefix='/api/scraping')
    app.register_blueprint(preprocessing_bp,  url_prefix='/api/preprocessing')
    app.register_blueprint(training_bp,       url_prefix='/api/training')
    app.register_blueprint(analysis_bp,       url_prefix='/api/analysis')
    app.register_blueprint(prediction_bp,     url_prefix='/api/prediction')

    # ── Health check ────────────────────────────────────────────────────────
    @app.get('/api/health')
    def health():
        return {'status': 'ok', 'env': env}

    # ── CLI: seed admin user ─────────────────────────────────────────────────
    @app.cli.command('seed-db')
    def seed_db():
        from .models.user import User
        if User.query.filter_by(email='admin@duosentimen.id').first():
            print('Admin already exists.')
            return
        admin = User(email='admin@duosentimen.id', name='Admin', role='admin')
        admin.set_password('admin123')
        db.session.add(admin)
        db.session.commit()
        print('[OK] Admin user created  ->  admin@duosentimen.id / admin123')

    return app
