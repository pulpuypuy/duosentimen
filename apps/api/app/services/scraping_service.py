"""
Scraping service — wraps google-play-scraper and manages background threads.
Progress is updated in the DB every BATCH_SIZE reviews; the frontend polls
GET /api/scraping/jobs/{id} to get live progress.
"""
import threading
import hashlib
import random
from datetime import datetime, date

from app.extensions import db
from app.models.scraping_job import ScrapingJob
from app.models.review import Review

# Map of running threads + stop signals  {job_id: threading.Event}
_stop_flags: dict[int, threading.Event] = {}

BATCH_SIZE = 50   # commit to DB every N reviews


# ── Public API ────────────────────────────────────────────────────────────────

def start_job(params: dict, user_id: int, app) -> ScrapingJob:
    job = ScrapingJob(
        target_app_id  = params['target_app_id'],
        max_reviews    = int(params.get('max_reviews', 1000)),
        filter_bintang = params.get('filter_bintang', 'Semua'),
        date_from      = _parse_date(params.get('date_from')),
        date_to        = _parse_date(params.get('date_to')),
        status         = 'PENDING',
        created_by     = user_id,
    )
    db.session.add(job)
    db.session.commit()

    stop_event = threading.Event()
    _stop_flags[job.id] = stop_event

    t = threading.Thread(target=_run_scraping, args=(job.id, stop_event, app), daemon=True)
    t.start()
    return job


def stop_job(job_id: int) -> bool:
    flag = _stop_flags.get(job_id)
    if flag:
        flag.set()
        return True
    return False


def get_job(job_id: int) -> ScrapingJob:
    return ScrapingJob.query.get(job_id)


def list_jobs(page: int = 1, per_page: int = 10):
    return ScrapingJob.query.order_by(ScrapingJob.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )


def delete_job(job_id: int) -> bool:
    job = ScrapingJob.query.get(job_id)
    if not job:
        return False
    # remove associated reviews first
    Review.query.filter_by(scraping_job_id=job_id).delete()
    db.session.delete(job)
    db.session.commit()
    return True


def get_dataset_stats() -> dict:
    total = Review.query.count()
    return {'total_dataset': total}


# ── Background thread ─────────────────────────────────────────────────────────

def _run_scraping(job_id: int, stop_event: threading.Event, app):
    with app.app_context():
        job = ScrapingJob.query.get(job_id)
        if not job:
            return

        job.status     = 'RUNNING'
        job.started_at = datetime.utcnow()
        db.session.commit()

        try:
            reviews_data = _fetch_reviews(
                app_id         = job.target_app_id,
                count          = job.max_reviews,
                filter_bintang = job.filter_bintang,
                stop_event     = stop_event,
            )

            batch = []
            for i, r in enumerate(reviews_data):
                if stop_event.is_set():
                    break

                rating = r.get('score', 3)
                review = Review(
                    scraping_job_id = job.id,
                    user_id_hash    = _hash_user(r.get('userName', f'user_{i}')),
                    raw_text        = r.get('content', ''),
                    rating          = rating,
                    app_version     = r.get('appVersion', ''),
                    review_date     = _parse_gp_date(r.get('at')),
                    sentiment_label = Review.label_from_rating(rating),
                )
                batch.append(review)
                job.reviews_scraped = i + 1

                if len(batch) >= BATCH_SIZE:
                    db.session.add_all(batch)
                    db.session.commit()
                    batch.clear()

            if batch:
                db.session.add_all(batch)

            job.status       = 'SELESAI' if not stop_event.is_set() else 'GAGAL'
            job.completed_at = datetime.utcnow()
            db.session.commit()

        except Exception as exc:
            job.status        = 'GAGAL'
            job.error_message = str(exc)
            job.completed_at  = datetime.utcnow()
            db.session.commit()
        finally:
            _stop_flags.pop(job_id, None)


def _fetch_reviews(app_id: str, count: int, filter_bintang: str, stop_event) -> list:
    """Try google-play-scraper; fall back to generated mock data."""
    try:
        from google_play_scraper import reviews, Sort
        score_filter = _bintang_to_scores(filter_bintang)
        all_reviews  = []
        continuation = None

        while len(all_reviews) < count and not stop_event.is_set():
            batch_size = min(200, count - len(all_reviews))
            result, continuation = reviews(
                app_id,
                lang         = 'id',
                country      = 'id',
                sort         = Sort.NEWEST,
                count        = batch_size,
                continuation_token = continuation,
            )
            if score_filter:
                result = [r for r in result if r['score'] in score_filter]
            all_reviews.extend(result)
            if not continuation:
                break

        return all_reviews[:count]

    except Exception:
        # Fallback: generate mock reviews for dev/demo purposes
        return _generate_mock_reviews(count)


def _generate_mock_reviews(count: int) -> list:
    templates = [
        ("Aplikasi ini sangat membantu belajar bahasa baru!", 5),
        ("Sering crash saat update terbaru. Tolong perbaiki!", 1),
        ("Biasa saja, tidak ada yang istimewa.", 3),
        ("Fiturnya keren tapi iklannya mengganggu.", 4),
        ("Error terus saat mau submit latihan.", 2),
        ("Mantap! Streak 100 hari tercapai.", 5),
        ("Loading lama banget, lemot sekali.", 1),
        ("Desain UI-nya bagus dan mudah dipakai.", 4),
        ("Crash melulu setelah update kemarin.", 2),
        ("Sangat membantu untuk belajar Spanyol setiap hari.", 5),
    ]
    versions = ['1.0.0', '1.0.1', '1.0.2', '1.0.3', '1.0.4']
    now = datetime.utcnow()
    result = []
    for i in range(count):
        text, rating = templates[i % len(templates)]
        result.append({
            'content':    text,
            'score':      rating,
            'userName':   f'user_{i}',
            'appVersion': f'v{random.choice(versions)}',
            'at':         now,
        })
    return result


def _bintang_to_scores(filter_str: str) -> list:
    mapping = {
        'Bintang 1-2': [1, 2],
        'Bintang 3':   [3],
        'Bintang 4-5': [4, 5],
    }
    return mapping.get(filter_str, [])


def _hash_user(name: str) -> str:
    return 'usr_' + hashlib.md5(name.encode()).hexdigest()[:6]


def _parse_date(val) -> date:
    if not val:
        return None
    try:
        return datetime.strptime(val, '%Y-%m-%d').date()
    except Exception:
        return None


def _parse_gp_date(val) -> date:
    if isinstance(val, datetime):
        return val.date()
    return None
