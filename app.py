import streamlit as st
import pandas as pd
from datetime import datetime
import requests
import plotly.express as px

# 1. KONFIGURASI HALAMAN & TEMA
st.set_page_config(page_title="Kasir Pro Jaya", layout="wide", page_icon="💰")

# CSS untuk mempercantik tampilan
st.markdown("""
    <style>
    .main { background-color: #f5f7f9; }
    .stButton>button { width: 100%; border-radius: 10px; height: 3em; background-color: #007bff; color: white; }
    .card { padding: 20px; background: white; border-radius: 15px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
    .price-tag { color: #28a745; font-weight: bold; font-size: 20px; }
    </style>
    """, unsafe_allow_html=True)

# 2. DATABASE STOK & BARANG
if 'master_barang' not in st.session_state:
    st.session_state.master_barang = {
        "☕ Kopi Espresso": [15000, 50],
        "🍞 Roti Bakar": [20000, 30],
        "🥤 Air Mineral": [5000, 100],
        "🍵 Teh Manis": [8000, 40]
    }

if 'keranjang' not in st.session_state:
    st.session_state.keranjang = []

# 3. FUNGSI KIRIM KE GOOGLE SHEETS
def simpan_ke_cloud(item, total):
    url = "https://docs.google.com/forms/d/e/1FAIpQLSc8wjCuUX01A4MRBLuGx1UaAIAhdQ6G9yPsnhskJ1fKtEFzgA/formResponse"
    tgl = datetime.today().strftime('%Y-%m-%d')
    payload = {
        "entry.1444153920": "Pemasukan",
        "entry.2065873155": item,
        "entry.143715201": total,
        "entry.1098693740": tgl
    }
    try:
        requests.post(url, data=payload)
        return True
    except:
        return False

# 4. SIDEBAR MENU
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/4300/4300058.png", width=100)
    st.title("Sistem Kasir Pro")
    menu = st.radio("Pilih Menu:", ["🛒 Kasir Utama", "📦 Manajemen Stok", "📊 Grafik Penjualan"])

# --- HALAMAN 1: KASIR UTAMA ---
if menu == "🛒 Kasir Utama":
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("🛍️ Pilih Produk")
        # Menampilkan barang dalam bentuk Grid agar keren
        items = list(st.session_state.master_barang.keys())
        cols = st.columns(3)
        for i, item in enumerate(items):
            with cols[i % 3]:
                st.markdown(f"**{item}**")
                st.write(f"Rp {st.session_state.master_barang[item][0]:,.0f}")
                if st.button(f"Tambah", key=item):
                    st.session_state.keranjang.append({"item": item, "harga": st.session_state.master_barang[item][0]})
                    st.toast(f"{item} ditambah!")

    with col2:
        st.subheader("🧾 Ringkasan")
        if st.session_state.keranjang:
            df_keranjang = pd.DataFrame(st.session_state.keranjang)
            total_bayar = df_keranjang['harga'].sum()
            
            st.table(df_keranjang)
            st.markdown(f"### Total: Rp {total_bayar:,.0f}")
            
            bayar = st.number_input("Uang Dibayar:", min_value=0)
            
            if bayar >= total_bayar:
                st.write(f"Kembali: **Rp {bayar - total_bayar:,.0f}**")
                if st.button("🚀 SELESAIKAN TRANSAKSI"):
                    # Kirim gabungan nama barang ke Cloud
                    nama_semua = ", ".join(df_keranjang['item'].tolist())
                    if simpan_ke_cloud(nama_semua, total_bayar):
                        # Potong Stok
                        for i in df_keranjang['item']:
                            st.session_state.master_barang[i][1] -= 1
                        st.session_state.keranjang = []
                        st.success("Transaksi Berhasil & Cloud Tersimpan!")
                        st.balloons()
            
            if st.button("🗑️ Kosongkan Keranjang"):
                st.session_state.keranjang = []
                st.rerun()
        else:
            st.info("Keranjang kosong. Pilih barang di samping!")

# --- HALAMAN 2: MANAJEMEN STOK ---
elif menu == "📦 Manajemen Stok":
    st.subheader("🛠️ Atur Harga & Stok")
    df_stok = pd.DataFrame.from_dict(st.session_state.master_barang, orient='index', columns=['Harga', 'Stok'])
    st.data_editor(df_stok) # Bisa edit langsung di tabel!
    st.info("Edit tabel di atas lalu simpan jika ingin mengubah data secara cepat.")

# --- HALAMAN 3: GRAFIK PENJUALAN ---
else:
    st.subheader("📈 Visual Penjualan Real-time")
    # Contoh data untuk grafik (ideal nya ditarik dari Google Sheets)
    data_grafik = pd.DataFrame({
        "Hari": ["Senin", "Selasa", "Rabu", "Kamis", "Jumat"],
        "Omzet": [150000, 200000, 180000, 250000, 300000]
    })
    fig = px.bar(data_grafik, x="Hari", y="Omzet", title="Omzet Mingguan", color="Omzet")
    st.plotly_chart(fig, use_container_width=True)
    st.write("Hubungkan Google Sheets kamu untuk menampilkan data asli di sini.")
