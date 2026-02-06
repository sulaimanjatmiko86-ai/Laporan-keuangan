import streamlit as st
import pandas as pd
from datetime import datetime
import requests
import plotly.express as px

# 1. DATABASE & CONFIG
URL_CSV = "https://docs.google.com/spreadsheets/d/1P64EoKz-DZgwGyOMtgPbN_vLdax4IUxluWHLi8cmnwo/export?format=csv"
st.set_page_config(page_title="Kasir", layout="centered")

# 2. CSS SAKTI (HEADLINE MINI & FIX TOMBOL KEPOTONG)
st.markdown("""
    <style>
    /* Hilangkan padding berlebih */
    .block-container { padding: 1rem 0.5rem !important; max-width: 100% !important; }
    
    /* Headline Super Kecil */
    .mini-head { font-size: 14px; font-weight: bold; text-align: center; color: #888; margin-bottom: 10px; }

    /* PAKSA JEJER 3 MENGGUNAKAN GRID CSS */
    div[data-testid="stHorizontalBlock"] {
        display: grid !important;
        grid-template-columns: 1fr 1fr 1fr !important; /* Bagi 3 rata */
        gap: 5px !important;
        width: 100% !important;
    }
    div[data-testid="column"] {
        width: 100% !important;
        min-width: 0px !important;
        flex: none !important;
    }
    
    /* Tombol Pas & Rapi */
    button { 
        width: 100% !important;
        height: 45px !important; 
        font-size: 13px !important;
        margin: 0px !important;
        border-radius: 8px !important;
    }

    /* Rapikan input agar tidak terlalu renggang */
    .stNumberInput, .stSelectbox { margin-bottom: -10px !important; }
    </style>
    """, unsafe_allow_html=True)

# Sinkronisasi state uang bayar
if 'b' not in st.session_state: st.session_state.b = 0
if 'master' not in st.session_state:
    st.session_state.master = {"Kopi": [15000, 100], "Roti": [20000, 50]}

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
st.markdown("<div class='mini-head'>POS JAYA v5 (FIXED)</div>", unsafe_allow_html=True)

tab1, tab2, tab3 = st.tabs(["🛒 KASIR", "📦 STOK", "📊 INFO"])

with tab1:
    pilih = st.selectbox("Pilih Menu", list(st.session_state.master.keys()), label_visibility="collapsed")
    
    # Qty & Total Jejer 2
    cq, ct = st.columns(2)
    qty = cq.number_input("Qty", min_value=1, value=1)
    harga = st.session_state.master[pilih][0]
    total = harga * qty
    ct.metric("Tagihan", f"{total:,.0f}")

    st.write("💰 **Uang Bayar:**")
    
    # BARIS 1 (PAS, 5rb, 10rb)
    c1, c2, c3 = st.columns(3)
    with c1: 
        if st.button("PAS"): st.session_state.b = total
    with c2: 
        if st.button("5rb"): st.session_state.b = 5000
    with c3: 
        if st.button("10rb"): st.session_state.b = 10000
    
    # BARIS 2 (20rb, 50rb, 100rb)
    c4, c5, c6 = st.columns(3)
    with c4: 
        if st.button("20rb"): st.session_state.b = 20000
    with c5: 
        if st.button("50rb"): st.session_state.b = 50000
    with c6: 
        if st.button("100rb"): st.session_state.b = 100000
    
    bayar = st.number_input("Nominal", value=st.session_state.b, label_visibility="collapsed")
    
    if bayar >= total:
        st.info(f"Kembali: {bayar-total:,.0f}")
        if st.button("✅ SELESAIKAN TRANSAKSI", use_container_width=True):
            payload = {
                "entry.1005808381": "Pemasukan", "entry.544255428": pilih,
                "entry.1418739506": str(total), "entry.1637268017": datetime.today().strftime('%Y-%m-%d')
            }
            requests.post("https://docs.google.com/forms/d/e/1FAIpQLSc8wjCuUX01A4MRBLuGx1UaAIAhdQ6G9yPsnhskJ1fKtEFzgA/formResponse", data=payload)
            st.session_state.master[pilih][1] -= qty
            st.session_state.b = 0
            st.rerun()

with tab2:
    st.write("### Edit Stok & Produk")
    df_m = pd.DataFrame.from_dict(st.session_state.master, orient='index', columns=['Harga', 'Stok'])
    edit_df = st.data_editor(df_m, use_container_width=True)
    if st.button("Update Data"):
        for i in edit_df.index:
            st.session_state.master[i] = [edit_df.at[i, 'Harga'], edit_df.at[i, 'Stok']]
        st.success("Tersimpan!"); st.rerun()

    with st.expander("+ Tambah Barang"):
        n_n = st.text_input("Nama"); n_h = st.number_input("Harga", 0); n_s = st.number_input("Stok", 0)
        if st.button("Simpan Baru"):
            if n_n: st.session_state.master[n_n] = [n_h, n_s]; st.rerun()

with tab3:
    df = get_data()
    if not df.empty:
        sel_bln = st.selectbox("Pilih Bulan", df['Bulan'].unique())
        df_f = df[df['Bulan'] == sel_bln]
        st.metric("Total Omzet", f"Rp {df_f['Total'].sum():,.0f}")
        fig = px.bar(df_f.groupby('Produk')['Total'].sum().reset_index(), x='Produk', y='Total')
        st.plotly_chart(fig, use_container_width=True)
