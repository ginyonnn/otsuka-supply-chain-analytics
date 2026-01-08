-- DDL untuk Membuat Schema Sumber Data (Simulasi ERP/OLTP)
-- Di dunia nyata, database ini dikelola oleh tim Software Engineer Aplikasi,
-- kita hanya "menarik" data dari sini.

-- 1. Tabel Produk Master (Raw)
CREATE TABLE IF NOT EXISTS raw_products (
    product_id VARCHAR(50) PRIMARY KEY, -- Kode produk (misal: POC-250ML)
    product_name VARCHAR(100),
    category VARCHAR(50), -- Minuman/Makanan
    unit_price NUMERIC(15, 2), -- Harga satuan
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. Tabel Toko/Distributor Master (Raw)
CREATE TABLE IF NOT EXISTS raw_stores (
    store_id VARCHAR(20) PRIMARY KEY,
    store_name VARCHAR(100),
    city VARCHAR(50),
    region VARCHAR(50),
    channel VARCHAR(50) -- General Trade / Modern Trade
);

-- 3. Tabel Transaksi Penjualan (Raw Transaction)
-- Ini adalah tabel yang "berisik", jutaan data masuk ke sini
CREATE TABLE IF NOT EXISTS raw_sales_transactions (
    transaction_id VARCHAR(50) PRIMARY KEY,
    date DATE,
    store_id VARCHAR(20),
    product_id VARCHAR(50),
    quantity_sold INT,
    discount_amount NUMERIC(15, 2),
    FOREIGN KEY (store_id) REFERENCES raw_stores(store_id),
    FOREIGN KEY (product_id) REFERENCES raw_products(product_id)
);

-- 4. Tabel Inventory Pabrik (Raw Inventory)
CREATE TABLE IF NOT EXISTS raw_inventory (
    inventory_id SERIAL PRIMARY KEY,
    warehouse_date DATE,
    product_id VARCHAR(50),
    stock_on_hand INT,
    FOREIGN KEY (product_id) REFERENCES raw_products(product_id)
);