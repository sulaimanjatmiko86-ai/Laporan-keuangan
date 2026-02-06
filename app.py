import streamlit as st
import pandas as pd
from datetime import datetime
import requests
import plotly.express as px

# 1. DATABASE & CONFIG
URL_CSV = "https://docs.google.com/spreadsheets/d/1P64EoKz-DZgwGyOMtgPbN_vLdax4IUxluWHLi8cmnwo/export?format=csv"
st.set_page_config(page_title="Kasir Jaya", layout="centered")

# 2. CSS "FIXED GRID" (MENGUNCI TOMBOL AGAR SELALU JEJER 3 RAPI)
st.markdown("""
    <style>
    .block-container { padding: 0.7rem !important; max-width: 100% !important; }
    
    /* Box Tagihan Biru Rapi */
    .tagihan-box {
        background: #1e2130; padding: 12px; border-radius: 10px;
        border-left: 5px solid #007bff; margin-bottom: 10px;
        display: flex; justify-content: space-between; align-items: center;
    }
    .tagihan-angka { color: #007bff; font-size: 20px; font-weight: bold; }

    /* PAKSA KOLOM TETAP JEJER 3 (ANTI TUMPUK) */
    div[data-testid="column"] {
        flex: 1 !important;
        min-width: 30% !important;
    }
    div[data-testid="stHorizontalBlock"] {
        display: flex !important;
        flex-direction: row !important;
        flex-wrap: nowrap !important;
        gap: 6px !important;
    }
    
    /* Ukuran Tombol Standar Kasir */
    .stButton button {
        height: 48px !important;
        font-size: 14px !important;
        font-weight: bold !important;
        border-radius: 8px !important;
    }
    </style>
    """, unsafe_allow_html=True)

# State Management
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

st.markdown("<h4 style='text-align:center; color:#888;'>POS JAYA ORDERLY v16</h4>", unsafe_allow_html=True)

tab1, tab2, tab3 = st.tabs(["🛒 KASIR", "📦 STOK", "📊 INFO"])

with tab1:
    pilih = st.selectbox("Pilih Menu", list(st.session_state.master.keys()), label_visibility="collapsed")
    
    c_qty, c_t = st.columns([0.4, 0.6])
    qty = c_qty.number_input("Qty", min_value=1, value=1)
    harga = st.session_state.master[pilih][0]
    total_t = harga * qty
    
    st.markdown(f"""
        <div class="tagihan-box">
            <span style="color:#aaa; font-size:12px;">Tagihan</span>
            <span class="tagihan-angka">Rp {total_t:,.0f}</span>
        </div>
    """, unsafe_allow_html=True)

    st.write("💰 **Pilih Nominal Uang:**")
    
    # --- SUSUNAN RAPI SESUAI PERMINTAAN ---
    # Baris 1: 5rb, 10rb, 20rb
    r1_c1, r1_c2, r1_c3 = st.columns(3)
    if r1_c1.button("5rb", use_container_width=True): st.session_state.b = 5000
    if r1_c2.button("10rb", use_container_width=True): st.session_state.b = 10000
    if r1_c3.button("20rb", use_container_width=True): st.session_state.b = 20000
    
    # Baris 2: 50rb, 100rb, PAS
    r2_c1, r2_c2, r2_c3 = st.columns(3)
    if r2_c1.button("50rb", use_container_width=True): st.session_state.b = 50000
    if r2_c2.button("100rb", use_container_width=True): st.session_state.b = 100000
    if r2_c3.button("PAS", use_container_width=True): st.session_state.b = total_t

    # Input Bayar (Nol Otomatis Hilang)
    bayar = st.number_input("Nominal Bayar", value=st.session_state.b, placeholder="Atau ketik di sini...", step=500)
    
    col_del, col_save = st.columns([0.4, 0.6])
    if col_del.button("❌ Hapus", use_container_width=True):
        st.session_state.b = None
        st.rerun()
    
    if bayar and bayar >= total_t:
        st.success(f"Kembali: Rp {bayar-total_t:,.0f}")
        if col_save.button("✅ SIMPAN", use_container_width=True):
            payload = {
                "entry.1005808381": "Pemasukan", "entry.544255428": pilih,
                "entry.1418739506": str(total_t), "entry.1637268017": datetime.today().strftime('%Y-%m-%d')
            }
            requests.post("https://docs.google.com/forms/d/e/1FAIpQLSc8wjCuUX01A4MRBLuGx1UaAIAhdQ6G9yPsnhskJ1fKtEFzgA/formResponse", data=payload)
            st.session_state.master[pilih][1] -= qty
            st.session_state.b = None
            st.rerun()

    # Rekap Penjualan Hari Ini
    st.divider()
    df_all = get_data()
    if not df_all.empty:
        df_today = df_all[df_all['Tanggal'] == datetime.today().date()]
        if not df_today.empty:
            rekap = df_today.groupby('Produk').agg(Laku=('Produk','count'), Total=('Total','sum')).reset_index()
            st.write("📊 **Riwayat Hari Ini:**")
            st.dataframe(rekap, use_container_width=True, hide_index=True)

# Tab Lainnya (Stok & Info) tetap aman
with tab2:
    st.write("### Edit Stok")
    df_m = pd.DataFrame.from_dict(st.session_state.master, orient='index', columns=['Harga', 'Stok'])
    st.data_editor(df_m, use_container_width=True)

with tab3:
    st.write("### Grafik Penjualan")
    df = get_data()
    if not df.empty:
        st.plotly_chart(px.pie(df, values='Total', names='Produk', hole=0.4), use_container_width=True)
