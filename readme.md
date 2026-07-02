# DuoSentimen 🦉

### Analisis Sentimen Ulasan Aplikasi Duolingo pada Google Play Store Menggunakan Metode Naive Bayes

**By Ahmad Saifulla**

---

## 📋 Deskripsi

DuoSentimen adalah aplikasi web berbasis Flask untuk menganalisis sentimen ulasan pengguna aplikasi Duolingo di Google Play Store. Sistem ini menggunakan metode **Naive Bayes** dengan pembobotan **TF-IDF** untuk mengklasifikasikan ulasan ke dalam 3 kategori sentimen: **Positif**, **Negatif**, dan **Netral**.

## ✨ Fitur Utama

- 🔍 **Scraping Google Play Store** - Otomatis mengambil ulasan dari Google Play Store
- 📝 **Text Preprocessing** - Pipeline lengkap untuk Bahasa Indonesia (case folding, cleansing, normalisasi, tokenisasi, stopword removal, stemming)
- 📊 **TF-IDF Feature Extraction** - Pembobotan kata menggunakan TF-IDF
- 🤖 **Klasifikasi Naive Bayes** - Klasifikasi sentimen otomatis 3 kelas
- 📈 **Visualisasi Interaktif** - Pie chart, bar chart, word cloud, confusion matrix
- 🖨️ **Cetak Hasil** - Setiap hasil analisis dapat dicetak/di-print
- 🔐 **Autentikasi** - Sistem login dan registrasi pengguna
- 📱 **Responsive Design** - Tampilan modern dengan sidebar navigasi

## 🛠️ Tech Stack

| Komponen | Teknologi |
|----------|-----------|
| Backend | Python 3, Flask |
| Database | MySQL |
| NLP | Sastrawi |
| ML | Naive Bayes (custom), TF-IDF |
| Scraping | google-play-scraper |
| Visualisasi | Plotly, Matplotlib, WordCloud |
| Frontend | HTML5, CSS3, JavaScript, Bootstrap 5 |
| Auth | Flask-Bcrypt, Flask-WTF (CSRF) |

## 📁 Struktur Proyek

```
duosentimen-playstore/
├── assets/                     # Folder upload dataset
├── database/
│   └── duosentimen_db.sql      # Skema database MySQL
├── static/
│   ├── css/style.css           # Custom CSS
│   └── js/script.js            # Custom JavaScript
├── templates/                  # HTML Templates (Jinja2)
├── config_db.py                # Konfigurasi database
├── form.py                     # Flask-WTF forms
├── genplot.py                  # Visualisasi (chart, wordcloud)
├── main_app.py                 # Aplikasi utama Flask
├── naive_bayes.py              # Algoritma Naive Bayes
├── normalisasi.json            # Kamus normalisasi kata slang
├── preprocesing_text.py        # Text preprocessing pipeline
├── pwd_hash.py                 # Password hashing
├── requirements.txt            # Python dependencies
├── scraper.py                  # Scraping Google Play Store
├── stopwords.txt               # Daftar stop words Indonesia
└── tf_idf.py                   # Pembobotan TF-IDF
```

## 🚀 Instalasi & Setup

### 1. Buat Virtual Environment
```bash
python -m venv env
```

### 2. Aktifkan Environment
**Windows:**
```bash
env\Scripts\activate
```
**Linux/Mac:**
```bash
source env/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Setup Database
- Pastikan MySQL sudah berjalan
- Import skema database:
```bash
mysql -u root -p < database/duosentimen_db.sql
```

### 5. Konfigurasi Environment
- Salin `.envcontoh` menjadi `.env`
- Sesuaikan konfigurasi database:
```
DB_USERNAME=root
DB_PASSWORD=password_anda
DB_HOST=localhost
DB_NAME=duosentimen_db
SECRET_KEY=ganti-dengan-key-rahasia
```

### 6. Jalankan Aplikasi
```bash
python main_app.py
```
Buka browser: `http://localhost:5000`

## 🔑 Login Default
- **Username:** admin
- **Password:** admin123

## 📖 Cara Penggunaan

1. **Login** → Masuk dengan akun admin atau daftar akun baru
2. **Scraping** → Buka menu Scraping, atur jumlah ulasan dan tahun, klik "Mulai Scraping"
3. **Dataset** → Lihat data hasil scraping, klik "Jalankan Preprocessing"
4. **Training** → Bagi data 80:20, lalu klik "Jalankan Training"
5. **Hasil Uji** → Lihat akurasi, confusion matrix, word cloud, dan detail hasil
6. **Dashboard** → Gunakan input manual untuk mengklasifikasikan teks baru

## 📄 Lisensi

MIT License - © 2026 Ahmad Saifulla

## 📞 Kontak

- **Author:** Ahmad Saifulla
- **Project:** DuoSentimen
