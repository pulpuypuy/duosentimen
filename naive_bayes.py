"""
naive_bayes.py - Modul Multinomial Naive Bayes Classifier

Modul ini menyediakan implementasi manual algoritma Multinomial Naive Bayes
untuk klasifikasi sentimen 3 kelas (positif, negatif, netral) dengan
Laplace smoothing dan log probability untuk menghindari underflow.
"""

import math
import logging
from typing import List, Dict, Tuple
from collections import Counter

logger = logging.getLogger(__name__)


def train_naive_bayes(
    training_docs_tokens: List[List[str]],
    training_labels: List[str]
) -> Dict:
    """
    Melatih model Multinomial Naive Bayes.

    Menghitung prior probability untuk setiap kelas dan conditional
    probability untuk setiap kata di setiap kelas menggunakan
    Laplace smoothing (alpha=1).

    Rumus:
    - Prior: P(c) = N_c / N
    - Likelihood: P(w|c) = (count(w,c) + alpha) / (total_words_c + alpha * |V|)

    Semua probabilitas disimpan dalam bentuk log untuk menghindari
    numerical underflow.

    Args:
        training_docs_tokens: List berisi list token dari setiap
                              dokumen training.
        training_labels: List berisi label sentimen untuk setiap dokumen.

    Returns:
        Dictionary model dengan keys:
        - prior_probs (dict): Log prior probability {kelas: log_prob}.
        - word_probs (dict): Log conditional probability
          {kelas: {kata: log_prob}}.
        - vocabulary (list): Daftar seluruh kata unik.
        - classes (list): Daftar kelas sentimen.

    Raises:
        ValueError: Jika jumlah dokumen tidak sama dengan jumlah label,
                    atau jika data training kosong.
    """
    if len(training_docs_tokens) != len(training_labels):
        raise ValueError(
            f"Jumlah dokumen ({len(training_docs_tokens)}) tidak sama "
            f"dengan jumlah label ({len(training_labels)})"
        )

    if not training_docs_tokens:
        raise ValueError("Data training tidak boleh kosong")

    alpha = 1  # Laplace smoothing parameter
    total_docs = len(training_labels)
    classes = sorted(list(set(training_labels)))

    logger.info(
        f"Training Naive Bayes: {total_docs} dokumen, "
        f"{len(classes)} kelas: {classes}"
    )

    # Bangun vocabulary dari seluruh dokumen training
    vocabulary = sorted(list(set(
        word for doc in training_docs_tokens for word in doc
    )))
    vocab_size = len(vocabulary)

    logger.info(f"Vocabulary size: {vocab_size}")

    # Hitung prior probability per kelas
    label_counts = Counter(training_labels)
    prior_probs = {
        cls: math.log(label_counts[cls] / total_docs)
        for cls in classes
    }

    # Hitung conditional probability per kata per kelas
    word_probs: Dict[str, Dict[str, float]] = {}

    for cls in classes:
        # Kumpulkan semua kata dari dokumen kelas ini
        class_words: List[str] = []
        for i, label in enumerate(training_labels):
            if label == cls:
                class_words.extend(training_docs_tokens[i])

        # Hitung frekuensi setiap kata di kelas ini
        word_counts = Counter(class_words)
        total_words_in_class = len(class_words)

        # Hitung log conditional probability dengan Laplace smoothing
        word_probs[cls] = {}
        for word in vocabulary:
            count = word_counts.get(word, 0)
            prob = (count + alpha) / (total_words_in_class + alpha * vocab_size)
            word_probs[cls][word] = math.log(prob)

    logger.info("Training Naive Bayes selesai")

    return {
        'prior_probs': prior_probs,
        'word_probs': word_probs,
        'vocabulary': vocabulary,
        'classes': classes
    }


def predict_single(document_tokens: List[str], model: Dict) -> str:
    """
    Memprediksi label sentimen untuk satu dokumen.

    Menghitung log posterior probability untuk setiap kelas dan
    mengembalikan kelas dengan probability tertinggi.

    Rumus: log P(c|d) = log P(c) + Σ log P(w|c)

    Kata yang tidak ada di vocabulary diabaikan (unknown word handling).

    Args:
        document_tokens: List berisi token kata-kata dari dokumen.
        model: Dictionary model hasil dari train_naive_bayes().

    Returns:
        String label sentimen prediksi ('positif', 'negatif', atau 'netral').
    """
    prior_probs = model['prior_probs']
    word_probs = model['word_probs']
    vocabulary = set(model['vocabulary'])
    classes = model['classes']
    alpha = 1
    vocab_size = len(model['vocabulary'])

    best_class = None
    best_score = float('-inf')

    for cls in classes:
        # Mulai dengan log prior
        score = prior_probs[cls]

        # Tambahkan log likelihood setiap kata
        for word in document_tokens:
            if word in vocabulary:
                score += word_probs[cls][word]
            else:
                # Kata tidak dikenal (unknown word):
                # Gunakan Laplace smoothing saja
                # P(unknown|c) = alpha / (total_words_c + alpha * (V+1))
                # Karena kita tidak menyimpan total_words_c secara eksplisit,
                # kita bisa melewati kata yang tidak dikenal
                pass

        if score > best_score:
            best_score = score
            best_class = cls

    return best_class


def predict_batch(
    documents_tokens: List[List[str]],
    model: Dict
) -> List[str]:
    """
    Memprediksi label sentimen untuk batch dokumen.

    Args:
        documents_tokens: List berisi list token dari setiap dokumen.
        model: Dictionary model hasil dari train_naive_bayes().

    Returns:
        List berisi label sentimen prediksi untuk setiap dokumen.
    """
    predictions = []

    for i, doc_tokens in enumerate(documents_tokens):
        prediction = predict_single(doc_tokens, model)
        predictions.append(prediction)

        if (i + 1) % 500 == 0:
            logger.info(f"Prediksi: {i + 1}/{len(documents_tokens)}")

    logger.info(f"Prediksi batch selesai: {len(predictions)} dokumen")
    return predictions


def evaluate_model(
    test_docs_tokens: List[List[str]],
    test_labels: List[str],
    model: Dict
) -> Dict:
    """
    Mengevaluasi performa model pada data testing.

    Menghitung metrik evaluasi komprehensif termasuk accuracy,
    precision, recall, dan F1-score per kelas serta macro average.

    Args:
        test_docs_tokens: List berisi list token dari setiap dokumen test.
        test_labels: List berisi label sentimen asli (ground truth).
        model: Dictionary model hasil dari train_naive_bayes().

    Returns:
        Dictionary dengan keys:
        - accuracy (float): Akurasi keseluruhan (0-1).
        - precision (dict): Precision per kelas {kelas: nilai}.
        - recall (dict): Recall per kelas {kelas: nilai}.
        - f1 (dict): F1-score per kelas {kelas: nilai}.
        - macro_precision (float): Rata-rata precision semua kelas.
        - macro_recall (float): Rata-rata recall semua kelas.
        - macro_f1 (float): Rata-rata F1-score semua kelas.
        - confusion_matrix (dict): Confusion matrix
          {label_asli: {label_prediksi: count}}.
        - details (list): List detail per dokumen
          [{ulasan, label_asli, label_prediksi, benar}, ...].

    Raises:
        ValueError: Jika jumlah dokumen test tidak sama dengan jumlah label.
    """
    if len(test_docs_tokens) != len(test_labels):
        raise ValueError(
            f"Jumlah dokumen test ({len(test_docs_tokens)}) tidak sama "
            f"dengan jumlah label ({len(test_labels)})"
        )

    classes = model['classes']
    predictions = predict_batch(test_docs_tokens, model)

    # Hitung detail per dokumen
    details = []
    correct = 0
    for i in range(len(test_labels)):
        is_correct = 1 if predictions[i] == test_labels[i] else 0
        correct += is_correct
        details.append({
            'ulasan': ' '.join(test_docs_tokens[i]),
            'label_asli': test_labels[i],
            'label_prediksi': predictions[i],
            'benar': is_correct
        })

    # Akurasi
    total = len(test_labels)
    accuracy = correct / total if total > 0 else 0.0

    # Confusion Matrix
    confusion_matrix: Dict[str, Dict[str, int]] = {}
    for cls in classes:
        confusion_matrix[cls] = {c: 0 for c in classes}

    for actual, predicted in zip(test_labels, predictions):
        if actual in confusion_matrix and predicted in confusion_matrix[actual]:
            confusion_matrix[actual][predicted] += 1

    # Precision, Recall, F1 per kelas
    precision: Dict[str, float] = {}
    recall: Dict[str, float] = {}
    f1: Dict[str, float] = {}

    for cls in classes:
        # True Positive: prediksi benar untuk kelas ini
        tp = confusion_matrix[cls][cls]

        # False Positive: prediksi kelas ini tapi salah
        fp = sum(
            confusion_matrix[other_cls][cls]
            for other_cls in classes
            if other_cls != cls
        )

        # False Negative: seharusnya kelas ini tapi prediksi lain
        fn = sum(
            confusion_matrix[cls][other_cls]
            for other_cls in classes
            if other_cls != cls
        )

        # Precision = TP / (TP + FP)
        precision[cls] = tp / (tp + fp) if (tp + fp) > 0 else 0.0

        # Recall = TP / (TP + FN)
        recall[cls] = tp / (tp + fn) if (tp + fn) > 0 else 0.0

        # F1 = 2 * Precision * Recall / (Precision + Recall)
        if (precision[cls] + recall[cls]) > 0:
            f1[cls] = (
                2 * precision[cls] * recall[cls]
                / (precision[cls] + recall[cls])
            )
        else:
            f1[cls] = 0.0

    # Macro averages
    num_classes = len(classes)
    macro_precision = sum(precision.values()) / num_classes if num_classes > 0 else 0.0
    macro_recall = sum(recall.values()) / num_classes if num_classes > 0 else 0.0
    macro_f1 = sum(f1.values()) / num_classes if num_classes > 0 else 0.0

    logger.info(
        f"Evaluasi selesai: Accuracy={accuracy:.4f}, "
        f"Macro F1={macro_f1:.4f}"
    )

    return {
        'accuracy': accuracy,
        'precision': precision,
        'recall': recall,
        'f1': f1,
        'macro_precision': macro_precision,
        'macro_recall': macro_recall,
        'macro_f1': macro_f1,
        'confusion_matrix': confusion_matrix,
        'details': details
    }
