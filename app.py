import streamlit as st
import pandas as pd
from datetime import datetime
import requests

# 1. KONFIGURASI HALAMAN
st.set_page_config(page_title="wk ahas", layout="wide", page_icon="🏪")

# 2. DATABASE BARANG (Memory Sementara untuk Stok)
if 'master_barang' not in st.session_state:
    st.session_state.master_barang = {
        "Kopi Espresso": [15000, 50],
        "Roti Bakar": [20000, 30],
        "Air Mineral": [5000, 100]
    }

# State pembayaran
if 'jml_bayar' not in st.session_state:
    st.session_state.jml_bayar = 0

# 3. FUNGSI KIRIM KE GOOGLE SHEETS (DENGAN ID ENTRY ASLI)
def simpan_ke_google(tipe, kategori, jumlah, tanggal):
    url = "https://forms.gle/y7xmJZQkyuCekRdr9"
    
    # ID Entry ini sudah disesuaikan dengan Form kamu
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

# 4. TAMPILAN GAYA (CSS)
st.markdown("""
    <style>
    .header-mini { padding: 10px; background: #1e3c72; color: white; border-radius: 8px; margin-bottom: 15px; text-align: center;}
    .struk-box { background: white; padding: 15px; border: 1px dashed black; font-family: monospace; color: black; line-height: 1.2; }
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
                
                st.write(f"### Tagihan: Rp {total_tagihan:,.0f}")
                
                # Pembayaran
                c1, c2 = st.columns(2)
                with c1:
                    if st.button("💵 UANG PAS"): st.session_state.jml_bayar = total_tagihan
                    pecahan = st.selectbox("Uang Pecahan:", [0, 10000, 20000, 50000, 100000])
                    if pecahan > 0: st.session_state.jml_bayar = pecahan
                with c2:
                    manual = st.number_input("Input Manual:", min_value=0, step=500)
                    if manual > 0: st.session_state.jml_bayar = manual
                
                st.write(f"Diterima: **Rp {st.session_state.jml_bayar:,.0f}**")
                
                if st.session_state.jml_bayar >= total_tagihan and st.session_state.jml_bayar > 0:
                    kembali = st.session_state.jml_bayar - total_tagihan
                    st.success(f"Kembalian: Rp {kembali:,.0f}")
                    
                    if st.button("✅ PROSES & SIMPAN CLOUD", use_container_width=True):
                        if qty <= stok_ada:
                            tgl_skrg = datetime.today().strftime('%Y-%m-%d')
                            # KIRIM KE GOOGLE SHEETS
                            sukses = simpan_ke_google("Pemasukan", pilihan, total_tagihan, tgl_skrg)
                            
                            if sukses:
                                st.session_state.master_barang[pilihan][1] -= qty
                                st.success("✅ Tersimpan di Google Sheets!")
                                st.balloons()
                                # Tampilkan Struk
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
                                st.error("❌ Gagal kirim ke Cloud. Cek internet!")
                        else:
                            st.error("Stok tidak cukup!")

    with col2:
        if st.button("🔄 Reset Transaksi"):
            st.session_state.jml_bayar = 0
            st.rerun()

elif menu == "📦 Stok Barang":
    st.subheader("Manajemen Produk")
    for b, d in st.session_state.master_barang.items():
        st.write(f"**{b}** - Stok: {d[1]} | Harga: Rp {d[0]:,.0f}")

else:
    st.subheader("📊 Laporan Keuangan")
    st.info("Catatan: Data riwayat tersimpan secara permanen di file Google Sheets kamu.")
    st.write("Silakan buka file **'Database kasir'** di Google Drive kamu untuk melihat detailnya.")
