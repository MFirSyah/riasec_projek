# AGENTS.md — Panduan AI Agent untuk Proyek RIASEC Career App

## Gambaran Proyek

Aplikasi web berbasis **Streamlit** untuk membantu siswa SMA/SMK/sederajat menentukan pilihan program studi berdasarkan:
1. Profil kepribadian RIASEC (Holland Theory)
2. Nilai akademik dari rapor

Teknologi utama: `Python`, `Streamlit`, `Scikit-learn`, `Supabase`, `Plotly`

---

## Struktur Folder

```
riasec-career-app/
├── data/
│   ├── riasec_academic_68programs.csv   # Dataset training model ML
│   ├── prodi_info.csv                   # Info deskripsi 68 program studi
│   └── questionnaire.json               # 24 item kuesioner RIASEC
│
├── model/
│   ├── train_model.py                   # Script training Random Forest
│   ├── rf_model.pkl                     # Model terlatih (hasil train_model.py)
│   └── scaler.pkl                       # StandardScaler (hasil train_model.py)
│
├── pages/
│   ├── 1_questionnaire.py               # Step 1: Kuesioner RIASEC 24 item
│   ├── 2_academic_input.py              # Step 2: Input nilai rapor
│   ├── 3_result.py                      # Step 3: Hasil rekomendasi prodi
│   ├── 4_dashboard_bk.py                # Dashboard guru BK (role: guru_bk)
│   └── 5_profile.py                     # Halaman profil & histori siswa
│
├── utils/
│   ├── supabase_client.py               # Koneksi dan helper Supabase
│   ├── predict.py                       # Fungsi prediksi & scoring
│   └── pdf_export.py                    # Generate PDF hasil rekomendasi
│
├── app.py                               # Entry point, routing role-based
├── requirements.txt                     # Dependensi Python
└── .env                                 # API keys (JANGAN di-commit ke git)
```

---

## Alur Aplikasi (User Flow)

```
[Landing / Login]
       │
       ▼
[Daftar Akun] ──► pilih role: siswa | guru_bk
       │
       ▼
[Step 1] Kuesioner RIASEC 24 item (skala 1–5)
       │  → hitung skor R, I, A, S, E, C (dinormalisasi 0–100)
       ▼
[Step 2] Input Nilai Rapor (10 mata pelajaran + GPA)
       │  → simpan ke session_state
       ▼
[Step 3] Hasil Rekomendasi
       │  → top 5 prodi + confidence score + penjelasan
       │  → info prodi: deskripsi, prospek, kampus, biaya
       │  → simpan ke Supabase (tabel: hasil_tes)
       │  → export PDF
       ▼
[Feedback] Form kepuasan siswa → simpan ke Supabase (tabel: feedback)
```

---

## Data

### `data/riasec_academic_68programs.csv`
Dataset training dengan 800 baris, 19 kolom.

| Kolom | Tipe | Keterangan |
|---|---|---|
| `student_id` | string | ID unik siswa (STU_XXXX) |
| `bahasa_indonesia` | float | Nilai 0–100 |
| `bahasa_inggris` | float | Nilai 0–100 |
| `matematika` | float | Nilai 0–100 |
| `informatika` | float | Nilai 0–100 |
| `ipa` | float | Nilai 0–100 |
| `ips` | float | Nilai 0–100 |
| `ppkn` | float | Nilai 0–100 |
| `penjas` | float | Nilai 0–100 |
| `seni` | float | Nilai 0–100 |
| `gpa` | float | Rata-rata nilai keseluruhan |
| `riasec_r` | float | Skor Realistic (0–100) |
| `riasec_i` | float | Skor Investigative (0–100) |
| `riasec_a` | float | Skor Artistic (0–100) |
| `riasec_s` | float | Skor Social (0–100) |
| `riasec_e` | float | Skor Enterprising (0–100) |
| `riasec_c` | float | Skor Conventional (0–100) |
| `program_id` | int | ID program studi (1–68) |
| `program_name` | string | Nama program studi |

**Fitur untuk model (16 kolom):**
`riasec_r`, `riasec_i`, `riasec_a`, `riasec_s`, `riasec_e`, `riasec_c`,
`bahasa_indonesia`, `bahasa_inggris`, `matematika`, `informatika`,
`ipa`, `ips`, `ppkn`, `penjas`, `seni`, `gpa`

**Target:** `program_id` (68 kelas)

---

### `data/prodi_info.csv`
Info statis 68 program studi. Join key: `program_id`.

| Kolom | Tipe | Keterangan |
|---|---|---|
| `program_id` | int | Primary key (1–68), harus cocok dengan dataset training |
| `program_name` | string | Nama resmi program studi |
| `deskripsi` | string | Deskripsi singkat program studi |
| `prospek_kerja` | string | Daftar prospek karir (dipisah koma) |
| `mata_kuliah_unggulan` | string | Contoh mata kuliah unggulan |
| `durasi_studi` | string | Contoh: "4 tahun (S1)" |
| `jenjang` | string | S1 / D3 / D4 / S1 & D4 |
| `kelompok_prodi` | string | Kategori: Teknik, Kesehatan, Sosial, dll |
| `akreditasi_umum` | string | Unggul / A / B (gambaran umum) |
| `top_kampus_prodi` | string | 3 kampus terbaik untuk prodi ini |
| `est_biaya` | string | Estimasi UKT per semester |
| `list_kampus_prodi` | string | Daftar kampus yang memiliki prodi ini |

---

### `data/questionnaire.json`
Format:
```json
{
  "questions": [
    {
      "id": 1,
      "dimension": "R",
      "text": "Saya suka kegiatan yang melibatkan alat, mesin, atau pekerjaan tangan."
    },
    ...
  ]
}
```
Total: 24 pertanyaan, 4 per dimensi (R, I, A, S, E, C). Skala jawaban 1–5.

**Cara hitung skor per dimensi:**
```
skor_mentah = jumlah jawaban 4 item (min: 4, max: 20)
skor_normalized = (skor_mentah - 4) / (20 - 4) * 100
```

---

## Model Machine Learning

### `model/train_model.py`
Script ini harus:
1. Load `data/riasec_academic_68programs.csv`
2. Pisahkan fitur (16 kolom) dan target (`program_id`)
3. Lakukan `StandardScaler` pada fitur → simpan sebagai `scaler.pkl`
4. Train `RandomForestClassifier` dengan:
   - `n_estimators=200`
   - `random_state=42`
   - `class_weight='balanced'` (karena data tidak seimbang per kelas)
5. Simpan model sebagai `rf_model.pkl`
6. Print classification report dan akurasi

### `model/rf_model.pkl` dan `model/scaler.pkl`
Dibuat dengan menjalankan `python model/train_model.py`.
Diload di `utils/predict.py` saat startup aplikasi.

---

### `utils/predict.py`
Fungsi utama yang harus ada:

```python
def predict_top5(riasec_scores: dict, academic_scores: dict) -> list[dict]:
    """
    Input:
        riasec_scores: {'r': float, 'i': float, 'a': float, 's': float, 'e': float, 'c': float}
        academic_scores: {'bahasa_indonesia': float, ..., 'gpa': float}
    
    Output: list 5 dict, masing-masing berisi:
        {
            'program_id': int,
            'program_name': str,
            'confidence': float,      # probabilitas 0.0–1.0
            'top_features': list[str] # 3 fitur paling berpengaruh untuk prediksi ini
        }
    """
```

**Cara hitung `top_features`:** Gunakan `feature_importances_` dari Random Forest,
filter ke 3 fitur tertinggi yang nilainya di atas rata-rata user, lalu buat kalimat penjelasan:
- Contoh: `"Skor Investigative kamu tinggi"` atau `"Nilai Matematika kamu di atas rata-rata"`

---

## Autentikasi & Role

### Supabase Auth
- Gunakan Supabase Auth (email + password, **tanpa email verification**)
- Saat register, simpan field `role` ke tabel `profiles`

### Tabel Supabase: `profiles`
```sql
id          uuid references auth.users primary key
full_name   text
role        text check (role in ('siswa', 'guru_bk'))
school      text
created_at  timestamp default now()
```

### Routing di `app.py`
```python
role = st.session_state['user']['role']
if role == 'guru_bk':
    # tampilkan sidebar dengan akses ke dashboard_bk
elif role == 'siswa':
    # tampilkan sidebar step 1 → 2 → 3 saja
```

---

## Tabel Supabase Lengkap

### `hasil_tes`
```sql
id              uuid primary key default gen_random_uuid()
user_id         uuid references auth.users
riasec_r        float
riasec_i        float
riasec_a        float
riasec_s        float
riasec_e        float
riasec_c        float
nilai_akademik  jsonb   -- semua nilai rapor dalam format JSON
top5_rekomendasi jsonb  -- hasil prediksi top 5
created_at      timestamp default now()
```

### `feedback`
```sql
id          uuid primary key default gen_random_uuid()
user_id     uuid references auth.users
hasil_id    uuid references hasil_tes
rating      int check (rating between 1 and 5)
komentar    text
created_at  timestamp default now()
```

---

## Halaman Detail

### `pages/1_questionnaire.py`
- Tampilkan 24 pertanyaan dalam 6 blok (per dimensi), satu blok per layar atau semua sekaligus
- Gunakan `st.slider` atau `st.radio` dengan label: Sangat Tidak Setuju (1) → Sangat Setuju (5)
- Tampilkan progress bar
- Simpan hasil skor ke `st.session_state['riasec_scores']`
- Tampilkan radar chart (Plotly) setelah submit

### `pages/2_academic_input.py`
- Form input 10 nilai mapel + GPA (input numerik 0–100)
- Validasi: tidak boleh ada nilai kosong, nilai harus 0–100
- Simpan ke `st.session_state['academic_scores']`
- Tombol "Lihat Rekomendasi" → redirect ke halaman 3

### `pages/3_result.py`
- Load skor dari session_state
- Panggil `predict_top5()` dari `utils/predict.py`
- Tampilkan top 5 rekomendasi sebagai card:
  - Nama prodi + confidence score (progress bar / persentase)
  - Penjelasan singkat ("Kenapa prodi ini cocok untuk kamu")
  - Expander: deskripsi, prospek kerja, top 3 kampus, estimasi biaya, list kampus
- Tombol "Simpan Hasil" → simpan ke Supabase
- Tombol "Export PDF" → panggil `utils/pdf_export.py`
- Form feedback di bawah

### `pages/4_dashboard_bk.py`
- Hanya bisa diakses jika `role == 'guru_bk'`
- Tampilkan:
  - Jumlah siswa yang sudah tes
  - Distribusi rekomendasi prodi (bar chart)
  - Distribusi skor RIASEC (radar/bar chart)
  - Tabel histori semua siswa (bisa filter per tanggal)
  - Rata-rata confidence score

### `pages/5_profile.py`
- Info akun (nama, sekolah, role)
- Histori hasil tes siswa sendiri
- Tombol tes ulang

---

## Environment Variables (`.env`)

```
SUPABASE_URL=https://xxxx.supabase.co
SUPABASE_ANON_KEY=xxxx
```

Load dengan `python-dotenv` di `utils/supabase_client.py`.

---

## `requirements.txt`

```
streamlit>=1.35.0
scikit-learn>=1.4.0
pandas>=2.0.0
numpy>=1.26.0
plotly>=5.20.0
supabase>=2.4.0
python-dotenv>=1.0.0
reportlab>=4.0.0
joblib>=1.3.0
```

---

## Catatan Penting untuk Agent

1. **Jangan hardcode API key** — selalu ambil dari environment variable
2. **Cek session_state** sebelum akses halaman result (pastikan riasec_scores dan academic_scores ada)
3. **`program_id` adalah join key** antara `rf_model` output dan `prodi_info.csv` — pastikan konsisten
4. **`rf_model.pkl` harus dibuat dulu** dengan menjalankan `train_model.py` sebelum aplikasi bisa berjalan
5. **Role check** harus dilakukan di awal setiap halaman yang restricted (dashboard BK)
6. **Radar chart** untuk visualisasi RIASEC gunakan Plotly `go.Scatterpolar`
7. **Streamlit multipage** — penamaan file di `pages/` otomatis jadi menu sidebar (format: `N_nama.py`)