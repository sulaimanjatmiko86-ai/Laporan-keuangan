import streamlit as st
import pandas as pd
from datetime import datetime
import requests
import plotly.express as px

# 1. DATABASE LINK (ID Sheets Kamu)
URL_CSV = "https://docs.google.com/spreadsheets/d/1P64EoKz-DZgwGyOMtgPbN_vLdax4IUxluWHLi8cmnwo/export?format=csv"

# 2. KONFIGURASI TAMPILAN (Bersih & Elegan)
st.set_page_config(page_title="Kasir Jaya v2", layout="centered")

st.markdown("""
    <style>
    .main { background-color: #f9f9f9; }
    div.stButton > button { 
        width: 100%; height: 50px; border-radius: 12px; 
        font-weight: bold; border: none; background-color: #ffffff;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    div.stButton > button:hover { border: 1px solid #007bff; color: #007bff; }
    .stSelectbox, .stNumberInput { margin-bottom: 15px; }
    </style>
    """, unsafe_allow_html=True)

# 3. FUNGSI AMBIL DATA (Sistem Pembersih Angka Otomatis)
def ambil_data_sheets():
    try:
        df = pd.read_csv(URL_CSV)
        # Menyesuaikan kolom: Timestamp, Tipe, Katagori, Jumlah, Tanggal
        df.columns = ['Waktu', 'Tipe', 'Produk', 'Total', 'Tanggal']
        
        # Bersihkan Angka: Hilangkan Rp, titik, koma, dan paksa jadi angka
        df['Total'] = pd.to_numeric(df['Total'], errors='coerce').fillna(0).astype(int)
        
        # Bersihkan Tanggal
        df['Tanggal'] = pd.to_datetime(df['Tanggal'], errors='coerce')
        df = df.dropna(subset=['Tanggal'])
        df['Bulan'] = df['Tanggal'].dt.strftime('%b %Y')
        return df
    except:
        return pd.DataFrame()

# 4. LOGIKA STOK & INPUT
if 'stok' not in st.session_state:
    st.session_state.stok = {"Kopi Espresso": [15000, 100], "Roti Bakar": [20000, 50], "Air Mineral": [5000, 200]}

# --- SIDEBAR NAVIGASI ---
with st.sidebar:
    st.title("🚀 JAYA POS")
    menu = st.radio("Menu Utama:", ["🛒 Kasir", "📊 Laporan", "⚙️ Stok"])
    st.divider()
    st.info("Data otomatis sinkron ke Google Sheets")

# --- HALAMAN 1: KASIR (TAMPILAN BERSIH) ---
if menu == "🛒 Kasir":
    st.subheader("Kasir Baru")
    
    col_a, col_b = st.columns([2, 1])
    with col_a:
        prod = st.selectbox("Pilih Produk", list(st.session_state.stok.keys()))
    with col_b:
        qty = st.number_input("Qty", min_value=1, value=1)
    
    total = st.session_state.stok[prod][0] * qty
    st.markdown(f"<h1 style='color: #007bff;'>Rp {total:,.0f}</h1>", unsafe_allow_html=True)
    
    st.write("💳 **Metode Bayar Cepat:**")
    c1, c2, c3 = st.columns(3)
    if c1.button("PAS"): st.session_state.b = total
    if c1.button("20rb"): st.session_state.b = 20000
    if c2.button("5rb"): st.session_state.b = 5000
    if c2.button("50rb"): st.session_state.b = 50000
    if c3.button("10rb"): st.session_state.b = 10000
    if c3.button("100rb"): st.session_state.b = 100000
    
    bayar = st.number_input("Diterima (Rp):", value=st.session_state.get('b', 0))
    
    if bayar >= total:
        st.warning(f"Kembalian: Rp {bayar - total:,.0f}")
        if st.button("🔥 SELESAIKAN TRANSAKSI", use_container_width=True):
            # Kirim ke Sheets
            payload = {
                "entry.1005808381": "Pemasukan",
                "entry.544255428": prod,
                "entry.1418739506": str(total),
                "entry.1637268017": datetime.today().strftime('%Y-%m-%d')
            }
            requests.post("https://docs.google.com/forms/d/e/1FAIpQLSc8wjCuUX01A4MRBLuGx1UaAIAhdQ6G9yPsnhskJ1fKtEFzgA/formResponse", data=payload)
            st.session_state.stok[prod][1] -= qty
            st.success("Tersimpan!"); st.balloons()
            st.session_state.b = 0
            st.rerun()

# --- HALAMAN 2: LAPORAN (INFOGRAFIS BERSIH) ---
elif menu == "📊 Laporan":
    st.subheader("Analisis Bulanan")
    df = ambil_data_sheets()
    
    if not df.empty:
        # Ringkasan Atas
        bln_pilih = st.selectbox("Pilih Bulan", df['Bulan'].unique())
        df_f = df[df['Bulan'] == bln_pilih]
        
        st.metric("Total Omzet", f"Rp {df_f['Total'].sum():,.0f}")
        
        # Grafik Bersih
        fig = px.bar(df_f.groupby('Produk')['Total'].sum().reset_index(), 
                     x='Produk', y='Total', template='plotly_white',
                     color_discrete_sequence=['#007bff'])
        fig.update_layout(margin=dict(l=20, r=20, t=20, b=20))
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Sedang menarik data dari Cloud...")

# --- HALAMAN 3: STOK ---
else:
    st.subheader("Manajemen Stok")
    df_stok = pd.DataFrame.from_dict(st.session_state.stok, orient='index', columns=['Harga', 'Sisa Stok'])
    edited = st.data_editor(df_stok, use_container_width=True)
    if st.button("Simpan Perubahan"):
        for i in edited.index:
            st.session_state.stok[i] = [edited.at[i, 'Harga'], edited.at[i, 'Sisa Stok']]
        st.success("Stok Diupdate!")
