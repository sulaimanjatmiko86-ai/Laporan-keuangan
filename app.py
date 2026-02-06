import streamlit as st
import pandas as pd
from datetime import datetime
import requests
import plotly.express as px

# 1. DATABASE & CONFIG
URL_CSV = "https://docs.google.com/spreadsheets/d/1P64EoKz-DZgwGyOMtgPbN_vLdax4IUxluWHLi8cmnwo/export?format=csv"
st.set_page_config(page_title="Kasir Jaya", layout="centered")

# 2. CSS ANTI-KEBAWAH & ANTI-POTONG (TETAP DIKUNCI JEJER 3)
st.markdown("""
    <style>
    .block-container { padding: 0.5rem !important; max-width: 100% !important; }
    .tagihan-box {
        background: #1e2130; padding: 12px; border-radius: 12px;
        border-left: 5px solid #007bff; margin-bottom: 10px;
        display: flex; justify-content: space-between; align-items: center;
    }
    .tagihan-label { color: #aaa; font-size: 12px; }
    .tagihan-angka { color: #007bff; font-size: 20px; font-weight: bold; white-space: nowrap; }

    /* PAKSA JEJER 3 DI SEMUA HP */
    [data-testid="stHorizontalBlock"] {
        display: flex !important; flex-direction: row !important;
        gap: 5px !important; width: 100% !important;
    }
    [data-testid="column"] { flex: 1 !important; min-width: 0px !important; }
    button { height: 45px !important; font-size: 12px !important; border-radius: 8px !important; }
    
    /* Input Nominal Bayar agar lebih menonjol */
    .stNumberInput input { font-size: 18px !important; font-weight: bold !important; color: #28a745 !important; }
    </style>
    """, unsafe_allow_html=True)

# State Management
if 'b' not in st.session_state: st.session_state.b = None # Set None agar 0 hilang
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

st.markdown("<div style='font-size:10px; text-align:center; color:#555;'>POS JAYA v12 - AUTO CLEAR</div>", unsafe_allow_html=True)

tab1, tab2, tab3 = st.tabs(["🛒 KASIR", "📦 STOK", "📊 INFO"])

with tab1:
    pilih = st.selectbox("Menu", list(st.session_state.master.keys()), label_visibility="collapsed")
    
    cq, ct = st.columns([0.4, 0.6])
    qty = cq.number_input("Qty", min_value=1, value=1)
    harga = st.session_state.master[pilih][0]
    total_t = harga * qty
    
    st.markdown(f"""
        <div class="tagihan-box">
            <span class="tagihan-label">Total Tagihan</span>
            <span class="tagihan-angka">Rp {total_t:,.0f}</span>
        </div>
    """, unsafe_allow_html=True)

    st.write("💰 **Klik Tombol Uang:**")
    
    # Baris 1
    c1, c2, c3 = st.columns(3)
    if c1.button("PAS"): st.session_state.b = total_t
    if c2.button("5rb"): st.session_state.b = 5000
    if c3.button("10rb"): st.session_state.b = 10000
    
    # Baris 2
    c4, c5, c6 = st.columns(3)
    if c4.button("20rb"): st.session_state.b = 20000
    if c5.button("50rb"): st.session_state.b = 50000
    if c6.button("100rb"): st.session_state.b = 100000
    
    # Tombol Reset Manual
    if st.button("Hapus Nominal / Ketik Manual"): st.session_state.b = None

    # INPUT BAYAR: Sekarang pakai value=st.session_state.b yang bisa None
    bayar = st.number_input("Nominal Bayar", value=st.session_state.b, placeholder="Ketik nominal di sini...", step=500)
    
    if bayar and bayar >= total_t:
        st.success(f"Kembali: Rp {bayar-total_t:,.0f}")
        if st.button("✅ SELESAIKAN TRANSAKSI", use_container_width=True):
            payload = {
                "entry.1005808381": "Pemasukan", "entry.544255428": pilih,
                "entry.1418739506": str(total_t), "entry.1637268017": datetime.today().strftime('%Y-%m-%d')
            }
            requests.post("https://docs.google.com/forms/d/e/1FAIpQLSc8wjCuUX01A4MRBLuGx1UaAIAhdQ6G9yPsnhskJ1fKtEFzgA/formResponse", data=payload)
            st.session_state.master[pilih][1] -= qty
            st.session_state.b = None # Reset ke kosong lagi
            st.rerun()

    # REKAP PENJUALAN
    st.divider()
    df_all = get_data()
    if not df_all.empty:
        df_today = df_all[df_all['Tanggal'] == datetime.today().date()]
        if not df_today.empty:
            rekap = df_today.groupby('Produk').agg(Laku=('Produk','count'), Total=('Total','sum')).reset_index()
            st.write("📊 **Rekap Hari Ini:**")
            st.dataframe(rekap, use_container_width=True, hide_index=True)
            st.info(f"Total Uang: Rp {rekap['Total'].sum():,.0f}")

with tab2:
    st.write("### 📦 Stok")
    df_m = pd.DataFrame.from_dict(st.session_state.master, orient='index', columns=['Harga', 'Stok'])
    edit_df = st.data_editor(df_m, use_container_width=True)
    if st.button("Update Stok"):
        for i in edit_df.index:
            st.session_state.master[i] = [edit_df.at[i, 'Harga'], edit_df.at[i, 'Stok']]
        st.rerun()

with tab3:
    st.write("### 📊 Laporan")
    df = get_data()
    if not df.empty:
        df['Bulan'] = pd.to_datetime(df['Tanggal']).dt.strftime('%b %Y')
        sel_bln = st.selectbox("Bulan", df['Bulan'].unique())
        df_f = df[df['Bulan'] == sel_bln]
        st.metric("Omzet", f"Rp {df_f['Total'].sum():,.0f}")
        st.plotly_chart(px.pie(df_f, values='Total', names='Produk', hole=0.5), use_container_width=True)
