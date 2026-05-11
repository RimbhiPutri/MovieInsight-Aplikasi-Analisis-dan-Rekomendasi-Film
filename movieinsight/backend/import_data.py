import pandas as pd
import sqlite3
import os

# Lokasi file CSV
csv_path = r'C:\Users\Hp\Documents\coolyeah\sems 4\PASD\movieinsight\data\processed_movies.csv'
# Cek apakah file CSV ada
if not os.path.exists(csv_path):
    print("File CSV tidak ditemukan di: {csv_path}")
    exit() 

df = pd.read_csv(csv_path)
print(f"Total film: {len(df)} baris")
print(f"Kolom yang tersedia: {list(df.columns)}")

# Koneksi ke database SQLite
db_path = 'movies.db'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Buat tabel movies (sesuai dengan struktur CSV)
cursor.execute('''
CREATE TABLE IF NOT EXISTS movies (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT,
    release_date TEXT,
    year INTEGER,
    vote_average REAL,
    popularity REAL,
    vote_count INTEGER,
    original_language TEXT,
    genre TEXT,
    genres_list TEXT,
    main_genre TEXT,
    overview TEXT,
    poster_url TEXT
)
''')

# Hapus data lama agar tidak double
cursor.execute('DELETE FROM movies')
print("   Menghapus data lama...")

# Insert data dari CSV
print("   Mengimpor data...")
count = 0
for _, row in df.iterrows():
    cursor.execute('''
    INSERT INTO movies (
        title, release_date, year, vote_average, popularity, 
        vote_count, original_language, genre, genres_list, 
        main_genre, overview, poster_url
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        row.get('Title', ''),
        row.get('Release_Date', ''),
        int(row.get('release_year', 0)) if pd.notna(row.get('release_year')) else 0,
        float(row.get('Vote_Average', 0)) if pd.notna(row.get('Vote_Average')) else 0,
        float(row.get('Popularity', 0)) if pd.notna(row.get('Popularity')) else 0,
        int(row.get('Vote_Count', 0)) if pd.notna(row.get('Vote_Count')) else 0,
        row.get('Original_Language', ''),
        row.get('Genre', ''),
        row.get('genres_list', ''),
        row.get('main_genre', ''),
        row.get('Overview', ''),
        row.get('Poster_Url', '')
    ))
    count += 1
    
    # Cetak progress setiap 1000 film
    if count % 1000 == 0:
        print(f"Progress: {count}/{len(df)} film...")

conn.commit()
conn.close()

print(f"SELESAI! Database berhasil dibuat: {db_path}")
print(f"Total film: {count}")
print(f"Lokasi: {os.path.abspath(db_path)}")

# Tampilkan contoh data
conn = sqlite3.connect(db_path)
sample = pd.read_sql_query("SELECT id, title, year, vote_average, main_genre FROM movies LIMIT 5", conn)
conn.close()
print("\nContoh data dalam database:")
print(sample.to_string(index=False))