import streamlit as st
import pandas as pd
from datetime import datetime
import requests
import plotly.express as px

# 1. DATABASE & CONFIG
URL_CSV = "https://docs.google.com/spreadsheets/d/1P64EoKz-DZgwGyOMtgPbN_vLdax4IUxluWHLi8cmnwo/export?format=csv"
st.set_page_config(page_title="Kasir Jaya", layout="centered")

# 2. CSS "RAPAT & PADAT" (HILANGKAN JARAK JAUH)
st.markdown("""
    <style>
    /* Hilangkan padding luar agar layar maksimal */
    .block-container { padding: 0.5rem !important; max-width: 100% !important; }
    
    /* Box Tagihan - Ukuran Pas */
    .tagihan-box {
        background: #1e2130; padding: 10px; border-radius: 8px;
        border-left: 5px solid #007bff; margin-bottom: 10px;
        display: flex; justify-content: space-between; align-items: center;
    }
    .tagihan-angka { color: #007bff; font-size: 20px; font-weight: bold; }

    /* PAKSA KOLOM RAPAT (HILANGKAN JARAK JAUH) */
    [data-testid="column"] {
        flex: 1 !important;
        min-width: 0px !important;
        padding: 0px 2px !important; /* Jarak kiri kanan cuma 2px biar rapat */
    }
    [data-testid="stHorizontalBlock"] {
        gap: 0px !important; /* Hilangkan gap bawaan Streamlit */
    }
    
    /* Tombol Kasir - Lebar Penuh dalam Kolom Rapat */
    .stButton button {
        width: 100% !important;
        height: 45px !important;
        font-size: 14px !important;
        font-weight: bold !important;
        border-radius: 6px !important;
        margin: 0px !important;
    }
    
    /* Input Nominal Bayar biar gak terlalu tinggi */
    .stNumberInput div { margin-top: -10px; }
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

st.markdown("<h4 style='text-align:center; color:#888; margin-top:-20px;'>POS JAYA COMPACT v21</h4>", unsafe_allow_html=True)

tab1, tab2, tab3 = st.tabs(["🛒 KASIR", "📦 STOK", "📊 INFO"])

with tab1:
    pilih = st.selectbox("Menu", list(st.session_state.master.keys()), label_visibility="collapsed")
    
    c_qty, c_t = st.columns([0.4, 0.6])
    qty = c_qty.number_input("Qty", min_value=1, value=1)
    harga = st.session_state.master[pilih][0]
    total_t = harga * qty
    
    st.markdown(f"""
        <div class="tagihan-box">
            <span style="color:#aaa; font-size:11px;">Total</span>
            <span class="tagihan-angka">Rp {total_t:,.0f}</span>
        </div>
    """, unsafe_allow_html=True)

    # --- BARIS 1: 5rb | 10rb | 20rb (RAPAT) ---
    c1, c2, c3 = st.columns(3)
    with c1: 
        if st.button("5rb"): st.session_state.b = 5000
    with c2: 
        if st.button("10rb"): st.session_state.b = 10000
    with c3: 
        if st.button("20rb"): st.session_state.b = 20000
    
    # --- BARIS 2: 50rb | 100rb | PAS (RAPAT) ---
    c4, c5, c6 = st.columns(3)
    with c4: 
        if st.button("50rb"): st.session_state.b = 50000
    with c5: 
        if st.button("100rb"): st.session_state.b = 100000
    with c6: 
        if st.button("PAS"): st.session_state.b = total_t

    st.markdown("<div style='margin-top:10px;'></div>", unsafe_allow_html=True)
    bayar = st.number_input("Nominal Bayar", value=st.session_state.b, placeholder="Ketik manual...", step=500)
    
    # Tombol Aksi Bawah
    c_del, c_save = st.columns([0.4, 0.6])
    with c_del:
        if st.button("❌ Hapus"):
            st.session_state.b = None
            st.rerun()
    with c_save:
        if bayar and bayar >= total_t:
            if st.button("✅ SIMPAN"):
                payload = {
                    "entry.1005808381": "Pemasukan", "entry.544255428": pilih,
                    "entry.1418739506": str(total_t), "entry.1637268017": datetime.today().strftime('%Y-%m-%d')
                }
                requests.post("https://docs.google.com/forms/d/e/1FAIpQLSc8wjCuUX01A4MRBLuGx1UaAIAhdQ6G9yPsnhskJ1fKtEFzgA/formResponse", data=payload)
                st.session_state.master[pilih][1] -= qty
                st.session_state.b = None
                st.rerun()

    # Riwayat Bawah
    df_all = get_data()
    if not df_all.empty:
        df_today = df_all[df_all['Tanggal'] == datetime.today().date()]
        if not df_today.empty:
            st.divider()
            rekap = df_today.groupby('Produk').agg(Laku=('Produk','count'), Total=('Total','sum')).reset_index()
            st.dataframe(rekap, use_container_width=True, hide_index=True)

with tab2:
    st.write("### Edit Stok")
    df_m = pd.DataFrame.from_dict(st.session_state.master, orient='index', columns=['Harga', 'Stok'])
    st.data_editor(df_m, use_container_width=True)

with tab3:
    st.write("### Laporan Grafik")
    df = get_data()
    if not df.empty:
        st.plotly_chart(px.pie(df, values='Total', names='Produk', hole=0.4), use_container_width=True)
