"""
Dashboard Interaktif - Indeks Perilaku Anti Korupsi (IPAK) Indonesia 2012-2024
Sumber data: Badan Pusat Statistik (BPS)

Cara menjalankan:
    streamlit run dashboard_ipak.py
"""

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# ----------------------------------------------------------------------------
# KONFIGURASI HALAMAN
# ----------------------------------------------------------------------------
st.set_page_config(
    page_title="Dashboard IPAK Indonesia 2012-2024",
    page_icon="📊",
    layout="wide",
)

# ----------------------------------------------------------------------------
# LOAD & SIAPKAN DATA
# ----------------------------------------------------------------------------
CSV_PATH = "BPS_IPAK_Indonesia_2012-2024.csv"


@st.cache_data
def load_data(path: str) -> pd.DataFrame:
    df = pd.read_csv(path)
    df["Tahun"] = df["Tahun"].astype(int)
    return df


df = load_data(CSV_PATH)

# ----------------------------------------------------------------------------
# SIDEBAR - FILTER
# ----------------------------------------------------------------------------
st.sidebar.title("⚙️ Filter Dashboard")

tahun_min, tahun_max = int(df["Tahun"].min()), int(df["Tahun"].max())
rentang_tahun = st.sidebar.slider(
    "Pilih rentang tahun:",
    min_value=tahun_min,
    max_value=tahun_max,
    value=(tahun_min, tahun_max),
)

df_filtered = df[(df["Tahun"] >= rentang_tahun[0]) & (df["Tahun"] <= rentang_tahun[1])]

st.sidebar.markdown("---")
st.sidebar.markdown(
    """
**Tentang IPAK**

Indeks Perilaku Anti Korupsi (IPAK) mengukur tingkat permisivitas
masyarakat terhadap perilaku korupsi dalam skala **0 - 5**.
Semakin mendekati 5, semakin anti korupsi perilaku masyarakat.

IPAK terdiri dari dua dimensi:
- **Indeks Persepsi**
- **Indeks Pengalaman**

Sumber: Badan Pusat Statistik (BPS), Survei Perilaku Anti Korupsi (SPAK).
"""
)

# ----------------------------------------------------------------------------
# HEADER
# ----------------------------------------------------------------------------
st.title("📊 Dashboard Indeks Perilaku Anti Korupsi (IPAK) Indonesia")
st.markdown("**Periode 2012 - 2024** | Sumber: Badan Pusat Statistik (BPS)")
st.markdown("---")

# ----------------------------------------------------------------------------
# METRIK RINGKASAN (KPI CARDS)
# ----------------------------------------------------------------------------
df_valid = df_filtered.dropna(subset=["IPAK_Nasional"])

if not df_valid.empty:
    nilai_terbaru = df_valid.iloc[-1]
    nilai_awal = df_valid.iloc[0]
    selisih = nilai_terbaru["IPAK_Nasional"] - nilai_awal["IPAK_Nasional"]
    rata_rata = df_valid["IPAK_Nasional"].mean()
    nilai_tertinggi_row = df_valid.loc[df_valid["IPAK_Nasional"].idxmax()]

    col1, col2, col3, col4 = st.columns(4)
    col1.metric(
        label=f"IPAK Tahun {int(nilai_terbaru['Tahun'])}",
        value=f"{nilai_terbaru['IPAK_Nasional']:.2f}",
        delta=f"{selisih:+.2f} sejak {int(nilai_awal['Tahun'])}",
    )
    col2.metric(label="Rata-rata IPAK (periode terpilih)", value=f"{rata_rata:.2f}")
    col3.metric(
        label="IPAK Tertinggi",
        value=f"{nilai_tertinggi_row['IPAK_Nasional']:.2f}",
        delta=f"Tahun {int(nilai_tertinggi_row['Tahun'])}",
    )
    col4.metric(label="Jumlah Tahun Survei", value=f"{len(df_valid)} tahun")
else:
    st.warning("Tidak ada data IPAK Nasional pada rentang tahun yang dipilih.")

st.markdown("---")

# ----------------------------------------------------------------------------
# GRAFIK 1 - TREN IPAK NASIONAL (LINE CHART)
# ----------------------------------------------------------------------------
st.subheader("1️⃣ Tren IPAK Nasional dari Tahun ke Tahun")

fig1 = px.line(
    df_valid,
    x="Tahun",
    y="IPAK_Nasional",
    markers=True,
    text="IPAK_Nasional",
    title="Perkembangan IPAK Nasional (Skala 0-5)",
)
fig1.update_traces(texttemplate="%{text:.2f}", textposition="top center", line=dict(width=3))
fig1.update_layout(yaxis_range=[3, 4.2], xaxis=dict(dtick=1), hovermode="x unified")
st.plotly_chart(fig1, use_container_width=True)

with st.expander("ℹ️ Catatan data tahun ini"):
    st.dataframe(
        df_filtered[["Tahun", "IPAK_Nasional", "Catatan"]].set_index("Tahun"),
        use_container_width=True,
    )

st.markdown("---")

# ----------------------------------------------------------------------------
# GRAFIK 2 - PERBANDINGAN DIMENSI PERSEPSI vs PENGALAMAN (GROUPED BAR)
# ----------------------------------------------------------------------------
st.subheader("2️⃣ Perbandingan Dimensi: Indeks Persepsi vs Indeks Pengalaman")

df_dimensi = df_filtered.dropna(subset=["Indeks_Persepsi", "Indeks_Pengalaman"])

if not df_dimensi.empty:
    fig2 = go.Figure()
    fig2.add_trace(
        go.Bar(
            x=df_dimensi["Tahun"],
            y=df_dimensi["Indeks_Persepsi"],
            name="Indeks Persepsi",
            text=df_dimensi["Indeks_Persepsi"],
            texttemplate="%{text:.2f}",
            textposition="outside",
        )
    )
    fig2.add_trace(
        go.Bar(
            x=df_dimensi["Tahun"],
            y=df_dimensi["Indeks_Pengalaman"],
            name="Indeks Pengalaman",
            text=df_dimensi["Indeks_Pengalaman"],
            texttemplate="%{text:.2f}",
            textposition="outside",
        )
    )
    fig2.update_layout(
        barmode="group",
        xaxis=dict(dtick=1, title="Tahun"),
        yaxis=dict(title="Nilai Indeks", range=[3, 4.3]),
        title="Indeks Persepsi vs Indeks Pengalaman per Tahun",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    )
    st.plotly_chart(fig2, use_container_width=True)
    st.caption(
        "ℹ️ Data dimensi (Persepsi & Pengalaman) baru tersedia sejak tahun 2020."
    )
else:
    st.info("Data dimensi Persepsi & Pengalaman belum tersedia pada rentang tahun yang dipilih (data baru ada sejak 2020).")

st.markdown("---")

# ----------------------------------------------------------------------------
# GRAFIK 3 - PERBANDINGAN WILAYAH: PERKOTAAN vs PERDESAAN (LINE CHART)
# ----------------------------------------------------------------------------
st.subheader("3️⃣ Perbandingan IPAK Wilayah: Perkotaan vs Perdesaan")

df_wilayah = df_filtered.dropna(subset=["IPAK_Perkotaan", "IPAK_Perdesaan"])

if not df_wilayah.empty:
    df_wilayah_melt = df_wilayah.melt(
        id_vars="Tahun",
        value_vars=["IPAK_Perkotaan", "IPAK_Perdesaan"],
        var_name="Wilayah",
        value_name="Nilai_IPAK",
    )
    df_wilayah_melt["Wilayah"] = df_wilayah_melt["Wilayah"].replace(
        {"IPAK_Perkotaan": "Perkotaan", "IPAK_Perdesaan": "Perdesaan"}
    )

    fig3 = px.line(
        df_wilayah_melt,
        x="Tahun",
        y="Nilai_IPAK",
        color="Wilayah",
        markers=True,
        title="IPAK Perkotaan vs Perdesaan",
    )
    fig3.update_traces(line=dict(width=3))
    fig3.update_layout(xaxis=dict(dtick=1), yaxis=dict(title="Nilai IPAK", range=[3.5, 4.1]))
    st.plotly_chart(fig3, use_container_width=True)
    st.caption("ℹ️ Data wilayah baru tersedia sejak tahun 2020.")
else:
    st.info("Data IPAK Perkotaan & Perdesaan belum tersedia pada rentang tahun yang dipilih (data baru ada sejak 2020).")

st.markdown("---")

# ----------------------------------------------------------------------------
# GRAFIK 4 - IPAK BERDASARKAN TINGKAT PENDIDIKAN (BAR CHART PER TAHUN TERPILIH)
# ----------------------------------------------------------------------------
st.subheader("4️⃣ IPAK Berdasarkan Tingkat Pendidikan")

kolom_pendidikan = [
    "IPAK_Pendidikan_Di_bawah_SLTA",
    "IPAK_Pendidikan_SLTA",
    "IPAK_Pendidikan_Di_atas_SLTA",
]
df_pendidikan = df_filtered.dropna(subset=kolom_pendidikan, how="all")

if not df_pendidikan.empty:
    tahun_tersedia = sorted(df_pendidikan["Tahun"].unique())
    tahun_pilihan = st.selectbox(
        "Pilih tahun untuk melihat detail per tingkat pendidikan:",
        options=tahun_tersedia,
        index=len(tahun_tersedia) - 1,
    )

    baris = df_pendidikan[df_pendidikan["Tahun"] == tahun_pilihan].iloc[0]
    data_pendidikan = pd.DataFrame(
        {
            "Tingkat Pendidikan": ["Di bawah SLTA", "SLTA", "Di atas SLTA"],
            "Nilai IPAK": [
                baris["IPAK_Pendidikan_Di_bawah_SLTA"],
                baris["IPAK_Pendidikan_SLTA"],
                baris["IPAK_Pendidikan_Di_atas_SLTA"],
            ],
        }
    )

    fig4 = px.bar(
        data_pendidikan,
        x="Tingkat Pendidikan",
        y="Nilai IPAK",
        color="Tingkat Pendidikan",
        text="Nilai IPAK",
        title=f"IPAK Berdasarkan Tingkat Pendidikan - Tahun {tahun_pilihan}",
    )
    fig4.update_traces(texttemplate="%{text:.2f}", textposition="outside")
    fig4.update_layout(yaxis=dict(range=[3.5, 4.2]), showlegend=False)
    st.plotly_chart(fig4, use_container_width=True)
    st.caption("ℹ️ Data tingkat pendidikan baru tersedia sejak tahun 2021.")
else:
    st.info("Data IPAK berdasarkan tingkat pendidikan belum tersedia pada rentang tahun yang dipilih (data baru ada sejak 2021).")

st.markdown("---")

# ----------------------------------------------------------------------------
# GRAFIK 5 - HEATMAP KORELASI ANTAR INDIKATOR
# ----------------------------------------------------------------------------
st.subheader("5️⃣ Korelasi Antar Indikator IPAK")

kolom_numerik = [
    "IPAK_Nasional",
    "Indeks_Persepsi",
    "Indeks_Pengalaman",
    "IPAK_Perkotaan",
    "IPAK_Perdesaan",
    "IPAK_Pendidikan_Di_bawah_SLTA",
    "IPAK_Pendidikan_SLTA",
    "IPAK_Pendidikan_Di_atas_SLTA",
]
df_numerik = df_filtered[kolom_numerik].dropna(thresh=2)

if df_numerik.shape[0] >= 2:
    corr = df_numerik.corr()
    label_singkat = {
        "IPAK_Nasional": "Nasional",
        "Indeks_Persepsi": "Persepsi",
        "Indeks_Pengalaman": "Pengalaman",
        "IPAK_Perkotaan": "Perkotaan",
        "IPAK_Perdesaan": "Perdesaan",
        "IPAK_Pendidikan_Di_bawah_SLTA": "Di bawah SLTA",
        "IPAK_Pendidikan_SLTA": "SLTA",
        "IPAK_Pendidikan_Di_atas_SLTA": "Di atas SLTA",
    }
    corr = corr.rename(index=label_singkat, columns=label_singkat)

    fig5 = px.imshow(
        corr,
        text_auto=".2f",
        color_continuous_scale="RdBu_r",
        zmin=-1,
        zmax=1,
        title="Heatmap Korelasi Antar Indikator IPAK",
        aspect="auto",
    )
    fig5.update_layout(height=550)
    st.plotly_chart(fig5, use_container_width=True)
    st.caption(
        "ℹ️ Korelasi dihitung dari data yang tersedia pada rentang tahun terpilih. "
        "Karena sebagian indikator baru ada sejak 2020/2021, jumlah data yang dipakai untuk korelasi terbatas."
    )
else:
    st.info("Data tidak cukup untuk menghitung korelasi pada rentang tahun yang dipilih.")

st.markdown("---")

# ----------------------------------------------------------------------------
# TABEL DATA MENTAH
# ----------------------------------------------------------------------------
with st.expander("📄 Lihat Data Mentah"):
    st.dataframe(df_filtered, use_container_width=True)
    st.download_button(
        label="⬇️ Unduh Data (CSV)",
        data=df_filtered.to_csv(index=False).encode("utf-8"),
        file_name="ipak_filtered.csv",
        mime="text/csv",
    )

st.caption("Dashboard dibuat dengan Streamlit & Plotly | Data: BPS - Survei Perilaku Anti Korupsi (SPAK)")
