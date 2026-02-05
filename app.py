import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

# 1. KONFIGURASI HALAMAN
st.set_page_config(page_title="Kasir Jaya Digital", layout="wide", page_icon="🏪")

# 2. DATABASE BARANG (Kamu bisa edit nama & harga di sini)
DAFTAR_BARANG = {
    "--- Pilih Barang ---": 0,
    "Kopi Espresso": 15000,
    "Roti Bakar": 20000,
    "Air Mineral": 5000,
    "Teh Manis": 8000,
    "Pulsa 10rb": 12500,
    "Indomie Tante": 12000
}

# 3. INISIALISASI DATA (Agar data tersimpan selama aplikasi jalan)
if 'data' not in st.session_state:
    st.session_state.data = pd.DataFrame(columns=['Tipe', 'Kategori', 'Jumlah', 'Tanggal'])

# 4. CSS KUSTOM UNTUK TAMPILAN MODERN (INFOGRAFIS)
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stMetric {
        background-color: #ffffff;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        border-left: 5px solid #1E88E5;
    }
    .header-style {
        text-align: center;
        padding: 20px;
        background-color: #1E88E5;
        color: white;
        border-radius: 15px;
        margin-bottom: 25px;
    }
    </style>
    """, unsafe_allow_html=True)

# 5. HEADER (LOGO & NAMA TOKO)
st.markdown("""
    <div class="header-style">
        <h1>🏪 KASIR JAYA DIGITAL</h1>
        <p>Solusi Cerdas Pengelolaan Keuangan Toko Anda</p>
    </div>
    """, unsafe_allow_html=True)

# 6. NAVIGASI SIDEBAR
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/3135/3135715.png", width=100) # Contoh Logo
    st.title("MENU UTAMA")
    menu = st.radio("Pilih Halaman:", ["🛒 Mesin Kasir", "📊 Laporan Infografis"])
    st.divider()
    st.write("Logged in as: **Admin Toko**")

# --- HALAMAN 1: MESIN KASIR ---
if menu == "🛒 Mesin Kasir":
    st.subheader("📝 Catat Transaksi Baru")
    
    tab1, tab2 = st.tabs(["✨ Input Barang Otomatis", "✍️ Input Manual"])
    
    with tab1:
        c1, c2 = st.columns([2, 1])
        with c1:
            barang_sel = st.selectbox("Cari Produk:", list(DAFTAR_BARANG.keys()))
            qty = st.number_input("Jumlah (Qty):", min_value=1, value=1)
        with c2:
            harga_satuan = DAFTAR_BARANG[barang_sel]
            total_bayar = harga_satuan * qty
            st.markdown(f"### Total: \n # Rp {total_bayar:,.0f}")
            
        if st.button("➕ Tambahkan ke Keranjang", use_container_width=True):
            if barang_sel != "--- Pilih Barang ---":
                new_row = pd.DataFrame({
                    'Tipe': ['Pemasukan'], 
                    'Kategori': [barang_sel], 
                    'Jumlah': [total_bayar], 
                    'Tanggal': [datetime.today().date()]
                })
                st.session_state.data = pd.concat([st.session_state.data, new_row], ignore_index=True)
                st.success(f"Berhasil! {barang_sel} ditambahkan.")
            else:
                st.error("Silakan pilih barang terlebih dahulu!")

    with tab2:
        with st.form("manual_form"):
            col_m1, col_m2 = st.columns(2)
            tipe_m = col_m1.selectbox("Jenis:", ["Pemasukan", "Pengeluaran"])
            tgl_m = col_m1.date_input("Tanggal:", value=datetime.today())
            nama_m = col_m2.text_input("Keterangan:", placeholder="Contoh: Bayar Listrik")
            jumlah_m = col_m2.number_input("Nominal (Rp):", min_value=0)
            
            submit_m = st.form_submit_button("💾 Simpan Transaksi Manual")
            if submit_m:
                if nama_m and jumlah_m > 0:
                    new_row = pd.DataFrame({
                        'Tipe': [tipe_m], 'Kategori': [nama_m], 
                        'Jumlah': [jumlah_m], 'Tanggal': [tgl_m]
                    })
                    st.session_state.data = pd.concat([st.session_state.data, new_row], ignore_index=True)
                    st.success("Transaksi manual berhasil disimpan!")

# --- HALAMAN 2: LAPORAN INFOGRAFIS ---
else:
    st.subheader("📈 Dashboard Laporan Keuangan")
    
    # Hitung Data
    total_masuk = st.session_state.data[st.session_state.data['Tipe'] == 'Pemasukan']['Jumlah'].sum()
    total_keluar = st.session_state.data[st.session_state.data['Tipe'] == 'Pengeluaran']['Jumlah'].sum()
    saldo_akhir = total_masuk - total_keluar
    
    # Baris Info Grafis (Metric Cards)
    m1, m2, m3 = st.columns(3)
    m1.metric("💰 Saldo Kas", f"Rp {saldo_akhir:,.0f}")
    m2.metric("📈 Total Omzet", f"Rp {total_masuk:,.0f}")
    m3.metric("📉 Pengeluaran", f"Rp {total_keluar:,.0f}")
    
    st.divider()
    
    col_chart1, col_chart2 = st.columns([1, 1])
    
    with col_chart1:
        st.write("### 🥧 Komposisi Keuangan")
        if not st.session_state.data.empty:
            fig_pie = px.pie(st.session_state.data, values='Jumlah', names='Tipe', 
                           hole=0.5, color_discrete_map={'Pemasukan':'#1E88E5', 'Pengeluaran':'#E53935'})
            st.plotly_chart(fig_pie, use_container_width=True)
        else:
            st.info("Belum ada data.")

    with col_chart2:
        st.write("### 📋 Riwayat Transaksi Terakhir")
        st.dataframe(st.session_state.data.sort_values(by='Tanggal', ascending=False), use_container_width=True)

    # Tombol Download
    csv = st.session_state.data.to_csv(index=False).encode('utf-8')
    st.download_button("📥 Download Laporan Lengkap (CSV)", data=csv, file_name="laporan_kasir.csv", mime="text/csv")
