import streamlit as st
import pandas as pd
from datetime import datetime
import requests
import plotly.express as px

# 1. KONFIGURASI & DATABASE
URL_CSV = "https://docs.google.com/spreadsheets/d/1P64EoKz-DZgwGyOMtgPbN_vLdax4IUxluWHLi8cmnwo/export?format=csv"
st.set_page_config(page_title="Kasir", layout="centered")

# 2. CSS SAKTI (Mengecilkan Headline & Paksa Jejer 3)
st.markdown("""
    <style>
    /* Hilangkan padding atas streamlit */
    .block-container { padding-top: 1rem !important; }
    
    /* Judul Super Kecil */
    .mini-head { font-size: 16px; font-weight: bold; text-align: center; margin-bottom: 10px; color: #555; }
    
    /* Paksa kolom tetap 3 ke samping di HP */
    [data-testid="column"] {
        width: 31% !important;
        flex: unset !important;
        min-width: 31% !important;
    }
    
    /* Tombol lebih ramping */
    button { height: 40px !important; font-size: 13px !important; padding: 0 !important; }
    
    /* Tab Header Ramping */
    .stTabs [data-baseweb="tab"] { padding: 5px 10px !important; font-size: 12px !important; }
    </style>
    """, unsafe_allow_html=True)

if 'master' not in st.session_state:
    st.session_state.master = {"Kopi": [15000, 100], "Roti": [20000, 50]}
if 'b' not in st.session_state: st.session_state.b = 0

def get_data():
    try:
        df = pd.read_csv(URL_CSV)
        df.columns = ['Waktu', 'Tipe', 'Produk', 'Total', 'Tanggal']
        df['Total'] = pd.to_numeric(df['Total'], errors='coerce').fillna(0)
        df['Tanggal'] = pd.to_datetime(df['Tanggal'], errors='coerce')
        df['Bulan'] = df['Tanggal'].dt.strftime('%b %Y')
        return df.dropna(subset=['Tanggal'])
    except: return pd.DataFrame()

# --- HEADER MINI ---
st.markdown("<div class='mini-head'>🏪 JAYA POS v2</div>", unsafe_allow_html=True)

tab1, tab2, tab3 = st.tabs(["🛒 KASIR", "📦 STOK", "📊 INFO"])

with tab1:
    pilih = st.selectbox("Menu", list(st.session_state.master.keys()), label_visibility="collapsed")
    
    c_q, c_h = st.columns([1, 1])
    qty = c_q.number_input("Qty", min_value=1, value=1)
    harga = st.session_state.master[pilih][0]
    total = harga * qty
    c_h.metric("Total", f"{total:,.0f}")

    st.write("💰 **Bayar:**")
    # Baris 1: Jejer 3
    c1, c2, c3 = st.columns(3)
    if c1.button("PAS"): st.session_state.b = total
    if c2.button("5rb"): st.session_state.b = 5000
    if c3.button("10rb"): st.session_state.b = 10000
    
    # Baris 2: Jejer 3
    c4, c5, c6 = st.columns(3)
    if c4.button("20rb"): st.session_state.b = 20000
    if c5.button("50rb"): st.session_state.b = 50000
    if c6.button("100rb"): st.session_state.b = 100000
    
    bayar = st.number_input("Nominal", value=st.session_state.b, label_visibility="collapsed")
    
    if bayar >= total:
        st.info(f"Kembali: {bayar-total:,.0f}")
        if st.button("✅ SELESAI", use_container_width=True):
            payload = {
                "entry.1005808381": "Pemasukan", "entry.544255428": pilih,
                "entry.1418739506": str(total), "entry.1637268017": datetime.today().strftime('%Y-%m-%d')
            }
            requests.post("https://docs.google.com/forms/d/e/1FAIpQLSc8wjCuUX01A4MRBLuGx1UaAIAhdQ6G9yPsnhskJ1fKtEFzgA/formResponse", data=payload)
            st.session_state.master[pilih][1] -= qty
            st.session_state.b = 0
            st.rerun()

with tab2:
    st.write("### Edit Stok")
    df_m = pd.DataFrame.from_dict(st.session_state.master, orient='index', columns=['Harga', 'Stok'])
    edit_df = st.data_editor(df_m, use_container_width=True)
    if st.button("Simpan Perubahan"):
        for i in edit_df.index:
            st.session_state.master[i] = [edit_df.at[i, 'Harga'], edit_df.at[i, 'Stok']]
        st.success("Sip!"); st.rerun()

    with st.expander("+ Tambah Barang"):
        n_n = st.text_input("Nama"); n_h = st.number_input("Harga", 0); n_s = st.number_input("Stok", 0)
        if st.button("Simpan Barang"):
            if n_n: st.session_state.master[n_n] = [n_h, n_s]; st.rerun()

with tab3:
    df = get_data()
    if not df.empty:
        sel_bln = st.selectbox("Bulan", df['Bulan'].unique())
        df_f = df[df['Bulan'] == sel_bln]
        st.metric("Omzet", f"Rp {df_f['Total'].sum():,.0f}")
        fig = px.bar(df_f.groupby('Produk')['Total'].sum().reset_index(), x='Produk', y='Total')
        st.plotly_chart(fig, use_container_width=True)
