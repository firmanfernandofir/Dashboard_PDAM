import streamlit as st
import pandas as pd
import numpy as np
import plotly.figure_factory as ff

# Judul dashboard
st.title("📊 Dashboard Evaluasi Cabang PDAM (Naik/Turun)")

# Upload file Excel
uploaded_file = st.file_uploader("/content/Data Evaluasi Cabang PDAM.xlsx", type=["xlsx"])

if uploaded_file:
    # Ambil semua sheet dari file Excel
    xls = pd.ExcelFile(uploaded_file)
    semua_sheet = xls.sheet_names

    st.write("📑 **Sheet tersedia:**", semua_sheet)

    # Pilihan bulan pembanding
    col1, col2 = st.columns(2)
    with col1:
        bulan_awal = st.selectbox("📅 Pilih Sheet Awal", semua_sheet, index=0)
    with col2:
        bulan_akhir = st.selectbox("📅 Pilih Sheet Pembanding", semua_sheet, index=1)

    # Pastikan sheet berbeda
    if bulan_akhir == bulan_awal:
        st.warning("⚠️ Pilih dua sheet yang berbeda untuk dibandingkan!")
    else:
        # Baca dua sheet
        df_awal = pd.read_excel(uploaded_file, sheet_name=bulan_awal)
        df_akhir = pd.read_excel(uploaded_file, sheet_name=bulan_akhir)

        # Samakan nama kolom
        df_awal.columns = df_awal.columns.str.strip()
        df_akhir.columns = df_akhir.columns.str.strip()

        # Gabungkan dua bulan berdasarkan kolom CABANG
        if "CABANG" not in df_awal.columns or "CABANG" not in df_akhir.columns:
            st.error("❌ Kolom 'CABANG' tidak ditemukan pada salah satu sheet!")
        else:
            df = pd.merge(df_awal, df_akhir, on="CABANG", suffixes=(f"_{bulan_awal}", f"_{bulan_akhir}"))

            # Daftar kolom yang akan dibandingkan
            pairs = [
                ("JUMLAH PELANGGAN BULAN", "Pelanggan"),
                ("KONSUMSI GOL 2 BULAN", "Konsumsi Gol 2"),
                ("KONSUMSI TOTAL BULAN", "Konsumsi Total"),
                ("AIR DISTRIBUSI BULAN", "Distribusi"),
                ("AIR TERJUAL BULAN", "Terjual"),
                ("PENDAPATAN AIR BULAN", "Pendapatan"),
            ]

            # Loop setiap pasangan dan hitung NAIK/TURUN
            for base, label in pairs:
                col_awal = [c for c in df.columns if base in c and bulan_awal.upper() in c]
                col_akhir = [c for c in df.columns if base in c and bulan_akhir.upper() in c]
                if col_awal and col_akhir:
                    df[label] = np.where(df[col_akhir[0]] > df[col_awal[0]], "NAIK", "TURUN")
                else:
                    df[label] = "DATA TIDAK ADA"

            # Pilih kolom utama untuk visualisasi
            df_status = df[["CABANG", "Pelanggan", "Konsumsi Gol 2", "Konsumsi Total", "Distribusi", "Terjual", "Pendapatan"]]

            # Tampilkan tabel hasil
            st.subheader(f"📈 Kondisi Cabang PDAM: {bulan_awal} → {bulan_akhir}")
            st.dataframe(df_status, use_container_width=True)

            # Buat heatmap warna (NAIK = hijau, TURUN = oranye)
            status_matrix = df_status.set_index("CABANG").replace({"NAIK": 1, "TURUN": 0, "DATA TIDAK ADA": np.nan})
            fig = ff.create_annotated_heatmap(
                z=status_matrix.fillna(0.5).values,
                x=status_matrix.columns.tolist(),
                y=status_matrix.index.tolist(),
                annotation_text=df_status.set_index("CABANG").values,
                colorscale=[[0, "#f4a261"], [0.5, "#cccccc"], [1, "#2a9d8f"]],  # oranye / abu / hijau
                showscale=False
            )

            st.plotly_chart(fig, use_container_width=True)

            # Tambahkan keterangan warna
            st.markdown(f"""
            **Keterangan warna:**
            - 🟩 **NAIK** → nilai {bulan_akhir} lebih besar dari {bulan_awal}  
            - 🟧 **TURUN** → nilai {bulan_akhir} lebih kecil atau sama dengan {bulan_awal}  
            - ⬜ **DATA TIDAK ADA** → kolom tidak ditemukan di salah satu sheet
            """)

else:
    st.info("Silakan unggah file Excel terlebih dahulu.")
