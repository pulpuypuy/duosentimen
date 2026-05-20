"""
scraper.py - Modul Scraping Ulasan Google Play Store untuk Duolingo

Modul ini menyediakan fungsi-fungsi untuk mengambil ulasan aplikasi Duolingo
dari Google Play Store menggunakan library google_play_scraper, memfilter
berdasarkan tahun, dan melakukan pelabelan otomatis berdasarkan rating.
"""

import time
import logging
from typing import List, Dict, Optional
from google_play_scraper import Sort, reviews

logger = logging.getLogger(__name__)

# ID aplikasi Duolingo di Google Play Store
APP_ID = 'com.duolingo'


def scrape_duolingo_reviews(
    count: int = 5000,
    lang: str = 'id',
    country: str = 'id'
) -> List[Dict]:
    """
    Mengambil ulasan Duolingo dari Google Play Store.

    Menggunakan pagination dengan continuation_token untuk mengambil
    ulasan dalam batch. Setiap batch diambil dengan jeda 1 detik
    untuk menghindari rate limiting.

    Args:
        count: Jumlah ulasan yang ingin diambil (default: 5000).
        lang: Kode bahasa ulasan (default: 'id' untuk Indonesia).
        country: Kode negara (default: 'id' untuk Indonesia).

    Returns:
        List berisi dictionary ulasan dari Google Play Store.
        Setiap dictionary memiliki keys seperti 'userName', 'score',
        'content', 'at', dll.

    Raises:
        Exception: Jika terjadi error saat mengambil ulasan dari API.
    """
    all_reviews = []
    batch_size = 200
    continuation_token = None

    logger.info(
        f"Memulai scraping {count} ulasan Duolingo "
        f"(lang={lang}, country={country})"
    )

    try:
        while len(all_reviews) < count:
            # Hitung sisa ulasan yang perlu diambil
            remaining = count - len(all_reviews)
            current_batch_size = min(batch_size, remaining)

            # Ambil batch ulasan
            result, continuation_token = reviews(
                APP_ID,
                lang=lang,
                country=country,
                sort=Sort.NEWEST,
                count=current_batch_size,
                continuation_token=continuation_token
            )

            if not result:
                logger.warning("Tidak ada ulasan lagi yang tersedia.")
                break

            all_reviews.extend(result)
            logger.info(
                f"Batch berhasil: {len(result)} ulasan diambil. "
                f"Total: {len(all_reviews)}/{count}"
            )

            # Berhenti jika tidak ada token lanjutan
            if continuation_token is None:
                logger.info("Tidak ada continuation token, scraping selesai.")
                break

            # Jeda antar batch untuk menghindari rate limiting
            time.sleep(1)

    except Exception as e:
        logger.error(f"Error saat scraping ulasan: {str(e)}")
        raise

    logger.info(f"Scraping selesai. Total ulasan: {len(all_reviews)}")
    return all_reviews[:count]


def filter_by_year(reviews_data: List[Dict], year: int = 2026) -> List[Dict]:
    """
    Memfilter ulasan berdasarkan tahun.

    Args:
        reviews_data: List berisi dictionary ulasan hasil scraping.
        year: Tahun yang diinginkan (default: 2026).

    Returns:
        List berisi dictionary ulasan yang sesuai dengan tahun filter.
    """
    filtered = []
    for review in reviews_data:
        review_date = review.get('at')
        if review_date is not None:
            try:
                if review_date.year == year:
                    filtered.append(review)
            except AttributeError:
                logger.warning(
                    f"Format tanggal tidak valid untuk ulasan: "
                    f"{review.get('userName', 'Unknown')}"
                )
                continue

    logger.info(
        f"Filter tahun {year}: {len(filtered)} dari "
        f"{len(reviews_data)} ulasan"
    )
    return filtered


def auto_label(rating: int) -> str:
    """
    Melakukan pelabelan sentimen otomatis berdasarkan rating.

    Aturan pelabelan:
    - Rating 1-2: negatif
    - Rating 3: netral
    - Rating 4-5: positif

    Args:
        rating: Nilai rating ulasan (1-5).

    Returns:
        String label sentimen: 'positif', 'negatif', atau 'netral'.

    Raises:
        ValueError: Jika rating bukan angka antara 1-5.
    """
    if not isinstance(rating, (int, float)) or rating < 1 or rating > 5:
        raise ValueError(
            f"Rating harus berupa angka antara 1-5, diterima: {rating}"
        )

    if rating <= 2:
        return 'negatif'
    elif rating == 3:
        return 'netral'
    else:
        return 'positif'


def process_reviews(reviews_data: List[Dict]) -> List[Dict]:
    """
    Memproses ulasan mentah menjadi format yang siap disimpan ke database.

    Mengekstrak informasi yang relevan dari setiap ulasan dan menambahkan
    label sentimen otomatis berdasarkan rating.

    Args:
        reviews_data: List berisi dictionary ulasan mentah dari scraper.

    Returns:
        List berisi dictionary dengan keys:
        - nama_user (str): Nama pengguna yang memberikan ulasan.
        - rating (int): Nilai rating (1-5).
        - ulasan (str): Teks ulasan.
        - tanggal (datetime): Tanggal ulasan diberikan.
        - label (str): Label sentimen otomatis.
    """
    processed = []

    for review in reviews_data:
        try:
            rating = review.get('score', 0)
            content = review.get('content', '')

            # Lewati ulasan kosong
            if not content or not content.strip():
                logger.debug(
                    f"Ulasan kosong dari {review.get('userName', 'Unknown')}, "
                    f"dilewati."
                )
                continue

            processed_review = {
                'nama_user': review.get('userName', 'Anonim'),
                'rating': int(rating),
                'ulasan': content.strip(),
                'tanggal': review.get('at'),
                'label': auto_label(int(rating))
            }
            processed.append(processed_review)

        except (ValueError, TypeError) as e:
            logger.warning(
                f"Error memproses ulasan dari "
                f"{review.get('userName', 'Unknown')}: {str(e)}"
            )
            continue

    logger.info(
        f"Proses ulasan selesai: {len(processed)} dari "
        f"{len(reviews_data)} ulasan berhasil diproses"
    )
    return processed
