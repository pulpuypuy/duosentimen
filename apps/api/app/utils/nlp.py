"""
Indonesian NLP pipeline helpers used by both preprocessing_service
and prediction_service (inline preprocessing at inference time).

Pipeline sesuai kerangka kerja:
  Case Folding → Cleaning → Tokenizing → Normalisasi → Stopword Removal → Stemming
"""
import re
from typing import List

# ── Slang / abbreviation normalisation dictionary ───────────────────────────
SLANG_DICT = {
    'bgt': 'banget', 'banget': 'banget', 'gak': 'tidak', 'ga': 'tidak',
    'gk': 'tidak', 'nggak': 'tidak', 'ngga': 'tidak', 'enggak': 'tidak',
    'sy': 'saya', 'gw': 'saya', 'gue': 'saya', 'aku': 'saya',
    'lo': 'kamu', 'lu': 'kamu', 'yg': 'yang', 'klo': 'kalau',
    'kl': 'kalau', 'kal': 'kalau', 'dg': 'dengan', 'dgn': 'dengan',
    'utk': 'untuk', 'dr': 'dari', 'pk': 'pakai', 'tdk': 'tidak',
    'sdh': 'sudah', 'blm': 'belum', 'krn': 'karena', 'tp': 'tapi',
    'tpi': 'tapi', 'gmn': 'bagaimana', 'gimana': 'bagaimana',
    'nih': 'ini', 'tuh': 'itu', 'sih': '', 'deh': '', 'dong': '',
    'lho': '', 'lah': '', 'wkwk': '', 'haha': '', 'hehe': '',
    'gbsa': 'tidak bisa', 'bikin': 'buat', 'mantul': 'mantap',
    'kuy': 'ayo', 'cuy': '', 'bro': '', 'mimin': 'admin',
    'min': 'admin', 'woyy': 'hei', 'woy': 'hei', 'tolong': 'tolong',
    'pliss': 'tolong', 'pls': 'tolong', 'thx': 'terima kasih',
    'makasih': 'terima kasih', 'makasi': 'terima kasih',
    'ngebug': 'error', 'lemot': 'lambat', 'lelet': 'lambat',
    'males': 'malas', 'niat': 'niat', 'asik': 'asyik',
    'mantap': 'mantap', 'keren': 'keren', 'bagus': 'bagus',
}

# ── Indonesian stopwords (curated subset) ───────────────────────────────────
STOPWORDS = {
    'yang', 'dan', 'di', 'ke', 'dari', 'dengan', 'untuk', 'ini', 'itu',
    'ada', 'akan', 'adalah', 'saya', 'kamu', 'mereka', 'kami', 'kita',
    'tidak', 'bisa', 'jika', 'maka', 'pada', 'atau', 'juga', 'sudah',
    'belum', 'sudah', 'saat', 'masih', 'lagi', 'jadi', 'seperti', 'lebih',
    'cara', 'bisa', 'dapat', 'harus', 'saja', 'pun', 'lah', 'pula',
    'bahwa', 'satu', 'dua', 'tiga', 'empat', 'lima', 'enam', 'tujuh',
    'delapan', 'sembilan', 'sepuluh', 'sangat', 'sekali', 'agak', 'cukup',
    'kalau', 'mau', 'ya', 'iya', 'oh', 'ah', 'eh', 'hm',
}

# ── Sastrawi stemmer (lazy-loaded) ──────────────────────────────────────────
_stemmer = None


def _get_stemmer():
    global _stemmer
    if _stemmer is None:
        try:
            from Sastrawi.Stemmer.StemmerFactory import StemmerFactory
            _stemmer = StemmerFactory().create_stemmer()
        except ImportError:
            _stemmer = None   # graceful fallback
    return _stemmer


# ── Pipeline steps ───────────────────────────────────────────────────────────

def case_fold(text: str) -> str:
    """Langkah 1: Case Folding — mengubah semua huruf menjadi huruf kecil."""
    return text.lower()


def clean_text(text: str) -> str:
    """Langkah 2: Cleaning — hapus URL, mention, hashtag, emoji, simbol."""
    text = re.sub(r'https?://\S+|www\.\S+', '', text)
    text = re.sub(r'@\w+', '', text)
    text = re.sub(r'#\w+', '', text)
    # remove emoji / non-latin characters
    text = text.encode('ascii', 'ignore').decode('ascii')
    text = re.sub(r'[^a-zA-Z0-9\s.,!?]', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text


def tokenize(text: str) -> List[str]:
    """Langkah 3: Tokenizing — memecah teks menjadi token/kata."""
    return [t for t in re.split(r'[\s.,!?;:\"\'()\-]+', text) if t]


def normalize(tokens: List[str]) -> List[str]:
    """Normalisasi slang dan singkatan Bahasa Indonesia."""
    return [SLANG_DICT.get(t, t) for t in tokens if SLANG_DICT.get(t, t) != '']


def remove_stopwords(tokens: List[str]) -> List[str]:
    """Langkah 4: Stopword Removal — hapus kata-kata umum yang tidak bermakna."""
    return [t for t in tokens if t not in STOPWORDS]


def stem(tokens: List[str]) -> List[str]:
    """Langkah 5: Stemming — mengubah kata ke bentuk dasar (PySastrawi)."""
    stemmer = _get_stemmer()
    if stemmer:
        return [stemmer.stem(t) for t in tokens]
    return tokens   # no-op if Sastrawi not installed


def full_pipeline(raw: str) -> str:
    """Jalankan pipeline preprocessing lengkap sesuai kerangka kerja:
    1. Case Folding
    2. Cleaning (URL, simbol, emoji)
    3. Tokenizing
    4. Normalisasi (slang/singkatan)
    5. Stopword Removal
    6. Stemming
    """
    text   = case_fold(raw)            # 1. Case Folding
    text   = clean_text(text)          # 2. Cleaning
    tokens = tokenize(text)            # 3. Tokenizing
    tokens = normalize(tokens)         # 4. Normalisasi slang
    tokens = remove_stopwords(tokens)  # 5. Stopword Removal
    tokens = stem(tokens)              # 6. Stemming
    return ' '.join(tokens)
