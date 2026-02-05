import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

# Set halaman agar lebih lebar dan modern
st.set_page_config(page_title="App Kasir Keuangan", layout="wide")

# Gaya CSS Kustom untuk tampilan kartu
st.markdown("""
    <style>
    .stMetric {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 15px;
        box-shadow: 2px 2px 10px rgba(0,0,0,0.1);
    }
    </style>
    """, unsafe_allow_html=True)

# Inisialisasi data agar tidak hilang
if 'data' not in st.session_state:
    st.session_state.data = pd.DataFrame(columns=['Tipe', 'Kategori', 'Jumlah', 'Tanggal'])

# --- NAVIGASI HALAMAN ---
st.sidebar.title("🏧 MENU KASIR")
menu = st.sidebar.radio("Pilih Halaman:", ["Input Transaksi (Kasir)", "Laporan & Grafik"])

if menu == "Input Transaksi (Kasir)":
    st.title("🛒 Input Transaksi")
    st.info("Gunakan halaman ini untuk memasukkan data transaksi harian.")
    
    with st.container():
        col1, col2 = st.columns(2)
        with col1:
            tipe = st.selectbox("Jenis Transaksi", ["Pemasukan", "Pengeluaran"])
            kategori = st.text_input("Nama Barang / Kategori", placeholder="Contoh: Jual Kopi / Bayar Listrik")
        with col2:
            jumlah = st.number_input("Jumlah (Rp)", min_value=0, step=1000)
            tanggal = st.date_input("Tanggal", value=datetime.today())
        
        if st.button("🔴 SIMPAN TRANSAKSI", use_container_width=True):
            if kategori and jumlah > 0:
                new_data = pd.DataFrame({'Tipe': [tipe], 'Kategori': [kategori], 'Jumlah': [jumlah], 'Tanggal': [tanggal]})
                st.session_state.data = pd.concat([st.session_state.data, new_data], ignore_index=True)
                st.success("✅ Berhasil disimpan!")
            else:
                st.warning("Mohon isi nama kategori dan jumlah uang!")

elif menu == "Laporan & Grafik":
    st.title("📊 Laporan Keuangan")
    
    # Ringkasan Angka
    income = st.session_state.data[st.session_state.data['Tipe'] == 'Pemasukan']['Jumlah'].sum()
    expense = st.session_state.data[st.session_state.data['Tipe'] == 'Pengeluaran']['Jumlah'].sum()
    saldo = income - expense
    
    c1, c2, c3 = st.columns(3)
    c1.metric("Sisa Saldo", f"Rp {saldo:,.0f}")
    c2.metric("Total Masuk", f"Rp {income:,.0f}", delta_color="normal")
    c3.metric("Total Keluar", f"Rp {expense:,.0f}", delta="-")
    
    st.divider()
    
    # Bagian Visualisasi
    col_chart1, col_chart2 = st.columns(2)
    
    with col_chart1:
        st.subheader("🥧 Distribusi Pengeluaran")
        df_exp = st.session_state.data[st.session_state.data['Tipe'] == 'Pengeluaran']
        if not df_exp.empty:
            fig = px.pie(df_exp, values='Jumlah', names='Kategori', hole=0.5, color_discrete_sequence=px.colors.sequential.RdBu)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.write("Belum ada data pengeluaran.")

    with col_chart2:
        st.subheader("📑 Tabel Riwayat Transaksi")
        st.dataframe(st.session_state.data, use_container_width=True)

    # Tombol Ekspor
    st.download_button(
        label="📥 Download Data ke Excel",
        data=st.session_state.data.to_csv(index=False),
        file_name="laporan_kasir.csv",
        mime="text/csv"
    )
