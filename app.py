import streamlit as st
import pandas as pd
from datetime import datetime
import requests
import time

# 1. KONFIGURASI
st.set_page_config(page_title="Kasir Jaya", layout="centered", page_icon="🏪")

# CSS untuk mengecilkan tombol uang dan merapikan tampilan
st.markdown("""
    <style>
    .stButton>button { 
        padding: 5px !important; 
        font-size: 14px !important; 
        height: 2.5em !important; 
        border-radius: 8px;
    }
    .main-header { text-align: center; color: #1e3c72; margin-bottom: 20px; }
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

# 3. FUNGSI SIMPAN KE GOOGLE (DIPERBAIKI)
def simpan_ke_cloud(kategori, jumlah):
    # Gunakan URL formResponse yang benar
    url = "https://docs.google.com/forms/d/e/1FAIpQLSc8wjCuUX01A4MRBLuGx1UaAIAhdQ6G9yPsnhskJ1fKtEFzgA/formResponse"
    tgl = datetime.today().strftime('%Y-%m-%d')
    
    # Payload dengan ID Entry yang sudah divalidasi
    payload = {
        "entry.1444153920": "Pemasukan",
        "entry.2065873155": kategori,
        "entry.143715201": str(jumlah), # Pastikan jumlah terkirim sebagai string
        "entry.1098693740": tgl
    }
    
    try:
        # Menambahkan timeout agar tidak menggantung jika sinyal jelek
        response = requests.post(url, data=payload, timeout=10)
        return response.status_code == 200 or response.status_code == 302
    except:
        return False

# 4. TAMPILAN UTAMA
st.markdown("<h2 class='main-header'>🏪 KASIR JAYA DIGITAL</h2>", unsafe_allow_html=True)

menu = st.sidebar.radio("MENU", ["🛒 Kasir Utama", "📦 Stok Barang", "📊 Laporan"])

if menu == "🛒 Kasir Utama":
    pilihan = st.selectbox("Pilih Produk:", list(st.session_state.master_barang.keys()))
    qty = st.number_input("Jumlah Beli:", min_value=1, value=1)
    
    harga = st.session_state.master_barang[pilihan][0]
    stok_skrg = st.session_state.master_barang[pilihan][1]
    total = harga * qty
    
    st.info(f"Stok: {stok_skrg} | Tagihan: Rp {total:,.0f}")
    st.divider()

    # --- TOMBOL UANG VERSI KECIL ---
    st.write("### 💰 Pembayaran")
    
    # Baris 1: Uang Pas & Pecahan Kecil
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        if st.button("PAS", use_container_width=True): st.session_state.jml_bayar = total
    with c2:
        if st.button("5rb", use_container_width=True): st.session_state.jml_bayar = 5000
    with c3:
        if st.button("10rb", use_container_width=True): st.session_state.jml_bayar = 10000
    with c4:
        if st.button("20rb", use_container_width=True): st.session_state.jml_bayar = 20000

    # Baris 2: Pecahan Besar & Manual
    c5, c6, c7 = st.columns([1, 1, 2])
    with c5:
        if st.button("50rb", use_container_width=True): st.session_state.jml_bayar = 50000
    with c6:
        if st.button("100rb", use_container_width=True): st.session_state.jml_bayar = 100000
    with c7:
        input_manual = st.number_input("Manual (Rp):", min_value=0, step=500, label_visibility="collapsed")
        if input_manual > 0: st.session_state.jml_bayar = input_manual

    st.markdown(f"**Diterima: Rp {st.session_state.jml_bayar:,.0f}**")

    if st.session_state.jml_bayar >= total and st.session_state.jml_bayar > 0:
        kembali = st.session_state.jml_bayar - total
        st.warning(f"Kembalian: Rp {kembali:,.0f}")
        
        if st.button("✅ SELESAIKAN & SIMPAN", use_container_width=True):
            if qty <= stok_skrg:
                with st.spinner('Menyimpan ke Cloud...'):
                    if simpan_ke_cloud(pilihan, total):
                        st.session_state.master_barang[pilihan][1] -= qty
                        st.success("Tersimpan!")
                        st.balloons()
                        time.sleep(1) # Jeda sebentar agar user bisa lihat pesan sukses
                        st.session_state.jml_bayar = 0 
                        st.rerun()
                    else:
                        st.error("Gagal simpan! Pastikan internet aktif.")
            else:
                st.error("Stok Kurang!")

elif menu == "📦 Stok Barang":
    st.subheader("Manajemen Stok")
    df_stok = pd.DataFrame.from_dict(st.session_state.master_barang, orient='index', columns=['Harga', 'Stok'])
    st.data_editor(df_stok)

else:
    st.subheader("📊 Laporan")
    st.write("Data tersimpan di Google Sheets.")
