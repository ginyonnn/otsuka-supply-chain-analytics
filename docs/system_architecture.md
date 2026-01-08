# Otsuka Supply Chain & Sales Analytics Platform (OS-CAP)

## 1. System Overview
Sistem ini dirancang untuk mensimulasikan integrasi data End-to-End dari fase Manufaktur hingga Penjualan Retail. Menggunakan arsitektur ELT (Extract, Load, Transform) berbasis Python dan Apache Airflow.

## 2. Data Modeling Strategy

### A. Source System (OLTP Simulation)
Simulasi data mentah dari sistem operasional pabrik dan lapangan.
- **Scope:** Raw transactions (Produksi harian & Sales order).
- **Format:** Normalized (3NF) - Fokus pada efisiensi insert data.
- **Technology:** PostgreSQL (Schema: `raw_source`)

### B. Data Warehouse (OLAP - Target)
Gudang data terpusat untuk kebutuhan analitik.
- **Architecture:** Kimball's Star Schema.
- **Grain (Level Detail):** Transaksi harian per SKU per Toko.
- **Schema:**
  - **Fact Tables:** Tabel utama yang berisi angka/metrik (Sales Amount, Qty Produced).
  - **Dimension Tables:** Tabel referensi (Produk, Toko, Waktu).
- **Technology:** PostgreSQL (Schema: `dwh_analytics`)

## 3. Data Governance Policy
- Naming Convention: `snake_case` untuk kolom dan tabel.
- Primary Keys: Menggunakan Surrogate Key (ID unik buatan sistem) pada tabel Dimensi.
- Currency: IDR (Indonesian Rupiah).