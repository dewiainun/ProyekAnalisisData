# Bike Sharing Operational Analytics Dashboard 🚲

Dokumentasi proyek akhir analisis data dan pengembangan dashboard interaktif menggunakan **Bike Sharing Dataset (Capital Bikeshare 2011–2012)**. Proyek ini bertujuan untuk mengevaluasi pengaruh kondisi cuaca, pergantian musim, pola jam operasional (*peak hours*), serta segmentasi waktu dan suhu udara terhadap volume penyewaan sepeda guna mendukung pengambilan keputusan operasional berbasis data.

---

## 📌 Latar Belakang & Pertanyaan Bisnis (SMART Framework)

1. **Pertanyaan 1 (Alokasi Armada Berdasarkan Cuaca & Musim):**
   Bagaimana perbandingan rata-rata dan total penyewaan sepeda (`cnt`) antara kondisi cuaca cerah (`weathersit = 1`) dengan kondisi cuaca buruk/hujan (`weathersit = 3` dan `4`) di setiap musim (`season`) sepanjang periode tahun 2011 hingga 2012 untuk menentukan alokasi ketersediaan armada?
2. **Pertanyaan 2 (Optimasi Distribusi pada Jam Sibuk / *Peak Hours*):**
   Pada jam berapa saja (`hr`) terjadi lonjakan tertinggi (*peak hours*) penyewaan sepeda oleh pengguna terdaftar (`registered`) dibandingkan pengguna biasa (`casual`) pada hari kerja (`workingday = 1`) versus hari libur (`workingday = 0`) selama periode tahun 2011 hingga 2012?

---

## 📂 Struktur Direktori Proyek

```text
submission/
├── dashboard/
│   ├── dashboard.py          # Source code utama aplikasi Streamlit
│   └── main_data.csv         # Dataset hasil cleaning & clustering untuk dashboard
├── data/
│   ├── day.csv               # Dataset mentah agregasi harian (731 baris)
│   └── hour.csv              # Dataset mentah agregasi per jam (17.379 baris)
├── notebook.ipynb            # Jupyter/Colab Notebook proses analisis data end-to-end
├── README.md                 # Dokumentasi proyek dan instruksi instalasi
├── requirements.txt          # Daftar dependensi pustaka Python
└── url.txt                   # Tautan aplikasi Streamlit Community Cloud
```

---

## 📊 Fitur Utama Dashboard

- **Interactive Sidebar Filters:** Memungkinkan pengguna memfilter data secara dinamis berdasarkan rentang tanggal (`2011-01-01` s.d. `2012-12-31`), musim (*Fall*, *Summer*, *Winter*, *Spring*), dan kondisi cuaca.
- **Executive KPI Metrics:** Menampilkan ringkasan metrik utama secara *real-time* meliputi Total Penyewaan, jumlah serta persentase pengguna *Registered* dan *Casual*, serta Rata-Rata Penyewaan Harian.
- **Analisis Cuaca & Musim:** Visualisasi komparatif rata-rata penyewaan harian berdasarkan kondisi cuaca dan interaksinya di setiap musim.
- **Analisis Jam Operasional (*Peak Hours*):** Grafik deret waktu per jam (`00:00`–`23:00`) yang memisahkan perilaku komuter di Hari Kerja (*bimodal*) dan perilaku rekreasi di Hari Libur (*unimodal*).
- **Analisis Lanjutan (Clustering Non-ML):**
  - *Manual Grouping Waktu Operasional:* Pengelompokan jam ke dalam 4 klaster waktu (*Pagi*, *Siang*, *Sore*, *Malam*).
  - *Temperature Binning:* Pengelompokan suhu udara aktual ke dalam 3 kategori kenyamanan termal (*Dingin <15°C*, *Sejuk/Ideal 15-26°C*, *Panas >26°C*).

---

## 🚀 Panduan Menjalankan Dashboard Secara Lokal

Ikuti langkah-langkah berikut untuk menjalankan aplikasi dashboard di komputer lokal Anda:

### 1. Prasyarat (*Prerequisites*)
Pastikan komputer Anda telah terinstal **Python (versi 3.9 hingga 3.12)**.

### 2. Persiapan *Virtual Environment*

**Opsi A — Menggunakan `venv` (Bawaan Python):**
```bash
# Masuk ke direktori proyek
cd submission

# Membuat virtual environment
python -m venv .venv

# Mengaktifkan virtual environment (Windows - PowerShell/CMD)
.venv\Scripts\activate

# Mengaktifkan virtual environment (macOS/Linux/Git Bash)
source .venv/bin/activate
```

**Opsi B — Menggunakan `conda` (Anaconda/Miniconda):**
```bash
conda create --name bikesharing-ds python=3.11 -y
conda activate bikesharing-ds
```

### 3. Instalasi Dependensi (*Dependencies*)
Instal seluruh pustaka yang dibutuhkan melalui berkas `requirements.txt`:
```bash
pip install -r requirements.txt
```

### 4. Menjalankan Aplikasi Streamlit
Jalankan perintah berikut dari direktori utama (`submission/`):
```bash
streamlit run dashboard/dashboard.py
```
Atau jika Anda berada di dalam direktori `dashboard/`:
```bash
cd dashboard
streamlit run dashboard.py
```

Aplikasi dashboard akan otomatis terbuka pada peramban (*browser*) Anda di alamat:
👉 `http://localhost:8501`

---

## 💡 Ringkasan Temuan & Rekomendasi Strategis

1. **Dampak Cuaca & Musim:** Kondisi cuaca **Cerah/Berawan** mencatat rata-rata penyewaan tertinggi (**4.877 unit/hari**), sedangkan **Hujan/Salju Ringan** menurunkan rata-rata penyewaan sebesar **63%** (**1.803 unit/hari**). Musim **Fall** dan **Summer** dengan klaster suhu **Sejuk/Ideal (15–26°C)** dan **Panas (>26°C)** merupakan periode paling produktif.
   - *Action Item:* Operasikan 100% kapasitas armada pada musim *Fall* dan *Summer* saat cuaca cerah, serta alokasikan jadwal perawatan besar (*preventive maintenance*) pada musim *Spring*, hari berprakiraan hujan, atau pada klaster waktu **Malam (19:00–04:59)** (rata-rata hanya 107 penyewaan/jam).
2. **Pola Jam Sibuk (*Peak Hours*):** Pada **Hari Kerja**, lonjakan tertinggi didominasi pengguna *Registered* pada pukul **08:00 pagi** (455 unit/jam) dan **17:00–18:00 sore** (442–468 unit/jam). Pada **Hari Libur**, lonjakan bergeser ke pukul **11:00–17:00** dengan kenaikan pengguna *Casual* lebih dari 2 kali lipat.
   - *Action Item:* Lakukan redistribusi unit sepeda ke stasiun pemukiman sebelum pukul **07:00** dan ke area perkantoran sebelum pukul **16:00** di hari kerja. Luncurkan promosi *Weekend Pass* pada pukul **11:00–17:00** di akhir pekan untuk mendorong konversi pengguna *Casual* menjadi pelanggan tetap (*Registered*).

---

**Disusun oleh:** Dewi Ainun Amaliah