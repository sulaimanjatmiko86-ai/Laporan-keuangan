import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

# 1. TAMPILAN MEWAH (INFOGRAFIS)
st.set_page_config(page_title="Kasir Jaya Digital", layout="wide", page_icon="🏪")

# 2. DATABASE BARANG (Bisa kamu tambah sendiri di sini)
if 'master_barang' not in st.session_state:
    st.session_state.master_barang = {
        "Kopi Espresso": 15000,
        "Roti Bakar": 20000,
        "Air Mineral": 5000,
        "Teh Manis": 8000,
        "Indomie Telur": 12000
    }

# 3. PENYIMPANAN DATA
if 'data' not in st.session_state:
    st.session_state.data = pd.DataFrame(columns=['Tipe', 'Kategori', 'Jumlah', 'Tanggal'])

# 4. GAYA DESAIN (CSS)
st.markdown("""
    <style>
    .header-box {
        text-align: center;
        padding: 25px;
        background: linear-gradient(to right, #1e3c72, #2a5298);
        color: white;
        border-radius: 15px;
        margin-bottom: 20px;
    }
    .stMetric {
        background-color: #ffffff;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    </style>
    """, unsafe_allow_html=True)

# 5. JUDUL TOKO
st.markdown('<div class="header-box"><h1>🏪 KASIR JAYA DIGITAL</h1><p>Sistem Laporan Keuangan Modern</p></div>', unsafe_allow_html=True)

# 6. MENU NAVIGASI
with st.sidebar:
    st.title("📌 MENU")
    menu = st.radio("Pilih Halaman:", ["🛒 Mesin Kasir", "📦 Tambah Barang", "📊 Laporan"])

# --- HALAMAN 1: KASIR ---
if menu == "🛒 Mesin Kasir":
    st.subheader("📝 Catat Transaksi")
    col1, col2 = st.columns([2, 1])
    
    with col1:
        with st.expander("✨ Pilih Produk Otomatis", expanded=True):
            daftar = ["--- Pilih Barang ---"] + list(st.session_state.master_barang.keys())
            pilihan = st.selectbox("Cari Produk:", daftar)
            qty = st.number_input("Jumlah:", min_value=1, value=1)
            harga = st.session_state.master_barang.get(pilihan, 0)
            total = harga * qty
            if pilihan != "--- Pilih Barang ---":
                st.write(f"Subtotal: **Rp {total:,.0f}**")
                if st.button("➕ Tambah ke Kasir"):
                    new_row = pd.DataFrame({'Tipe':['Pemasukan'], 'Kategori':[pilihan], 'Jumlah':[total], 'Tanggal':[datetime.today().date()]})
                    st.session_state.data = pd.concat([st.session_state.data, new_row], ignore_index=True)
                    st.success("Berhasil ditambahkan!")

    with col2:
        with st.expander("✍️ Input Manual"):
            tipe_m = st.selectbox("Jenis:", ["Pemasukan", "Pengeluaran"])
            nama_m = st.text_input("Keterangan:")
            jumlah_m = st.number_input("Nominal (Rp):", min_value=0)
            if st.button("💾 Simpan"):
                if nama_m and jumlah_m > 0:
                    new_row = pd.DataFrame({'Tipe':[tipe_m], 'Kategori':[nama_m], 'Jumlah':[jumlah_m], 'Tanggal':[datetime.today().date()]})
                    st.session_state.data = pd.concat([st.session_state.data, new_row], ignore_index=True)
                    st.success("Data tersimpan!")

# --- HALAMAN 2: TAMBAH BARANG ---
elif menu == "📦 Tambah Barang":
    st.subheader("⚙️ Atur Daftar Produk")
    with st.form("add_p"):
        n = st.text_input("Nama Barang Baru:")
        h = st.number_input("Harga Jual (Rp):", min_value=0)
        if st.form_submit_button("✅ Simpan ke Menu"):
            if n and h > 0:
                st.session_state.master_barang[n] = h
                st.success(f"'{n}' sudah masuk di menu kasir!")

# --- HALAMAN 3: LAPORAN ---
else:
    st.subheader("📊 Dashboard Laporan")
    in_sum = st.session_state.data[st.session_state.data['Tipe'] == 'Pemasukan']['Jumlah'].sum()
    out_sum = st.session_state.data[st.session_state.data['Tipe'] == 'Pengeluaran']['Jumlah'].sum()
    
    c1, c2, c3 = st.columns(3)
    c1.metric("💰 Saldo", f"Rp {in_sum - out_sum:,.0f}")
    c2.metric("📈 Masuk", f"Rp {in_sum:,.0f}")
    c3.metric("📉 Keluar", f"Rp {out_sum:,.0f}")
    
    st.divider()
    col_a, col_b = st.columns(2)
    with col_a:
        if not st.session_state.data.empty:
            fig = px.pie(st.session_state.data, values='Jumlah', names='Tipe', hole=0.5, title="Arus Kas")
            st.plotly_chart(fig, use_container_width=True)
    with col_b:
        st.write("**Riwayat Transaksi**")
        st.dataframe(st.session_state.data, use_container_width=True)
