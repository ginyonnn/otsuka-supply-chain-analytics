-- DDL untuk Data Warehouse (Star Schema)
-- Designed for Business Intelligence

-- =========================================================
-- A. DIMENSION TABLES (Tabel Referensi "Siapa", "Apa", "Dimana")
-- =========================================================

-- Dimensi Produk: Menyimpan sejarah perubahan atribut produk (SCD Type 1 Concept)
CREATE TABLE IF NOT EXISTS dim_products (
    product_sk SERIAL PRIMARY KEY, -- Surrogate Key (Integer, urut) bukan Product Code asli
    original_product_id VARCHAR(50), -- Business Key asli
    product_name VARCHAR(100),
    product_category VARCHAR(50),
    product_brand VARCHAR(50),     -- Tambahan hierarki untuk analisis
    current_price NUMERIC(15,2),
    is_active BOOLEAN DEFAULT TRUE -- Untuk filter produk yang sudah discontinue
);

-- Dimensi Toko/Lokasi
CREATE TABLE IF NOT EXISTS dim_stores (
    store_sk SERIAL PRIMARY KEY,
    original_store_id VARCHAR(20),
    store_name VARCHAR(100),
    city VARCHAR(50),
    region VARCHAR(50),
    sales_channel VARCHAR(50) -- Contoh: Minimarket vs Supermarket
);

-- Dimensi Waktu (Time Intelligence)
-- Sangat penting di BI agar bisa analisis "Year-on-Year" atau "Quarterly"
CREATE TABLE IF NOT EXISTS dim_date (
    date_id INT PRIMARY KEY, -- Format YYYYMMDD (e.g., 20240108)
    full_date DATE,
    year INT,
    month INT,
    month_name VARCHAR(15),
    quarter INT, -- Q1, Q2, Q3, Q4
    week_of_year INT,
    is_weekend BOOLEAN
);

-- =========================================================
-- B. FACT TABLES (Tabel Pusat berisi "Angka/Fakta")
-- =========================================================

-- Fakta Penjualan (Transactional Fact)
CREATE TABLE IF NOT EXISTS fact_sales (
    fact_sales_id SERIAL PRIMARY KEY,
    date_id INT,    -- Terhubung ke dim_date
    product_sk INT, -- Terhubung ke dim_products (bukan ID asli!)
    store_sk INT,   -- Terhubung ke dim_stores
    
    -- Metrics (Apa yang dihitung)
    sales_qty INT,
    sales_amount_gross NUMERIC(15,2), -- (Qty * Harga) sebelum diskon
    discount_amount NUMERIC(15,2),
    sales_amount_net NUMERIC(15,2),   -- (Gross - Diskon) revenue bersih
    
    FOREIGN KEY (date_id) REFERENCES dim_date(date_id),
    FOREIGN KEY (product_sk) REFERENCES dim_products(product_sk),
    FOREIGN KEY (store_sk) REFERENCES dim_stores(store_sk)
);

-- Fakta Inventory (Snapshot Fact)
CREATE TABLE IF NOT EXISTS fact_inventory (
    fact_inv_id SERIAL PRIMARY KEY,
    date_id INT,
    product_sk INT,
    stock_qty INT, -- Jumlah stok di gudang pada akhir hari
    
    FOREIGN KEY (date_id) REFERENCES dim_date(date_id),
    FOREIGN KEY (product_sk) REFERENCES dim_products(product_sk)
);