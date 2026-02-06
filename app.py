import streamlit as st
import pandas as pd
from datetime import datetime
import requests

# 1. KONFIGURASI TAMPILAN
st.set_page_config(page_title="Kasir Jaya", layout="centered")

# CSS Agar rapi di HP & Laptop
st.markdown("""
    <style>
    /* Mengecilkan tombol agar pas di layar HP */
    div.stButton > button {
        width: 100%;
        height: 45px !important;
        font-size: 14px !important;
        border-radius: 10px;
        margin-bottom: 5px;
        background-color: #f8f9fa;
        color: #333;
        border: 1px solid #ddd;
    }
    div.stButton > button:hover { border-color: #007bff; color: #007bff; }
    </style>
    """, unsafe_allow_html=True)

# 2. DATABASE (Tambah hitungan Terjual)
if 'master_barang' not in st.session_state:
    # Format: [Harga, Stok, Terjual]
    st.session_state.master_barang = {
        "Kopi Espresso": [15000, 50, 0],
        "Roti Bakar": [20000, 30, 0],
        "Air Mineral": [5000, 100, 0]
    }

if 'jml_bayar' not in st.session_state:
    st.session_state.jml_bayar = 0

# 3. FUNGSI SIMPAN KE CLOUD
def simpan_ke_cloud(kategori, jumlah):
    url = "https://docs.google.com/forms/d/e/1FAIpQLSc8wjCuUX01A4MRBLuGx1UaAIAhdQ6G9yPsnhskJ1fKtEFzgA/formResponse"
    tgl_skrg = datetime.today().strftime('%Y-%m-%d')
    payload = {
        "entry.1005808381": "Pemasukan",
        "entry.544255428": kategori,
        "entry.1418739506": str(jumlah),
        "entry.1637268017": tgl_skrg
    }
    try:
        requests.post(url, data=payload, timeout=5)
        return True
    except:
        return False

# 4. TAMPILAN UTAMA
st.markdown("<h3 style='text-align: center;'>🏪 KASIR JAYA DIGITAL</h3>", unsafe_allow_html=True)

menu = st.sidebar.radio("MENU", ["🛒 Kasir", "📦 Stok & Terjual"])

if menu == "🛒 Kasir":
    pilihan = st.selectbox("Pilih Produk:", list(st.session_state.master_barang.keys()))
    qty = st.number_input("Jumlah:", min_value=1, value=1)
    
    total = st.session_state.master_barang[pilihan][0] * qty
    st.markdown(f"### Total: Rp {total:,.0f}")
    st.divider()

    # --- TOMBOL UANG (Rapi di HP: 3 Kolom x 2 Baris) ---
    st.write("💰 **Pilih Pembayaran:**")
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("PAS"): st.session_state.jml_bayar = total
        if st.button("20rb"): st.session_state.jml_bayar = 20000
    with col2:
        if st.button("5rb"): st.session_state.jml_bayar = 5000
        if st.button("50rb"): st.session_state.jml_bayar = 50000
    with col3:
        if st.button("10rb"): st.session_state.jml_bayar = 10000
        if st.button("100rb"): st.session_state.jml_bayar = 100000

    input_manual = st.number_input("Ketik Manual (Rp):", min_value=0, step=500)
    if input_manual > 0: st.session_state.jml_bayar = input_manual

    st.write(f"Diterima: **Rp {st.session_state.jml_bayar:,.0f}**")

    if st.session_state.jml_bayar >= total and st.session_state.jml_bayar > 0:
        kembali = st.session_state.jml_bayar - total
        st.warning(f"Kembalian: Rp {kembali:,.0f}")
        
        if st.button("✅ SELESAIKAN & SIMPAN", use_container_width=True):
            if simpan_ke_cloud(pilihan, total):
                # Update Stok & Terjual
                st.session_state.master_barang[pilihan][1] -= qty # Kurangi Stok
                st.session_state.master_barang[pilihan][2] += qty # Tambah Terjual
                
                st.success("BERHASIL DISIMPAN!")
                st.balloons()
                st.session_state.jml_bayar = 0 
                st.rerun()

# --- MENU STOK & TERJUAL ---
else:
    st.subheader("📦 Data Stok & Penjualan")
    # Tampilkan tabel yang lebih informatif
    df = pd.DataFrame.from_dict(
        st.session_state.master_barang, 
        orient='index', 
        columns=['Harga', 'Sisa Stok', 'Total Terjual']
    )
    st.table(df)
    
    if st.button("Reset Terjual"):
        for k in st.session_state.master_barang:
            st.session_state.master_barang[k][2] = 0
        st.rerun()
