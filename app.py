import streamlit as st
import pandas as pd
from datetime import datetime
import requests
import plotly.express as px

# 1. DATABASE & CONFIG
URL_CSV = "https://docs.google.com/spreadsheets/d/1P64EoKz-DZgwGyOMtgPbN_vLdax4IUxluWHLi8cmnwo/export?format=csv"
st.set_page_config(page_title="Kasir Simple", layout="centered")

# 2. CSS BIAR TAMPILAN BERSIH & MODERN
st.markdown("""
    <style>
    .stApp { background-color: #FFFFFF; }
    .stButton>button { 
        border-radius: 8px; height: 3em; font-weight: bold; 
        border: 1px solid #E0E0E0; background-color: #F9F9F9;
    }
    .stTabs [data-baseweb="tab-list"] { gap: 10px; }
    .stTabs [data-baseweb="tab"] {
        background-color: #F1F1F1; border-radius: 5px; padding: 10px 20px;
    }
    .stMetric { border: 1px solid #F1F1F1; padding: 10px; border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

# 3. INITIAL STATE
if 'master' not in st.session_state:
    st.session_state.master = {"Kopi": [15000, 100], "Roti": [20000, 50]}
if 'b' not in st.session_state: st.session_state.b = 0

# 4. FUNGSI AMBIL DATA SHEETS
def get_data():
    try:
        df = pd.read_csv(URL_CSV)
        df.columns = ['Waktu', 'Tipe', 'Produk', 'Total', 'Tanggal']
        df['Total'] = pd.to_numeric(df['Total'], errors='coerce').fillna(0)
        df['Tanggal'] = pd.to_datetime(df['Tanggal'], errors='coerce')
        df['Bulan'] = df['Tanggal'].dt.strftime('%b %Y')
        return df.dropna(subset=['Tanggal'])
    except: return pd.DataFrame()

# --- HEADER ---
st.markdown("<h2 style='text-align: center;'>KASIR JAYA</h2>", unsafe_allow_html=True)

# --- MENU TAB (SIMPEL) ---
tab1, tab2, tab3 = st.tabs(["🛒 KASIR", "📦 STOK", "📊 INFO"])

with tab1:
    pilih = st.selectbox("Produk", list(st.session_state.master.keys()))
    col1, col2 = st.columns(2)
    qty = col1.number_input("Jumlah", min_value=1, value=1)
    harga = st.session_state.master[pilih][0]
    total = harga * qty
    col2.metric("Total Tagihan", f"Rp {total:,.0f}")

    st.write("Cepat:")
    c1, c2, c3, c4 = st.columns(4)
    if c1.button("PAS"): st.session_state.b = total
    if c2.button("20rb"): st.session_state.b = 20000
    if c3.button("50rb"): st.session_state.b = 50000
    if c4.button("100rb"): st.session_state.b = 100000
    
    bayar = st.number_input("Uang Diterima", value=st.session_state.b)
    
    if bayar >= total:
        st.success(f"Kembalian: Rp {bayar-total:,.0f}")
        if st.button("PROSES SELESAI", use_container_width=True):
            # Kirim Data
            payload = {
                "entry.1005808381": "Pemasukan",
                "entry.544255428": pilih,
                "entry.1418739506": str(total),
                "entry.1637268017": datetime.today().strftime('%Y-%m-%d')
            }
            requests.post("https://docs.google.com/forms/d/e/1FAIpQLSc8wjCuUX01A4MRBLuGx1UaAIAhdQ6G9yPsnhskJ1fKtEFzgA/formResponse", data=payload)
            st.session_state.master[pilih][1] -= qty
            st.session_state.b = 0
            st.rerun()

with tab2:
    st.write("### Kelola Barang")
    # Tabel Edit Stok
    df_m = pd.DataFrame.from_dict(st.session_state.master, orient='index', columns=['Harga', 'Stok'])
    edit_df = st.data_editor(df_m, use_container_width=True)
    if st.button("Update Stok & Harga"):
        for i in edit_df.index:
            st.session_state.master[i] = [edit_df.at[i, 'Harga'], edit_df.at[i, 'Stok']]
        st.rerun()

    st.divider()
    st.write("### + Tambah Barang Baru")
    with st.expander("Klik untuk tambah produk"):
        new_name = st.text_input("Nama Produk")
        new_price = st.number_input("Harga", min_value=0)
        new_stock = st.number_input("Stok Awal", min_value=0)
        if st.button("Simpan Barang Baru"):
            if new_name:
                st.session_state.master[new_name] = [new_price, new_stock]
                st.success(f"{new_name} ditambahkan!")
                st.rerun()

with tab3:
    st.write("### Laporan Penjualan")
    df = get_data()
    if not df.empty:
        bulans = df['Bulan'].unique()
        sel_bln = st.selectbox("Bulan", bulans)
        df_f = df[df['Bulan'] == sel_bln]
        st.metric("Total Omzet", f"Rp {df_f['Total'].sum():,.0f}")
        fig = px.bar(df_f.groupby('Produk')['Total'].sum().reset_index(), x='Produk', y='Total')
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.write("Belum ada data.")
