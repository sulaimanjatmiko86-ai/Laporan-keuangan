import streamlit as st
import pandas as pd
from datetime import datetime
import requests
import plotly.express as px

# 1. LINK DATABASE (SUDAH SAYA KONVERSI KE CSV)
# Menggunakan ID Sheets kamu: 1P64EoKz-DZgwGyOMtgPbN_vLdax4IUxluWHLi8cmnwo
URL_CSV = "https://docs.google.com/spreadsheets/d/1P64EoKz-DZgwGyOMtgPbN_vLdax4IUxluWHLi8cmnwo/export?format=csv"

# 2. SETTING HALAMAN
st.set_page_config(page_title="Kasir Jaya Paten", layout="centered")

st.markdown("""
    <style>
    div.stButton > button { width: 100%; height: 45px; border-radius: 10px; font-weight: bold; background-color: #f8f9fa; }
    .stMetric { background: #ffffff; border: 1px solid #ddd; padding: 15px; border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

# 3. FUNGSI AMBIL DATA DARI CLOUD
def ambil_data_sheets():
    try:
        df = pd.read_csv(URL_CSV)
        # Nama kolom sesuai Form: Timestamp, Tipe, Katagori, Jumlah, tanggal
        df.columns = ['Waktu', 'Tipe', 'Produk', 'Total', 'Tanggal']
        df['Tanggal'] = pd.to_datetime(df['Tanggal'])
        df['Bulan'] = df['Tanggal'].dt.strftime('%B %Y')
        return df
    except:
        return pd.DataFrame()

# 4. DATABASE BARANG (Master)
if 'master_stok' not in st.session_state:
    st.session_state.master_stok = {
        "Kopi Espresso": [15000, 100],
        "Roti Bakar": [20000, 50],
        "Air Mineral": [5000, 200]
    }

if 'bayar_input' not in st.session_state:
    st.session_state.bayar_input = 0

# --- NAVIGASI ---
menu = st.sidebar.radio("NAVIGASI", ["🛒 Kasir Utama", "📊 Infografis Bulanan", "📦 Stok & Produk"])

# --- HALAMAN 1: KASIR ---
if menu == "🛒 Kasir Utama":
    st.markdown("<h2 style='text-align: center;'>🏪 KASIR JAYA</h2>", unsafe_allow_html=True)
    
    prod = st.selectbox("Pilih Produk:", list(st.session_state.master_stok.keys()))
    qty = st.number_input("Jumlah Beli:", min_value=1, value=1)
    
    harga_satuan = st.session_state.master_stok[prod][0]
    total_tagihan = harga_satuan * qty
    
    st.markdown(f"### Total Tagihan: Rp {total_tagihan:,.0f}")
    st.divider()

    st.write("💰 **Pilih Uang Pembayaran:**")
    c1, c2, c3 = st.columns(3)
    with c1:
        if st.button("PAS"): st.session_state.bayar_input = total_tagihan
        if st.button("20rb"): st.session_state.bayar_input = 20000
    with c2:
        if st.button("5rb"): st.session_state.bayar_input = 5000
        if st.button("50rb"): st.session_state.bayar_input = 50000
    with c3:
        if st.button("10rb"): st.session_state.bayar_input = 10000
        if st.button("100rb"): st.session_state.bayar_input = 100000

    nominal = st.number_input("Atau Ketik Manual:", value=st.session_state.bayar_input)
    
    if nominal >= total_tagihan:
        kembalian = nominal - total_tagihan
        st.success(f"Kembalian: Rp {kembalian:,.0f}")
        
        if st.button("✅ SELESAIKAN & KIRIM KE SHEETS", use_container_width=True):
            # Kirim data ke Google Form
            url_form = "https://docs.google.com/forms/d/e/1FAIpQLSc8wjCuUX01A4MRBLuGx1UaAIAhdQ6G9yPsnhskJ1fKtEFzgA/formResponse"
            payload = {
                "entry.1005808381": "Pemasukan",
                "entry.544255428": prod,
                "entry.1418739506": str(total_tagihan),
                "entry.1637268017": datetime.today().strftime('%Y-%m-%d')
            }
            requests.post(url_form, data=payload)
            
            # Update stok lokal
            st.session_state.master_stok[prod][1] -= qty
            st.balloons()
            st.session_state.bayar_input = 0
            st.rerun()

# --- HALAMAN 2: INFOGRAFIS ---
elif menu == "📊 Infografis Bulanan":
    st.header("📊 Analisis Penjualan Bulanan")
    data = ambil_data_sheets()
    
    if not data.empty:
        # Pilihan Bulan
        bln = st.selectbox("Pilih Periode:", data['Bulan'].unique())
        df_filtered = data[data['Bulan'] == bln]
        
        # Grafik Omzet per Produk
        st.subheader(f"Omzet Produk - {bln}")
        fig1 = px.bar(df_filtered.groupby('Produk')['Total'].sum().reset_index(), 
                     x='Produk', y='Total', color='Total', 
                     text_auto='.2s', color_continuous_scale='Viridis')
        st.plotly_chart(fig1, use_container_width=True)
        
        # Ringkasan Total
        total_omzet = df_filtered['Total'].sum()
        st.metric("Total Pemasukan Bulan Ini", f"Rp {total_omzet:,.0f}")
    else:
        st.error("Data tidak terbaca. Pastikan Sheets sudah ada isinya!")

# --- HALAMAN 3: STOK ---
else:
    st.header("📦 Kelola Produk & Stok")
    df_stok = pd.DataFrame.from_dict(st.session_state.master_stok, orient='index', columns=['Harga', 'Sisa Stok'])
    edited = st.data_editor(df_stok, use_container_width=True)
    
    if st.button("💾 Update Data Stok"):
        for item in edited.index:
            st.session_state.master_stok[item] = [edited.at[item, 'Harga'], edited.at[item, 'Sisa Stok']]
        st.success("Stok diperbarui!")
