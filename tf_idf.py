"""
tf_idf.py - Modul TF-IDF (Term Frequency - Inverse Document Frequency)

Modul ini menyediakan implementasi manual TF-IDF untuk ekstraksi fitur
dari teks ulasan. TF-IDF digunakan sebagai representasi numerik dari
dokumen teks sebelum diklasifikasikan oleh Naive Bayes.
"""

import math
import logging
from typing import List, Dict, Tuple
from collections import Counter

logger = logging.getLogger(__name__)


def calculate_tf(document_tokens: List[str]) -> Dict[str, float]:
    """
    Menghitung Term Frequency (TF) untuk setiap kata dalam satu dokumen.

    TF dihitung sebagai jumlah kemunculan kata dibagi total kata dalam
    dokumen: TF(t,d) = count(t) / |d|

    Args:
        document_tokens: List berisi token kata-kata dari satu dokumen.

    Returns:
        Dictionary {kata: nilai_tf} untuk setiap kata dalam dokumen.
    """
    if not document_tokens:
        return {}

    total_words = len(document_tokens)
    word_counts = Counter(document_tokens)

    tf_dict = {
        word: count / total_words
        for word, count in word_counts.items()
    }

    return tf_dict


def calculate_df(all_documents_tokens: List[List[str]]) -> Dict[str, int]:
    """
    Menghitung Document Frequency (DF) untuk setiap kata di seluruh dokumen.

    DF menghitung jumlah dokumen yang mengandung kata tertentu.

    Args:
        all_documents_tokens: List berisi list token dari setiap dokumen.

    Returns:
        Dictionary {kata: jumlah_dokumen_yang_mengandung_kata}.
    """
    if not all_documents_tokens:
        return {}

    df_dict: Dict[str, int] = {}

    for doc_tokens in all_documents_tokens:
        # Gunakan set untuk menghindari penghitungan ganda
        # dalam satu dokumen yang sama
        unique_words = set(doc_tokens)
        for word in unique_words:
            df_dict[word] = df_dict.get(word, 0) + 1

    return df_dict


def calculate_idf(df_dict: Dict[str, int], total_docs: int) -> Dict[str, float]:
    """
    Menghitung Inverse Document Frequency (IDF) untuk setiap kata.

    IDF dihitung dengan rumus: IDF(t) = log(N / (DF(t) + 1))
    dimana N adalah total dokumen dan DF(t) adalah jumlah dokumen
    yang mengandung kata t. Ditambah 1 pada penyebut untuk smoothing.

    Args:
        df_dict: Dictionary {kata: document_frequency}.
        total_docs: Total jumlah dokumen dalam korpus.

    Returns:
        Dictionary {kata: nilai_idf} untuk setiap kata.
    """
    if not df_dict or total_docs <= 0:
        return {}

    idf_dict = {
        word: math.log(total_docs / (df + 1))
        for word, df in df_dict.items()
    }

    return idf_dict


def calculate_tfidf(
    documents_tokens: List[List[str]],
    labels: List[str]
) -> Dict:
    """
    Menghitung TF-IDF untuk seluruh koleksi dokumen.

    Proses:
    1. Hitung TF untuk setiap dokumen
    2. Hitung DF untuk seluruh dokumen
    3. Hitung IDF berdasarkan DF
    4. Kalikan TF × IDF untuk setiap kata di setiap dokumen

    Args:
        documents_tokens: List berisi list token dari setiap dokumen.
        labels: List berisi label sentimen untuk setiap dokumen.
                Harus memiliki panjang yang sama dengan documents_tokens.

    Returns:
        Dictionary dengan keys:
        - vocabulary (list): Daftar seluruh kata unik dalam korpus.
        - idf_values (dict): Nilai IDF untuk setiap kata.
        - tfidf_matrix (list): List berisi dictionary TF-IDF per dokumen.
        - labels (list): Label sentimen yang sesuai.

    Raises:
        ValueError: Jika jumlah dokumen tidak sama dengan jumlah label.
    """
    if len(documents_tokens) != len(labels):
        raise ValueError(
            f"Jumlah dokumen ({len(documents_tokens)}) tidak sama "
            f"dengan jumlah label ({len(labels)})"
        )

    total_docs = len(documents_tokens)

    if total_docs == 0:
        return {
            'vocabulary': [],
            'idf_values': {},
            'tfidf_matrix': [],
            'labels': []
        }

    logger.info(f"Menghitung TF-IDF untuk {total_docs} dokumen")

    # Step 1: Hitung DF
    df_dict = calculate_df(documents_tokens)

    # Step 2: Hitung IDF
    idf_values = calculate_idf(df_dict, total_docs)

    # Step 3: Bangun vocabulary (diurutkan untuk konsistensi)
    vocabulary = sorted(idf_values.keys())

    # Step 4: Hitung TF-IDF per dokumen
    tfidf_matrix = []
    for doc_tokens in documents_tokens:
        tf = calculate_tf(doc_tokens)
        tfidf_doc = {}
        for word in tf:
            if word in idf_values:
                tfidf_doc[word] = tf[word] * idf_values[word]
        tfidf_matrix.append(tfidf_doc)

    logger.info(
        f"TF-IDF selesai. Vocabulary: {len(vocabulary)} kata, "
        f"Dokumen: {len(tfidf_matrix)}"
    )

    return {
        'vocabulary': vocabulary,
        'idf_values': idf_values,
        'tfidf_matrix': tfidf_matrix,
        'labels': labels
    }


def get_tfidf_vector(
    document_tokens: List[str],
    vocabulary: List[str],
    idf_values: Dict[str, float]
) -> Dict[str, float]:
    """
    Menghitung vektor TF-IDF untuk satu dokumen baru.

    Digunakan untuk menghitung representasi TF-IDF dokumen baru
    berdasarkan vocabulary dan IDF values yang sudah ada dari
    data training.

    Args:
        document_tokens: List berisi token kata-kata dari dokumen.
        vocabulary: List berisi seluruh kata dalam vocabulary.
        idf_values: Dictionary nilai IDF dari data training.

    Returns:
        Dictionary {kata: nilai_tfidf} untuk kata-kata yang ada
        di vocabulary.
    """
    tf = calculate_tf(document_tokens)
    tfidf_vector = {}

    for word in vocabulary:
        if word in tf and word in idf_values:
            tfidf_vector[word] = tf[word] * idf_values[word]
        else:
            tfidf_vector[word] = 0.0

    return tfidf_vector


def build_class_tfidf(tfidf_result: Dict) -> Dict[str, Dict[str, float]]:
    """
    Membangun representasi TF-IDF rata-rata per kelas sentimen.

    Menghitung rata-rata nilai TF-IDF untuk setiap kata di setiap
    kelas sentimen. Berguna untuk analisis kata-kata yang paling
    relevan dengan masing-masing kelas.

    Args:
        tfidf_result: Dictionary hasil dari calculate_tfidf() yang
                      berisi keys: tfidf_matrix, labels, vocabulary.

    Returns:
        Dictionary {kelas: {kata: rata_rata_tfidf}} untuk setiap kelas.
        Contoh: {'positif': {'bagus': 0.15, 'baik': 0.12, ...}, ...}
    """
    tfidf_matrix = tfidf_result['tfidf_matrix']
    labels = tfidf_result['labels']
    vocabulary = tfidf_result['vocabulary']

    if not tfidf_matrix or not labels:
        return {}

    # Kelompokkan dokumen berdasarkan kelas
    class_docs: Dict[str, List[Dict[str, float]]] = {}
    for i, label in enumerate(labels):
        if label not in class_docs:
            class_docs[label] = []
        class_docs[label].append(tfidf_matrix[i])

    # Hitung rata-rata TF-IDF per kelas
    class_tfidf: Dict[str, Dict[str, float]] = {}

    for label, docs in class_docs.items():
        word_sums: Dict[str, float] = {}
        num_docs = len(docs)

        for doc in docs:
            for word, value in doc.items():
                word_sums[word] = word_sums.get(word, 0.0) + value

        # Hitung rata-rata
        class_tfidf[label] = {
            word: total / num_docs
            for word, total in word_sums.items()
        }

    logger.info(
        f"Class TF-IDF dibangun untuk {len(class_tfidf)} kelas: "
        f"{list(class_tfidf.keys())}"
    )

    return class_tfidf
