username = input("Username : ")
password = input("Password : ")

if username == "alfi" and password == "telkominfra" :
    print("Loging sukses.")

else :
    print("login gagal bro")
import streamlit as st
import pandas as pd
import re

# Konfigurasi Halaman
st.set_page_config(
    page_title="Dashboard STS TI",
    page_icon="📶",
    layout="wide"
)

# --- FUNGSI PEMROSESAN DATA ---
def process_data(df):
    """
    Meniru logika parsing JavaScript untuk mengekstrak SITE ID, BAND, dan Sector.
    """
    def extract_info(cell_id):
        if not isinstance(cell_id, str):
            return None, None, None
        
        # Regex: (\w+)_(\d+)_(\d+)
        match = re.match(r"(\w+)_(\d+)_(\d+)", cell_id)
        if match:
            return match.group(1), match.group(2), match.group(3)
        else:
            # Fallback logic dari JS
            site_id = cell_id[:6]
            band = cell_id[6:8]
            sector = cell_id[-1]
            return site_id, band, sector

    # Terapkan ekstraksi
    df[['SITE ID', 'BAND', 'Sector']] = df['CELLNAME'].apply(
        lambda x: pd.Series(extract_info(x))
    )
    
    # Konversi DATE_ID dan HOURS ke Datetime untuk sorting grafik
    try:
        # Mencoba konversi tanggal yang fleksibel
        df['DateTime'] = pd.to_datetime(df['DATE_ID'] + ' ' + df['HOURS'].astype(str).str.zfill(2) + ':00:00')
    except:
        # Jika gagal, buat kolom urutan string agar tetap bisa diurutkan
        df['DateTime'] = df['DATE_ID'].astype(str) + ' ' + df['HOURS'].astype(str).str.zfill(2)
        
    return df

# --- UI HEADER ---
st.title("DASHBOARD STS TI")
st.markdown("### by ALFISYAHRIN (Streamlit Version)")

# --- SIDEBAR (UPLOAD & FILTERS) ---
st.sidebar.header("📂 Data & Filter")
uploaded_file = st.sidebar.file_uploader("Unggah File Data (.txt atau .csv)", type=["txt", "csv"])

if uploaded_file is not None:
    try:
        # Logika untuk menentukan separator berdasarkan ekstensi file
        if uploaded_file.name.endswith('.csv'):
            raw_df = pd.read_csv(uploaded_file)
        else:
            raw_df = pd.read_csv(uploaded_file, sep='\t')
        
        # Validasi header minimal
        required_cols = ['CELLNAME', 'DATE_ID', 'HOURS']
        if not all(col in raw_df.columns for col in required_cols):
            st.error(f"File tidak valid. Pastikan kolom berikut tersedia: {', '.join(required_cols)}")
            st.stop()
            
        df = process_data(raw_df)
        
        # --- LOGIKA FILTER ---
        # 1. Filter Site ID
        available_sites = sorted(df['SITE ID'].dropna().unique())
        selected_sites = st.sidebar.multiselect("Pilih SITE ID", options=available_sites)
        
        # 2. Filter Band
        available_bands = sorted(df['BAND'].dropna().unique())
        selected_bands = st.sidebar.multiselect("Pilih BAND", options=available_bands)
        
        # 3. Filter Cell
        filtered_df = df.copy()
        if selected_sites:
            filtered_df = filtered_df[filtered_df['SITE ID'].isin(selected_sites)]
        if selected_bands:
            filtered_df = filtered_df[filtered_df['BAND'].isin(selected_bands)]
            
        available_cells = sorted(filtered_df['CELLNAME'].unique())
        selected_cells = st.sidebar.multiselect("Pilih CELLNAME", options=available_cells)
        
        if selected_cells:
            filtered_df = filtered_df[filtered_df['CELLNAME'].isin(selected_cells)]

        # --- SELEKSI METRIK ---
        st.subheader("⚙️ Pilih Metrik Analisis")
        numeric_cols = df.select_dtypes(include=['number', 'float', 'int']).columns.tolist()
        exclude_cols = ['HOURS', 'Sector']
        available_metrics = [c for c in numeric_cols if c not in exclude_cols]
        
        if not available_metrics:
            st.warning("Tidak ditemukan kolom numerik untuk dijadikan metrik.")
            st.stop()
            
        selected_metric = st.selectbox("Metrik yang akan ditampilkan di Grafik", options=available_metrics)

        # --- GRID GRAFIK PER SEKTOR ---
        st.divider()
        st.subheader(f"Grafik Tren: {selected_metric}")
        
        # Kelompokkan berdasarkan Sektor (1-6)
        sectors = ['1', '2', '3', '4', '5', '6']
        
        # Membuat layout kolom
        cols = st.columns(2)
        
        for idx, sector in enumerate(sectors):
            sector_data = filtered_df[filtered_df['Sector'] == sector]
            
            with cols[idx % 2]:
                st.write(f"#### Sektor {sector}")
                if not sector_data.empty:
                    # Sorting data berdasarkan waktu
                    sector_data = sector_data.sort_values('DateTime')
                    
                    # Menggunakan model st.line_chart sesuai permintaan
                    st.line_chart(
                        sector_data,
                        x='DateTime',
                        y=selected_metric,
                        color='CELLNAME',
                        use_container_width=True
                    )
                else:
                    st.info(f"Tidak ada data untuk Sektor {sector}")

        # --- DATA TABLE ---
        with st.expander("Lihat Detail Data Mentah"):
            st.dataframe(filtered_df, use_container_width=True)

    except Exception as e:
        st.error(f"Terjadi kesalahan saat memproses data: {e}")
else:
    st.info("Silakan unggah file .txt atau .csv di sidebar untuk memulai.")
    st.image("https://via.placeholder.com/800x400.png?text=Menunggu+Upload+Data+CSV/TXT", use_container_width=True)

# Footer
st.markdown("---")

st.caption("Dashboard dikembangkan menggunakan native Streamlit charts untuk tampilan yang lebih konsisten.")


