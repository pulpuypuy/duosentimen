"""
nltk_config.py - Konfigurasi dan Download Data NLTK

Modul ini menangani download otomatis data NLTK yang diperlukan
untuk preprocessing teks. Data yang di-download meliputi tokenizer
(punkt) dan stopwords.

Data akan di-download secara otomatis saat modul pertama kali diimpor.
"""

import logging
import nltk

logger = logging.getLogger(__name__)


def setup_nltk() -> None:
    """
    Mendownload data NLTK yang diperlukan.

    Data yang di-download:
    - punkt: Tokenizer untuk memecah kalimat menjadi kata.
    - punkt_tab: Data tabulasi untuk punkt tokenizer.
    - stopwords: Daftar stopwords untuk berbagai bahasa.

    Download dilakukan secara quiet (tanpa output verbose).
    Jika data sudah ada, download akan di-skip secara otomatis.

    Returns:
        None
    """
    required_data = [
        'punkt',
        'punkt_tab',
        'stopwords'
    ]

    for data_name in required_data:
        try:
            nltk.download(data_name, quiet=True)
            logger.info(f"NLTK data '{data_name}' berhasil dimuat")
        except Exception as e:
            logger.error(
                f"Error saat mendownload NLTK data '{data_name}': {str(e)}"
            )


# Auto-download saat modul diimpor
setup_nltk()
