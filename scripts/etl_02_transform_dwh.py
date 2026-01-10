import pandas as pd
import numpy as np
from sqlalchemy import text
from datetime import datetime, timedelta
from db_connection import get_engine

def clear_dwh_tables(engine):
    """
    FIX ERROR: DependentObjectsStillExist.
    Fungsi ini bertugas membersihkan tabel DWH dengan urutan yang BENAR.
    Hapus Anak dulu (Fact), baru Induk (Dim).
    """
    print("  > [System] Resetting Data Warehouse Tables...")
    with engine.connect() as conn:
        # Gunakan CASCADE untuk memastikan ketergantungan dibersihkan aman
        # Urutan: Fact Sales dibuang isinya, baru Dimension bisa diotak-atik
        conn.execute(text("TRUNCATE TABLE fact_sales RESTART IDENTITY CASCADE;"))
        conn.execute(text("TRUNCATE TABLE dim_products, dim_stores, dim_date RESTART IDENTITY CASCADE;"))
        conn.commit()
    print("  > [System] Tables Cleared & Ready.")

def generate_dim_date(engine):
    """
    Membuat data kalender.
    Perbaikan: Menggunakan if_exists='append' (bukan replace).
    """
    print("  > Processing Dimension: Date (Calendar)...")
    
    start_date = datetime(2023, 1, 1)
    end_date = datetime(2025, 12, 31)
    
    delta = end_date - start_date
    date_list = [start_date + timedelta(days=i) for i in range(delta.days + 1)]
    
    df_date = pd.DataFrame({'full_date': date_list})
    
    df_date['date_id'] = df_date['full_date'].apply(lambda x: int(x.strftime('%Y%m%d')))
    df_date['year'] = df_date['full_date'].dt.year
    df_date['month'] = df_date['full_date'].dt.month
    df_date['month_name'] = df_date['full_date'].dt.strftime('%B')
    df_date['quarter'] = df_date['full_date'].dt.quarter
    df_date['week_of_year'] = df_date['full_date'].dt.isocalendar().week
    df_date['is_weekend'] = df_date['full_date'].dt.dayofweek.isin([5, 6]) 
    
    # PERBAIKAN DI SINI: if_exists='append'
    df_date.to_sql('dim_date', engine, if_exists='append', index=False, method='multi', chunksize=1000)

def populate_dimensions(engine):
    """
    Memindahkan Master Data Produk & Toko.
    Perbaikan: Menghapus truncate internal karena sudah dilakukan di clear_dwh_tables
    """
    print("  > Processing Dimension: Products & Stores...")
    
    # 1. LOAD DIM_STORES
    df_stores = pd.read_sql("SELECT store_id, store_name, city, region, channel FROM raw_stores", engine)
    df_stores.rename(columns={'store_id': 'original_store_id', 'channel': 'sales_channel'}, inplace=True)
    df_stores.to_sql('dim_stores', engine, if_exists='append', index=False)
    
    # 2. LOAD DIM_PRODUCTS
    df_products = pd.read_sql("SELECT product_id, product_name, category, unit_price FROM raw_products", engine)
    df_products.rename(columns={'product_id': 'original_product_id', 'unit_price': 'current_price'}, inplace=True)
    df_products['product_brand'] = 'Otsuka' # Simulasi brand
    df_products['is_active'] = True
    df_products.rename(columns={'category': 'product_category'}, inplace=True)
    df_products.to_sql('dim_products', engine, if_exists='append', index=False)

def populate_fact_sales(engine):
    """
    ETL untuk Sales Transaction
    """
    print("  > Processing Fact Table: Sales Transaction...")
    
    # Extract
    df_sales_raw = pd.read_sql("SELECT * FROM raw_sales_transactions", engine)
    df_dim_prod = pd.read_sql("SELECT product_sk, original_product_id, current_price FROM dim_products", engine)
    df_dim_store = pd.read_sql("SELECT store_sk, original_store_id FROM dim_stores", engine)
    df_dim_date = pd.read_sql("SELECT date_id, full_date FROM dim_date", engine)
    
    # Transform: Preprocessing Dates
    df_sales_raw['date'] = pd.to_datetime(df_sales_raw['date'])
    df_dim_date['full_date'] = pd.to_datetime(df_dim_date['full_date'])
    
    # Transform: Merging / Lookup (The 'Vlookup' Part)
    # Join Product
    df_merged = pd.merge(df_sales_raw, df_dim_prod, left_on='product_id', right_on='original_product_id', how='inner')
    # Join Store
    df_merged = pd.merge(df_merged, df_dim_store, left_on='store_id', right_on='original_store_id', how='inner')
    # Join Date
    df_merged = pd.merge(df_merged, df_dim_date, left_on='date', right_on='full_date', how='inner')
    
    # Transform: Calculation
    df_merged['sales_amount_gross'] = df_merged['quantity_sold'] * df_merged['current_price']
    df_merged['sales_amount_net'] = df_merged['sales_amount_gross'] - df_merged['discount_amount']
    
    # Load Preparation
    final_df = df_merged[[
        'date_id', 
        'product_sk', 
        'store_sk', 
        'quantity_sold', 
        'sales_amount_gross', 
        'discount_amount', 
        'sales_amount_net'
    ]].copy()
    
    final_df.rename(columns={'quantity_sold': 'sales_qty'}, inplace=True)
    
    # PERBAIKAN: Hanya append, jangan truncate di sini lagi
    final_df.to_sql('fact_sales', engine, if_exists='append', index=False, chunksize=5000)
    print(f"    [SUCCESS] Loaded {len(final_df)} rows into fact_sales.")

def run_transformations():
    engine = get_engine()
    print("=== STARTING ETL JOB: TRANSFORM TO STAR SCHEMA ===")
    
    # Step 1: Kosongkan dulu semua tabel DWH dengan urutan benar (Child -> Parent)
    clear_dwh_tables(engine)
    
    # Step 2: Isi Ulang
    generate_dim_date(engine)
    populate_dimensions(engine)
    populate_fact_sales(engine)
    
    print("=== JOB COMPLETED SUCCESSFULLY ===")

if __name__ == "__main__":
    run_transformations()