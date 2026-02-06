import streamlit as st
import pandas as pd
from datetime import datetime
import requests
import plotly.express as px

# 1. DATABASE & CONFIG
URL_CSV = "https://docs.google.com/spreadsheets/d/1P64EoKz-DZgwGyOMtgPbN_vLdax4IUxluWHLi8cmnwo/export?format=csv"
st.set_page_config(page_title="Kasir Jaya", layout="centered")

# 2. CSS & JS PAMUNGKAS (ANTI-KE BAWAH & ANTI-POTONG)
st.markdown("""
    <style>
    /* Paksa layar full tanpa margin */
    .block-container { padding: 0.5rem !important; max-width: 100% !important; }
    
    /* Box Tagihan yang Gak Bakal Kepotong */
    .tagihan-box {
        background: #1e2130;
        padding: 12px;
        border-radius: 12px;
        border-left: 5px solid #007bff;
        margin-bottom: 10px;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    .tagihan-label { color: #aaa; font-size: 12px; }
    .tagihan-angka { color: #007bff; font-size: 20px; font-weight: bold; }

    /* CONTAINER TOMBOL JEJER 3 MURNI */
    .grid-container {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 8px;
        width: 100%;
        margin-bottom: 10px;
    }
    .grid-item {
        background-color: #262730;
        color: white;
        border: 1px solid #444;
        padding: 12px 0;
        text-align: center;
        border-radius: 8px;
        cursor: pointer;
        font-weight: bold;
        font-size: 14px;
    }
    .grid-item:active { background-color: #007bff; }
    </style>
    """, unsafe_allow_html=True)

# State Management
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

st.markdown("<div style='font-size:10px; text-align:center; color:#555;'>POS JAYA ULTIMATE v11</div>", unsafe_allow_html=True)

tab1, tab2, tab3 = st.tabs(["🛒 KASIR", "📦 STOK", "📊 INFO"])

with tab1:
    pilih = st.selectbox("Menu", list(st.session_state.master.keys()), label_visibility="collapsed")
    
    # Bagian Input Qty & Tagihan
    cq, ct = st.columns([0.4, 0.6])
    qty = cq.number_input("Qty", min_value=1, value=1)
    harga = st.session_state.master[pilih][0]
    total_t = harga * qty
    
    # Tagihan Custom HTML
    st.markdown(f"""
        <div class="tagihan-box">
            <span class="tagihan-label">Total Tagihan</span>
            <span class="tagihan-angka">Rp {total_t:,.0f}</span>
        </div>
    """, unsafe_allow_html=True)

    st.write("💰 **Uang Bayar (Jejer 3):**")
    
    # TEKNIK BARU: Tombol Jejer 3 Pakai Button Bawaan tapi CSS Diperketat
    # Kita tidak pakai columns(3) lagi, tapi pakai container CSS Grid
    st.markdown('<div class="grid-container">', unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    with c1: 
        if st.button("PAS", key="btn_pas", use_container_width=True): st.session_state.b = total_t
    with c2: 
        if st.button("5rb", key="btn_5", use_container_width=True): st.session_state.b = 5000
    with c3: 
        if st.button("10rb", key="btn_10", use_container_width=True): st.session_state.b = 10000
    
    c4, c5, c6 = st.columns(3)
    with c4: 
        if st.button("20rb", key="btn_20", use_container_width=True): st.session_state.b = 20000
    with c5: 
        if st.button("50rb", key="btn_50", use_container_width=True): st.session_state.b = 50000
    with c6: 
        if st.button("100rb", key="btn_100", use_container_width=True): st.session_state.b = 100000
    
    bayar = st.number_input("Input Bayar", value=st.session_state.b, label_visibility="collapsed")
    
    if bayar >= total_t:
        st.success(f"Kembali: Rp {bayar-total_t:,.0f}")
        if st.button("✅ SELESAIKAN TRANSAKSI", use_container_width=True):
            payload = {
                "entry.1005808381": "Pemasukan", "entry.544255428": pilih,
                "entry.1418739506": str(total_t), "entry.1637268017": datetime.today().strftime('%Y-%m-%d')
            }
            requests.post("https://docs.google.com/forms/d/e/1FAIpQLSc8wjCuUX01A4MRBLuGx1UaAIAhdQ6G9yPsnhskJ1fKtEFzgA/formResponse", data=payload)
            st.session_state.master[pilih][1] -= qty
            st.session_state.b = 0
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
    st.write("### 📊 Info")
    df = get_data()
    if not df.empty:
        df['Bulan'] = pd.to_datetime(df['Tanggal']).dt.strftime('%b %Y')
        sel_bln = st.selectbox("Bulan", df['Bulan'].unique())
        df_f = df[df['Bulan'] == sel_bln]
        st.metric("Omzet", f"Rp {df_f['Total'].sum():,.0f}")
        st.plotly_chart(px.pie(df_f, values='Total', names='Produk', hole=0.5), use_container_width=True)
