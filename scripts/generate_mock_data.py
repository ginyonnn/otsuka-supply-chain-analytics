import pandas as pd
import numpy as np
import os
import random
from faker import Faker
from datetime import datetime, timedelta

# Inisiasi Faker (Lokasi Indonesia)
fake = Faker('id_ID')

# ==========================================
# CONFIGURATION
# ==========================================
NUM_TRANSACTIONS = 15000  # Kita simulasi 15 ribu transaksi
START_DATE = datetime(2023, 10, 1) # Data 3 bulan terakhir
END_DATE = datetime(2024, 1, 10)

DATA_FOLDER = 'data' # Lokasi simpan file CSV

# Master Data Produk (Spesifik Otsuka & Kompetitor Simulasi)
PRODUCTS = [
    {"product_id": "P-001", "name": "Pocari Sweat 350ml", "category": "Isotonic", "price": 7000},
    {"product_id": "P-002", "name": "Pocari Sweat 500ml", "category": "Isotonic", "price": 9500},
    {"product_id": "P-003", "name": "Pocari Sweat 2L", "category": "Isotonic", "price": 22000},
    {"product_id": "P-004", "name": "SoyJoy Almond & Chocolate", "category": "Snack", "price": 10500},
    {"product_id": "P-005", "name": "SoyJoy Strawberry", "category": "Snack", "price": 10500},
    {"product_id": "P-006", "name": "Oronamin C 120ml", "category": "Vitamin C", "price": 8000},
    {"product_id": "P-007", "name": "Ion Water 500ml", "category": "Isotonic Low Cal", "price": 9000},
]

# Master Data Kota untuk Toko
CITIES = ['Jakarta Selatan', 'Jakarta Pusat', 'Bandung', 'Surabaya', 'Medan', 'Denpasar']
STORE_CHANNELS = ['Minimarket', 'Supermarket', 'Hypermarket']

def generate_products():
    """Membuat CSV Master Produk"""
    print("Generating Products Data...")
    df_product = pd.DataFrame(PRODUCTS)
    file_path = os.path.join(DATA_FOLDER, 'raw_products.csv')
    df_product.to_csv(file_path, index=False)
    print(f"  Saved: {file_path}")
    return df_product

def generate_stores(num_stores=50):
    """Membuat CSV Master Toko"""
    print("Generating Stores Data...")
    stores = []
    for i in range(1, num_stores + 1):
        city = random.choice(CITIES)
        stores.append({
            "store_id": f"S-{str(i).zfill(3)}", # S-001, S-002...
            "store_name": f"Toko {fake.first_name()} {fake.street_suffix()} - {random.choice(['Jaya', 'Berkah', 'Abadi', 'Makmur'])}",
            "city": city,
            "region": "Java" if city != 'Medan' else "Sumatera",
            "channel": random.choice(STORE_CHANNELS)
        })
    df_stores = pd.DataFrame(stores)
    file_path = os.path.join(DATA_FOLDER, 'raw_stores.csv')
    df_stores.to_csv(file_path, index=False)
    print(f"  Saved: {file_path}")
    return df_stores

def generate_transactions(products, stores):
    """Membuat CSV Transaksi (Jantung dari project ini)"""
    print(f"Generating {NUM_TRANSACTIONS} Transactions Data (This may take a while)...")
    
    txn_data = []
    product_ids = [p['product_id'] for p in PRODUCTS]
    product_prices = {p['product_id']: p['price'] for p in PRODUCTS}
    store_ids = stores['store_id'].tolist()
    
    # Range Hari
    delta = END_DATE - START_DATE
    all_dates = [START_DATE + timedelta(days=i) for i in range(delta.days + 1)]
    
    for _ in range(NUM_TRANSACTIONS):
        # 1. Pilih Tanggal Acak (Weighted ke Weekend biar realistis)
        txn_date = random.choice(all_dates)
        
        # 2. Pilih Toko & Produk
        store = random.choice(store_ids)
        prod = random.choice(product_ids)
        
        # 3. Logika Jumlah Beli
        qty = np.random.choice([1, 2, 3, 4, 5, 10, 24], p=[0.5, 0.2, 0.1, 0.1, 0.05, 0.03, 0.02])
        
        # 4. Hitung Harga & Diskon Random
        gross_amt = qty * product_prices[prod]
        is_discount = random.random() > 0.8 # 20% kemungkinan ada diskon
        disc_amt = gross_amt * 0.10 if is_discount else 0
        
        txn_data.append({
            "transaction_id": fake.uuid4(),
            "date": txn_date.strftime("%Y-%m-%d"),
            "store_id": store,
            "product_id": prod,
            "quantity_sold": qty,
            "discount_amount": int(disc_amt)
        })
        
    df_txn = pd.DataFrame(txn_data)
    
    # Sort berdasarkan tanggal biar rapi
    df_txn.sort_values(by='date', inplace=True)
    
    file_path = os.path.join(DATA_FOLDER, 'raw_sales_transactions.csv')
    df_txn.to_csv(file_path, index=False)
    print(f"  Saved: {file_path}")

def main():
    # Pastikan folder 'data' ada
    os.makedirs(DATA_FOLDER, exist_ok=True)
    
    # Eksekusi generator
    generate_products()
    stores_df = generate_stores()
    generate_transactions(PRODUCTS, stores_df)
    
    print("\n[SUCCESS] Mock Data Generation Completed!")

if __name__ == "__main__":
    main()