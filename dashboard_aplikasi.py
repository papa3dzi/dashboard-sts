import streamlit as st
import pandas as pd
import re

# --- KONFIGURASI HALAMAN ---
st.set_page_config(
    page_title="Dashboard STS TI",
    page_icon="📶",
    layout="wide"
)

# --- FUNGSI LOGIN ---
def login():
    st.title("🔐 Login Dashboard STS TI")
    
    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submit_button = st.form_submit_button("Login")
        
        if submit_button:
            if username == "alfi" and password == "1234":
                st.session_state["logged_in"] = True
                st.success("Login Berhasil!")
                st.rerun() # Refresh halaman untuk masuk ke dashboard
            else:
                st.error("Username atau Password salah")

# --- INISIALISASI SESSION STATE ---
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False

# --- LOGIKA TAMPILAN ---
if not st.session_state["logged_in"]:
    login()
else:
    # --- TOMBOL LOGOUT DI SIDEBAR ---
    if st.sidebar.button("Logout"):
        st.session_state["logged_in"] = False
        st.rerun()

    # --- KODE DASHBOARD UTAMA ANDA DIMULAI DI SINI ---
    
    # --- FUNGSI PEMROSESAN DATA ---
    def process_data(df):
        def extract_info(cell_id):
            if not isinstance(cell_id, str):
                return None, None, None
            match = re.match(r"(\w+)_(\d+)_(\d+)", cell_id)
            if match:
                return match.group(1), match.group(2), match.group(3)
            else:
                site_id = cell_id[:6]
                band = cell_id[6:8]
                sector = cell_id[-1]
                return site_id, band, sector

        df[['SITE ID', 'BAND', 'Sector']] = df['CELLNAME'].apply(
            lambda x: pd.Series(extract_info(x))
        )
        
        try:
            df['DateTime'] = pd.to_datetime(df['DATE_ID'] + ' ' + df['HOURS'].astype(str).str.zfill(2) + ':00:00')
        except:
            df['DateTime'] = df['DATE_ID'].astype(str) + ' ' + df['HOURS'].astype(str).str.zfill(2)
        return df

    # UI HEADER
    st.title("DASHBOARD STS TI")
   

    # SIDEBAR (UPLOAD & FILTERS)
    st.sidebar.header("📂 Data & Filter")
    uploaded_file = st.sidebar.file_uploader("Unggah File Data (.txt atau .csv)", type=["txt", "csv"])

    if uploaded_file is not None:
        try:
            if uploaded_file.name.endswith('.csv'):
                raw_df = pd.read_csv(uploaded_file)
            else:
                raw_df = pd.read_csv(uploaded_file, sep='\t')
            
            required_cols = ['CELLNAME', 'DATE_ID', 'HOURS']
            if not all(col in raw_df.columns for col in required_cols):
                st.error(f"File tidak valid. Pastikan kolom berikut tersedia: {', '.join(required_cols)}")
                st.stop()
                
            df = process_data(raw_df)
            
            # Filter Logic
            available_sites = sorted(df['SITE ID'].dropna().unique())
            selected_sites = st.sidebar.multiselect("Pilih SITE ID", options=available_sites)
            
            available_bands = sorted(df['BAND'].dropna().unique())
            selected_bands = st.sidebar.multiselect("Pilih BAND", options=available_bands)
            
            filtered_df = df.copy()
            if selected_sites:
                filtered_df = filtered_df[filtered_df['SITE ID'].isin(selected_sites)]
            if selected_bands:
                filtered_df = filtered_df[filtered_df['BAND'].isin(selected_bands)]
                
            available_cells = sorted(filtered_df['CELLNAME'].unique())
            selected_cells = st.sidebar.multiselect("Pilih CELLNAME", options=available_cells)
            
            if selected_cells:
                filtered_df = filtered_df[filtered_df['CELLNAME'].isin(selected_cells)]

            # Metrik Analisis
            st.subheader("⚙️ Pilih KPI Analisis")
            numeric_cols = df.select_dtypes(include=['number', 'float', 'int']).columns.tolist()
            exclude_cols = ['HOURS', 'Sector']
            available_metrics = [c for c in numeric_cols if c not in exclude_cols]
            
            if not available_metrics:
                st.warning("Tidak ditemukan kolom numerik.")
                st.stop()
                
            selected_metric = st.selectbox("KPI di Grafik", options=available_metrics)

            # Grafik Per Sektor
            st.divider()
            st.subheader(f" {selected_metric}")
            sectors = ['1', '2', '3', '4', '5', '6']
            cols = st.columns(2)
            
            for idx, sector in enumerate(sectors):
                sector_data = filtered_df[filtered_df['Sector'] == sector]
                with cols[idx % 2]:
                    st.write(f"#### Sektor {sector}")
                    if not sector_data.empty:
                        sector_data = sector_data.sort_values('DateTime')
                        st.line_chart(sector_data, x='DateTime', y=selected_metric, color='CELLNAME')
                    else:
                        st.info(f"Tidak ada data Sektor {sector}")

            with st.expander("Lihat Detail Data Mentah"):
                st.dataframe(filtered_df, use_container_width=True)

        except Exception as e:
            st.error(f"Terjadi kesalahan: {e}")
    else:
        st.info("Silakan unggah file .txt atau .csv di sidebar untuk memulai.")

    st.markdown("---")
    st.caption("Dashboard STS TI - 2026")


