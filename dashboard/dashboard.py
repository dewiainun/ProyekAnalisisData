from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st

# ==========================================
# 1. KONFIGURASI HALAMAN & TEMA VISUALISASI
# ==========================================
st.set_page_config(
    page_title="Bike Sharing Analytics Dashboard",
    page_icon="🚲",
    layout="wide",
    initial_sidebar_state="expanded",
)

sns.set_theme(style="whitegrid")
plt.rcParams["font.sans-serif"] = "DejaVu Sans"
plt.rcParams["axes.edgecolor"] = "#CCCCCC"
plt.rcParams["axes.linewidth"] = 0.8


# ==========================================
# 2. FUNGSI PEMUATAN DATA (DENGAN CACHING)
# ==========================================
@st.cache_data
def load_data() -> pd.DataFrame:
    """Memuat data main_data.csv dengan resolusi path otomatis."""
    current_dir = Path(__file__).parent if "__file__" in locals() else Path.cwd()
    file_path = current_dir / "main_data.csv"

    if not file_path.exists():
        file_path = Path("dashboard/main_data.csv")

    df = pd.read_csv(file_path)
    df["dteday"] = pd.to_datetime(df["dteday"])
    return df


# ==========================================
# 3. FUNGSI HELPER AGREGASI DATA
# ==========================================
def create_daily_df(df: pd.DataFrame) -> pd.DataFrame:
    """Mengagregasi data per jam menjadi level harian."""
    daily_df = (
        df.groupby(
            [
                "dteday",
                "season_label",
                "yr_label",
                "weather_label",
                "workingday_label",
                "temp_category",
            ],
            observed=False,
        )
        .agg(
            {
                "casual": "sum",
                "registered": "sum",
                "cnt": "sum",
                "temp_celsius": "mean",
                "hum_percent": "mean",
                "windspeed_original": "mean",
            }
        )
        .reset_index()
    )
    daily_df = daily_df[daily_df["cnt"] > 0].reset_index(drop=True)
    return daily_df


def create_hourly_pattern_df(df: pd.DataFrame) -> pd.DataFrame:
    """Mengagregasi rata-rata penyewaan per jam berdasarkan hari kerja/libur."""
    return (
        df.groupby(["workingday_label", "hr"])[["registered", "casual", "cnt"]]
        .mean()
        .reset_index()
    )


# ==========================================
# 4. MEMUAT DATA UTAMA
# ==========================================
try:
    main_df = load_data()
except Exception as e:
    st.error(
        f"Gagal memuat berkas `main_data.csv`. Pastikan `main_data.csv` berada satu folder dengan `dashboard.py`. Detail: {e}"
    )
    st.stop()

min_date = main_df["dteday"].min().date()
max_date = main_df["dteday"].max().date()

# ==========================================
# 5. SIDEBAR & FILTER INTERAKTIF
# ==========================================
with st.sidebar:
    st.title("🚲 Capital Bikeshare")
    st.caption("Sistem Pemantauan Operasional & Mobilitas (2011–2012)")
    st.markdown("---")

    st.subheader("Filter Data")

    date_range = st.date_input(
        label="Rentang Waktu",
        min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date],
    )

    if len(date_range) == 2:
        start_date, end_date = date_range
    else:
        start_date, end_date = min_date, max_date

    season_options = ["Fall", "Summer", "Winter", "Spring"]
    selected_seasons = st.multiselect(
        label="Musim (Season)",
        options=season_options,
        default=season_options,
    )

    weather_options = list(main_df["weather_label"].unique())
    selected_weather = st.multiselect(
        label="Kondisi Cuaca",
        options=weather_options,
        default=weather_options,
    )

    st.markdown("---")
    st.markdown(
        "**Disusun oleh:**\n"
        "- Dewi Ainun Amaliah\n"
        "- Proyek Akhir Analisis Data"
    )

# Terapkan Filter ke DataFrame
filtered_hour_df = main_df[
    (main_df["dteday"].dt.date >= start_date)
    & (main_df["dteday"].dt.date <= end_date)
    & (main_df["season_label"].isin(selected_seasons))
    & (main_df["weather_label"].isin(selected_weather))
]

if filtered_hour_df.empty:
    st.warning("Tidak ada data yang sesuai dengan filter yang dipilih. Silakan ubah filter di sidebar.")
    st.stop()

filtered_day_df = create_daily_df(filtered_hour_df)

# ==========================================
# 6. HEADER & KEY PERFORMANCE INDICATORS (KPI)
# ==========================================
st.title("Bike Sharing Operational Dashboard")
st.markdown(
    f"Menampilkan analisis performa penyewaan sepeda periode **{start_date.strftime('%d %b %Y')}** "
    f"hingga **{end_date.strftime('%d %b %Y')}**."
)

col1, col2, col3, col4 = st.columns(4)

total_rentals = int(filtered_hour_df["cnt"].sum())
total_registered = int(filtered_hour_df["registered"].sum())
total_casual = int(filtered_hour_df["casual"].sum())
avg_daily_rentals = filtered_day_df["cnt"].mean()

registered_pct = (total_registered / total_rentals * 100) if total_rentals > 0 else 0
casual_pct = (total_casual / total_rentals * 100) if total_rentals > 0 else 0

with col1:
    st.metric(label="Total Penyewaan (Unit)", value=f"{total_rentals:,}")
with col2:
    st.metric(
        label="Pengguna Registered",
        value=f"{total_registered:,}",
        delta=f"{registered_pct:.1f}% dari total",
        delta_color="off",
    )
with col3:
    st.metric(
        label="Pengguna Casual",
        value=f"{total_casual:,}",
        delta=f"{casual_pct:.1f}% dari total",
        delta_color="off",
    )
with col4:
    st.metric(label="Rata-Rata Harian (Unit/Hari)", value=f"{avg_daily_rentals:,.0f}")

st.markdown("---")

# ==========================================
# 7. VISUALISASI PERTANYAAN 1: CUACA & MUSIM
# ==========================================
st.subheader("1. Dampak Kondisi Cuaca dan Musim terhadap Penyewaan Sepeda")
st.caption("Perbandingan rata-rata penyewaan sepeda harian berdasarkan kondisi cuaca dan interaksi antar-musim.")

fig1, axes1 = plt.subplots(1, 2, figsize=(16, 5.5))

weather_order = [
    w for w in ["Cerah/Berawan", "Berkabut/Mendung", "Hujan/Salju Ringan", "Cuaca Ekstrem"]
    if w in filtered_day_df["weather_label"].unique()
]
season_order = [
    s for s in ["Fall", "Summer", "Winter", "Spring"]
    if s in filtered_day_df["season_label"].unique()
]
weather_palette = {
    "Cerah/Berawan": "#1f77b4",
    "Berkabut/Mendung": "#9ecae1",
    "Hujan/Salju Ringan": "#d95f02",
    "Cuaca Ekstrem": "#7570b3",
}

sns.barplot(
    data=filtered_day_df,
    x="weather_label",
    y="cnt",
    order=weather_order,
    palette=[weather_palette[w] for w in weather_order],
    errorbar=None,
    ax=axes1[0],
)
axes1[0].set_title("Rata-Rata Penyewaan Harian Berdasarkan Cuaca", fontsize=12, fontweight="bold")
axes1[0].set_xlabel("Kondisi Cuaca", fontsize=10)
axes1[0].set_ylabel("Rata-Rata Penyewaan Harian", fontsize=10)
for container in axes1[0].containers:
    axes1[0].bar_label(container, fmt="%.0f", padding=3, fontsize=9)

sns.barplot(
    data=filtered_day_df,
    x="season_label",
    y="cnt",
    hue="weather_label",
    order=season_order,
    hue_order=weather_order,
    palette=weather_palette,
    errorbar=None,
    ax=axes1[1],
)
axes1[1].set_title("Rata-Rata Penyewaan per Musim dan Kondisi Cuaca", fontsize=12, fontweight="bold")
axes1[1].set_xlabel("Musim (Season)", fontsize=10)
axes1[1].set_ylabel("Rata-Rata Penyewaan Harian", fontsize=10)
axes1[1].legend(title="Kondisi Cuaca", fontsize=9, title_fontsize=9)

plt.tight_layout()
st.pyplot(fig1)

with st.expander("Lihat Insight Analisis Cuaca & Musim"):
    st.markdown(
        "- **Dominasi Cuaca Cerah:** Kondisi **Cerah/Berawan** menghasilkan rata-rata penyewaan tertinggi (**4.877 unit/hari**), sedangkan kondisi **Hujan/Salju Ringan** menurunkan permintaan hingga **63%** (**1.803 unit/hari**).\n"
        "- **Pola Musiman:** Musim **Fall (Gugur)** dan **Summer (Panas)** mencatat rata-rata permintaan tertinggi di setiap kondisi cuaca, sementara **Spring (Semi)** mencatat permintaan terendah."
    )

st.markdown("---")

# ==========================================
# 8. VISUALISASI PERTANYAAN 2: PEAK HOURS
# ==========================================
st.subheader("2. Pola Jam Operasional (Peak Hours): Hari Kerja vs Hari Libur")
st.caption("Perbandingan perilaku penyewaan per jam antara pengguna Registered dan Casual pada Hari Kerja dibandingkan Hari Libur/Akhir Pekan.")

hourly_pattern = create_hourly_pattern_df(filtered_hour_df)
workday_hourly = hourly_pattern[hourly_pattern["workingday_label"] == "Hari Kerja"]
holiday_hourly = hourly_pattern[hourly_pattern["workingday_label"] == "Hari Libur"]

fig2, axes2 = plt.subplots(2, 1, figsize=(14, 8.5), sharex=True)

if not workday_hourly.empty:
    axes2[0].plot(
        workday_hourly["hr"],
        workday_hourly["registered"],
        marker="o",
        linewidth=2.5,
        color="#1f77b4",
        label="Registered",
    )
    axes2[0].plot(
        workday_hourly["hr"],
        workday_hourly["casual"],
        marker="s",
        linewidth=2.5,
        color="#ff7f0e",
        label="Casual",
    )
axes2[0].set_title("Rata-Rata Penyewaan per Jam pada HARI KERJA", fontsize=12, fontweight="bold")
axes2[0].set_ylabel("Rata-Rata Penyewaan", fontsize=10)
axes2[0].set_xticks(range(0, 24))
axes2[0].axvspan(7, 9, color="#1f77b4", alpha=0.12, label="Peak Pagi (07:00-09:00)")
axes2[0].axvspan(16, 19, color="#2ca02c", alpha=0.12, label="Peak Sore (16:00-19:00)")
axes2[0].legend(loc="upper left", fontsize=9)

if not holiday_hourly.empty:
    axes2[1].plot(
        holiday_hourly["hr"],
        holiday_hourly["registered"],
        marker="o",
        linewidth=2.5,
        color="#1f77b4",
        label="Registered",
    )
    axes2[1].plot(
        holiday_hourly["hr"],
        holiday_hourly["casual"],
        marker="s",
        linewidth=2.5,
        color="#ff7f0e",
        label="Casual",
    )
axes2[1].set_title("Rata-Rata Penyewaan per Jam pada HARI LIBUR / AKHIR PEKAN", fontsize=12, fontweight="bold")
axes2[1].set_xlabel("Jam Operasional (00:00 - 23:00)", fontsize=10)
axes2[1].set_ylabel("Rata-Rata Penyewaan", fontsize=10)
axes2[1].set_xticks(range(0, 24))
axes2[1].axvspan(11, 17, color="#ff7f0e", alpha=0.15, label="Peak Siang-Sore (11:00-17:00)")
axes2[1].legend(loc="upper left", fontsize=9)

plt.tight_layout()
st.pyplot(fig2)

with st.expander("Lihat Insight Analisis Peak Hours"):
    st.markdown(
        "- **Pola Komuter di Hari Kerja (Bimodal):** Lonjakan tertinggi didominasi oleh pengguna **Registered** pada pukul **08:00 pagi** (454,74 unit/jam) dan **17:00–18:00 sore** (441,78–468,39 unit/jam).\n"
        "- **Pola Rekreasi di Hari Libur (Unimodal):** Puncak penyewaan bergeser ke rentang pukul **11:00–17:00 siang/sore**, dengan peningkatan pengguna **Casual** lebih dari 2 kali lipat (126,25–139,59 unit/jam)."
    )

st.markdown("---")

# ==========================================
# 9. VISUALISASI ANALISIS LANJUTAN: CLUSTERING
# ==========================================
st.subheader("3. Analisis Lanjutan: Clustering Waktu Operasional & Kenyamanan Suhu")
st.caption("Pengelompokan beban operasional menggunakan Manual Grouping pada segmen waktu harian dan Binning pada kategori suhu udara.")

fig3, axes3 = plt.subplots(1, 2, figsize=(16, 5.5))

time_order = [
    "Sore (15:00-18:59)",
    "Siang (11:00-14:59)",
    "Pagi (05:00-10:59)",
    "Malam (19:00-04:59)",
]
temp_order = [
    "Dingin (<15°C)",
    "Sejuk/Ideal (15-26°C)",
    "Panas (>26°C)",
]

sns.barplot(
    data=filtered_hour_df,
    x="time_of_day",
    y="cnt",
    order=time_order,
    palette=["#1f77b4", "#9ecae1", "#9ecae1", "#c7c7c7"],
    errorbar=None,
    ax=axes3[0],
)
axes3[0].set_title("Rata-Rata Penyewaan per Jam Berdasarkan Klaster Waktu", fontsize=12, fontweight="bold")
axes3[0].set_xlabel("Klaster Waktu Operasional", fontsize=10)
axes3[0].set_ylabel("Rata-Rata Penyewaan per Jam", fontsize=10)
axes3[0].tick_params(axis="x", rotation=12)
for container in axes3[0].containers:
    axes3[0].bar_label(container, fmt="%.0f", padding=3, fontsize=9)

sns.barplot(
    data=filtered_day_df,
    x="temp_category",
    y="cnt",
    order=temp_order,
    palette=["#c7c7c7", "#1f77b4", "#2ca02c"],
    errorbar=None,
    ax=axes3[1],
)
axes3[1].set_title("Rata-Rata Penyewaan Harian Berdasarkan Klaster Suhu (Binning)", fontsize=12, fontweight="bold")
axes3[1].set_xlabel("Kategori Suhu Udara", fontsize=10)
axes3[1].set_ylabel("Rata-Rata Penyewaan Harian", fontsize=10)
for container in axes3[1].containers:
    axes3[1].bar_label(container, fmt="%.0f", padding=3, fontsize=9)

plt.tight_layout()
st.pyplot(fig3)

with st.expander("Lihat Rekomendasi Strategis (Action Items)"):
    st.markdown(
        "1. **Manajemen Armada & Maintenance Berbasis Cuaca/Musim:** Operasikan kapasitas penuh pada musim **Fall** dan **Summer** saat cuaca cerah dan suhu berada di atas **15°C** (klaster Sejuk/Ideal dan Panas). Jadwalkan *preventive maintenance* pada musim **Spring**, hari berprakiraan hujan, atau pada klaster waktu **Malam (19:00–04:59)**.\n"
        "2. **Redistribusi Stasiun & Promosi Segmen Casual:** Lakukan redistribusi unit sepeda ke stasiun pemukiman sebelum pukul **07:00** dan ke area perkantoran sebelum pukul **16:00** pada hari kerja. Luncurkan promo *Weekend Pass* pada pukul **11:00–17:00** di hari libur untuk mengonversi pengguna *Casual* menjadi *Registered*."
    )

st.caption("Copyright © 2026 Dewi Ainun Amaliah | Capital Bikeshare Dataset (2011–2012)")