import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

# 1. KONFIGURASI HALAMAN
st.set_page_config(page_title="Kasir Jaya Digital", layout="wide", page_icon="🏪")

# 2. INISIALISASI DATABASE
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
    .bayar-box {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        border-left: 5px solid #1E88E5;
    }
    </style>
    """, unsafe_allow_html=True)

st.markdown('<div class="header-box"><h1>🏪 KASIR JAYA DIGITAL</h1><p>Sistem Kasir Pintar & Hitung Kembalian</p></div>', unsafe_allow_html=True)

# 4. NAVIGASI
with st.sidebar:
    st.title("📌 MENU UTAMA")
    menu = st.radio("Pilih Halaman:", ["🛒 Mesin Kasir", "📦 Kelola Produk & Stok", "📊 Laporan Keuangan"])

# --- HALAMAN 1: MESIN KASIR ---
if menu == "🛒 Mesin Kasir":
    st.subheader("📝 Transaksi Baru")
    col1, col2 = st.columns([1.5, 1])
    
    with col1:
        with st.expander("✨ Pilih Produk", expanded=True):
            daftar = ["--- Pilih Barang ---"] + list(st.session_state.master_barang.keys())
            pilihan = st.selectbox("Cari Produk:", daftar)
            qty = st.number_input("Jumlah Beli:", min_value=1, value=1)
            
            if pilihan != "--- Pilih Barang ---":
                harga_satuan = st.session_state.master_barang[pilihan][0]
                stok_tersedia = st.session_state.master_barang[pilihan][1]
                total_harga = harga_satuan * qty
                
                st.write(f"Harga: **Rp {harga_satuan:,.0f}** | Stok: **{stok_tersedia}**")
                st.markdown(f"### Total Tagihan: Rp {total_harga:,.0f}")
                
                st.divider()
                st.write("💰 **Pembayaran**")
                
                # Pilihan uang cepat & manual
                col_uang1, col_uang2 = st.columns(2)
                with col_uang1:
                    uang_pas = st.button(f"Uang Pas (Rp {total_harga:,.0f})")
                    pecahan = st.selectbox("Pilihan Uang Pecahan:", [0, 5000, 10000, 20000, 50000, 100000])
                
                with col_uang2:
                    bayar_manual = st.number_input("Input Uang Manual (Rp):", min_value=0, step=500)
                
                # Menentukan jumlah bayar
                jumlah_bayar = 0
                if uang_pas:
                    jumlah_bayar = total_harga
                elif bayar_manual > 0:
                    jumlah_bayar = bayar_manual
                elif pecahan > 0:
                    jumlah_bayar = pecahan

                if jumlah_bayar > 0:
                    kembalian = jumlah_bayar - total_harga
                    st.markdown(f"""
                    <div class="bayar-box">
                        <p>Bayar: <b>Rp {jumlah_bayar:,.0f}</b></p>
                        <h3>Kembalian: Rp {kembalian:,.0f}</h3>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    if kembalian < 0:
                        st.error("Uang tidak cukup!")
                    else:
                        if st.button("✅ SELESAIKAN TRANSAKSI", use_container_width=True):
                            if qty <= stok_tersedia:
                                # Update Stok & Data
                                st.session_state.master_barang[pilihan][1] -= qty
                                new_row = pd.DataFrame({'Tipe':['Pemasukan'], 'Kategori':[pilihan], 'Jumlah':[total_harga], 'Tanggal':[datetime.today().date()]})
                                st.session_state.data = pd.concat([st.session_state.data, new_row], ignore_index=True)
                                st.balloons()
                                st.success(f"Transaksi Berhasil! Kembalian diberikan: Rp {kembalian:,.0f}")
                            else:
                                st.error("Stok habis!")

    with col2:
        with st.expander("✍️ Pengeluaran/Lainnya"):
            tipe_m = st.selectbox("Jenis:", ["Pengeluaran", "Pemasukan Lain"])
            nama_m = st.text_input("Keterangan:")
            jumlah_m = st.number_input("Nominal (Rp):", min_value=0)
            if st.button("Simpan Data"):
                if nama_m and jumlah_m > 0:
                    new_row = pd.DataFrame({'Tipe':['Pemasukan' if tipe_m=='Pemasukan Lain' else 'Pengeluaran'], 'Kategori':[nama_m], 'Jumlah':[jumlah_m], 'Tanggal':[datetime.today().date()]})
                    st.session_state.data = pd.concat([st.session_state.data, new_row], ignore_index=True)
                    st.success("Tersimpan!")

# --- HALAMAN 2 & 3 TETAP SAMA SEPERTI SEBELUMNYA ---
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
                st.write(f"Stok: **{st.session_state.master_barang[pilih_p][1]}**")
                up_stok = st.number_input("Tambah/Kurang Stok:", value=0)
                if st.button("Update Stok"):
                    st.session_state.master_barang[pilih_p][1] += up_stok
                    st.success("Stok diperbarui!")
            with c_b:
                if st.button("🗑️ Hapus Produk", type="primary"):
                    del st.session_state.master_barang[pilih_p]
                    st.rerun()

else:
    st.subheader("📊 Laporan Keuangan")
    in_sum = st.session_state.data[st.session_state.data['Tipe'] == 'Pemasukan']['Jumlah'].sum()
    out_sum = st.session_state.data[st.session_state.data['Tipe'] == 'Pengeluaran']['Jumlah'].sum()
    c1, c2, c3 = st.columns(3)
    c1.metric("💰 Saldo Kas", f"Rp {in_sum - out_sum:,.0f}")
    c2.metric("📈 Total Masuk", f"Rp {in_sum:,.0f}")
    c3.metric("📉 Total Keluar", f"Rp {out_sum:,.0f}")
    st.divider()
    st.dataframe(st.session_state.data.sort_values(by='Tanggal', ascending=False), use_container_width=True)
