import streamlit as st
import pandas as pd
from datetime import datetime
import requests
import plotly.express as px

# 1. DATABASE & CONFIG
URL_CSV = "https://docs.google.com/spreadsheets/d/1P64EoKz-DZgwGyOMtgPbN_vLdax4IUxluWHLi8cmnwo/export?format=csv"
st.set_page_config(page_title="Kasir Jaya", layout="centered")

# 2. CSS CUSTOM (HEADLINE KECIL & TOMBOL JEJER 3)
st.markdown("""
    <style>
    /* Perkecil Judul (Headline) */
    .small-header {
        font-size: 20px !important;
        font-weight: bold;
        text-align: center;
        margin-top: -50px;
        padding-bottom: 10px;
        color: #333;
    }
    /* Tombol Uang Jejer 3 Rapi */
    div[data-testid="stHorizontalBlock"] button {
        width: 100% !important;
        height: 45px !important;
        padding: 0px !important;
        font-size: 14px !important;
        margin-bottom: -10px;
    }
    /* Tab Header Lebih Ramping */
    .stTabs [data-baseweb="tab-list"] { gap: 5px; }
    .stTabs [data-baseweb="tab"] { padding: 8px 12px; font-size: 12px; }
    </style>
    """, unsafe_allow_html=True)

# 3. INITIAL STATE
if 'master' not in st.session_state:
    st.session_state.master = {"Kopi": [15000, 100], "Roti": [20000, 50]}
if 'b' not in st.session_state: st.session_state.b = 0

# 4. FUNGSI AMBIL DATA
def get_data():
    try:
        df = pd.read_csv(URL_CSV)
        df.columns = ['Waktu', 'Tipe', 'Produk', 'Total', 'Tanggal']
        df['Total'] = pd.to_numeric(df['Total'], errors='coerce').fillna(0)
        df['Tanggal'] = pd.to_datetime(df['Tanggal'], errors='coerce')
        df['Bulan'] = df['Tanggal'].dt.strftime('%b %Y')
        return df.dropna(subset=['Tanggal'])
    except: return pd.DataFrame()

# --- HEADLINE KECIL ---
st.markdown("<div class='small-header'>🏪 KASIR JAYA</div>", unsafe_allow_html=True)

# --- MENU TAB ---
tab1, tab2, tab3 = st.tabs(["🛒 KASIR", "📦 STOK", "📊 INFO"])

with tab1:
    pilih = st.selectbox("Produk", list(st.session_state.master.keys()))
    col_qty, col_price = st.columns(2)
    qty = col_qty.number_input("Jumlah", min_value=1, value=1)
    harga = st.session_state.master[pilih][0]
    total = harga * qty
    col_price.metric("Total", f"Rp {total:,.0f}")

    st.write("💰 **Uang Bayar (Jejer 3):**")
    
    # BARIS 1 (PAS, 5rb, 10rb)
    c1, c2, c3 = st.columns(3)
    if c1.button("PAS"): st.session_state.b = total
    if c2.button("5rb"): st.session_state.b = 5000
    if c3.button("10rb"): st.session_state.b = 10000
    
    # BARIS 2 (20rb, 50rb, 100rb)
    c4, c5, c6 = st.columns(3)
    if c4.button("20rb"): st.session_state.b = 20000
    if c5.button("50rb"): st.session_state.b = 50000
    if c6.button("100rb"): st.session_state.b = 100000
    
    bayar = st.number_input("Nominal Bayar:", value=st.session_state.b)
    
    if bayar >= total:
        st.warning(f"Kembalian: Rp {bayar-total:,.0f}")
        if st.button("✅ SELESAIKAN", use_container_width=True):
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
    df_m = pd.DataFrame.from_dict(st.session_state.master, orient='index', columns=['Harga', 'Stok'])
    edit_df = st.data_editor(df_m, use_container_width=True)
    if st.button("Update Stok & Harga"):
        for i in edit_df.index:
            st.session_state.master[i] = [edit_df.at[i, 'Harga'], edit_df.at[i, 'Stok']]
        st.rerun()

    st.divider()
    st.write("### + Tambah Produk")
    with st.expander("Klik Isi Data"):
        n_nama = st.text_input("Nama")
        n_harga = st.number_input("Harga Jual", min_value=0)
        n_stok = st.number_input("Stok", min_value=0)
        if st.button("Simpan Baru"):
            if n_nama:
                st.session_state.master[n_nama] = [n_harga, n_stok]
                st.rerun()

with tab3:
    st.write("### Laporan")
    df = get_data()
    if not df.empty:
        sel_bln = st.selectbox("Bulan", df['Bulan'].unique())
        df_f = df[df['Bulan'] == sel_bln]
        st.metric("Omzet", f"Rp {df_f['Total'].sum():,.0f}")
        fig = px.bar(df_f.groupby('Produk')['Total'].sum().reset_index(), x='Produk', y='Total')
        st.plotly_chart(fig, use_container_width=True)
