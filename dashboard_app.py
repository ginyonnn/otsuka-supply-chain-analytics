import streamlit as st
import pandas as pd
import plotly.express as px
from sqlalchemy import text
from scripts.db_connection import get_engine
import os

# ==========================================
# 1. KONFIGURASI HALAMAN
# ==========================================
st.set_page_config(
    page_title="Otsuka Sales Distribution Hub",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ==========================================
# 2. CSS STYLING (FIX CARD FILTER & UI)
# ==========================================
st.markdown("""
<style>
    /* 1. Global Background */
    .stApp {
        background-color: #F0F2F5; /* Abu-abu Soft */
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }

    /* 2. HEADER STYLE */
    .header-title {
        color: #00529B; /* Otsuka Deep Blue */
        font-weight: 800;
        font-size: 28px;
        margin-bottom: 0px;
        line-height: 1.2;
    }
    .header-subtitle {
        color: #666;
        font-size: 14px;
        margin-top: 5px;
    }

    /* 3. VISUAL FIX: LEFT FILTER COLUMN CARD */
    /* Target blok horizontal utama (konten), ambil kolom pertama (kiri), lalu styling div di dalamnya */
    div[data-testid="stHorizontalBlock"]:nth-of-type(2) > div[data-testid="column"]:nth-of-type(1) > div[data-testid="stVerticalBlock"] {
        background-color: #FFFFFF;
        padding: 20px;
        border-radius: 15px;
        border: 1px solid #EAEAEA;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
        gap: 1rem;
    }

    /* 4. METRIC CARDS STYLE */
    .metric-card-box {
        background-color: white;
        border-radius: 12px;
        padding: 15px 20px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.05);
        display: flex;
        flex-direction: row;
        align-items: center;
        border: 1px solid #EAEAEA;
    }
    .metric-icon-bg {
        width: 45px;
        height: 45px;
        background-color: #F8F9FA;
        border-radius: 8px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 22px;
        margin-right: 15px;
    }
    .metric-text {
        display: flex;
        flex-direction: column;
    }
    .metric-label-text {
        color: #888;
        font-size: 11px;
        font-weight: 700;
        text-transform: uppercase;
        margin-bottom: 4px;
    }
    .metric-value-text {
        color: #002D58; 
        font-size: 20px;
        font-weight: 800;
    }

    /* 5. CHART & EXPANDER CONTAINER */
    .chart-container {
        background-color: #FFFFFF;
        border-radius: 15px;
        padding: 20px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.03);
        border: 1px solid #EAEAEA;
        margin-bottom: 20px;
    }
    
    /* 6. WARNING BOX */
    .warning-box {
        background-color: #FFF8E6;
        border-left: 4px solid #FFC107;
        padding: 15px;
        border-radius: 6px;
        margin-top: 15px;
        font-size: 13px;
    }

    /* Custom Styling for Selectbox Titles to look smaller */
    .filter-label {
        font-weight: 600;
        font-size: 14px;
        color: #333;
        margin-bottom: 5px;
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 3. DATA LOGIC (WITH STORE NAME)
# ==========================================
@st.cache_data
def load_data():
    engine = get_engine()
    # SQL Query: Menambahkan 'store_name' dan perbaikan GROUP logic
    query = """
    SELECT 
        d.full_date,
        p.product_name,
        CASE 
            WHEN p.product_name LIKE '%%Pocari%%' THEN 'Pocari Sweat'
            WHEN p.product_name LIKE '%%SoyJoy%%' THEN 'SoyJoy'
            WHEN p.product_name LIKE '%%Oronamin%%' THEN 'Oronamin C'
            WHEN p.product_name LIKE '%%Ion%%' THEN 'Ion Water'
            ELSE p.product_category 
        END AS category,
        s.store_name,  -- FIXED: Memastikan Nama Toko terambil
        s.city,
        s.sales_channel AS channel,
        f.sales_qty,
        f.sales_amount_net
    FROM fact_sales f
    JOIN dim_products p ON f.product_sk = p.product_sk
    JOIN dim_stores s ON f.store_sk = s.store_sk
    JOIN dim_date d ON f.date_id = d.date_id
    WHERE d.year >= 2023
    ORDER BY d.full_date;
    """
    try:
        conn = engine.connect()
        df = pd.read_sql(text(query), conn)
        conn.close()
        return df
    except Exception as e:
        return pd.DataFrame()

# ==========================================
# 4. DASHBOARD LAYOUT
# ==========================================

# A. Header Section
c_logo, c_title = st.columns([1.5, 10.5])
with c_logo:
    if os.path.exists("assets/otsuka_logo.png"):
        st.image("assets/otsuka_logo.png", width=130)
    else:
        st.markdown("# 🔵")

with c_title:
    st.markdown("""
        <div style="margin-top: 10px;">
            <div class="header-title">Otsuka Sales & Distribution Hub</div>
            <div class="header-subtitle">Monitoring performance from Raw Manufacturing to Retail Sales</div>
        </div>
    """, unsafe_allow_html=True)

st.write("") 

# Load Data
df_raw = load_data()

if not df_raw.empty:
    df_raw["full_date"] = pd.to_datetime(df_raw["full_date"])
    
    # B. MAIN BODY: KOLOM FILTER (Kiri) vs KONTEN UTAMA (Kanan)
    # Rasio kolom disesuaikan agar card filter proporsional
    col_filters, col_main = st.columns([1.5, 4.5], gap="medium")

    # --- KOLOM KIRI (FILTER DATA) ---
    with col_filters:
        # Title Filter
        st.markdown('##### 🎯 Filter Data')
        st.write("")

        # Filter 1: Kota
        st.markdown('<div class="filter-label">Pilih Kota:</div>', unsafe_allow_html=True)
        all_cities = sorted(df_raw['city'].unique())
        # Default: KOSONG (Sesuai request 'No Default Fix')
        city_filter = st.multiselect("", options=all_cities, default=[], key="city_f", label_visibility="collapsed")
        
        st.write("")

        # Filter 2: Kategori
        st.markdown('<div class="filter-label">Kategori Produk:</div>', unsafe_allow_html=True)
        cats = sorted(df_raw['category'].unique().tolist())
        cats_display = cats + ["Fibe Mini"]
        # Default: KOSONG
        category_filter = st.multiselect("", options=cats_display, default=[], key="cat_f", label_visibility="collapsed")

        # Warning Fibe Mini
        if "Fibe Mini" in category_filter:
            st.markdown("""
            <div class="warning-box">
                <b>⚠️ Fibe Mini is Coming Soon!</b><br>
                Produk ini sedang dalam integrasi sistem.
            </div>
            """, unsafe_allow_html=True)
            
        # Logic Filter Python
        # Jika filter kosong, tampilkan semua (optional) atau kosong
        # Di sini kita biarkan behavior standard: Jika kosong = Data Kosong (user harus pilih)
        # Tapi karena filter kosong = df query akan return 0 row kalau pakai logika `in`,
        # Kita perlu handling jika user belum pilih apapun.
        
        if not city_filter and not category_filter:
            # Skenario 1: Belum ada filter, tampilkan 0 atau Semua? 
            # Sesuai screenshot Anda sebelumnya (Rp 0), maka kita biarkan empty query
            df_select = pd.DataFrame(columns=df_raw.columns) 
        elif not city_filter:
            df_select = df_raw.query("category == @category_filter").copy()
        elif not category_filter:
             df_select = df_raw.query("city == @city_filter").copy()
        else:
            df_select = df_raw.query("city == @city_filter & category == @category_filter").copy()

    # --- KOLOM KANAN (CONTENT) ---
    with col_main:
        
        # 1. KARTU KPI
        # Handle jika df_select kosong (agar tidak error sum)
        rev = df_select['sales_amount_net'].sum() if not df_select.empty else 0
        item = df_select['sales_qty'].sum() if not df_select.empty else 0
        avg = df_select['sales_amount_net'].mean() if not df_select.empty else 0

        c_kpi1, c_kpi2, c_kpi3 = st.columns(3)

        def kpi_card(col, icon, title, val):
            col.markdown(f"""
            <div class="metric-card-box">
                <div class="metric-icon-bg">{icon}</div>
                <div class="metric-text">
                    <span class="metric-label-text">{title}</span>
                    <span class="metric-value-text">{val}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
        kpi_card(c_kpi1, "💰", "TOTAL REVENUE", f"Rp {rev:,.0f}")
        kpi_card(c_kpi2, "📦", "TOTAL ITEMS SOLD", f"{item:,.0f}") # Unit Pcs dihapus biar muat/bersih atau ditambahin boleh
        kpi_card(c_kpi3, "🧾", "AVG. TRANSACTION", f"Rp {avg:,.0f}")

        st.write("") # Spacer

        # Jika data kosong (karena belum filter), stop rendering chart biar rapi (cuma muncul 0 di KPI)
        # Sesuai screenshot "No data available" yang muncul otomatis di Chart
        
        # 2. CHART AREA
        gc1, gc2 = st.columns(2)
        
        # PREP DATA
        if not df_select.empty:
            bar_data = df_select.groupby('product_name')[['sales_amount_net']].sum().reset_index().sort_values('sales_amount_net', ascending=True)
            df_select['YYYYMM'] = df_select['full_date'].dt.to_period('M').astype(str)
            line_data = df_select.groupby('YYYYMM')[['sales_amount_net']].sum().reset_index()
        
        with gc1:
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            st.markdown('**Penjualan per Produk (Best Sellers)**')
            if not df_select.empty:
                fig_bar = px.bar(bar_data, y='product_name', x='sales_amount_net', orientation='h', color_discrete_sequence=['#0097D8'])
                fig_bar.update_layout(margin=dict(l=0, r=0, t=10, b=0), height=250, xaxis=dict(showgrid=False), yaxis=dict(title=None), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
                st.plotly_chart(fig_bar, use_container_width=True)
            else:
                st.info("No data available")
            st.markdown('</div>', unsafe_allow_html=True)
            
        with gc2:
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            st.markdown('**Tren Penjualan Bulanan**')
            if not df_select.empty:
                fig_line = px.area(line_data, x='YYYYMM', y='sales_amount_net', markers=True)
                fig_line.update_traces(line_color='#00529B', fillcolor='rgba(0, 151, 216, 0.15)')
                fig_line.update_layout(margin=dict(l=0, r=0, t=10, b=0), height=250, xaxis=dict(showgrid=False), yaxis=dict(showgrid=True, gridcolor='#f4f4f4'), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
                st.plotly_chart(fig_line, use_container_width=True)
            else:
                st.info("No data available")
            st.markdown('</div>', unsafe_allow_html=True)

        # 3. TABEL DETAIL LENGKAP (DATA REVISI: Ada Store Name)
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        with st.expander("▼ Lihat Detail Data Tabel (Lengkap)", expanded=False):
            if not df_select.empty:
                # Memilih kolom yang mau ditampilkan & Mengubah nama header biar cantik
                show_df = df_select[[
                    'full_date', 
                    'store_name',    # <- NAMA TOKO HADIR DISINI
                    'city', 
                    'product_name', 
                    'category', 
                    'channel', 
                    'sales_qty', 
                    'sales_amount_net'
                ]].rename(columns={
                    'full_date': 'Tanggal',
                    'store_name': 'Nama Toko',
                    'city': 'Kota',
                    'product_name': 'Produk',
                    'category': 'Kategori',
                    'channel': 'Channel',
                    'sales_qty': 'Qty',
                    'sales_amount_net': 'Total (Rp)'
                })
                
                # Format Tabel
                st.dataframe(
                    show_df.style.format({
                        'Tanggal': lambda t: t.strftime('%Y-%m-%d'),
                        'Qty': '{:,.0f}',
                        'Total (Rp)': 'Rp {:,.0f}'
                    }), 
                    use_container_width=True
                )
            else:
                st.info("Silakan pilih filter untuk melihat detail data tabel.")
        st.markdown('</div>', unsafe_allow_html=True)