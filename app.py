import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

# 1. KONFIGURASI HALAMAN
st.set_page_config(page_title="Kasir Jaya", layout="wide", page_icon="🏪")

# 2. INISIALISASI DATABASE
if 'master_barang' not in st.session_state:
    st.session_state.master_barang = {
        "Kopi Espresso": [15000, 50],
        "Roti Bakar": [20000, 30],
        "Air Mineral": [5000, 100]
    }

if 'data' not in st.session_state:
    st.session_state.data = pd.DataFrame(columns=['Tipe', 'Kategori', 'Jumlah', 'Tanggal'])

# 3. GAYA DESAIN (JUDUL LEBIH KECIL & RINGKAS)
st.markdown("""
    <style>
    .header-mini {
        text-align: left;
        padding: 10px;
        background: #1e3c72;
        color: white;
        border-radius: 8px;
        margin-bottom: 15px;
    }
    .header-mini h2 { margin: 0; font-size: 20px; }
    .header-mini p { margin: 0; font-size: 12px; opacity: 0.8; }
    .bayar-box {
        background-color: #f0f2f6;
        padding: 15px;
        border-radius: 10px;
        border-left: 5px solid #1E88E5;
        margin-top: 10px;
    }
    .struk-box {
        background-color: #fff;
        padding: 20px;
        border: 1px dashed #000;
        font-family: monospace;
        color: #000;
    }
    </style>
    """, unsafe_allow_html=True)

# JUDUL VERSI KECIL (HEMAT LAYAR)
st.markdown('<div class="header-mini"><h2>🏪 KASIR JAYA DIGITAL</h2><p>Sistem Kasir v2.1</p></div>', unsafe_allow_html=True)

# 4. NAVIGASI
with st.sidebar:
    menu = st.radio("MENU:", ["🛒 Kasir", "📦 Produk", "📊 Laporan"])

# --- HALAMAN 1: KASIR ---
if menu == "🛒 Kasir":
    col1, col2 = st.columns([1.5, 1])
    
    with col1:
        with st.expander("✨ Pilih Produk", expanded=True):
            daftar = ["--- Pilih ---"] + list(st.session_state.master_barang.keys())
            pilihan = st.selectbox("Produk:", daftar)
            qty = st.number_input("Qty:", min_value=1, value=1)
            
            if pilihan != "--- Pilih ---":
                harga_satuan = st.session_state.master_barang[pilihan][0]
                stok_skrg = st.session_state.master_barang[pilihan][1]
                total_tagihan = harga_satuan * qty
                
                st.write(f"Harga: **Rp {harga_satuan:,.0f}** | Stok: **{stok_skrg}**")
                st.write(f"### Tagihan: Rp {total_tagihan:,.0f}")
                
                st.divider()
                # PEMBAYARAN
                c_u1, c_u2 = st.columns(2)
                with c_u1:
                    uang_pas = st.button(f"Uang Pas")
                    bayar_manual = st.number_input("Bayar Manual (Rp):", min_value=0, step=500)
                with c_u2:
                    pecahan = st.selectbox("Pecahan:", [0, 10000, 20000, 50000, 100000])
                
                jml_bayar = total_tagihan if uang_pas else (bayar_manual if bayar_manual > 0 else pecahan)

                if jml_bayar >= total_tagihan and jml_bayar > 0:
                    kembali = jml_bayar - total_tagihan
                    st.markdown(f'<div class="bayar-box">Kembalian: <b>Rp {kembali:,.0f}</b></div>', unsafe_allow_html=True)
                    
                    if st.button("✅ PROSES & CETAK STRUK", use_container_width=True):
                        if qty <= stok_skrg:
                            st.session_state.master_barang[pilihan][1] -= qty
                            new_tr = pd.DataFrame({'Tipe':['Pemasukan'], 'Kategori':[pilihan], 'Jumlah':[total_tagihan], 'Tanggal':[datetime.today().date()]})
                            st.session_state.data = pd.concat([st.session_state.data, new_tr], ignore_index=True)
                            
                            # TAMPILAN STRUK
                            st.divider()
                            st.subheader("📄 STRUK BELANJA")
                            st.markdown(f"""
                            <div class="struk-box">
                                <center><b>KASIR JAYA DIGITAL</b><br>{datetime.now().strftime('%d/%m/%Y %H:%M')}</center>
                                <hr>
                                {pilihan} x {qty} : Rp {total_tagihan:,.0f}<br>
                                <hr>
                                <b>TOTAL    : Rp {total_tagihan:,.0f}</b><br>
                                BAYAR    : Rp {jml_bayar:,.0f}<br>
                                KEMBALI  : Rp {kembali:,.0f}<br>
                                <hr>
                                <center>Terima Kasih!</center>
                            </div>
                            """, unsafe_allow_html=True)
                            st.balloons()
                        else:
                            st.error("Stok Kurang!")
                elif jml_bayar > 0:
                    st.warning("Uang kurang!")

    with col2:
        with st.expander("✍️ Lainnya"):
            t_m = st.selectbox("Tipe:", ["Pengeluaran", "Pemasukan"])
            k_m = st.text_input("Ket:")
            j_m = st.number_input("Nominal:", min_value=0)
            if st.button("Simpan"):
                if k_m and j_m > 0:
                    new_tr = pd.DataFrame({'Tipe':[t_m], 'Kategori':[k_m], 'Jumlah':[j_m], 'Tanggal':[datetime.today().date()]})
                    st.session_state.data = pd.concat([st.session_state.data, new_tr], ignore_index=True)
                    st.success("Ok!")

# --- HALAMAN PRODUK & LAPORAN TETAP SAMA (Efisien) ---
elif menu == "📦 Produk":
    t1, t2 = st.tabs(["➕ Tambah", "🔧 Stok"])
    with t1:
        with st.form("add"):
            n = st.text_input("Nama:")
            h = st.number_input("Harga:", min_value=0)
            s = st.number_input("Stok:", min_value=0)
            if st.form_submit_button("Simpan"):
                st.session_state.master_barang[n] = [h, s]
                st.rerun()
    with t2:
        if st.session_state.master_barang:
            p = st.selectbox("Pilih Produk:", list(st.session_state.master_barang.keys()))
            up = st.number_input("Tambah/Kurang Stok:", value=0)
            if st.button("Update"):
                st.session_state.master_barang[p][1] += up
                st.success("Stok Update!")
            if st.button("🗑️ Hapus Produk"):
                del st.session_state.master_barang[p]
                st.rerun()

else:
    st.subheader("📊 Laporan")
    in_s = st.session_state.data[st.session_state.data['Tipe'] == 'Pemasukan']['Jumlah'].sum()
    out_s = st.session_state.data[st.session_state.data['Tipe'] == 'Pengeluaran']['Jumlah'].sum()
    st.columns(3)[0].metric("Saldo", f"Rp {in_s - out_s:,.0f}")
    st.dataframe(st.session_state.data.sort_values(by='Tanggal', ascending=False), use_container_width=True)
