import streamlit as st
import pandas as pd
from datetime import datetime
import requests
import plotly.express as px

# 1. DATABASE & CONFIG
URL_CSV = "https://docs.google.com/spreadsheets/d/1P64EoKz-DZgwGyOMtgPbN_vLdax4IUxluWHLi8cmnwo/export?format=csv"
st.set_page_config(page_title="Kasir Jaya", layout="centered")

# 2. CSS "SUPER MEPEET" (HAPUS SEMUA JARAK GAK PENTING)
st.markdown("""
    <style>
    .block-container { padding: 0.5rem !important; max-width: 100% !important; }
    
    /* Box Tagihan Biru Rapi */
    .tagihan-box {
        background: #1e2130; padding: 10px; border-radius: 8px;
        border-left: 5px solid #007bff; margin-bottom: 8px;
        display: flex; justify-content: space-between; align-items: center;
    }
    .tagihan-angka { color: #007bff; font-size: 20px; font-weight: bold; }

    /* PAKSA JEJER 3 & MEPEET (ANTI JARAK JAUH) */
    div[data-testid="column"] {
        flex: 1 1 0% !important;
        min-width: 0px !important;
        padding: 0px 1px !important; /* Jarak cuma 1 pixel biar rapat banget */
    }
    div[data-testid="stHorizontalBlock"] {
        gap: 2px !important; /* Jarak antar kolom cuma 2 pixel */
    }
    
    /* Tombol - Rapat & Kecil */
    .stButton button {
        width: 100% !important;
        height: 42px !important;
        font-size: 13px !important;
        font-weight: bold !important;
        border-radius: 6px !important;
        margin: 0px !important;
        padding: 0px !important;
    }
    
    /* Input Angka Diperkecil Marginnya */
    .stNumberInput { margin-top: -15px; }
    </style>
    """, unsafe_allow_html=True)

if 'b' not in st.session_state: st.session_state.b = None
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

st.markdown("<h5 style='text-align:center; color:#888; margin-top:-20px;'>POS JAYA SUPER COMPACT</h5>", unsafe_allow_html=True)

tab1, tab2, tab3 = st.tabs(["🛒 KASIR", "📦 STOK", "📊 INFO"])

with tab1:
    pilih = st.selectbox("Menu", list(st.session_state.master.keys()), label_visibility="collapsed")
    
    c_qty, c_t = st.columns([0.4, 0.6])
    qty = c_qty.number_input("Qty", min_value=1, value=1)
    harga = st.session_state.master[pilih][0]
    total_t = harga * qty
    
    st.markdown(f"""
        <div class="tagihan-box">
            <span style="color:#aaa; font-size:10px;">Tagihan</span>
            <span class="tagihan-angka">Rp {total_t:,.0f}</span>
        </div>
    """, unsafe_allow_html=True)

    # BARIS 1: 5rb | 10rb | 20rb (SANGAT RAPAT)
    c1, c2, c3 = st.columns(3)
    if c1.button("5rb"): st.session_state.b = 5000
    if c2.button("10rb"): st.session_state.b = 10000
    if c3.button("20rb"): st.session_state.b = 20000
    
    # BARIS 2: 50rb | 100rb | PAS (SANGAT RAPAT)
    c4, c5, c6 = st.columns(3)
    if c4.button("50rb"): st.session_state.b = 50000
    if c5.button("100rb"): st.session_state.b = 100000
    if c6.button("PAS"): st.session_state.b = total_t

    st.write("") # Spasi kecil
    bayar = st.number_input("Nominal Bayar", value=st.session_state.b, placeholder="Ketik manual...", step=500)
    
    # Tombol Simpan & Hapus
    c_del, c_save = st.columns([0.35, 0.65])
    if c_del.button("❌ Batal"):
        st.session_state.b = None
        st.rerun()
    if bayar and bayar >= total_t:
        if c_save.button("✅ SIMPAN & CETAK"):
            payload = {
                "entry.1005808381": "Pemasukan", "entry.544255428": pilih,
                "entry.1418739506": str(total_t), "entry.1637268017": datetime.today().strftime('%Y-%m-%d')
            }
            requests.post("https://docs.google.com/forms/d/e/1FAIpQLSc8wjCuUX01A4MRBLuGx1UaAIAhdQ6G9yPsnhskJ1fKtEFzgA/formResponse", data=payload)
            st.session_state.master[pilih][1] -= qty
            st.session_state.b = None
            st.rerun()

    # Riwayat Ringkas
    df_all = get_data()
    if not df_all.empty:
        df_today = df_all[df_all['Tanggal'] == datetime.today().date()]
        if not df_today.empty:
            st.divider()
            rekap = df_today.groupby('Produk').agg(Laku=('Produk','count'), Total=('Total','sum')).reset_index()
            st.dataframe(rekap, use_container_width=True, hide_index=True)

with tab2:
    st.write("### Stok Barang")
    df_m = pd.DataFrame.from_dict(st.session_state.master, orient='index', columns=['Harga', 'Stok'])
    st.data_editor(df_m, use_container_width=True)

with tab3:
    st.write("### Info Penjualan")
    df = get_data()
    if not df.empty:
        st.plotly_chart(px.pie(df, values='Total', names='Produk', hole=0.4), use_container_width=True)
