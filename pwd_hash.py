"""
pwd_hash.py - Modul Hashing Password

Modul ini menyediakan fungsi-fungsi untuk hashing dan validasi password
menggunakan bcrypt melalui Flask-Bcrypt. Bcrypt secara otomatis menangani
salt generation dan cost factor untuk keamanan password.
"""

import logging
from flask_bcrypt import Bcrypt

logger = logging.getLogger(__name__)

# Instance Bcrypt global
bcrypt = Bcrypt()


def init_bcrypt(app) -> None:
    """
    Menginisialisasi Flask-Bcrypt dengan instance aplikasi Flask.

    Harus dipanggil saat inisialisasi aplikasi Flask agar bcrypt
    dapat menggunakan konfigurasi aplikasi.

    Args:
        app: Instance aplikasi Flask.

    Returns:
        None
    """
    bcrypt.init_app(app)
    logger.info("Flask-Bcrypt berhasil diinisialisasi")


def hash_password(password: str) -> str:
    """
    Meng-hash password menggunakan bcrypt.

    Bcrypt secara otomatis menghasilkan salt unik untuk setiap
    password dan menggunakan cost factor default (12 rounds).

    Args:
        password: Password plaintext yang akan di-hash.

    Returns:
        String hash password dalam format UTF-8.

    Raises:
        ValueError: Jika password kosong atau None.
    """
    if not password:
        raise ValueError("Password tidak boleh kosong")

    try:
        hashed = bcrypt.generate_password_hash(password).decode('utf-8')
        logger.debug("Password berhasil di-hash")
        return hashed
    except Exception as e:
        logger.error(f"Error saat hashing password: {str(e)}")
        raise


def validate_pass(password: str, hashed: str) -> str:
    """
    Memvalidasi password plaintext terhadap hash yang tersimpan.

    Args:
        password: Password plaintext yang akan diverifikasi.
        hashed: String hash bcrypt yang tersimpan di database.

    Returns:
        'sukses' jika password cocok dengan hash.
        'gagal' jika password tidak cocok atau terjadi error.
    """
    if not password or not hashed:
        logger.warning("Password atau hash kosong saat validasi")
        return 'gagal'

    try:
        is_valid = bcrypt.check_password_hash(hashed, password)
        if is_valid:
            logger.debug("Validasi password berhasil")
            return 'sukses'
        else:
            logger.debug("Validasi password gagal: password tidak cocok")
            return 'gagal'
    except Exception as e:
        logger.error(f"Error saat validasi password: {str(e)}")
        return 'gagal'
