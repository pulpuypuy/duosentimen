"""
Analysis service — aggregation queries powering the Dashboard and
Hasil Analisis pages. Reads from `reviews` and `sentiment_trends`.
"""
from sqlalchemy import func, text, distinct

from app.extensions import db
from app.models.review import Review
from app.models.sentiment_trend import SentimentTrend
from app.models.model_version import ModelVersion


# ── Summary (Dashboard stat cards) ───────────────────────────────────────────

def get_summary() -> dict:
    total = Review.query.count()

    counts = (
        db.session.query(Review.sentiment_label, func.count(Review.id))
        .group_by(Review.sentiment_label)
        .all()
    )
    count_map = {label: cnt for label, cnt in counts}
    pos = count_map.get('POSITIF', 0)
    neg = count_map.get('NEGATIF', 0)
    neu = count_map.get('NETRAL', 0)

    active_model = ModelVersion.query.filter_by(is_active=True).first()

    return {
        'total_reviews': total,
        'positif_pct':   round(pos / total * 100, 1) if total else 0,
        'negatif_pct':   round(neg / total * 100, 1) if total else 0,
        'netral_pct':    round(neu / total * 100, 1) if total else 0,
        'model_accuracy': float(active_model.accuracy) * 100 if active_model and active_model.accuracy else None,
        'model_version':  active_model.version_tag if active_model else None,
    }


# ── Distribution (donut chart) ────────────────────────────────────────────────

def get_distribution() -> list:
    counts = (
        db.session.query(Review.sentiment_label, func.count(Review.id))
        .group_by(Review.sentiment_label)
        .all()
    )
    total = sum(c for _, c in counts) or 1
    return [
        {'label': label, 'count': cnt, 'pct': round(cnt / total * 100, 1)}
        for label, cnt in counts
        if label
    ]


# ── Trends (line chart) ───────────────────────────────────────────────────────

def get_trends(period_type: str = 'monthly') -> list:
    rows = (
        SentimentTrend.query
        .filter_by(period_type=period_type)
        .order_by(SentimentTrend.period_key)
        .all()
    )
    return [r.to_dict() for r in rows]


def rebuild_trends():
    """Rebuild sentiment_trends from the reviews table (call after preprocessing)."""
    # monthly
    monthly = (
        db.session.query(
            func.date_format(Review.review_date, '%Y-%m').label('period'),
            Review.sentiment_label,
            func.count(Review.id).label('cnt'),
        )
        .filter(Review.review_date.isnot(None))
        .group_by('period', Review.sentiment_label)
        .all()
    )
    _upsert_trends(monthly, 'monthly')

    # weekly
    weekly = (
        db.session.query(
            func.date_format(Review.review_date, '%x-W%v').label('period'),
            Review.sentiment_label,
            func.count(Review.id).label('cnt'),
        )
        .filter(Review.review_date.isnot(None))
        .group_by('period', Review.sentiment_label)
        .all()
    )
    _upsert_trends(weekly, 'weekly')
    db.session.commit()


def _upsert_trends(rows, period_type):
    data: dict[str, dict] = {}
    for period, label, cnt in rows:
        if period not in data:
            data[period] = {'positif': 0, 'negatif': 0, 'netral': 0}
        key = {'POSITIF': 'positif', 'NEGATIF': 'negatif', 'NETRAL': 'netral'}.get(label)
        if key:
            data[period][key] = cnt

    for period, vals in data.items():
        existing = SentimentTrend.query.filter_by(period_type=period_type, period_key=period).first()
        if existing:
            existing.positif = vals['positif']
            existing.negatif = vals['negatif']
            existing.netral  = vals['netral']
        else:
            db.session.add(SentimentTrend(
                period_type=period_type, period_key=period, **vals
            ))


# ── By version (bar chart) ───────────────────────────────────────────────────

def get_by_version() -> list:
    rows = (
        db.session.query(
            Review.app_version,
            func.sum(func.IF(Review.sentiment_label == 'POSITIF', 1, 0)).label('pos'),
            func.count(Review.id).label('total'),
        )
        .filter(Review.app_version.isnot(None))
        .group_by(Review.app_version)
        .order_by(Review.app_version)
        .all()
    )
    return [
        {
            'version': r.app_version,
            'positif': int(r.pos or 0),
            'total':   int(r.total),
            'pos_rate': round(int(r.pos or 0) / int(r.total) * 100, 1) if r.total else 0,
        }
        for r in rows
    ]


# ── Top terms (word cloud) ────────────────────────────────────────────────────

def get_top_terms(n: int = 15) -> dict:
    try:
        from sklearn.feature_extraction.text import TfidfVectorizer
        import numpy as np

        def _top(label, n):
            texts = [
                r.cleaned_text for r in
                Review.query.filter_by(sentiment_label=label)
                .filter(Review.cleaned_text.isnot(None))
                .with_entities(Review.cleaned_text)
                .limit(5000).all()
            ]
            if not texts:
                return []
            vec    = TfidfVectorizer(max_features=500)
            X      = vec.fit_transform(texts)
            scores = np.array(X.mean(axis=0)).flatten()
            terms  = vec.get_feature_names_out()
            top_i  = scores.argsort()[-n:][::-1]
            return [{'word': terms[i], 'weight': round(float(scores[i]), 4)} for i in top_i]

        return {'positive': _top('POSITIF', n), 'negative': _top('NEGATIF', n)}

    except Exception:
        return {'positive': [], 'negative': []}


# ── Paginated review explorer ────────────────────────────────────────────────

def get_reviews(q: str = None, sentiment: str = None, version: str = None,
                date_from: str = None, date_to: str = None,
                page: int = 1, per_page: int = 20):
    query = Review.query

    if q:
        query = query.filter(Review.raw_text.ilike(f'%{q}%'))
    if sentiment:
        query = query.filter(Review.sentiment_label == sentiment.upper())
    if version:
        query = query.filter(Review.app_version == version)
    if date_from:
        query = query.filter(Review.review_date >= date_from)
    if date_to:
        query = query.filter(Review.review_date <= date_to)

    return query.order_by(Review.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
