import streamlit as st
import pandas as pd
from datetime import datetime
import requests

# 1. SETTING HALAMAN
st.set_page_config(page_title="Kasir Jaya Cloud", layout="wide", page_icon="🏪")

# 2. DATABASE STOK (PENTING: Dalam Streamlit Cloud, stok akan reset jika app di-reboot)
if 'master_barang' not in st.session_state:
    st.session_state.master_barang = {
        "Kopi Espresso": [15000, 50],
        "Roti Bakar": [20000, 30],
        "Air Mineral": [5000, 100]
    }

if 'jml_bayar' not in st.session_state:
    st.session_state.jml_bayar = 0

# 3. FUNGSI SIMPAN KE GOOGLE SHEETS
def simpan_permanen(tipe, kategori, jumlah, tanggal):
    url = "https://docs.google.com/forms/d/e/1FAIpQLSc8wjCuUX01A4MRBLuGx1UaAIAhdQ6G9yPsnhskJ1fKtEFzgA/formResponse"
    data_form = {
        "entry.1444153920": tipe,
        "entry.2065873155": kategori,
        "entry.143715201": jumlah,
        "entry.1098693740": tanggal
    }
    try:
        res = requests.post(url, data=data_form)
        return res.status_code == 200
    except:
        return False

# 4. TAMPILAN HEADER
st.markdown("<h2 style='text-align: center;'>🏪 KASIR JAYA DIGITAL</h2>", unsafe_allow_html=True)

menu = st.sidebar.radio("MENU", ["🛒 Kasir", "📦 Stok Barang", "📊 Laporan"])

# --- HALAMAN 1: KASIR ---
if menu == "🛒 Kasir":
    with st.expander("Kasir", expanded=True):
        pilihan = st.selectbox("Pilih Produk:", list(st.session_state.master_barang.keys()))
        qty = st.number_input("Jumlah Beli:", min_value=1, value=1)
        
        harga = st.session_state.master_barang[pilihan][0]
        stok_skrg = st.session_state.master_barang[pilihan][1]
        total = harga * qty
        
        st.write(f"Stok tersedia: **{stok_skrg}**")
        st.write(f"### Tagihan: Rp {total:,.0f}")
        
        c1, c2 = st.columns(2)
        with c1:
            if st.button("💵 UANG PAS"): st.session_state.jml_bayar = total
            manual = st.number_input("Bayar (Rp):", min_value=0, step=500)
            if manual > 0: st.session_state.jml_bayar = manual
            
        if st.session_state.jml_bayar >= total and st.session_state.jml_bayar > 0:
            kembali = st.session_state.jml_bayar - total
            st.info(f"Kembalian: Rp {kembali:,.0f}")
            
            if st.button("✅ SELESAIKAN & SIMPAN CLOUD", use_container_width=True):
                if qty <= stok_skrg:
                    tgl = datetime.today().strftime('%Y-%m-%d')
                    if simpan_permanen("Pemasukan", pilihan, total, tgl):
                        st.session_state.master_barang[pilihan][1] -= qty
                        st.success("Tersimpan di Google Sheets!")
                        st.balloons()
                        st.session_state.jml_bayar = 0
                    else:
                        st.error("Gagal simpan ke Cloud!")
                else:
                    st.error("Stok tidak cukup!")

# --- HALAMAN 2: STOK (SUDAH DIPERBAIKI) ---
elif menu == "📦 Stok Barang":
    st.subheader("🔧 Kelola Stok & Produk")
    
    tab1, tab2 = st.tabs(["Update Stok", "Tambah Produk Baru"])
    
    with tab1:
        item_edit = st.selectbox("Pilih Barang yang akan diubah:", list(st.session_state.master_barang.keys()))
        stok_lama = st.session_state.master_barang[item_edit][1]
        
        st.write(f"Stok saat ini: **{stok_lama}**")
        perubahan = st.number_input("Tambah/Kurang Stok (Gunakan minus '-' untuk mengurangi):", value=0)
        
        if st.button("Simpan Perubahan Stok"):
            st.session_state.master_barang[item_edit][1] += perubahan
            st.success(f"Stok {item_edit} berhasil diupdate menjadi {st.session_state.master_barang[item_edit][1]}!")
            st.rerun()

    with tab2:
        with st.form("tambah_baru"):
            nama_baru = st.text_input("Nama Barang Baru:")
            harga_baru = st.number_input("Harga Jual:", min_value=0)
            stok_awal = st.number_input("Stok Awal:", min_value=0)
            if st.form_submit_button("Tambah Produk"):
                if nama_baru:
                    st.session_state.master_barang[nama_baru] = [harga_baru, stok_awal]
                    st.success(f"{nama_baru} berhasil ditambahkan!")
                    st.rerun()

# --- HALAMAN 3: LAPORAN ---
else:
    st.write("### Laporan")
    st.info("Riwayat transaksi tersimpan permanen di Google Sheets kamu.")
