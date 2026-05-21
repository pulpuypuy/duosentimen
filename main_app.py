"""
====================================================
DuoSentimen - Main Flask Application
Analisis Sentimen Ulasan Duolingo (Google Play Store)
Menggunakan Metode Naive Bayes dengan TF-IDF
By Ahmad Saifulla
====================================================
"""

from flask import Flask, request, render_template, session, redirect, url_for, flash, jsonify
import pymysql
from pymysql.cursors import DictCursor
from flask_wtf.csrf import CSRFProtect, CSRFError
from werkzeug.utils import secure_filename
import os
import json
import random

from config_db import *
from pwd_hash import init_bcrypt, hash_password, validate_pass

import numpy as np
from datetime import datetime, timedelta

from form import LoginUserForm, RegisterUserForm, UploadDatasetForm, ManualSentimenForm
from preprocesing_text import preprocess_text
from tf_idf import calculate_tfidf, get_tfidf_vector, calculate_tf
from naive_bayes import train_naive_bayes, predict_single, evaluate_model
from genplot import (
    generate_pie_chart, generate_wordcloud_image,
    generate_confusion_matrix_chart, generate_accuracy_chart,
    generate_comparison_chart, generate_bar_chart
)

# ====================================================
# Inisialisasi Aplikasi Flask
# ====================================================
app = Flask(__name__)

# Konfigurasi dari config_db.py
app.config['SECRET_KEY'] = secret_key
app.config['FLASK_ENV'] = env
app.config['UPLOAD_FOLDER'] = assets_dir

# Konfigurasi Session
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=3)
app.config.update(
    SESSION_COOKIE_SECURE=False,
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE='Lax',
)

# File upload extensions
app.config['UPLOAD_EXTENSIONS'] = ['.xlsx', '.csv']

# Inisialisasi extensions
csrf = CSRFProtect(app)
csrf.init_app(app)
init_bcrypt(app)

# Buat folder assets jika belum ada
os.makedirs(assets_dir, exist_ok=True)

# Variabel global untuk model yang sudah di-training
trained_model = None


# ====================================================
# Helper Functions
# ====================================================
def get_db_connection():
    """Mendapatkan koneksi database MySQL menggunakan PyMySQL langsung"""
    conn = pymysql.connect(
        host=database_ip,
        user=database_username,
        password=database_password,
        database=database_name,
        charset='utf8mb4',
        cursorclass=DictCursor
    )
    return conn

def get_stats():
    """Mendapatkan statistik dataset"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) as total FROM dataset_scraping")
        total = cursor.fetchone()['total']
        
        cursor.execute("SELECT COUNT(*) as count FROM dataset_scraping WHERE label='positif'")
        positif = cursor.fetchone()['count']
        
        cursor.execute("SELECT COUNT(*) as count FROM dataset_scraping WHERE label='negatif'")
        negatif = cursor.fetchone()['count']
        
        cursor.execute("SELECT COUNT(*) as count FROM dataset_scraping WHERE label='netral'")
        netral = cursor.fetchone()['count']
        
        conn.close()
        return {'total': total, 'positif': positif, 'negatif': negatif, 'netral': netral}
    except Exception as e:
        print(f"Error getting stats: {e}")
        return {'total': 0, 'positif': 0, 'negatif': 0, 'netral': 0}

def ensure_admin_exists():
    """Memastikan user admin default ada di database"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM pengguna WHERE username = %s", ('admin',))
        if not cursor.fetchone():
            hashed = hash_password('admin123')
            cursor.execute(
                "INSERT INTO pengguna (username, password, nama_lengkap) VALUES (%s, %s, %s)",
                ('admin', hashed, 'Administrator')
            )
            conn.commit()
            print("[INFO] Default admin user created (username: admin, password: admin123)")
        conn.close()
    except Exception as e:
        print(f"[WARNING] Could not create admin user: {e}")


# ====================================================
# Error Handlers
# ====================================================
@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    return render_template('500.html'), 500

@app.errorhandler(CSRFError)
def handle_csrf_error(error):
    flash('Sesi telah kedaluwarsa. Silakan coba lagi.', 'danger')
    return render_template('500.html'), 400


# ====================================================
# Route: Index / Root
# ====================================================
@app.route('/')
def index():
    if 'loggedin' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))


# ====================================================
# Route: Login
# ====================================================
@app.route('/dashboard/login', methods=['GET', 'POST'])
def login():
    if 'loggedin' in session:
        return redirect(url_for('dashboard'))
    
    msg = ''
    form = LoginUserForm()
    
    if form.validate_on_submit():
        _username = form.clean_username(form.username).data
        _password = form.password.data
        
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id, username, password, nama_lengkap FROM pengguna WHERE username = %s",
                (_username,)
            )
            data = cursor.fetchone()
            conn.close()
            
            if data:
                if validate_pass(str(_password), str(data.get('password'))) == 'sukses':
                    session['loggedin'] = True
                    session['id'] = data['id']
                    session['username'] = data['username']
                    session['nama_lengkap'] = data.get('nama_lengkap', data['username'])
                    session.permanent = True
                    flash(f'Selamat datang, {data["username"]}!', 'success')
                    return redirect(url_for('dashboard'))
                else:
                    msg = 'Password salah!'
            else:
                msg = 'Username tidak ditemukan!'
        except Exception as e:
            msg = f'Terjadi kesalahan: {str(e)}'
    
    return render_template('index.html', msg=msg, form=form)


# ====================================================
# Route: Register
# ====================================================
@app.route('/dashboard/register', methods=['GET', 'POST'])
def register():
    if 'loggedin' in session:
        return redirect(url_for('dashboard'))
    
    msg = ''
    form = RegisterUserForm()
    
    if form.validate_on_submit():
        _nama = form.nama_lengkap.data.strip()
        _username = form.clean_username(form.username).data
        _password = form.password.data
        
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            # Cek apakah username sudah ada
            cursor.execute("SELECT id FROM pengguna WHERE username = %s", (_username,))
            if cursor.fetchone():
                msg = 'Username sudah digunakan!'
                conn.close()
                return render_template('register.html', msg=msg, form=form)
            
            # Hash password dan simpan
            hashed = hash_password(_password)
            cursor.execute(
                "INSERT INTO pengguna (username, password, nama_lengkap) VALUES (%s, %s, %s)",
                (_username, hashed, _nama)
            )
            conn.commit()
            conn.close()
            
            flash('Registrasi berhasil! Silakan login.', 'success')
            return redirect(url_for('login'))
        except Exception as e:
            msg = f'Terjadi kesalahan: {str(e)}'
    
    return render_template('register.html', msg=msg, form=form)


# ====================================================
# Route: Logout
# ====================================================
@app.route('/dashboard/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('username', None)
    session.pop('nama_lengkap', None)
    session.clear()
    flash('Anda telah logout.', 'info')
    return redirect(url_for('login'))


# ====================================================
# Route: Dashboard
# ====================================================
@app.route('/dashboard')
def dashboard():
    if 'loggedin' not in session:
        return redirect(url_for('login'))
    
    stats = get_stats()
    form = ManualSentimenForm()
    
    # Generate pie chart jika ada data
    pie_chart = None
    if stats['total'] > 0:
        label_counts = {
            'positif': stats['positif'],
            'negatif': stats['negatif'],
            'netral': stats['netral']
        }
        pie_chart = generate_pie_chart(label_counts)
    
    return render_template('dashboard.html',
                         username=session['username'],
                         stats=stats,
                         form=form,
                         pie_chart=pie_chart)


# ====================================================
# Route: Analisis Sentimen Manual
# ====================================================
@app.route('/sentimen', methods=['POST'])
def sentimen_manual():
    if 'loggedin' not in session:
        return redirect(url_for('login'))
    
    global trained_model
    form = ManualSentimenForm()
    stats = get_stats()
    
    input_text = ''
    hasil_sentimen = None
    pie_chart = None
    
    if stats['total'] > 0:
        label_counts = {
            'positif': stats['positif'],
            'negatif': stats['negatif'],
            'netral': stats['netral']
        }
        pie_chart = generate_pie_chart(label_counts)
    
    if form.validate_on_submit():
        input_text = form.input_text.data
        
        # Cek apakah model sudah di-training
        if trained_model is None:
            # Coba load model dari database
            try:
                conn = get_db_connection()
                cursor = conn.cursor()
                cursor.execute("SELECT config_value FROM model_config WHERE config_key = 'trained_model'")
                row = cursor.fetchone()
                conn.close()
                
                if row:
                    trained_model = json.loads(row['config_value'])
            except Exception as e:
                print(f"Error loading model: {e}")
        
        if trained_model is not None:
            # Preprocessing input
            cleaned_text = preprocess_text(input_text)
            tokens = cleaned_text.split()
            
            # Prediksi
            hasil_sentimen = predict_single(tokens, trained_model)
        else:
            flash('Model belum di-training! Silakan lakukan training terlebih dahulu.', 'warning')
    
    return render_template('dashboard.html',
                         username=session['username'],
                         stats=stats,
                         form=form,
                         input_text=input_text,
                         hasil_sentimen=hasil_sentimen,
                         pie_chart=pie_chart)




# ====================================================
# Route: Dataset
# ====================================================
@app.route('/dataset')
def dataset():
    if 'loggedin' not in session:
        return redirect(url_for('login'))
    
    page = request.args.get('page', 1, type=int)
    per_page = 25
    offset = (page - 1) * per_page
    
    data = []
    total_pages = 1
    preprocessed = False
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Cek apakah data sudah dipreprocessing
        cursor.execute("SELECT COUNT(*) as count FROM dataset_preprocessed")
        preprocessed_count = cursor.fetchone()['count']
        
        if preprocessed_count > 0:
            preprocessed = True
            # Ambil data preprocessed
            cursor.execute("SELECT COUNT(*) as total FROM dataset_preprocessed")
            total = cursor.fetchone()['total']
            total_pages = max(1, (total + per_page - 1) // per_page)
            
            cursor.execute(
                """SELECT dp.id, dp.ulasan_asli, dp.ulasan_bersih, dp.label 
                   FROM dataset_preprocessed dp 
                   ORDER BY dp.id ASC 
                   LIMIT %s OFFSET %s""",
                (per_page, offset)
            )
            data = cursor.fetchall()
        else:
            # Ambil data scraping
            cursor.execute("SELECT COUNT(*) as total FROM dataset_scraping")
            total = cursor.fetchone()['total']
            total_pages = max(1, (total + per_page - 1) // per_page)
            
            cursor.execute(
                """SELECT id, ulasan as ulasan_asli, '' as ulasan_bersih, label 
                   FROM dataset_scraping 
                   ORDER BY id ASC 
                   LIMIT %s OFFSET %s""",
                (per_page, offset)
            )
            data = cursor.fetchall()
        
        conn.close()
    except Exception as e:
        flash(f'Error mengambil dataset: {str(e)}', 'danger')
    
    form = UploadDatasetForm()
    
    return render_template('dataset.html',
                         username=session['username'],
                         data=data,
                         page=page,
                         total_pages=total_pages,
                         preprocessed=preprocessed,
                         form=form)


# ====================================================
# Helper: Auto-label berdasarkan rating
# ====================================================
def auto_label(rating):
    """Auto-label sentimen berdasarkan rating bintang"""
    try:
        rating = int(float(rating))
    except (ValueError, TypeError):
        return 'netral'
    if rating <= 2:
        return 'negatif'
    elif rating == 3:
        return 'netral'
    else:
        return 'positif'


# ====================================================
# Route: Upload Dataset CSV
# ====================================================
@app.route('/dataset/upload', methods=['POST'])
def upload_dataset():
    if 'loggedin' not in session:
        return redirect(url_for('login'))
    
    form = UploadDatasetForm()
    
    if form.validate_on_submit():
        file = form.file.data
        if file:
            filename = secure_filename(file.filename)
            ext = os.path.splitext(filename)[1].lower()
            
            if ext not in app.config['UPLOAD_EXTENSIONS']:
                flash('Format file tidak didukung! Gunakan file .csv', 'danger')
                return redirect(url_for('dataset'))
            
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            
            try:
                import pandas as pd
                
                if ext == '.xlsx':
                    df = pd.read_excel(filepath)
                else:
                    df = pd.read_csv(filepath)
                
                # Mapping kolom dari format CSV user
                # Format: Review ID, Username, Rating, Review Text, Date
                column_mapping = {
                    'Review ID': 'review_id',
                    'Username': 'nama_user',
                    'Rating': 'rating',
                    'Review Text': 'ulasan',
                    'Date': 'tanggal',
                    # Fallback untuk format kolom alternatif
                    'review_id': 'review_id',
                    'username': 'nama_user',
                    'nama_user': 'nama_user',
                    'rating': 'rating',
                    'ulasan': 'ulasan',
                    'review_text': 'ulasan',
                    'content': 'ulasan',
                    'date': 'tanggal',
                    'tanggal': 'tanggal',
                }
                
                # Rename kolom sesuai mapping
                df = df.rename(columns={k: v for k, v in column_mapping.items() if k in df.columns})
                
                # Validasi kolom wajib: minimal harus ada 'ulasan' dan 'rating'
                if 'ulasan' not in df.columns:
                    flash('File CSV harus memiliki kolom "Review Text" atau "ulasan"!', 'danger')
                    return redirect(url_for('dataset'))
                
                if 'rating' not in df.columns:
                    flash('File CSV harus memiliki kolom "Rating" atau "rating"!', 'danger')
                    return redirect(url_for('dataset'))
                
                # Bersihkan data kosong
                df = df.dropna(subset=['ulasan'])
                df['ulasan'] = df['ulasan'].astype(str)
                
                # Auto-label berdasarkan rating
                df['label'] = df['rating'].apply(auto_label)
                
                # Hapus data lama jika user memilih replace
                conn = get_db_connection()
                cursor = conn.cursor()
                
                replace_mode = request.form.get('replace_mode', 'append')
                if replace_mode == 'replace':
                    cursor.execute("DELETE FROM hasil_uji")
                    cursor.execute("DELETE FROM dataset_testing")
                    cursor.execute("DELETE FROM dataset_training")
                    cursor.execute("DELETE FROM dataset_preprocessed")
                    cursor.execute("DELETE FROM dataset_scraping")
                
                # Insert data ke database
                count = 0
                for _, row in df.iterrows():
                    nama_user = str(row.get('nama_user', 'Unknown'))
                    rating = int(float(row.get('rating', 0)))
                    ulasan = str(row['ulasan']).strip()
                    label = str(row['label'])
                    
                    # Parse tanggal
                    try:
                        tanggal = pd.to_datetime(row.get('tanggal', datetime.now()))
                    except:
                        tanggal = datetime.now()
                    
                    if ulasan and ulasan.lower() != 'nan':
                        cursor.execute(
                            """INSERT INTO dataset_scraping 
                               (nama_user, rating, ulasan, tanggal, label) 
                               VALUES (%s, %s, %s, %s, %s)""",
                            (nama_user, rating, ulasan, tanggal, label)
                        )
                        count += 1
                
                conn.commit()
                conn.close()
                
                # Statistik label
                pos = len(df[df['label'] == 'positif'])
                neg = len(df[df['label'] == 'negatif'])
                net = len(df[df['label'] == 'netral'])
                
                flash(
                    f'Berhasil upload {count} ulasan dari "{filename}"! '
                    f'(Positif: {pos}, Negatif: {neg}, Netral: {net})',
                    'success'
                )
            except Exception as e:
                flash(f'Error membaca file: {str(e)}', 'danger')
                import traceback
                traceback.print_exc()
    
    return redirect(url_for('dataset'))


# ====================================================
# Route: Jalankan Preprocessing
# ====================================================
@app.route('/preprocessing', methods=['POST'])
def run_preprocessing():
    if 'loggedin' not in session:
        return redirect(url_for('login'))
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Ambil semua data scraping
        cursor.execute("SELECT id, ulasan, label FROM dataset_scraping")
        data = cursor.fetchall()
        
        if not data:
            flash('Tidak ada data untuk dipreprocessing!', 'warning')
            return redirect(url_for('dataset'))
        
        # Hapus data preprocessed lama
        cursor.execute("DELETE FROM dataset_preprocessed")
        
        count = 0
        label_stats = {'positif': 0, 'negatif': 0, 'netral': 0}
        for item in data:
            ulasan_asli = item['ulasan']
            ulasan_bersih = preprocess_text(str(ulasan_asli))
            label = item['label']  # Menggunakan label dari rating
            
            if ulasan_bersih.strip():
                label_stats[label] = label_stats.get(label, 0) + 1
                
                cursor.execute(
                    """INSERT INTO dataset_preprocessed (id_scraping, ulasan_asli, ulasan_bersih, label) 
                       VALUES (%s, %s, %s, %s)""",
                    (item['id'], ulasan_asli, ulasan_bersih, label)
                )
                count += 1
        
        conn.commit()
        conn.close()
        
        flash(
            f'Preprocessing selesai! {count} data diproses. '
            f'(Positif: {label_stats.get("positif", 0)}, Negatif: {label_stats.get("negatif", 0)}, '
            f'Netral: {label_stats.get("netral", 0)})',
            'success'
        )
    except Exception as e:
        flash(f'Error preprocessing: {str(e)}', 'danger')
        import traceback
        traceback.print_exc()
    
    return redirect(url_for('dataset'))


# ====================================================
# Route: Split Data Training/Testing (70:30)
# ====================================================
@app.route('/split-data', methods=['POST'])
def split_data():
    if 'loggedin' not in session:
        return redirect(url_for('login'))
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Ambil data preprocessed
        cursor.execute("SELECT ulasan_bersih, label FROM dataset_preprocessed")
        data = cursor.fetchall()
        
        if not data:
            flash('Tidak ada data preprocessed! Jalankan preprocessing terlebih dahulu.', 'warning')
            return redirect(url_for('dataset'))
        
        # Shuffle data
        random.shuffle(data)
        
        # Split 70:30
        split_idx = int(len(data) * 0.7)
        training_data = data[:split_idx]
        testing_data = data[split_idx:]
        
        # Hapus data lama
        cursor.execute("DELETE FROM dataset_training")
        cursor.execute("DELETE FROM dataset_testing")
        
        # Insert training data
        for item in training_data:
            cursor.execute(
                "INSERT INTO dataset_training (ulasan, label) VALUES (%s, %s)",
                (item['ulasan_bersih'], item['label'])
            )
        
        # Insert testing data
        for item in testing_data:
            cursor.execute(
                "INSERT INTO dataset_testing (ulasan, label) VALUES (%s, %s)",
                (item['ulasan_bersih'], item['label'])
            )
        
        conn.commit()
        conn.close()
        
        flash(f'Data berhasil dibagi! Training: {len(training_data)}, Testing: {len(testing_data)}', 'success')
    except Exception as e:
        flash(f'Error splitting data: {str(e)}', 'danger')
    
    return redirect(url_for('dataset'))


# ====================================================
# Route: Training Model
# ====================================================
@app.route('/training', methods=['POST'])
def run_training():
    if 'loggedin' not in session:
        return redirect(url_for('login'))
    
    global trained_model
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Ambil data training
        cursor.execute("SELECT ulasan, label FROM dataset_training")
        training_data = cursor.fetchall()
        
        # Ambil data testing
        cursor.execute("SELECT ulasan, label FROM dataset_testing")
        testing_data = cursor.fetchall()
        
        if not training_data:
            flash('Tidak ada data training! Bagi data terlebih dahulu.', 'warning')
            conn.close()
            return redirect(url_for('dataset'))
        
        if not testing_data:
            flash('Tidak ada data testing! Bagi data terlebih dahulu.', 'warning')
            conn.close()
            return redirect(url_for('dataset'))
        
        # Prepare data
        train_docs = [item['ulasan'].split() for item in training_data]
        train_labels = [item['label'] for item in training_data]
        
        test_docs = [item['ulasan'].split() for item in testing_data]
        test_labels = [item['label'] for item in testing_data]
        
        # Training Naive Bayes
        trained_model = train_naive_bayes(train_docs, train_labels)
        
        # Evaluasi model
        eval_result = evaluate_model(test_docs, test_labels, trained_model)
        
        # Simpan hasil uji ke database
        cursor.execute("DELETE FROM hasil_uji")
        
        for detail in eval_result['details']:
            cursor.execute(
                """INSERT INTO hasil_uji (ulasan, label_asli, label_prediksi, benar) 
                   VALUES (%s, %s, %s, %s)""",
                (' '.join(detail['ulasan']) if isinstance(detail['ulasan'], list) else detail['ulasan'],
                 detail['label_asli'],
                 detail['label_prediksi'],
                 1 if detail['benar'] else 0)
            )
        
        # Simpan model ke database untuk persistence
        try:
            model_json = json.dumps(trained_model, default=str)
            cursor.execute("DELETE FROM model_config WHERE config_key = 'trained_model'")
            cursor.execute(
                "INSERT INTO model_config (config_key, config_value) VALUES (%s, %s)",
                ('trained_model', model_json)
            )
        except Exception as me:
            print(f"Warning: Could not save model to DB: {me}")
        
        # Simpan metrik
        metrics_json = json.dumps({
            'accuracy': eval_result['accuracy'],
            'macro_precision': eval_result['macro_precision'],
            'macro_recall': eval_result['macro_recall'],
            'macro_f1': eval_result['macro_f1'],
            'confusion_matrix': eval_result['confusion_matrix']
        })
        cursor.execute("DELETE FROM model_config WHERE config_key = 'metrics'")
        cursor.execute(
            "INSERT INTO model_config (config_key, config_value) VALUES (%s, %s)",
            ('metrics', metrics_json)
        )
        
        conn.commit()
        conn.close()
        
        flash(f'Training selesai! Akurasi: {eval_result["accuracy"]:.2f}%', 'success')
        return redirect(url_for('testing'))
        
    except Exception as e:
        flash(f'Error training: {str(e)}', 'danger')
        import traceback
        traceback.print_exc()
    
    return redirect(url_for('dataset'))


# ====================================================
# Route: Hasil Pengujian
# ====================================================
@app.route('/testing')
def testing():
    if 'loggedin' not in session:
        return redirect(url_for('login'))
    
    results = []
    accuracy = precision = recall = f1 = 0
    confusion_matrix_chart = None
    wc_positif = wc_negatif = wc_netral = None
    comparison_chart = None
    accuracy_chart = None
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Ambil hasil uji
        cursor.execute("SELECT * FROM hasil_uji ORDER BY id ASC")
        results = cursor.fetchall()
        
        if results:
            # Ambil metrik dari model_config
            cursor.execute("SELECT config_value FROM model_config WHERE config_key = 'metrics'")
            row = cursor.fetchone()
            
            if row:
                metrics = json.loads(row['config_value'])
                accuracy = metrics.get('accuracy', 0)
                precision = metrics.get('macro_precision', 0)
                recall = metrics.get('macro_recall', 0)
                f1 = metrics.get('macro_f1', 0)
                cm = metrics.get('confusion_matrix', {})
                
                # Generate confusion matrix chart
                labels = ['positif', 'negatif', 'netral']
                confusion_matrix_chart = generate_confusion_matrix_chart(cm, labels)
                
                # Generate accuracy chart
                accuracy_chart = generate_accuracy_chart({
                    'Accuracy': accuracy,
                    'Precision': precision,
                    'Recall': recall,
                    'F1-Score': f1
                })
            
            # Generate word clouds
            positif_texts = ' '.join([r['ulasan'] for r in results if r['label_asli'] == 'positif'])
            negatif_texts = ' '.join([r['ulasan'] for r in results if r['label_asli'] == 'negatif'])
            netral_texts = ' '.join([r['ulasan'] for r in results if r['label_asli'] == 'netral'])
            
            if positif_texts.strip():
                wc_positif = generate_wordcloud_image(positif_texts, 'Word Cloud Positif', 'Greens')
            if negatif_texts.strip():
                wc_negatif = generate_wordcloud_image(negatif_texts, 'Word Cloud Negatif', 'Reds')
            if netral_texts.strip():
                wc_netral = generate_wordcloud_image(netral_texts, 'Word Cloud Netral', 'YlOrBr')
            
            # Generate comparison chart
            label_asli_counts = {'positif': 0, 'negatif': 0, 'netral': 0}
            label_pred_counts = {'positif': 0, 'negatif': 0, 'netral': 0}
            
            for r in results:
                la = r['label_asli']
                lp = r['label_prediksi']
                if la in label_asli_counts:
                    label_asli_counts[la] += 1
                if lp in label_pred_counts:
                    label_pred_counts[lp] += 1
            
            comparison_chart = generate_comparison_chart(label_asli_counts, label_pred_counts)
        
        conn.close()
    except Exception as e:
        flash(f'Error mengambil hasil pengujian: {str(e)}', 'danger')
        import traceback
        traceback.print_exc()
    
    return render_template('hasil_uji.html',
                         username=session['username'],
                         results=results,
                         accuracy=accuracy,
                         precision=precision,
                         recall=recall,
                         f1=f1,
                         confusion_matrix_chart=confusion_matrix_chart,
                         wc_positif=wc_positif,
                         wc_negatif=wc_negatif,
                         wc_netral=wc_netral,
                         comparison_chart=comparison_chart,
                         accuracy_chart=accuracy_chart)


# ====================================================
# Route: About
# ====================================================
@app.route('/about')
def about():
    if 'loggedin' not in session:
        return redirect(url_for('login'))
    
    return render_template('about.html', username=session['username'])


# ====================================================
# Main Entry Point
# ====================================================
if __name__ == '__main__':
    # Setup NLTK data
    try:
        from nltk_config import setup_nltk
        setup_nltk()
    except Exception as e:
        print(f"[WARNING] NLTK setup failed: {e}")
    
    # Pastikan admin user ada
    ensure_admin_exists()
    
    # Jalankan Flask app
    print("=" * 50)
    print("  DuoSentimen - Sentiment Analysis Dashboard")
    print("  By Ahmad Saifulla")
    print("=" * 50)
    print(f"  Environment: {env}")
    print(f"  Database: {database_name}@{database_ip}")
    print("=" * 50)
    
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=(env == 'development')
    )
