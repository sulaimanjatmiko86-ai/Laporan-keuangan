import streamlit as st
import pandas as pd
from datetime import datetime
import requests
import plotly.express as px

# 1. DATABASE & CONFIG
URL_CSV = "https://docs.google.com/spreadsheets/d/1P64EoKz-DZgwGyOMtgPbN_vLdax4IUxluWHLi8cmnwo/export?format=csv"
st.set_page_config(page_title="Kasir Jaya", layout="centered")

# 2. CSS "FIX PERMANEN" (ANTI-RAKSASA, ANTI-TUMPANG TINDIH)
st.markdown("""
    <style>
    .block-container { padding: 0.5rem !important; max-width: 100% !important; }
    
    /* Box Tagihan Rapi */
    .tagihan-box {
        background: #1e2130; padding: 12px; border-radius: 12px;
        border-left: 5px solid #007bff; margin-bottom: 10px;
        display: flex; justify-content: space-between; align-items: center;
    }
    .tagihan-angka { color: #007bff; font-size: 22px; font-weight: bold; }

    /* TOMBOL CUSTOM (Gak bakal berubah ukuran di HP manapun) */
    .tombol-grid {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 8px;
        margin-bottom: 15px;
    }
    .stButton button {
        width: 100% !important;
        height: 45px !important;
        font-size: 14px !important;
        font-weight: bold !important;
        border-radius: 8px !important;
        padding: 0px !important;
    }
    
    /* Sembunyikan label bawaan agar ramping */
    div[data-testid="stMetricLabel"] { display: none; }
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
        # Fix data sampah seperti di foto (Hh, Vb, G)
        df['Total'] = pd.to_numeric(df['Total'], errors='coerce').fillna(0).astype(int)
        df['Tanggal'] = pd.to_datetime(df['Tanggal'], errors='coerce').dt.date
        return df
    except: return pd.DataFrame()

st.markdown("<h3 style='text-align:center; margin-bottom:0;'>POS JAYA PRO v15</h3>", unsafe_allow_html=True)

tab1, tab2, tab3 = st.tabs(["🛒 KASIR", "📦 STOK", "📊 INFO"])

with tab1:
    pilih = st.selectbox("Pilih Menu", list(st.session_state.master.keys()))
    
    c_qty, c_t = st.columns([0.4, 0.6])
    qty = c_qty.number_input("Qty", min_value=1, value=1)
    harga = st.session_state.master[pilih][0]
    total_t = harga * qty
    
    # Tampilan Tagihan
    st.markdown(f"""
        <div class="tagihan-box">
            <span style="color:#aaa; font-size:12px;">Total Tagihan</span>
            <span class="tagihan-angka">Rp {total_t:,.0f}</span>
        </div>
    """, unsafe_allow_html=True)

    st.write("💰 **Pilih Uang:**")
    
    # GRID TOMBOL HARGA MATI (JEJER 3 RAPI)
    c1, c2, c3 = st.columns(3)
    with c1: 
        if st.button("PAS", use_container_width=True): st.session_state.b = total_t
    with c2: 
        if st.button("5rb", use_container_width=True): st.session_state.b = 5000
    with c3: 
        if st.button("10rb", use_container_width=True): st.session_state.b = 10000
    
    c4, c5, c6 = st.columns(3)
    with c4: 
        if st.button("20rb", use_container_width=True): st.session_state.b = 20000
    with c5: 
        if st.button("50rb", use_container_width=True): st.session_state.b = 50000
    with c6: 
        if st.button("100rb", use_container_width=True): st.session_state.b = 100000
    
    # Input Nominal (Auto Clear 0)
    bayar = st.number_input("Nominal Bayar", value=st.session_state.b, placeholder="Ketik manual...", step=500)
    
    if st.button("❌ Hapus Nominal", use_container_width=True):
        st.session_state.b = None
        st.rerun()
    
    if bayar and bayar >= total_t:
        st.success(f"Kembali: Rp {bayar-total_t:,.0f}")
        if st.button("✅ SELESAIKAN TRANSAKSI", use_container_width=True):
            payload = {
                "entry.1005808381": "Pemasukan", "entry.544255428": pilih,
                "entry.1418739506": str(total_t), "entry.1637268017": datetime.today().strftime('%Y-%m-%d')
            }
            requests.post("https://docs.google.com/forms/d/e/1FAIpQLSc8wjCuUX01A4MRBLuGx1UaAIAhdQ6G9yPsnhskJ1fKtEFzgA/formResponse", data=payload)
            st.session_state.master[pilih][1] -= qty
            st.session_state.b = None
            st.rerun()

    # Rekap Hari Ini (Tabel)
    st.divider()
    df_all = get_data()
    if not df_all.empty:
        df_today = df_all[df_all['Tanggal'] == datetime.today().date()]
        if not df_today.empty:
            rekap = df_today.groupby('Produk').agg(Laku=('Produk','count'), Total=('Total','sum')).reset_index()
            st.write("📊 **Rekap Hari Ini:**")
            st.dataframe(rekap, use_container_width=True, hide_index=True)

with tab2:
    st.write("### 📦 Stok & Harga")
    df_m = pd.DataFrame.from_dict(st.session_state.master, orient='index', columns=['Harga', 'Stok'])
    edit_df = st.data_editor(df_m, use_container_width=True)
    if st.button("Simpan Perubahan"):
        for i in edit_df.index:
            st.session_state.master[i] = [edit_df.at[i, 'Harga'], edit_df.at[i, 'Stok']]
        st.success("Tersimpan!")

with tab3:
    st.write("### 📈 Grafik Penjualan")
    df = get_data()
    if not df.empty:
        # 1. Diagram Bulat (Dominasi Produk)
        st.write("🍩 **Produk Paling Laku**")
        fig_pie = px.pie(df, values='Total', names='Produk', hole=0.4, color_discrete_sequence=px.colors.qualitative.Pastel)
        st.plotly_chart(fig_pie, use_container_width=True)
        
        # 2. Grafik Batang
        st.write("📊 **Total Omzet per Produk**")
        summary = df.groupby('Produk')['Total'].sum().reset_index()
        fig_bar = px.bar(summary, x='Produk', y='Total', color='Produk', text_auto='.2s')
        st.plotly_chart(fig_bar, use_container_width=True)
