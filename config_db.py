"""
config_db.py - Konfigurasi Database dan Aplikasi DuoSentimen

Modul ini memuat konfigurasi koneksi database MySQL dan pengaturan
aplikasi Flask dari environment variables menggunakan python-dotenv.
"""

import os
from os.path import join, dirname
from dotenv import load_dotenv

# Load environment variables dari file .env
dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

# Konfigurasi Database MySQL
database_username = os.environ.get('DB_USERNAME', 'root')
database_password = os.environ.get('DB_PASSWORD', '')
database_ip = os.environ.get('DB_HOST', 'localhost')
database_name = os.environ.get('DB_NAME', 'duosentimen_db')

# Konfigurasi Aplikasi Flask
secret_key = os.environ.get('SECRET_KEY', 'duosentimen-secret-2026')
env = os.environ.get('FLASK_ENV', 'development')

# Direktori assets untuk menyimpan file statis
assets_dir = os.path.join(os.path.dirname(__file__), 'assets')
