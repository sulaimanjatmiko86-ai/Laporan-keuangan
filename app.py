import streamlit as st
import pandas as pd
from datetime import datetime
import requests
import plotly.express as px

# 1. DATABASE & CONFIG
URL_CSV = "https://docs.google.com/spreadsheets/d/1P64EoKz-DZgwGyOMtgPbN_vLdax4IUxluWHLi8cmnwo/export?format=csv"
st.set_page_config(page_title="Kasir Jaya", layout="centered")

st.markdown("""
    <style>
    /* Hilangkan spasi kosong di pinggir */
    .block-container { padding: 0.5rem !important; max-width: 100% !important; }
    
    /* Box Tagihan - Angka Tidak Akan Terpotong */
    .tagihan-box {
        background: #1e2130; padding: 12px; border-radius: 12px;
        border-left: 5px solid #007bff; margin-bottom: 10px;
        display: flex; justify-content: space-between; align-items: center;
    }
    .tagihan-angka { color: #007bff; font-size: 20px; font-weight: bold; }

  
    div[data-testid="stHorizontalBlock"] {
        display: flex !important;
        flex-direction: row !important; /* Paksa horizontal */
        flex-wrap: nowrap !important; /* Jangan biarkan turun ke bawah */
        gap: 5px !important;
    }
    div[data-testid="column"] {
        flex: 1 1 0% !important; /* Bagi 3 rata */
        min-width: 0px !important;
    }
    
    /* Tombol agar pas di kotak */
    button { 
        width: 100% !important; 
        padding: 0px !important; 
        height: 45px !important; 
        font-size: 13px !important;
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
        # Pastikan data Jumlah dibersihkan dari huruf (seperti 'G' di foto kamu)
        df['Total'] = pd.to_numeric(df['Total'], errors='coerce').fillna(0).astype(int)
        df['Tanggal'] = pd.to_datetime(df['Tanggal'], errors='coerce').dt.date
        return df
    except: return pd.DataFrame()

st.markdown("<div style='text-align:center; color:#555; font-size:10px;'>POS JAYA v13 - FIX GRID</div>", unsafe_allow_html=True)

tab1, tab2, tab3 = st.tabs(["🛒 KASIR", "📦 STOK", "📊 INFO"])

with tab1:
    pilih = st.selectbox("Menu", list(st.session_state.master.keys()), label_visibility="collapsed")
    
    # Qty dan Tagihan
    c_qty, c_tag = st.columns([0.4, 0.6])
    qty = c_qty.number_input("Qty", min_value=1, value=1)
    harga = st.session_state.master[pilih][0]
    total_t = harga * qty
    
    c_tag.markdown(f"""
        <div class="tagihan-box">
            <span style="color:#aaa; font-size:10px;">Total</span>
            <span class="tagihan-angka">Rp {total_t:,.0f}</span>
        </div>
    """, unsafe_allow_html=True)

    st.write("💰 **Uang Bayar:**")
    
    # BARIS 1: PAS, 5rb, 10rb 
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("PAS"): st.session_state.b = total_t
    with col2:
        if st.button("5rb"): st.session_state.b = 5000
    with col3:
        if st.button("10rb"): st.session_state.b = 10000
        
    # BARIS 2: 20rb, 50rb, 100rb 
    col4, col5, col6 = st.columns(3)
    with col4:
        if st.button("20rb"): st.session_state.b = 20000
    with col5:
        if st.button("50rb"): st.session_state.b = 50000
    with col6:
        if st.button("100rb"): st.session_state.b = 100000
    
    if st.button("❌ Hapus / Ketik Manual", use_container_width=True):
        st.session_state.b = None

    bayar = st.number_input("Nominal Bayar", value=st.session_state.b, placeholder="Ketik di sini...", step=500)
    
    if bayar and bayar >= total_t:
        st.success(f"Kembali: Rp {bayar-total_t:,.0f}")
        if st.button("✅ SELESAIKAN", use_container_width=True):
            payload = {
                "entry.1005808381": "Pemasukan", "entry.544255428": pilih,
                "entry.1418739506": str(total_t), "entry.1637268017": datetime.today().strftime('%Y-%m-%d')
            }
            requests.post("https://docs.google.com/forms/d/e/1FAIpQLSc8wjCuUX01A4MRBLuGx1UaAIAhdQ6G9yPsnhskJ1fKtEFzgA/formResponse", data=payload)
            st.session_state.master[pilih][1] -= qty
            st.session_state.b = None
            st.rerun()

    # Rekap Singkat
    df_all = get_data()
    if not df_all.empty:
        df_today = df_all[df_all['Tanggal'] == datetime.today().date()]
        if not df_today.empty:
            st.divider()
            rekap = df_today.groupby('Produk').agg(Laku=('Produk','count'), Total=('Total','sum')).reset_index()
            st.dataframe(rekap, use_container_width=True, hide_index=True)

with tab2:
    st.write("### 📦 Stok")
    df_m = pd.DataFrame.from_dict(st.session_state.master, orient='index', columns=['Harga', 'Stok'])
    edit_df = st.data_editor(df_m, use_container_width=True)
    if st.button("Update"):
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
