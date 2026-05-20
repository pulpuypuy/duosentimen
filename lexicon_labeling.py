"""
lexicon_labeling.py - Modul Labeling Sentimen Berbasis Lexicon

Modul ini menggunakan InSet (Indonesia Sentiment Lexicon) untuk 
melakukan labeling sentimen otomatis dengan 3 kelas:
- positif  (total skor > 0)
- negatif  (total skor < 0)
- netral   (total skor == 0)

Lexicon InSet memberikan bobot polarity pada kata-kata bahasa Indonesia
dengan rentang -5 (sangat negatif) hingga +5 (sangat positif).
"""

import os
import csv
import logging
from typing import Dict, List, Tuple, Optional

logger = logging.getLogger(__name__)

# Path file lexicon
_BASE_DIR = os.path.dirname(os.path.abspath(__file__))
_POSITIVE_LEXICON_PATH = os.path.join(_BASE_DIR, 'lexicon_positive.tsv')
_NEGATIVE_LEXICON_PATH = os.path.join(_BASE_DIR, 'lexicon_negative.tsv')

# Dictionary lexicon global {word: weight}
_lexicon_dict: Dict[str, int] = {}


def _load_lexicon(filepath: str) -> Dict[str, int]:
    """
    Memuat file lexicon TSV ke dictionary.
    
    Format file: word<tab>weight
    Header: word\tweight
    
    Args:
        filepath: Path ke file TSV lexicon.
    
    Returns:
        Dictionary {kata: bobot_polarity}
    """
    lexicon = {}
    try:
        if os.path.exists(filepath):
            with open(filepath, 'r', encoding='utf-8') as f:
                reader = csv.reader(f, delimiter='\t')
                header = next(reader, None)  # Skip header
                for row in reader:
                    if len(row) >= 2:
                        word = row[0].strip().lower()
                        try:
                            weight = int(row[1].strip())
                            lexicon[word] = weight
                        except ValueError:
                            continue
            logger.info(f"Lexicon dimuat dari {filepath}: {len(lexicon)} kata")
        else:
            logger.warning(f"File lexicon tidak ditemukan: {filepath}")
    except Exception as e:
        logger.error(f"Error memuat lexicon {filepath}: {str(e)}")
    return lexicon


def init_lexicon():
    """
    Inisialisasi dictionary lexicon dari file positif dan negatif.
    Dipanggil saat module diimport.
    """
    global _lexicon_dict
    
    positive = _load_lexicon(_POSITIVE_LEXICON_PATH)
    negative = _load_lexicon(_NEGATIVE_LEXICON_PATH)
    
    _lexicon_dict = {**positive, **negative}
    
    print(f"Lexicon InSet dimuat: {len(positive)} kata positif, "
          f"{len(negative)} kata negatif, total {len(_lexicon_dict)} kata")
    logger.info(f"Lexicon InSet dimuat: total {len(_lexicon_dict)} kata")


def get_word_score(word: str) -> int:
    """
    Mendapatkan skor polarity sebuah kata dari lexicon.
    
    Args:
        word: Kata yang akan dicari skornya.
    
    Returns:
        Skor polarity kata (-5 s/d +5), 0 jika tidak ditemukan.
    """
    return _lexicon_dict.get(word.lower().strip(), 0)


def calculate_sentiment_score(text: str) -> Tuple[int, List[Tuple[str, int]]]:
    """
    Menghitung total skor sentimen dari sebuah teks.
    
    Proses:
    1. Tokenisasi teks menjadi kata-kata
    2. Cari skor setiap kata di lexicon
    3. Handle negasi: jika kata sebelumnya adalah negasi 
       (tidak, bukan, jangan, belum, tanpa, tak), 
       maka skor dibalik (dikalikan -1)
    4. Jumlahkan semua skor
    
    Args:
        text: Teks yang sudah di-preprocessing.
    
    Returns:
        Tuple (total_skor, list_detail) dimana list_detail berisi 
        tuple (kata, skor) untuk setiap kata yang ada di lexicon.
    """
    if not text or not text.strip():
        return 0, []
    
    words = text.lower().split()
    negation_words = {'tidak', 'bukan', 'jangan', 'belum', 'tanpa', 'tak', 
                      'tiada', 'kurang', 'tanpa'}
    
    total_score = 0
    detail = []
    is_negated = False
    
    for word in words:
        # Cek apakah kata ini adalah kata negasi
        if word in negation_words:
            is_negated = True
            continue
        
        # Cari skor kata di lexicon
        score = get_word_score(word)
        
        if score != 0:
            # Jika sebelumnya ada negasi, balik skor
            if is_negated:
                score = score * -1
                detail.append((f"tidak_{word}", score))
            else:
                detail.append((word, score))
            
            total_score += score
        
        # Reset negasi setelah digunakan
        is_negated = False
    
    return total_score, detail


def label_sentiment(text: str) -> str:
    """
    Menentukan label sentimen berdasarkan skor lexicon.
    
    Rules:
    - skor > 0  → positif
    - skor < 0  → negatif
    - skor == 0 → netral
    
    Args:
        text: Teks yang sudah di-preprocessing.
    
    Returns:
        Label sentimen: 'positif', 'negatif', atau 'netral'
    """
    score, _ = calculate_sentiment_score(text)
    
    if score > 0:
        return 'positif'
    elif score < 0:
        return 'negatif'
    else:
        return 'netral'


def label_sentiment_detail(text: str) -> Dict:
    """
    Menentukan label sentimen dengan detail skor per kata.
    
    Args:
        text: Teks yang sudah di-preprocessing.
    
    Returns:
        Dictionary dengan keys:
        - label: 'positif'/'negatif'/'netral'
        - score: total skor
        - detail: list of (kata, skor)
    """
    score, detail = calculate_sentiment_score(text)
    
    if score > 0:
        label = 'positif'
    elif score < 0:
        label = 'negatif'
    else:
        label = 'netral'
    
    return {
        'label': label,
        'score': score,
        'detail': detail
    }


def label_dataframe(df, text_column='ulasan_bersih'):
    """
    Melakukan labeling sentimen pada DataFrame menggunakan lexicon.
    
    Args:
        df: DataFrame pandas dengan kolom teks.
        text_column: Nama kolom yang berisi teks preprocessed.
    
    Returns:
        DataFrame dengan kolom tambahan:
        - 'label': label sentimen (positif/negatif/netral)
        - 'skor_sentimen': skor numerik
    """
    import pandas as pd
    
    if text_column not in df.columns:
        raise ValueError(f"Kolom '{text_column}' tidak ditemukan. "
                        f"Kolom tersedia: {list(df.columns)}")
    
    df_result = df.copy()
    
    labels = []
    scores = []
    
    for _, row in df_result.iterrows():
        text = str(row[text_column]) if pd.notna(row[text_column]) else ''
        score, _ = calculate_sentiment_score(text)
        
        if score > 0:
            label = 'positif'
        elif score < 0:
            label = 'negatif'
        else:
            label = 'netral'
        
        labels.append(label)
        scores.append(score)
    
    df_result['label'] = labels
    df_result['skor_sentimen'] = scores
    
    # Log statistik
    from collections import Counter
    counts = Counter(labels)
    print(f"Labeling selesai: {counts}")
    logger.info(f"Labeling selesai: {counts}")
    
    return df_result


# Inisialisasi lexicon saat module diimport
init_lexicon()
