"""
Preprocessing service — runs the 6-step NLP pipeline on a dataset of reviews,
updating `reviews.cleaned_text` in batches and tracking progress in
`preprocessing_jobs`.
"""
import threading
from datetime import datetime

from app.extensions import db
from app.models.preprocessing_job import PreprocessingJob
from app.models.review import Review
from app.utils import nlp

_stop_flags: dict[int, threading.Event] = {}
BATCH_SIZE = 100   # reviews per DB commit


# ── Public API ────────────────────────────────────────────────────────────────

def start_job(scraping_job_id: int, user_id: int, app) -> PreprocessingJob:
    total = Review.query.filter_by(scraping_job_id=scraping_job_id).count()

    job = PreprocessingJob(
        scraping_job_id = scraping_job_id,
        dataset_size    = total,
        rows_processed  = 0,
        current_step    = 'cleaning',
        status          = 'RUNNING',
        created_by      = user_id,
    )
    db.session.add(job)
    db.session.commit()

    stop_event = threading.Event()
    _stop_flags[job.id] = stop_event

    t = threading.Thread(target=_run_pipeline, args=(job.id, scraping_job_id, stop_event, app), daemon=True)
    t.start()
    return job


def stop_job(job_id: int) -> bool:
    flag = _stop_flags.get(job_id)
    if flag:
        flag.set()
        return True
    return False


def get_job(job_id: int) -> PreprocessingJob:
    return PreprocessingJob.query.get(job_id)


def get_preview(job_id: int, limit: int = 10) -> list:
    job = PreprocessingJob.query.get(job_id)
    if not job:
        return []
    reviews = (
        Review.query
        .filter_by(scraping_job_id=job.scraping_job_id)
        .limit(limit)
        .all()
    )
    return [
        {
            'id':           f'#{r.id:03d}',
            'raw_text':     r.raw_text,
            'cleaned_text': r.cleaned_text,
            'done':         r.cleaned_text is not None,
        }
        for r in reviews
    ]


def get_distribution(job_id: int) -> dict:
    job = PreprocessingJob.query.get(job_id)
    if not job:
        return {}
    return {
        'POSITIF': float(job.pos_pct or 0),
        'NEGATIF': float(job.neg_pct or 0),
        'NETRAL':  float(job.neu_pct or 0),
    }


# ── Background thread ─────────────────────────────────────────────────────────

STEPS = ['case_folding', 'cleaning', 'tokenisasi', 'stopword_removal', 'stemming']


def _run_pipeline(job_id: int, scraping_job_id: int, stop_event: threading.Event, app):
    with app.app_context():
        job = PreprocessingJob.query.get(job_id)
        if not job:
            return

        try:
            query   = Review.query.filter_by(scraping_job_id=scraping_job_id)
            total   = query.count()
            offset  = 0
            done    = 0

            while offset < total and not stop_event.is_set():
                batch = query.offset(offset).limit(BATCH_SIZE).all()
                if not batch:
                    break

                for step in STEPS:
                    job.current_step = step
                    db.session.commit()

                for review in batch:
                    if stop_event.is_set():
                        break
                    review.cleaned_text = nlp.full_pipeline(review.raw_text)

                db.session.commit()
                done   += len(batch)
                offset += BATCH_SIZE
                job.rows_processed = done
                db.session.commit()

            # compute label distribution
            if not stop_event.is_set():
                pos = Review.query.filter_by(scraping_job_id=scraping_job_id, sentiment_label='POSITIF').count()
                neg = Review.query.filter_by(scraping_job_id=scraping_job_id, sentiment_label='NEGATIF').count()
                neu = Review.query.filter_by(scraping_job_id=scraping_job_id, sentiment_label='NETRAL').count()
                total_labelled = pos + neg + neu or 1
                job.pos_pct = round(pos / total_labelled * 100, 2)
                job.neg_pct = round(neg / total_labelled * 100, 2)
                job.neu_pct = round(neu / total_labelled * 100, 2)

            job.current_step  = 'done'
            job.status        = 'SELESAI' if not stop_event.is_set() else 'GAGAL'
            job.completed_at  = datetime.utcnow()
            db.session.commit()

        except Exception as exc:
            job.status        = 'GAGAL'
            job.completed_at  = datetime.utcnow()
            db.session.commit()
            raise exc
        finally:
            _stop_flags.pop(job_id, None)
