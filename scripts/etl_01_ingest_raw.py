import pandas as pd
import os
from db_connection import get_engine, execute_sql_file

def load_raw_data():
    """
    Fungsi ini bertugas:
    1. Me-reset schema database (Drop & Create Tables).
    2. Membaca CSV, MENYAMAKAN NAMA KOLOM, dan Upload.
    """
    engine = get_engine()
    
    print("\nSTEP 1: SETUP DATABASE SCHEMA (DDL)")
    execute_sql_file('01_create_source_tables.sql')
    execute_sql_file('02_create_dwh_tables.sql')
    
    print("\nSTEP 2: INGESTING RAW CSV TO DATABASE")
    
    # Mapping nama file ke nama tabel
    csv_to_table_map = {
        'raw_products.csv': 'raw_products',
        'raw_stores.csv': 'raw_stores',
        'raw_sales_transactions.csv': 'raw_sales_transactions'
    }
    
    # Direktori data
    current_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(os.path.dirname(current_dir), 'data')
    
    for csv_file, table_name in csv_to_table_map.items():
        file_path = os.path.join(data_dir, csv_file)
        
        if os.path.exists(file_path):
            print(f"Reading {csv_file}...")
            df = pd.read_csv(file_path)
            
            # --- START FIXED CODE: COLUMN MAPPING ---
            # Kita harus memastikan nama kolom di CSV sesuai dengan tabel SQL
            if csv_file == 'raw_products.csv':
                # Ubah nama kolom agar cocok dengan SQL (product_name & unit_price)
                df.rename(columns={
                    'name': 'product_name',
                    'price': 'unit_price'
                }, inplace=True)
                print("  (Transformed) Columns renamed for Database compatibility.")
            # --- END FIXED CODE ---
            
            # Data Cleaning Basic
            if 'product_id' in df.columns:
                df = df.dropna(subset=['product_id'])
            
            print(f"  Uploading {len(df)} rows to table '{table_name}'...")
            
            try:
                df.to_sql(table_name, engine, if_exists='append', index=False, method='multi', chunksize=1000)
                print(f"  [SUCCESS] {table_name} loaded.")
            except Exception as e:
                print(f"  [ERROR] Failed to load {table_name}: {e}")
                
        else:
            print(f"  [WARNING] File {file_path} not found.")

if __name__ == "__main__":
    print("=== STARTING ETL JOB: INGEST RAW DATA ===")
    load_raw_data()
    print("=== JOB COMPLETED ===")