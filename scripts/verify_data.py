import pandas as pd
from db_connection import get_engine
from sqlalchemy import text

def verify_dwh_content():
    engine = get_engine()
    print("=== VERIFIKASI HASIL ANALISA ===")
    
    # Query: Top Product Sales (Produk paling laku secara Rupiah)
    sql_query = """
    SELECT 
        d.product_name AS "Produk", 
        SUM(f.sales_qty) AS "Total Terjual (Unit)", 
        SUM(f.sales_amount_net) AS "Total Pendapatan (Rp)"
    FROM fact_sales f
    JOIN dim_products d ON f.product_sk = d.product_sk
    GROUP BY d.product_name
    ORDER BY "Total Pendapatan (Rp)" DESC;
    """
    
    # Jalankan Query
    df_result = pd.read_sql(text(sql_query), engine)
    
    # Tampilkan hasilnya dengan format rapi
    print("\n[REPORT] Laporan Penjualan Per Produk (Simulasi Otsuka):")
    
    # Format angka ke Rupiah agar mudah dibaca
    df_result['Total Pendapatan (Rp)'] = df_result['Total Pendapatan (Rp)'].apply(lambda x: f"Rp {x:,.0f}")
    df_result['Total Terjual (Unit)'] = df_result['Total Terjual (Unit)'].apply(lambda x: f"{x:,.0f}")
    
    print(df_result.to_string(index=False))
    print("\n=== VERIFIKASI SELESAI ===")

if __name__ == "__main__":
    verify_dwh_content()