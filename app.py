import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

# 1. KONFIGURASI HALAMAN
st.set_page_config(page_title="Kasir Jaya Digital", layout="wide", page_icon="🏪")

# 2. INISIALISASI DATABASE (Menggunakan format: "Nama": [Harga, Stok])
if 'master_barang' not in st.session_state:
    st.session_state.master_barang = {
        "Kopi Espresso": [15000, 50],
        "Roti Bakar": [20000, 30],
        "Air Mineral": [5000, 100]
    }

if 'data' not in st.session_state:
    st.session_state.data = pd.DataFrame(columns=['Tipe', 'Kategori', 'Jumlah', 'Tanggal'])

# 3. GAYA DESAIN (CSS)
st.markdown("""
    <style>
    .header-box {
        text-align: center;
        padding: 25px;
        background: linear-gradient(to right, #1e3c72, #2a5298);
        color: white;
        border-radius: 15px;
        margin-bottom: 20px;
    }
    .stMetric {
        background-color: #ffffff;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    </style>
    """, unsafe_allow_html=True)

# 4. JUDUL TOKO
st.markdown('<div class="header-box"><h1>🏪 KASIR JAYA DIGITAL</h1><p>Sistem Kasir & Stok Gudang Terintegrasi</p></div>', unsafe_allow_html=True)

# 5. NAVIGASI SIDEBAR
with st.sidebar:
    st.title("📌 MENU UTAMA")
    menu = st.radio("Pilih Halaman:", ["🛒 Mesin Kasir", "📦 Kelola Produk & Stok", "📊 Laporan Keuangan"])
    st.divider()
    st.info("Edit barang dan stok di menu 'Kelola Produk'.")

# --- HALAMAN 1: MESIN KASIR ---
if menu == "🛒 Mesin Kasir":
    st.subheader("📝 Catat Transaksi Baru")
    col1, col2 = st.columns([2, 1])
    
    with col1:
        with st.expander("✨ Input Barang Otomatis", expanded=True):
            daftar = ["--- Pilih Barang ---"] + list(st.session_state.master_barang.keys())
            pilihan = st.selectbox("Cari Produk:", daftar)
            qty = st.number_input("Jumlah Beli:", min_value=1, value=1)
            
            if pilihan != "--- Pilih Barang ---":
                harga_satuan = st.session_state.master_barang[pilihan][0]
                stok_tersedia = st.session_state.master_barang[pilihan][1]
                total_harga = harga_satuan * qty
                
                st.write(f"Harga Satuan: **Rp {harga_satuan:,.0f}**")
                st.write(f"Stok Tersedia: **{stok_tersedia}**")
                st.write(f"### Total Bayar: Rp {total_harga:,.0f}")
                
                if st.button("➕ Tambahkan ke Laporan", use_container_width=True):
                    if qty <= stok_tersedia:
                        # Kurangi Stok
                        st.session_state.master_barang[pilihan][1] -= qty
                        # Catat Transaksi
                        new_row = pd.DataFrame({'Tipe':['Pemasukan'], 'Kategori':[pilihan], 'Jumlah':[total_harga], 'Tanggal':[datetime.today().date()]})
                        st.session_state.data = pd.concat([st.session_state.data, new_row], ignore_index=True)
                        st.success(f"Berhasil! Stok {pilihan} sekarang: {st.session_state.master_barang[pilihan][1]}")
                    else:
                        st.error("Gagal! Stok tidak mencukupi.")

    with col2:
        with st.expander("✍️ Input Lainnya (Manual)"):
            tipe_m = st.selectbox("Jenis:", ["Pemasukan", "Pengeluaran"])
            nama_m = st.text_input("Keterangan:")
            jumlah_m = st.number_input("Nominal (Rp):", min_value=0)
            if st.button("💾 Simpan Manual"):
                if nama_m and jumlah_m > 0:
                    new_row = pd.DataFrame({'Tipe':[tipe_m], 'Kategori':[nama_m], 'Jumlah':[jumlah_m], 'Tanggal':[datetime.today().date()]})
                    st.session_state.data = pd.concat([st.session_state.data, new_row], ignore_index=True)
                    st.success("Tersimpan!")

# --- HALAMAN 2: KELOLA PRODUK & STOK ---
elif menu == "📦 Kelola Produk & Stok":
    st.subheader("⚙️ Manajemen Inventaris")
    t1, t2 = st.tabs(["➕ Tambah Produk Baru", "🔧 Update Stok & Hapus"])
    
    with t1:
        with st.form("tambah_p"):
            n_baru = st.text_input("Nama Barang:")
            h_baru = st.number_input("Harga Jual:", min_value=0)
            s_baru = st.number_input("Stok Awal:", min_value=0)
            if st.form_submit_button("Simpan Produk"):
                if n_baru and h_baru > 0:
                    st.session_state.master_barang[n_baru] = [h_baru, s_baru]
                    st.success(f"'{n_baru}' telah ditambahkan.")
                    st.rerun()

    with t2:
        if st.session_state.master_barang:
            pilih_p = st.selectbox("Pilih Produk:", list(st.session_state.master_barang.keys()))
            c_a, c_b = st.columns(2)
            with c_a:
                st.write(f"Stok Saat Ini: **{st.session_state.master_barang[pilih_p][1]}**")
                up_stok = st.number_input("Tambah Stok (isi angka negatif untuk mengurangi):", value=0)
                if st.button("Update Stok"):
                    st.session_state.master_barang[pilih_p][1] += up_stok
                    st.success("Stok diperbarui!")
            with c_b:
                st.write(f"Harga: **Rp {st.session_state.master_barang[pilih_p][0]:,.0f}**")
                if st.button("🗑️ Hapus Produk Ini", type="primary"):
                    del st.session_state.master_barang[pilih_p]
                    st.rerun()
        else:
            st.warning("Belum ada produk.")

# --- HALAMAN 3: LAPORAN ---
else:
    st.subheader("📊 Laporan Keuangan")
    in_sum = st.session_state.data[st.session_state.data['Tipe'] == 'Pemasukan']['Jumlah'].sum()
    out_sum = st.session_state.data[st.session_state.data['Tipe'] == 'Pengeluaran']['Jumlah'].sum()
    
    m1, m2, m3 = st.columns(3)
    m1.metric("💰 Saldo Kas", f"Rp {in_sum - out_sum:,.0f}")
    m2.metric("📈 Total Masuk", f"Rp {in_sum:,.0f}")
    m3.metric("📉 Total Keluar", f"Rp {out_sum:,.0f}")
    
    st.divider()
    st.write("**Riwayat Transaksi**")
    st.dataframe(st.session_state.data.sort_values(by='Tanggal', ascending=False), use_container_width=True)
