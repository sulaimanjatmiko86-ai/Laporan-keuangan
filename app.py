import streamlit as st
import pandas as pd
from datetime import datetime
import requests

# 1. SETTING HALAMAN
st.set_page_config(page_title="Kasir Jaya Cloud", layout="wide")

# 2. DATABASE STOK (Sifatnya sementara di memori browser)
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
    # Link Response Form kamu
    url = "https://docs.google.com/forms/d/e/1FAIpQLSc8wjCuUX01A4MRBLuGx1UaAIAhdQ6G9yPsnhskJ1fKtEFzgA/formResponse"
    
    # ID ini diambil langsung dari link yang kamu kirim
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

# 4. TAMPILAN
st.markdown("<h2 style='text-align: center;'>🏪 KASIR JAYA DIGITAL</h2>", unsafe_allow_html=True)

menu = st.sidebar.radio("MENU", ["🛒 Kasir", "📦 Stok", "📊 Laporan"])

if menu == "🛒 Kasir":
    with st.expander("Kasir", expanded=True):
        pilihan = st.selectbox("Pilih Produk:", list(st.session_state.master_barang.keys()))
        qty = st.number_input("Jumlah:", min_value=1, value=1)
        
        total = st.session_state.master_barang[pilihan][0] * qty
        st.write(f"### Tagihan: Rp {total:,.0f}")
        
        # Pembayaran
        c1, c2 = st.columns(2)
        with c1:
            if st.button("💵 UANG PAS"): st.session_state.jml_bayar = total
            manual = st.number_input("Bayar (Rp):", min_value=0, step=500)
            if manual > 0: st.session_state.jml_bayar = manual
            
        if st.session_state.jml_bayar >= total and st.session_state.jml_bayar > 0:
            kembali = st.session_state.jml_bayar - total
            st.warning(f"Kembalian: Rp {kembali:,.0f}")
            
            if st.button("✅ PROSES & SIMPAN CLOUD", use_container_width=True):
                tgl = datetime.today().strftime('%Y-%m-%d')
                # KIRIM KE GOOGLE
                berhasil = simpan_permanen("Pemasukan", pilihan, total, tgl)
                
                if berhasil:
                    st.session_state.master_barang[pilihan][1] -= qty
                    st.success("Berhasil! Data sudah masuk ke Google Sheets.")
                    st.balloons()
                    st.session_state.jml_bayar = 0
                else:
                    st.error("Gagal simpan! Periksa koneksi internet.")

elif menu == "📦 Stok":
    st.write("### Daftar Stok")
    st.table(pd.DataFrame.from_dict(st.session_state.master_barang, orient='index', columns=['Harga', 'Stok']))

else:
    st.write("### Laporan")
    st.info("Riwayat transaksi tersimpan permanen di Google Sheets kamu.")
