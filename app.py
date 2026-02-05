import streamlit as st
import pandas as pd
from datetime import datetime

# 1. KONFIGURASI HALAMAN
st.set_page_config(page_title="WK AHAS SMP YABAKII 1", layout="wide", page_icon="🏪")

# 2. DATABASE BARANG
if 'master_barang' not in st.session_state:
    st.session_state.master_barang = {
        "Kopi Espresso": [15000, 50],
        "Roti Bakar": [20000, 30],
        "Air Mineral": [5000, 100]
    }

if 'data' not in st.session_state:
    st.session_state.data = pd.DataFrame(columns=['Tipe', 'Kategori', 'Jumlah', 'Tanggal'])

# State untuk menampung jumlah bayar agar tombol Uang Pas bekerja
if 'jml_bayar' not in st.session_state:
    st.session_state.jml_bayar = 0

# 3. GAYA DESAIN
st.markdown("""
    <style>
    .header-mini { padding: 10px; background: #1e3c72; color: white; border-radius: 8px; margin-bottom: 15px; }
    .header-mini h2 { margin: 0; font-size: 20px; }
    .struk-box { 
        background-color: #fff; padding: 15px; border: 1px dashed #000; 
        font-family: monospace; color: #000; line-height: 1.2;
    }
    @media print { .no-print { display: none; } }
    </style>
    """, unsafe_allow_html=True)

st.markdown('<div class="header-mini"><h2>🏪 KASIR JAYA DIGITAL</h2></div>', unsafe_allow_html=True)

# 4. NAVIGASI
menu = st.sidebar.radio("MENU:", ["🛒 Kasir", "📦 Produk", "📊 Laporan"])

if menu == "🛒 Kasir":
    col1, col2 = st.columns([1.5, 1])
    
    with col1:
        with st.expander("✨ Transaksi", expanded=True):
            daftar = ["--- Pilih ---"] + list(st.session_state.master_barang.keys())
            pilihan = st.selectbox("Produk:", daftar)
            qty = st.number_input("Qty:", min_value=1, value=1)
            
            if pilihan != "--- Pilih ---":
                harga_satuan = st.session_state.master_barang[pilihan][0]
                stok_skrg = st.session_state.master_barang[pilihan][1]
                total_tagihan = harga_satuan * qty
                
                st.write(f"### Total: Rp {total_tagihan:,.0f}")
                
                st.divider()
                st.write("💰 **Pembayaran**")
                
                c1, c2 = st.columns(2)
                with c1:
                    if st.button("💵 UANG PAS"):
                        st.session_state.jml_bayar = total_tagihan
                    pecahan = st.selectbox("Pilih Pecahan:", [0, 10000, 20000, 50000, 100000])
                    if pecahan > 0: st.session_state.jml_bayar = pecahan
                
                with c2:
                    bayar_manual = st.number_input("Ketik Manual:", min_value=0, step=500)
                    if bayar_manual > 0: st.session_state.jml_bayar = bayar_manual

                # Tampilkan angka pembayaran saat ini
                st.write(f"Diterima: **Rp {st.session_state.jml_bayar:,.0f}**")

                if st.session_state.jml_bayar >= total_tagihan and st.session_state.jml_bayar > 0:
                    kembali = st.session_state.jml_bayar - total_tagihan
                    st.success(f"Kembalian: Rp {kembali:,.0f}")
                    
                    if st.button("✅ PROSES & TAMPILKAN STRUK", use_container_width=True):
                        if qty <= stok_skrg:
                            st.session_state.master_barang[pilihan][1] -= qty
                            new_tr = pd.DataFrame({'Tipe':['Pemasukan'], 'Kategori':[pilihan], 'Jumlah':[total_tagihan], 'Tanggal':[datetime.today().date()]})
                            st.session_state.data = pd.concat([st.session_state.data, new_tr], ignore_index=True)
                            
                            # AREA STRUK
                            st.markdown(f"""
                            <div class="struk-box" id="struk">
                                <center><b>KASIR JAYA DIGITAL</b><br>{datetime.now().strftime('%d/%m/%Y %H:%M')}</center>
                                <hr>
                                {pilihan}<br>{qty} x {harga_satuan:,.0f} = {total_tagihan:,.0f}<br>
                                <hr>
                                <b>TOTAL: Rp {total_tagihan:,.0f}</b><br>
                                BAYAR: Rp {st.session_state.jml_bayar:,.0f}<br>
                                KEMBALI: Rp {kembali:,.0f}<br>
                                <hr><center>Terima Kasih</center>
                            </div>
                            """, unsafe_allow_html=True)
                            
                            st.info("💡 **Tips Cetak:** Tekan lama pada struk di atas untuk 'Download Gambar' atau gunakan fitur 'Share' di browser untuk kirim ke WA/Printer Bluetooth.")
                            st.session_state.jml_bayar = 0 # Reset setelah sukses
                        else:
                            st.error("Stok habis!")

    with col2:
        with st.expander("✍️ Lain-lain"):
            if st.button("🔄 Reset Form"):
                st.session_state.jml_bayar = 0
                st.rerun()

# --- HALAMAN PRODUK & LAPORAN ---
elif menu == "📦 Produk":
    st.subheader("Manajemen Produk")
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
                st.success("Selesai!")
            if st.button("🗑️ Hapus"):
                del st.session_state.master_barang[p]
                st.rerun()

else:
    st.subheader("📊 Laporan")
    in_s = st.session_state.data[st.session_state.data['Tipe'] == 'Pemasukan']['Jumlah'].sum()
    out_s = st.session_state.data[st.session_state.data['Tipe'] == 'Pengeluaran']['Jumlah'].sum()
    st.metric("Saldo Kas", f"Rp {in_s - out_s:,.0f}")
    st.dataframe(st.session_state.data.sort_values(by='Tanggal', ascending=False), use_container_width=True)
