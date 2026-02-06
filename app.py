import streamlit as st
import pandas as pd
from datetime import datetime
import requests

# 1. KONFIGURASI TAMPILAN
st.set_page_config(page_title="Kasir Jaya", layout="centered")

# CSS untuk mengecilkan tombol dan menyusun ke samping
st.markdown("""
    <style>
    div.stButton > button {
        height: 35px !important;
        font-size: 13px !important;
        padding: 0px 2px !important;
        border-radius: 6px;
        margin-bottom: -10px;
    }
    .stNumberInput { margin-top: -15px; }
    </style>
    """, unsafe_allow_html=True)

# 2. DATABASE BARANG
if 'master_barang' not in st.session_state:
    st.session_state.master_barang = {
        "Kopi Espresso": [15000, 50],
        "Roti Bakar": [20000, 30],
        "Air Mineral": [5000, 100]
    }

if 'jml_bayar' not in st.session_state:
    st.session_state.jml_bayar = 0

# 3. FUNGSI SIMPAN KE CLOUD (MENGGUNAKAN 4 ENTRY BARU)
def simpan_ke_cloud(kategori, jumlah):
    url = "https://docs.google.com/forms/d/e/1FAIpQLSc8wjCuUX01A4MRBLuGx1UaAIAhdQ6G9yPsnhskJ1fKtEFzgA/formResponse"
    tgl_skrg = datetime.today().strftime('%Y-%m-%d')
    
    # ID Entry berdasarkan link terakhir kamu
    payload = {
        "entry.1005808381": "Pemasukan",   # Tipe
        "entry.544255428": kategori,       # Katagori
        "entry.1418739506": str(jumlah),    # Jumlah
        "entry.1637268017": tgl_skrg        # tanggal
    }
    
    try:
        requests.post(url, data=payload, timeout=5)
        return True
    except:
        return False

# 4. TAMPILAN UTAMA
st.subheader("🏪 KASIR JAYA")

pilihan = st.selectbox("Produk:", list(st.session_state.master_barang.keys()))
qty = st.number_input("Jumlah:", min_value=1, value=1)

total = st.session_state.master_barang[pilihan][0] * qty
st.markdown(f"### Total: Rp {total:,.0f}")

st.write("---")
st.write("💰 **Klik Uang Pembayaran:**")

# --- TOMBOL MENYAMPING (6 KOLOM) ---
c1, c2, c3, c4, c5, c6 = st.columns(6)
with c1:
    if st.button("PAS"): st.session_state.jml_bayar = total
with c2:
    if st.button("5rb"): st.session_state.jml_bayar = 5000
with c3:
    if st.button("10rb"): st.session_state.jml_bayar = 10000
with c4:
    if st.button("20rb"): st.session_state.jml_bayar = 20000
with c5:
    if st.button("50rb"): st.session_state.jml_bayar = 50000
with c6:
    if st.button("100rb"): st.session_state.jml_bayar = 100000

# Input manual jika uangnya receh
manual = st.number_input("Ketik Manual (Rp):", min_value=0, step=500)
if manual > 0:
    st.session_state.jml_bayar = manual

st.write(f"Diterima: **Rp {st.session_state.jml_bayar:,.0f}**")

# Logika Bayar
if st.session_state.jml_bayar >= total and st.session_state.jml_bayar > 0:
    kembali = st.session_state.jml_bayar - total
    st.warning(f"Kembalian: Rp {kembali:,.0f}")
    
    if st.button("✅ SELESAIKAN & SIMPAN CLOUD", use_container_width=True):
        if simpan_ke_cloud(pilihan, total):
            st.session_state.master_barang[pilihan][1] -= qty
            st.success("BERHASIL! Cek Google Sheets kamu.")
            st.balloons()
            st.session_state.jml_bayar = 0 
        else:
            st.error("Gagal kirim data.")

# Sidebar untuk cek stok
with st.sidebar:
    st.title("Admin")
    if st.checkbox("Lihat Stok Barang"):
        st.write(pd.DataFrame.from_dict(st.session_state.master_barang, orient='index', columns=['Harga', 'Stok']))
