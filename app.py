import streamlit as st
import pandas as pd
from datetime import datetime
import requests

# 1. KONFIGURASI HALAMAN
st.set_page_config(page_title="Kasir Jaya Cloud", layout="wide", page_icon="🏪")

# 2. DATABASE BARANG (Memory Sementara untuk Stok)
if 'master_barang' not in st.session_state:
    st.session_state.master_barang = {
        "Kopi Espresso": [15000, 50],
        "Roti Bakar": [20000, 30],
        "Air Mineral": [5000, 100]
    }

# State untuk hitung bayar
if 'jml_bayar' not in st.session_state:
    st.session_state.jml_bayar = 0

# 3. FUNGSI KIRIM KE GOOGLE SHEETS
def simpan_ke_google(tipe, kategori, jumlah, tanggal):
    # Ini adalah link formResponse milikmu
    url = "https://docs.google.com/forms/u/0/d/e/1FAIpQLSc8wjCuUX01A4MRBLuGx1UaAIAhdQ6G9yPsnhskJ1fKtEFzgA/formResponse"
    
    # Ini adalah ID kolom (entry) hasil bedah form kamu
    # Jika data tidak masuk, kemungkinan ID entry ini perlu disesuaikan lagi
    payload = {
        "entry.1444153920": tipe,     # Kolom Tipe
        "entry.2065873155": kategori, # Kolom Katagori
        "entry.143715201": jumlah,    # Kolom Jumlah
        "entry.1098693740": tanggal   # Kolom tanggal
    }
    
    try:
        response = requests.post(url, data=payload)
        return response.status_code == 200
    except:
        return False

# 4. TAMPILAN HEADER RINGKAS
st.markdown("""
    <style>
    .header-mini { padding: 10px; background: #1e3c72; color: white; border-radius: 8px; margin-bottom: 15px; text-align: center;}
    .struk-box { background: white; padding: 15px; border: 1px dashed black; font-family: monospace; color: black; }
    </style>
    <div class="header-mini"><h2>🏪 KASIR JAYA DIGITAL</h2></div>
    """, unsafe_allow_html=True)

# 5. MENU UTAMA
menu = st.sidebar.radio("MENU", ["🛒 Kasir", "📦 Stok Barang", "📊 Laporan"])

if menu == "🛒 Kasir":
    col1, col2 = st.columns([1.5, 1])
    
    with col1:
        with st.expander("📝 Transaksi Baru", expanded=True):
            daftar = ["--- Pilih ---"] + list(st.session_state.master_barang.keys())
            pilihan = st.selectbox("Produk:", daftar)
            qty = st.number_input("Qty:", min_value=1, value=1)
            
            if pilihan != "--- Pilih ---":
                harga_sat = st.session_state.master_barang[pilihan][0]
                stok_ada = st.session_state.master_barang[pilihan][1]
                total_tagihan = harga_sat * qty
                
                st.write(f"### Total: Rp {total_tagihan:,.0f}")
                st.divider()
                
                # Fitur Pembayaran
                c1, c2 = st.columns(2)
                with c1:
                    if st.button("💵 UANG PAS"): st.session_state.jml_bayar = total_tagihan
                    pecahan = st.selectbox("Pilih Pecahan:", [0, 20000, 50000, 100000])
                    if pecahan > 0: st.session_state.jml_bayar = pecahan
                with c2:
                    manual = st.number_input("Input Manual:", min_value=0, step=500)
                    if manual > 0: st.session_state.jml_bayar = manual
                
                st.write(f"Diterima: **Rp {st.session_state.jml_bayar:,.0f}**")
                
                if st.session_state.jml_bayar >= total_tagihan:
                    kembali = st.session_state.jml_bayar - total_tagihan
                    st.info(f"Kembalian: Rp {kembali:,.0f}")
                    
                    if st.button("✅ SELESAIKAN & SIMPAN CLOUD", use_container_width=True):
                        if qty <= stok_ada:
                            tgl_skrg = datetime.today().strftime('%Y-%m-%d')
                            # KIRIM KE GOOGLE SHEETS
                            sukses = simpan_ke_google("Pemasukan", pilihan, total_tagihan, tgl_skrg)
                            
                            if sukses:
                                st.session_state.master_barang[pilihan][1] -= qty
                                st.success("✅ Berhasil Simpan ke Google Sheets!")
                                st.balloons()
                                # Cetak Struk
                                st.markdown(f"""
                                <div class="struk-box">
                                    <center><b>KASIR JAYA DIGITAL</b><br>{tgl_skrg}</center><hr>
                                    {pilihan}<br>{qty} x {harga_sat:,.0f} = {total_tagihan:,.0f}<hr>
                                    TOTAL   : Rp {total_tagihan:,.0f}<br>
                                    BAYAR   : Rp {st.session_state.jml_bayar:,.0f}<br>
                                    KEMBALI : Rp {kembali:,.0f}<hr>
                                    <center>Terima Kasih</center>
                                </div>
                                """, unsafe_allow_html=True)
                                st.session_state.jml_bayar = 0
                            else:
                                st.error("❌ Gagal terhubung ke Cloud. Periksa internet!")
                        else:
                            st.error("Stok tidak cukup!")

    with col2:
        if st.button("🔄 Reset Form"):
            st.session_state.jml_bayar = 0
            st.rerun()

elif menu == "📦 Stok Barang":
    st.subheader("Manajemen Stok")
    for b, d in st.session_state.master_barang.items():
        st.write(f"**{b}** - Stok: {d[1]} | Harga: Rp {d[0]:,.0f}")

else:
    st.subheader("📊 Laporan")
    st.write("Silakan cek file Google Sheets kamu untuk melihat riwayat lengkap secara permanen.")
    st.link_button("📂 Buka Google Sheets", "https://docs.google.com/spreadsheets/d/1X_Ww-o7n9p3g9Wb8fU6E7W-Y4F9p8G7Y-U1B2C3D4E5/edit")
