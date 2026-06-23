"""
Training service — melatih model Naive Bayes dengan TF-IDF pada data ulasan
yang sudah dipreprocessing, mengevaluasi metrik, menyimpan model dengan joblib.

Sesuai kerangka kerja: TF-IDF → Pembagian 80:20 → Naive Bayes → Evaluasi
"""
import os
import threading
from datetime import datetime

import joblib
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score, confusion_matrix
)

from app.extensions import db
from app.models.model_version import ModelVersion
from app.models.review import Review

_training_flags: dict[int, threading.Event] = {}


# ── Public API ────────────────────────────────────────────────────────────────

def start_training(params: dict, user_id: int, model_dir: str, app) -> ModelVersion:
    # auto-increment version tag
    last = ModelVersion.query.order_by(ModelVersion.id.desc()).first()
    tag  = _next_version(last.version_tag if last else 'v1.0.0')

    mv = ModelVersion(
        version_tag    = tag,
        algorithm      = 'nb',       # Naive Bayes sesuai kerangka kerja
        feature_method = 'tfidf',    # TF-IDF sesuai kerangka kerja
        ngram_min      = int(params.get('ngram_min', 1)),
        ngram_max      = int(params.get('ngram_max', 2)),
        train_split    = int(params.get('train_split', 80)),
        trained_by     = user_id,
    )
    db.session.add(mv)
    db.session.commit()

    t = threading.Thread(
        target=_run_training, args=(mv.id, model_dir, app), daemon=True
    )
    t.start()
    return mv


def list_models() -> list:
    return ModelVersion.query.order_by(ModelVersion.trained_at.desc()).all()


def get_model(model_id: int) -> ModelVersion:
    return ModelVersion.query.get(model_id)


def get_active_model() -> ModelVersion:
    return ModelVersion.query.filter_by(is_active=True).first()


def deploy_model(model_id: int) -> ModelVersion:
    # deactivate all
    ModelVersion.query.update({'is_active': False})
    mv = ModelVersion.query.get(model_id)
    if mv:
        mv.is_active = True
        db.session.commit()
    return mv


# ── Background thread ─────────────────────────────────────────────────────────

def _run_training(model_id: int, model_dir: str, app):
    with app.app_context():
        mv = ModelVersion.query.get(model_id)
        if not mv:
            return
        try:
            # Ambil semua ulasan yang sudah dipreprocessing dan berlabel
            rows = (
                Review.query
                .filter(
                    Review.cleaned_text.isnot(None),
                    Review.sentiment_label.isnot(None),
                )
                .with_entities(Review.cleaned_text, Review.sentiment_label)
                .all()
            )

            if len(rows) < 10:
                raise ValueError('Dataset terlalu kecil untuk training (min 10 baris).')

            texts  = [r.cleaned_text for r in rows]
            labels = [r.sentiment_label for r in rows]
            test_size = 1 - (mv.train_split / 100)

            # Pembagian data 80:20
            X_train, X_test, y_train, y_test = train_test_split(
                texts, labels, test_size=test_size, random_state=42, stratify=labels
            )

            # Pipeline: TF-IDF + Naive Bayes
            pipeline = Pipeline([
                ('tfidf', TfidfVectorizer(
                    ngram_range=(mv.ngram_min, mv.ngram_max),
                    max_features=20000,
                    sublinear_tf=True,
                )),
                ('nb', MultinomialNB(alpha=1.0)),  # Laplace smoothing
            ])
            pipeline.fit(X_train, y_train)

            # Evaluasi
            y_pred  = pipeline.predict(X_test)
            classes = ['POSITIF', 'NEGATIF', 'NETRAL']
            acc  = accuracy_score(y_test, y_pred)
            prec = precision_score(y_test, y_pred, labels=classes, average='weighted', zero_division=0)
            rec  = recall_score(y_test, y_pred, labels=classes, average='weighted', zero_division=0)
            f1   = f1_score(y_test, y_pred, labels=classes, average='weighted', zero_division=0)

            # Confusion matrix
            cm = confusion_matrix(y_test, y_pred, labels=classes)
            tp = int(cm[0, 0])
            fn = int(cm[0, 1] + cm[0, 2])
            fp = int(cm[1, 0] + cm[2, 0])
            tn = int(cm[1, 1] + cm[1, 2] + cm[2, 1] + cm[2, 2])

            # Simpan model
            os.makedirs(model_dir, exist_ok=True)
            file_path = os.path.join(model_dir, f'model_{mv.version_tag}.pkl')
            joblib.dump(pipeline, file_path)

            mv.accuracy        = round(acc, 4)
            mv.precision_score = round(prec, 4)
            mv.recall_score    = round(rec, 4)
            mv.f1_score        = round(f1, 4)
            mv.tp, mv.fp, mv.fn, mv.tn = tp, fp, fn, tn
            mv.model_file_path = file_path
            db.session.commit()

        except Exception as exc:
            mv.model_file_path = None
            db.session.commit()
            raise exc


def _next_version(tag: str) -> str:
    try:
        base  = tag.lstrip('v')
        parts = base.split('.')
        parts[-1] = str(int(parts[-1]) + 1)
        return 'v' + '.'.join(parts)
    except Exception:
        return 'v1.0.0'
