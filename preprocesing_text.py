"""
preprocesing_text.py - Modul Preprocessing Teks Bahasa Indonesia

Modul ini menyediakan pipeline preprocessing teks lengkap untuk
analisis sentimen ulasan berbahasa Indonesia, termasuk case folding,
cleansing, normalisasi kata slang, tokenisasi, penghapusan stopwords,
dan stemming menggunakan Sastrawi.
"""

import re
import json
import os
import logging
from typing import List, Dict, Optional
import pandas as pd
from Sastrawi.Stemmer.StemmerFactory import StemmerFactory

logger = logging.getLogger(__name__)

# ============================================================
# Inisialisasi resource yang digunakan di seluruh modul
# ============================================================

# Path file resource
_BASE_DIR = os.path.dirname(os.path.abspath(__file__))
_NORMALISASI_PATH = os.path.join(_BASE_DIR, 'normalisasi.json')
_STOPWORDS_PATH = os.path.join(_BASE_DIR, 'stopwords.txt')

# Load kamus normalisasi (slang -> baku)
_normalisasi_dict: Dict[str, str] = {}
try:
    if os.path.exists(_NORMALISASI_PATH):
        with open(_NORMALISASI_PATH, 'r', encoding='utf-8') as f:
            _normalisasi_dict = json.load(f)
        logger.info(
            f"Kamus normalisasi dimuat: {len(_normalisasi_dict)} kata"
        )
    else:
        logger.warning(
            f"File normalisasi tidak ditemukan: {_NORMALISASI_PATH}"
        )
except (json.JSONDecodeError, IOError) as e:
    logger.error(f"Error memuat kamus normalisasi: {str(e)}")

# Load daftar stopwords
_stopwords_list: List[str] = []
try:
    if os.path.exists(_STOPWORDS_PATH):
        with open(_STOPWORDS_PATH, 'r', encoding='utf-8') as f:
            _stopwords_list = [
                line.strip() for line in f.readlines()
                if line.strip()
            ]
        logger.info(f"Stopwords dimuat: {len(_stopwords_list)} kata")
    else:
        logger.warning(f"File stopwords tidak ditemukan: {_STOPWORDS_PATH}")
except IOError as e:
    logger.error(f"Error memuat stopwords: {str(e)}")

# Inisialisasi Sastrawi Stemmer (singleton)
_stemmer = None
try:
    _factory = StemmerFactory()
    _stemmer = _factory.create_stemmer()
    print("Sastrawi stemmer berhasil diinisialisasi")
    logger.info("Sastrawi stemmer berhasil diinisialisasi")
except Exception as e:
    print(f"Error inisialisasi Sastrawi stemmer: {str(e)}")
    logger.error(f"Error inisialisasi Sastrawi stemmer: {str(e)}")
    _stemmer = None




# ============================================================
# Fungsi-fungsi Preprocessing
# ============================================================

def case_folding(text: str) -> str:
    """
    Mengubah seluruh teks menjadi huruf kecil (lowercase).

    Args:
        text: Teks input yang akan diproses.

    Returns:
        Teks dalam huruf kecil.
    """
    if not isinstance(text, str):
        return ''
    return text.lower()


def cleansing(text: str) -> str:
    """
    Membersihkan teks dari elemen yang tidak diperlukan.

    Proses pembersihan meliputi:
    1. Menghapus URL (http/https/www)
    2. Menghapus mention (@username)
    3. Menghapus hashtag (#tag)
    4. Menghapus angka
    5. Menghapus emoji dan karakter non-ASCII
    6. Menghapus tanda baca dan karakter spesial
    7. Menghapus spasi berlebih

    Args:
        text: Teks input yang akan dibersihkan.

    Returns:
        Teks yang sudah dibersihkan.
    """
    if not isinstance(text, str):
        return ''

    # Hapus URL
    text = re.sub(r'http\S+|www\.\S+', '', text)

    # Hapus mention (@username)
    text = re.sub(r'@\w+', '', text)

    # Hapus hashtag (#tag)
    text = re.sub(r'#\w+', '', text)

    # Hapus angka
    text = re.sub(r'\d+', '', text)

    # Hapus emoji dan karakter non-ASCII
    text = re.sub(
        r'[^\x00-\x7F]+',
        '',
        text
    )

    # Hapus tanda baca dan karakter spesial
    text = re.sub(r'[^\w\s]', '', text)

    # Hapus spasi berlebih
    text = re.sub(r'\s+', ' ', text).strip()

    return text


def normalize_text(text: str, norm_dict: Optional[Dict[str, str]] = None) -> str:
    """
    Menormalisasi kata-kata slang/singkatan menjadi bentuk baku.

    Menggunakan kamus normalisasi untuk mengganti kata-kata tidak baku
    dengan padanan bakunya. Pencocokan dilakukan per kata (whole word).

    Args:
        text: Teks input yang akan dinormalisasi.
        norm_dict: Dictionary normalisasi {slang: baku}.
                   Jika None, menggunakan kamus default dari normalisasi.json.

    Returns:
        Teks dengan kata-kata slang yang sudah dinormalisasi.
    """
    if not isinstance(text, str):
        return ''

    if norm_dict is None:
        norm_dict = _normalisasi_dict

    if not norm_dict:
        return text

    words = text.split()
    normalized_words = []

    for word in words:
        # Cari kata di kamus normalisasi (case-insensitive)
        normalized = norm_dict.get(word.lower(), word)
        normalized_words.append(normalized)

    return ' '.join(normalized_words)


def tokenize(text: str) -> List[str]:
    """
    Memecah teks menjadi daftar kata (token).

    Args:
        text: Teks input yang akan ditokenisasi.

    Returns:
        List berisi kata-kata hasil tokenisasi.
    """
    if not isinstance(text, str):
        return []

    tokens = text.split()
    # Filter token kosong dan token dengan panjang kurang dari 1 karakter
    tokens = [token for token in tokens if len(token) > 0]

    return tokens


def remove_stopwords(
    tokens: List[str],
    stopwords_list: Optional[List[str]] = None
) -> List[str]:
    """
    Menghapus stopwords (kata-kata umum yang tidak bermakna) dari daftar token.

    Args:
        tokens: List berisi kata-kata yang akan difilter.
        stopwords_list: List berisi kata-kata stopword.
                        Jika None, menggunakan daftar default dari stopwords.txt.

    Returns:
        List berisi kata-kata yang bukan stopword.
    """
    if stopwords_list is None:
        stopwords_list = _stopwords_list

    if not stopwords_list:
        return tokens

    # Gunakan set untuk pencarian O(1)
    stopwords_set = set(stopwords_list)

    return [
        token for token in tokens
        if token.lower() not in stopwords_set
    ]


def stemming(tokens: List[str]) -> List[str]:
    """
    Melakukan stemming pada daftar token menggunakan Sastrawi.

    Stemming mengubah kata berimbuhan menjadi kata dasar untuk
    bahasa Indonesia. Contoh: 'berlari' -> 'lari', 'memakan' -> 'makan'.

    Args:
        tokens: List berisi kata-kata yang akan di-stem.

    Returns:
        List berisi kata-kata yang sudah di-stem.
    """
    if _stemmer is None:
        logger.warning("Stemmer tidak tersedia, mengembalikan token asli.")
        return tokens

    stemmed_tokens = []
    for token in tokens:
        try:
            stemmed = _stemmer.stem(token)
            stemmed_tokens.append(stemmed)
        except Exception as e:
            logger.debug(f"Error stemming kata '{token}': {str(e)}")
            stemmed_tokens.append(token)

    return stemmed_tokens


def preprocess_text(text: str) -> str:
    """
    Menjalankan pipeline preprocessing teks secara lengkap.

    Pipeline preprocessing:
    1. Case Folding -> mengubah ke huruf kecil
    2. Cleansing -> membersihkan URL, mention, hashtag, dll.
    3. Normalisasi -> mengganti kata slang ke baku
    4. Tokenisasi -> memecah teks menjadi kata-kata
    5. Remove Stopwords -> menghapus kata umum tidak bermakna
    6. Stemming -> mengubah kata ke bentuk dasar
    7. Join -> menggabungkan kembali menjadi string

    Args:
        text: Teks mentah yang akan dipreproses.

    Returns:
        Teks yang sudah melalui seluruh tahapan preprocessing.
    """
    if not isinstance(text, str) or not text.strip():
        return ''

    # Step 1: Case folding
    text = case_folding(text)

    # Step 2: Cleansing
    text = cleansing(text)

    # Step 3: Normalisasi
    text = normalize_text(text)

    # Step 4: Tokenisasi
    tokens = tokenize(text)

    # Step 5: Remove stopwords
    tokens = remove_stopwords(tokens)

    # Step 6: Stemming
    tokens = stemming(tokens)

    # Step 7: Gabungkan kembali
    result = ' '.join(tokens)

    return result


def preprocess_dataframe(
    df: pd.DataFrame,
    text_column: str = 'ulasan'
) -> pd.DataFrame:
    """
    Melakukan preprocessing pada kolom teks dalam DataFrame.

    Menambahkan kolom baru 'ulasan_bersih' yang berisi hasil preprocessing
    dari kolom teks yang ditentukan.

    Args:
        df: DataFrame pandas yang berisi data ulasan.
        text_column: Nama kolom yang berisi teks ulasan
                     (default: 'ulasan').

    Returns:
        DataFrame dengan kolom tambahan 'ulasan_bersih'.

    Raises:
        ValueError: Jika kolom teks yang ditentukan tidak ada di DataFrame.
    """
    if text_column not in df.columns:
        raise ValueError(
            f"Kolom '{text_column}' tidak ditemukan dalam DataFrame. "
            f"Kolom yang tersedia: {list(df.columns)}"
        )

    # Buat salinan DataFrame agar tidak mengubah data asli
    df_result = df.copy()

    logger.info(
        f"Memulai preprocessing {len(df_result)} baris data "
        f"pada kolom '{text_column}'"
    )

    # Terapkan preprocessing pada setiap baris
    df_result['ulasan_bersih'] = df_result[text_column].apply(
        lambda x: preprocess_text(str(x)) if pd.notna(x) else ''
    )

    # Hitung statistik
    empty_count = (df_result['ulasan_bersih'] == '').sum()
    logger.info(
        f"Preprocessing selesai. "
        f"{len(df_result) - empty_count} baris berhasil diproses, "
        f"{empty_count} baris kosong setelah preprocessing."
    )

    return df_result
