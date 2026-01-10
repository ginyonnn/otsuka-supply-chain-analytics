import pandas as pd
from sqlalchemy import create_engine, text
import os

# Konfigurasi Koneksi (Sesuai docker-compose.yaml)
DB_USER = 'user_otsuka'
DB_PASSWORD = 'password_rahasia_123'
DB_HOST = 'localhost'
DB_PORT = '5432'
DB_NAME = 'otsuka_analytics'

# Membuat Connection String (URL Database)
DATABASE_URL = f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

def get_engine():
    """Membuat mesin koneksi SQLAlchemy"""
    try:
        engine = create_engine(DATABASE_URL)
        # Tes koneksi sederhana
        with engine.connect() as conn:
            pass
        return engine
    except Exception as e:
        print(f"Error connecting to database: {e}")
        raise e

def execute_sql_file(filename):
    """Membaca file SQL dari folder sql/ dan menjalankannya"""
    engine = get_engine()
    
    # Path handling agar aman di Mac/Windows
    # Mencari folder 'sql' relatif dari script ini
    current_dir = os.path.dirname(os.path.abspath(__file__)) # folder scripts/
    project_root = os.path.dirname(current_dir) # folder root project
    file_path = os.path.join(project_root, 'sql', filename)
    
    print(f"--- Executing SQL File: {filename} ---")
    try:
        with open(file_path, 'r') as file:
            sql_statements = file.read()
            
        with engine.connect() as connection:
            # Gunakan sqlalchemy text() untuk eksekusi raw query
            connection.execute(text(sql_statements))
            connection.commit() # Simpan perubahan
            
        print(f"[SUCCESS] Executed {filename}")
    except FileNotFoundError:
        print(f"[ERROR] File not found: {file_path}")
    except Exception as e:
        print(f"[ERROR] Failed executing SQL: {e}")

if __name__ == "__main__":
    # Test jika script ini dijalankan langsung
    print("Testing connection...")
    get_engine()
    print("Connection successful!")