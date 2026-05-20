-- =============================================
-- DuoSentimen Database Schema
-- Analisis Sentimen Ulasan Duolingo (Google Play Store)
-- By Ahmad Saifulla
-- =============================================

CREATE DATABASE IF NOT EXISTS duosentimen_db
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

USE duosentimen_db;

-- =============================================
-- Tabel: pengguna (User Authentication)
-- =============================================
CREATE TABLE IF NOT EXISTS pengguna (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(100) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    nama_lengkap VARCHAR(200) DEFAULT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Default admin user (password: admin123 - bcrypt hashed)
-- Password hash akan di-generate otomatis saat pertama kali menjalankan aplikasi
-- INSERT INTO pengguna (username, password, nama_lengkap) VALUES
-- ('admin', '<hash_akan_digenerate>', 'Administrator');

-- =============================================
-- Tabel: dataset_scraping (Data Ulasan Hasil Scraping)
-- =============================================
CREATE TABLE IF NOT EXISTS dataset_scraping (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nama_user VARCHAR(200) DEFAULT NULL,
    rating INT DEFAULT NULL,
    ulasan TEXT,
    tanggal DATETIME DEFAULT NULL,
    label VARCHAR(20) DEFAULT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_label (label),
    INDEX idx_rating (rating),
    INDEX idx_tanggal (tanggal)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =============================================
-- Tabel: dataset_preprocessed (Data Setelah Preprocessing)
-- =============================================
CREATE TABLE IF NOT EXISTS dataset_preprocessed (
    id INT AUTO_INCREMENT PRIMARY KEY,
    id_scraping INT DEFAULT NULL,
    ulasan_asli TEXT,
    ulasan_bersih TEXT,
    label VARCHAR(20) DEFAULT NULL,
    INDEX idx_label (label),
    FOREIGN KEY (id_scraping) REFERENCES dataset_scraping(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =============================================
-- Tabel: dataset_training (Data Training 80%)
-- =============================================
CREATE TABLE IF NOT EXISTS dataset_training (
    id INT AUTO_INCREMENT PRIMARY KEY,
    ulasan TEXT,
    label VARCHAR(20) DEFAULT NULL,
    INDEX idx_label (label)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =============================================
-- Tabel: dataset_testing (Data Testing 20%)
-- =============================================
CREATE TABLE IF NOT EXISTS dataset_testing (
    id INT AUTO_INCREMENT PRIMARY KEY,
    ulasan TEXT,
    label VARCHAR(20) DEFAULT NULL,
    INDEX idx_label (label)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =============================================
-- Tabel: hasil_uji (Hasil Pengujian Model)
-- =============================================
CREATE TABLE IF NOT EXISTS hasil_uji (
    id INT AUTO_INCREMENT PRIMARY KEY,
    ulasan TEXT,
    label_asli VARCHAR(20) DEFAULT NULL,
    label_prediksi VARCHAR(20) DEFAULT NULL,
    benar TINYINT(1) DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_benar (benar),
    INDEX idx_label_asli (label_asli),
    INDEX idx_label_prediksi (label_prediksi)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =============================================
-- Tabel: model_config (Konfigurasi Model Tersimpan)
-- =============================================
CREATE TABLE IF NOT EXISTS model_config (
    id INT AUTO_INCREMENT PRIMARY KEY,
    config_key VARCHAR(100) NOT NULL UNIQUE,
    config_value LONGTEXT,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
