"""
form.py - Modul Form Flask-WTF untuk DuoSentimen

Modul ini mendefinisikan kelas-kelas form menggunakan Flask-WTF
untuk validasi input pengguna di sisi server, termasuk form login,
registrasi, scraping, upload dataset, dan analisis sentimen manual.
"""

import re
from flask_wtf import FlaskForm
from wtforms import (
    StringField,
    PasswordField,
    IntegerField,
    SelectField,
    FileField,
    TextAreaField,
    SubmitField
)
from wtforms.validators import (
    DataRequired,
    Length,
    EqualTo,
    NumberRange
)


class LoginUserForm(FlaskForm):
    """
    Form untuk login pengguna.

    Fields:
        username: Username pengguna (3-50 karakter).
        password: Password pengguna.
        submit: Tombol submit login.

    Methods:
        clean_username: Membersihkan input username dari HTML tags
                        dan whitespace berlebih.
    """

    username = StringField(
        'Username',
        validators=[
            DataRequired(message='Username wajib diisi'),
            Length(
                min=3,
                max=50,
                message='Username harus antara 3-50 karakter'
            )
        ],
        render_kw={
            'placeholder': 'Masukkan username',
            'class': 'form-control',
            'id': 'login-username'
        }
    )

    password = PasswordField(
        'Password',
        validators=[
            DataRequired(message='Password wajib diisi')
        ],
        render_kw={
            'placeholder': 'Masukkan password',
            'class': 'form-control',
            'id': 'login-password'
        }
    )

    submit = SubmitField(
        'Login',
        render_kw={
            'class': 'btn btn-primary',
            'id': 'login-submit'
        }
    )

    def clean_username(self, username):
        """
        Membersihkan input username dari HTML tags dan whitespace.

        Menghapus tag HTML yang mungkin disuntikkan (XSS prevention)
        dan menghapus spasi di awal/akhir string.

        Args:
            username: Field username dari form.

        Returns:
            String username yang sudah dibersihkan.
        """
        if username.data:
            # Hapus HTML tags
            cleaned = re.sub(r'<[^>]+>', '', username.data)
            # Escape karakter HTML spesial
            cleaned = (
                cleaned
                .replace('&', '&amp;')
                .replace('<', '&lt;')
                .replace('>', '&gt;')
                .replace('"', '&quot;')
                .replace("'", '&#x27;')
            )
            # Hapus whitespace berlebih
            cleaned = cleaned.strip()
            username.data = cleaned
        return username


class RegisterUserForm(FlaskForm):
    """
    Form untuk registrasi pengguna baru.

    Fields:
        nama_lengkap: Nama lengkap pengguna (max 200 karakter).
        username: Username unik (3-100 karakter).
        password: Password (min 6 karakter).
        confirm_password: Konfirmasi password (harus sama dengan password).
        submit: Tombol submit registrasi.
    """

    nama_lengkap = StringField(
        'Nama Lengkap',
        validators=[
            DataRequired(message='Nama lengkap wajib diisi'),
            Length(
                max=200,
                message='Nama lengkap maksimal 200 karakter'
            )
        ],
        render_kw={
            'placeholder': 'Masukkan nama lengkap',
            'class': 'form-control',
            'id': 'register-nama'
        }
    )

    username = StringField(
        'Username',
        validators=[
            DataRequired(message='Username wajib diisi'),
            Length(
                min=3,
                max=100,
                message='Username harus antara 3-100 karakter'
            )
        ],
        render_kw={
            'placeholder': 'Masukkan username',
            'class': 'form-control',
            'id': 'register-username'
        }
    )

    password = PasswordField(
        'Password',
        validators=[
            DataRequired(message='Password wajib diisi'),
            Length(
                min=6,
                message='Password minimal 6 karakter'
            )
        ],
        render_kw={
            'placeholder': 'Masukkan password',
            'class': 'form-control',
            'id': 'register-password'
        }
    )

    confirm_password = PasswordField(
        'Konfirmasi Password',
        validators=[
            DataRequired(message='Konfirmasi password wajib diisi'),
            EqualTo(
                'password',
                message='Password tidak cocok'
            )
        ],
        render_kw={
            'placeholder': 'Konfirmasi password',
            'class': 'form-control',
            'id': 'register-confirm-password'
        }
    )

    submit = SubmitField(
        'Daftar',
        render_kw={
            'class': 'btn btn-success',
            'id': 'register-submit'
        }
    )


class ScrapingForm(FlaskForm):
    """
    Form untuk konfigurasi scraping ulasan Google Play Store.

    Fields:
        jumlah_ulasan: Jumlah ulasan yang ingin diambil (100-10000).
        bahasa: Pilihan bahasa ulasan (Indonesia/English).
        tahun: Tahun filter ulasan (2020-2030).
        submit: Tombol submit mulai scraping.
    """

    jumlah_ulasan = IntegerField(
        'Jumlah Ulasan',
        default=5000,
        validators=[
            DataRequired(message='Jumlah ulasan wajib diisi'),
            NumberRange(
                min=100,
                max=10000,
                message='Jumlah ulasan harus antara 100-10000'
            )
        ],
        render_kw={
            'placeholder': 'Masukkan jumlah ulasan (100-10000)',
            'class': 'form-control',
            'id': 'scraping-jumlah'
        }
    )

    bahasa = SelectField(
        'Bahasa',
        choices=[
            ('id', 'Indonesia'),
            ('en', 'English')
        ],
        default='id',
        render_kw={
            'class': 'form-select',
            'id': 'scraping-bahasa'
        }
    )

    tahun = IntegerField(
        'Tahun',
        default=2026,
        validators=[
            DataRequired(message='Tahun wajib diisi'),
            NumberRange(
                min=2020,
                max=2030,
                message='Tahun harus antara 2020-2030'
            )
        ],
        render_kw={
            'placeholder': 'Masukkan tahun filter',
            'class': 'form-control',
            'id': 'scraping-tahun'
        }
    )

    submit = SubmitField(
        'Mulai Scraping',
        render_kw={
            'class': 'btn btn-primary',
            'id': 'scraping-submit'
        }
    )


class UploadDatasetForm(FlaskForm):
    """
    Form untuk upload file dataset (CSV/Excel).

    Fields:
        file: File dataset yang akan di-upload.
        submit: Tombol submit upload.
    """

    file = FileField(
        'Pilih File Dataset',
        validators=[
            DataRequired(message='File wajib dipilih')
        ],
        render_kw={
            'class': 'form-control',
            'id': 'upload-file',
            'accept': '.csv,.xlsx,.xls'
        }
    )

    submit = SubmitField(
        'Upload',
        render_kw={
            'class': 'btn btn-primary',
            'id': 'upload-submit'
        }
    )


class ManualSentimenForm(FlaskForm):
    """
    Form untuk analisis sentimen manual (input teks langsung).

    Fields:
        input_text: Teks ulasan yang akan dianalisis.
        submit: Tombol submit analisis.
    """

    input_text = TextAreaField(
        'Teks Ulasan',
        validators=[
            DataRequired(message='Teks ulasan wajib diisi')
        ],
        render_kw={
            'placeholder': 'Masukkan teks ulasan untuk dianalisis...',
            'class': 'form-control',
            'id': 'manual-input-text',
            'rows': 5
        }
    )

    submit = SubmitField(
        'Analisis',
        render_kw={
            'class': 'btn btn-primary',
            'id': 'manual-submit'
        }
    )
