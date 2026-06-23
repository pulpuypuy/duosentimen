"""
Prediction service — loads the active sklearn model and runs inline
preprocessing + inference, logging every request to prediction_logs.
"""
import joblib

from app.extensions import db
from app.models.model_version import ModelVersion
from app.models.prediction_log import PredictionLog
from app.utils.nlp import full_pipeline

# in-process model cache  {model_id: pipeline}
_model_cache: dict = {}


def predict(raw_text: str, user_id: int = None) -> dict:
    active = ModelVersion.query.filter_by(is_active=True).first()
    if not active or not active.model_file_path:
        return _mock_predict(raw_text)

    pipeline = _load_model(active)
    if pipeline is None:
        return _mock_predict(raw_text)

    cleaned = full_pipeline(raw_text)

    # Probability scores
    classes = pipeline.classes_  # e.g. ['NEGATIF', 'NETRAL', 'POSITIF']
    if hasattr(pipeline, 'predict_proba'):
        probs = pipeline.predict_proba([cleaned])[0]
        score_map = {c: round(float(p), 4) for c, p in zip(classes, probs)}
    else:
        # LinearSVC — use decision_function as proxy
        decision = pipeline.decision_function([cleaned])[0]
        exp      = [2 ** d for d in decision]
        total    = sum(exp)
        score_map = {c: round(float(e / total), 4) for c, e in zip(classes, exp)}

    label = max(score_map, key=score_map.get)

    # Log to DB
    log = PredictionLog(
        raw_text        = raw_text,
        cleaned_text    = cleaned,
        predicted_label = label,
        conf_positif    = score_map.get('POSITIF', 0),
        conf_negatif    = score_map.get('NEGATIF', 0),
        conf_netral     = score_map.get('NETRAL',  0),
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


def _mock_predict(raw_text: str) -> dict:
    """Used when no trained model is deployed yet."""
    from app.utils.nlp import full_pipeline
    cleaned = full_pipeline(raw_text)
    neg_words = {'error', 'crash', 'bug', 'lambat', 'lemot', 'gagal', 'males', 'parah'}
    pos_words = {'bagus', 'keren', 'mantap', 'bantu', 'suka', 'cepat', 'mudah'}
    words = set(cleaned.split())
    neg_score = len(words & neg_words)
    pos_score = len(words & pos_words)

    if neg_score > pos_score:
        label  = 'NEGATIF'
        scores = {'NEGATIF': 0.85, 'POSITIF': 0.10, 'NETRAL': 0.05}
    elif pos_score > neg_score:
        label  = 'POSITIF'
        scores = {'POSITIF': 0.85, 'NEGATIF': 0.10, 'NETRAL': 0.05}
    else:
        label  = 'NETRAL'
        scores = {'NETRAL': 0.60, 'POSITIF': 0.22, 'NEGATIF': 0.18}

    return {
        'raw_text':      raw_text,
        'cleaned_text':  cleaned,
        'label':         label,
        'scores':        scores,
        'model_version': 'mock',
        'log_id':        None,
    }
