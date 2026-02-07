import streamlit as st
import pandas as pd
from datetime import datetime
import requests
import plotly.express as px

# 1. DATABASE & CONFIG
URL_CSV = "https://docs.google.com/spreadsheets/d/1P64EoKz-DZgwGyOMtgPbN_vLdax4IUxluWHLi8cmnwo/export?format=csv"
st.set_page_config(page_title="Kasir Jaya Pro", layout="centered")

# 2. CSS FINAL (FIX TULISAN & LAYOUT PADAT)
st.markdown("""
    <style>
    .block-container { padding: 1rem 0.5rem !important; max-width: 100% !important; }
    .mini-head { font-size: 14px; font-weight: bold; text-align: center; color: #888; margin-bottom: 5px; }
    [data-testid="stMetricValue"] { font-size: 22px !important; white-space: nowrap !important; font-weight: bold; color: #007bff; }
    div[data-testid="stHorizontalBlock"] {
        display: grid !important;
        grid-template-columns: 1fr 1fr 1fr !important;
        gap: 6px !important;
        width: 100% !important;
    }
    div[data-testid="column"] { width: 100% !important; min-width: 0px !important; flex: none !important; }
    button { width: 100% !important; height: 42px !important; border-radius: 8px !important; }
    .stDataFrame { border: 1px solid #eee; border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

if 'b' not in st.session_state: st.session_state.b = 0
if 'master' not in st.session_state:
    st.session_state.master = {"Kopi": [15000, 100], "Roti": [20000, 50], "Air": [5000, 200]}

def get_data():
    try:
        df = pd.read_csv(URL_CSV)
        df.columns = ['Waktu', 'Tipe', 'Produk', 'Total', 'Tanggal']
        df['Total'] = pd.to_numeric(df['Total'], errors='coerce').fillna(0).astype(int)
        df['Tanggal'] = pd.to_datetime(df['Tanggal'], errors='coerce').dt.date
        return df
    except: return pd.DataFrame()

# --- HEADER ---
st.markdown("<div class='mini-head'>POS JAYA SMART v8</div>", unsafe_allow_html=True)

tab1, tab2, tab3 = st.tabs(["🛒 KASIR", "📦 STOK", "📊 INFO"])

with tab1:
    pilih = st.selectbox("Menu", list(st.session_state.master.keys()), label_visibility="collapsed")
    
    cq, ct = st.columns(2)
    qty = cq.number_input("Qty", min_value=1, value=1)
    harga = st.session_state.master[pilih][0]
    total_t = harga * qty
    ct.metric("Tagihan", f"Rp {total_t:,.0f}")

    # TOMBOL UANG
    c1, c2, c3 = st.columns(3)
    with c1: 
        if st.button("PAS"): st.session_state.b = total_t
    with c2: 
        if st.button("5rb"): st.session_state.b = 5000
    with c3: 
        if st.button("10rb"): st.session_state.b = 10000
    
    c4, c5, c6 = st.columns(3)
    with c4: 
        if st.button("20rb"): st.session_state.b = 20000
    with c5: 
        if st.button("50rb"): st.session_state.b = 50000
    with c6: 
        if st.button("100rb"): st.session_state.b = 100000
    
    bayar = st.number_input("Bayar", value=st.session_state.b, label_visibility="collapsed")
    
    if bayar >= total_t:
        st.success(f"Kembali: Rp {bayar-total_t:,.0f}")
        if st.button("✅ SELESAI & SIMPAN", use_container_width=True):
            payload = {
                "entry.1005808381": "Pemasukan", "entry.544255428": pilih,
                "entry.1418739506": str(total_t), "entry.1637268017": datetime.today().strftime('%Y-%m-%d')
            }
            requests.post("https://docs.google.com/forms/d/e/1FAIpQLSc8wjCuUX01A4MRBLuGx1UaAIAhdQ6G9yPsnhskJ1fKtEFzgA/formResponse", data=payload)
            st.session_state.master[pilih][1] -= qty
            st.session_state.b = 0
            st.rerun()
    
    st.divider()
    
    # --- RINGKASAN PENJUALAN HARI INI ---
    st.write("📈 **Total Terjual Hari Ini:**")
    df_all = get_data()
    if not df_all.empty:
        hari_ini = datetime.today().date()
        df_today = df_all[df_all['Tanggal'] == hari_ini]
        
        if not df_today.empty:
            # Hitung total per produk
            rekap = df_today.groupby('Produk').agg(
                Terjual=('Produk', 'count'),
                Total_Rp=('Total', 'sum')
            ).reset_index()
            
            # Tampilkan tabel rekap
            st.dataframe(rekap, use_container_width=True, hide_index=True)
            
            # Total Uang Masuk Hari Ini
            total_duit = rekap['Total_Rp'].sum()
            st.info(f"💰 Total Uang Masuk: **Rp {total_duit:,.0f}**")
        else:
            st.write("Belum ada transaksi hari ini.")

with tab2:
    st.write("### 📦 Kelola Barang")
    df_m = pd.DataFrame.from_dict(st.session_state.master, orient='index', columns=['Harga', 'Stok'])
    edit_df = st.data_editor(df_m, use_container_width=True)
    if st.button("Simpan Perubahan"):
        for i in edit_df.index:
            st.session_state.master[i] = [edit_df.at[i, 'Harga'], edit_df.at[i, 'Stok']]
        st.success("Tersimpan!")

    with st.expander("+ Tambah Menu Baru"):
        n_n = st.text_input("Nama Produk")
        n_h = st.number_input("Harga", 0)
        n_s = st.number_input("Stok", 0)
        if st.button("Tambahkan"):
            if n_n: st.session_state.master[n_n] = [n_h, n_s]; st.rerun()

with tab3:
    st.write("### 📊 Laporan Bulanan")
    df = get_data()
    if not df.empty:
        # Tambahkan kolom bulan untuk filter
        df['Bulan'] = pd.to_datetime(df['Tanggal']).dt.strftime('%b %Y')
        sel_bln = st.selectbox("Periode", df['Bulan'].unique())
        df_f = df[df['Bulan'] == sel_bln].copy()
        
        st.metric("Total Omzet", f"Rp {df_f['Total'].sum():,.0f}")
        
        st.write("🍩 **Proporsi Produk Terlaris**")
        fig_pie = px.pie(df_f, values='Total', names='Produk', hole=0.5,
                         color_discrete_sequence=px.colors.qualitative.Bold)
        st.plotly_chart(fig_pie, use_container_width=True)
        
        st.write("📊 **Grafik Penjualan (Rp)**")
        summary = df_f.groupby('Produk')['Total'].sum().reset_index()
        fig_bar = px.bar(summary, x='Produk', y='Total', color='Produk', text_auto='.2s')
        st.plotly_chart(fig_bar, use_container_width=True)
    else:
        st.info("Menunggu data masuk...")
