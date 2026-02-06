import streamlit as st
import pandas as pd
from datetime import datetime
import requests
import plotly.express as px

# 1. DATABASE & CONFIG
URL_CSV = "https://docs.google.com/spreadsheets/d/1P64EoKz-DZgwGyOMtgPbN_vLdax4IUxluWHLi8cmnwo/export?format=csv"
st.set_page_config(page_title="Kasir Jaya", layout="centered")

# 2. CSS SAKTI (AUTO-SCALE UNTUK SEMUA JENIS HP)
st.markdown("""
    <style>
    /* Gunakan lebar maksimal layar */
    .block-container { padding: 0.5rem !important; max-width: 100% !important; }
    
    /* Judul Mini */
    .mini-head { font-size: 12px; text-align: center; color: #999; margin-bottom: 5px; }

    /* FIX: Angka Tagihan Auto-Resize (Biar Gak Kepotong di HP Kecil) */
    [data-testid="stMetricValue"] { 
        font-size: calc(14px + 1vw) !important; /* Huruf otomatis mengecil sesuai layar */
        white-space: nowrap !important; 
        font-weight: bold; 
        color: #007bff;
    }
    [data-testid="stMetricLabel"] { font-size: 12px !important; }

    /* GRID TOMBOL ANTI-KEPOTONG */
    div[data-testid="stHorizontalBlock"] {
        display: flex !important;
        flex-direction: row !important;
        gap: 4px !important;
    }
    div[data-testid="column"] { 
        flex: 1 !important; 
        min-width: 0px !important; 
    }
    
    /* Tombol Ramping */
    button { 
        width: 100% !important; 
        height: 40px !important; 
        font-size: 11px !important; /* Perkecil tulisan di tombol */
        padding: 0px !important;
    }

    /* Tabel Riwayat Ramping */
    .stDataFrame td, .stDataFrame th { font-size: 11px !important; padding: 2px !important; }
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

st.markdown("<div class='mini-head'>POS JAYA UNIVERSAL v9</div>", unsafe_allow_html=True)

tab1, tab2, tab3 = st.tabs(["🛒 KASIR", "📦 STOK", "📊 INFO"])

with tab1:
    pilih = st.selectbox("Menu", list(st.session_state.master.keys()), label_visibility="collapsed")
    
    cq, ct = st.columns([1, 1.2]) # Beri ruang lebih besar untuk angka tagihan
    qty = cq.number_input("Qty", min_value=1, value=1)
    harga = st.session_state.master[pilih][0]
    total_t = harga * qty
    ct.metric("Tagihan", f"Rp {total_t:,.0f}")

    # TOMBOL JEJER 3
    for row in [[("PAS", total_t), ("5rb", 5000), ("10rb", 10000)], 
                [("20rb", 20000), ("50rb", 50000), ("100rb", 100000)]]:
        cols = st.columns(3)
        for i, (label, val) in enumerate(row):
            if cols[i].button(label): st.session_state.b = val
    
    bayar = st.number_input("Bayar", value=st.session_state.b, label_visibility="collapsed")
    
    if bayar >= total_t:
        st.success(f"Kembali: {bayar-total_t:,.0f}")
        if st.button("✅ SIMPAN TRANSAKSI", use_container_width=True):
            payload = {
                "entry.1005808381": "Pemasukan", "entry.544255428": pilih,
                "entry.1418739506": str(total_t), "entry.1637268017": datetime.today().strftime('%Y-%m-%d')
            }
            requests.post("https://docs.google.com/forms/d/e/1FAIpQLSc8wjCuUX01A4MRBLuGx1UaAIAhdQ6G9yPsnhskJ1fKtEFzgA/formResponse", data=payload)
            st.session_state.master[pilih][1] -= qty
            st.session_state.b = 0
            st.rerun()
    
    st.divider()
    
    # REKAP HARI INI (DIBUAT LEBIH RAPI)
    df_all = get_data()
    if not df_all.empty:
        df_today = df_all[df_all['Tanggal'] == datetime.today().date()]
        if not df_today.empty:
            rekap = df_today.groupby('Produk').agg(Laku=('Produk', 'count'), Total=('Total', 'sum')).reset_index()
            st.write("📊 **Hari Ini:**")
            st.dataframe(rekap, use_container_width=True, hide_index=True)
            st.info(f"Duit: Rp {rekap['Total'].sum():,.0f}")

with tab2:
    st.write("### Edit Barang")
    df_m = pd.DataFrame.from_dict(st.session_state.master, orient='index', columns=['Harga', 'Stok'])
    edit_df = st.data_editor(df_m, use_container_width=True)
    if st.button("Simpan Data"):
        for i in edit_df.index:
            st.session_state.master[i] = [edit_df.at[i, 'Harga'], edit_df.at[i, 'Stok']]
        st.rerun()

    with st.expander("+ Produk Baru"):
        n_n = st.text_input("Nama"); n_h = st.number_input("Harga", 0); n_s = st.number_input("Stok", 0)
        if st.button("Simpan"):
            if n_n: st.session_state.master[n_n] = [n_h, n_s]; st.rerun()

with tab3:
    df = get_data()
    if not df.empty:
        df['Bulan'] = pd.to_datetime(df['Tanggal']).dt.strftime('%b %Y')
        sel_bln = st.selectbox("Bulan", df['Bulan'].unique())
        df_f = df[df['Bulan'] == sel_bln]
        st.metric("Total Omzet", f"Rp {df_f['Total'].sum():,.0f}")
        st.plotly_chart(px.pie(df_f, values='Total', names='Produk', hole=0.5), use_container_width=True)
        st.plotly_chart(px.bar(df_f.groupby('Produk')['Total'].sum().reset_index(), x='Produk', y='Total'), use_container_width=True)
