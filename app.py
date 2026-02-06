import streamlit as st
import pandas as pd
from datetime import datetime
import requests

# 1. KONFIGURASI & TEMA
st.set_page_config(page_title="Kasir Jaya", layout="wide", page_icon="🏪")

# 2. DATABASE BARANG
if 'master_barang' not in st.session_state:
    st.session_state.master_barang = {
        "Kopi Espresso": [15000, 50],
        "Roti Bakar": [20000, 30],
        "Air Mineral": [5000, 100]
    }

if 'jml_bayar' not in st.session_state:
    st.session_state.jml_bayar = 0

# 3. FUNGSI SIMPAN KE GOOGLE SHEETS
def simpan_ke_cloud(kategori, jumlah):
    url = "https://docs.google.com/forms/d/e/1FAIpQLSc8wjCuUX01A4MRBLuGx1UaAIAhdQ6G9yPsnhskJ1fKtEFzgA/formResponse"
    tgl = datetime.today().strftime('%Y-%m-%d')
    payload = {
        "entry.1444153920": "Pemasukan",
        "entry.2065873155": kategori,
        "entry.143715201": jumlah,
        "entry.1098693740": tgl
    }
    try:
        requests.post(url, data=payload)
        return True
    except:
        return False

# 4. TAMPILAN UTAMA
st.markdown("<h2 style='text-align: center;'>🏪 KASIR JAYA DIGITAL</h2>", unsafe_allow_html=True)

menu = st.sidebar.radio("MENU", ["🛒 Kasir Utama", "📦 Stok Barang", "📊 Laporan"])

if menu == "🛒 Kasir Utama":
    with st.container():
        st.subheader("📝 Transaksi")
        pilihan = st.selectbox("Pilih Produk:", list(st.session_state.master_barang.keys()))
        qty = st.number_input("Jumlah Beli:", min_value=1, value=1)
        
        harga = st.session_state.master_barang[pilihan][0]
        stok_skrg = st.session_state.master_barang[pilihan][1]
        total = harga * qty
        
        st.write(f"Stok: **{stok_skrg}** | Harga: **Rp {harga:,.0f}**")
        st.markdown(f"## Total Tagihan: Rp {total:,.0f}")
        st.divider()

        # --- BAGIAN PEMBAYARAN OTOMATIS & MANUAL ---
        st.write("### 💰 Pembayaran")
        c1, c2, c3 = st.columns([1, 1, 1])
        
        with c1:
            if st.button("💵 UANG PAS", use_container_width=True):
                st.session_state.jml_bayar = total
        with c2:
            # Tombol bantuan uang pecahan umum
            if st.button("💵 Rp 50.000", use_container_width=True):
                st.session_state.jml_bayar = 50000
            if st.button("💵 Rp 100.000", use_container_width=True):
                st.session_state.jml_bayar = 100000
        with c3:
            # Input manual tetap ada
            input_manual = st.number_input("Ketik Manual (Rp):", min_value=0, step=500, key="manual")
            if input_manual > 0:
                st.session_state.jml_bayar = input_manual

        st.markdown(f"### Diterima: **Rp {st.session_state.jml_bayar:,.0f}**")

        if st.session_state.jml_bayar >= total and st.session_state.jml_bayar > 0:
            kembali = st.session_state.jml_bayar - total
            st.success(f"Kembalian: Rp {kembali:,.0f}")
            
            if st.button("✅ SELESAIKAN & SIMPAN CLOUD", use_container_width=True):
                if qty <= stok_skrg:
                    if simpan_ke_cloud(pilihan, total):
                        st.session_state.master_barang[pilihan][1] -= qty
                        st.success("Berhasil! Data masuk ke Google Sheets.")
                        st.balloons()
                        st.session_state.jml_bayar = 0 # Reset uang bayar
                    else:
                        st.error("Gagal simpan ke Cloud!")
                else:
                    st.error("Stok tidak cukup!")

elif menu == "📦 Stok Barang":
    st.subheader("🔧 Manajemen Stok")
    # Tabel edit stok yang canggih
    df_stok = pd.DataFrame.from_dict(st.session_state.master_barang, orient='index', columns=['Harga', 'Stok'])
    edited_df = st.data_editor(df_stok)
    if st.button("Simpan Perubahan Tabel"):
        # Update session state dari hasil edit tabel
        for item in edited_df.index:
            st.session_state.master_barang[item] = [edited_df.at[item, 'Harga'], edited_df.at[item, 'Stok']]
        st.success("Data Stok diperbarui!")

else:
    st.subheader("📊 Laporan")
    st.info("Cek file Google Sheets kamu untuk melihat riwayat permanen.")
