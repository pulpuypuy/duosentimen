"""
Prediction service — memuat model Naive Bayes aktif dan menjalankan
preprocessing + inferensi, mencatat setiap prediksi ke prediction_logs.
"""
import joblib

from app.extensions import db
from app.models.model_version import ModelVersion
from app.models.prediction_log import PredictionLog
from app.utils.nlp import full_pipeline

# Cache model di memori  {model_id: pipeline}
_model_cache: dict = {}


def predict(raw_text: str, user_id: int = None) -> dict:
    active = ModelVersion.query.filter_by(is_active=True).first()
    if not active or not active.model_file_path:
        return {
            'error': 'Belum ada model aktif. Silakan lakukan training terlebih dahulu.',
            'raw_text': raw_text,
        }

    pipeline = _load_model(active)
    if pipeline is None:
        return {
            'error': 'Gagal memuat model. Silakan lakukan training ulang.',
            'raw_text': raw_text,
        }

    cleaned = full_pipeline(raw_text)

    # Probabilitas tiap kelas
    classes = pipeline.classes_  # ['NEGATIF', 'NETRAL', 'POSITIF']
    probs   = pipeline.predict_proba([cleaned])[0]
    score_map = {c: round(float(p), 4) for c, p in zip(classes, probs)}

    label = max(score_map, key=score_map.get)

    # Simpan log ke DB
    log = PredictionLog(
        raw_text         = raw_text,
        cleaned_text     = cleaned,
        predicted_label  = label,
        conf_positif     = score_map.get('POSITIF', 0),
        conf_negatif     = score_map.get('NEGATIF', 0),
        conf_netral      = score_map.get('NETRAL',  0),
        model_version_id = active.id,
        user_id          = user_id,
    )
    db.session.add(log)
    db.session.commit()

    return {
        'raw_text':      raw_text,
        'cleaned_text':  cleaned,
        'label':         label,
        'scores':        score_map,
        'model_version': active.version_tag,
        'log_id':        log.id,
    }


def get_history(user_id: int = None, limit: int = 10) -> list:
    q = PredictionLog.query
    if user_id:
        q = q.filter_by(user_id=user_id)
    rows = q.order_by(PredictionLog.created_at.desc()).limit(limit).all()
    return [r.to_dict() for r in rows]


# ── Helpers ───────────────────────────────────────────────────────────────────

def _load_model(mv: ModelVersion):
    if mv.id in _model_cache:
        return _model_cache[mv.id]
    try:
        pipeline = joblib.load(mv.model_file_path)
        _model_cache[mv.id] = pipeline
        return pipeline
    except Exception:
        return None
