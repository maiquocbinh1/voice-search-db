import sqlite3
import json
import pandas as pd
from pathlib import Path
import numpy as np

PROCESSED_DIR = Path(__file__).resolve().parent.parent / "processed_audio"
DB_FILE = PROCESSED_DIR / "voice_database.db"
FEATURES_JSON = PROCESSED_DIR / "features.json"
METADATA_CSV = PROCESSED_DIR / "metadata.csv"

def create_database():
    """Tạo cơ sở dữ liệu SQLite với các bảng cần thiết"""
    conn = sqlite3.connect(str(DB_FILE))
    cursor = conn.cursor()

    # Bảng metadata
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS metadata (
            file_id TEXT PRIMARY KEY,
            source_path TEXT,
            sample_rate INTEGER,
            duration_s REAL,
            n_samples INTEGER
        )
    ''')

    # Bảng features (lưu dưới dạng JSON)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS features (
            file_id TEXT PRIMARY KEY,
            mfcc_mean TEXT,
            mfcc_std TEXT,
            mel_spec_mean TEXT,
            mel_spec_std TEXT,
            chroma_mean TEXT,
            chroma_std TEXT,
            spectral_centroid_mean REAL,
            spectral_centroid_std REAL,
            spectral_contrast_mean TEXT,
            spectral_contrast_std TEXT,
            zcr_mean REAL,
            zcr_std REAL,
            energy REAL,
            rms_mean REAL,
            rms_std REAL,
            FOREIGN KEY (file_id) REFERENCES metadata (file_id)
        )
    ''')

    # Tạo index để tìm kiếm nhanh
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_file_id ON metadata (file_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_sample_rate ON metadata (sample_rate)')

    conn.commit()
    conn.close()

def import_metadata():
    """Import metadata từ CSV vào database"""
    df = pd.read_csv(METADATA_CSV)

    conn = sqlite3.connect(str(DB_FILE))
    cursor = conn.cursor()

    # Xóa dữ liệu cũ nếu có
    cursor.execute('DELETE FROM metadata')

    # Insert dữ liệu mới
    for _, row in df.iterrows():
        cursor.execute('''
            INSERT INTO metadata (file_id, source_path, sample_rate, duration_s, n_samples)
            VALUES (?, ?, ?, ?, ?)
        ''', (
            row['file_id'],
            row['source_path'],
            int(row['sample_rate']),
            float(row['duration_s']),
            int(row['n_samples'])
        ))

    conn.commit()
    conn.close()
    print(f"✓ Đã import {len(df)} records metadata")

def import_features():
    """Import features từ JSON vào database"""
    with open(FEATURES_JSON, 'r', encoding='utf-8') as f:
        features_data = json.load(f)

    conn = sqlite3.connect(str(DB_FILE))
    cursor = conn.cursor()

    # Xóa dữ liệu cũ nếu có
    cursor.execute('DELETE FROM features')

    # Insert dữ liệu mới
    count = 0
    for file_id, features in features_data.items():
        cursor.execute('''
            INSERT INTO features (
                file_id, mfcc_mean, mfcc_std, mel_spec_mean, mel_spec_std,
                chroma_mean, chroma_std, spectral_centroid_mean, spectral_centroid_std,
                spectral_contrast_mean, spectral_contrast_std, zcr_mean, zcr_std,
                energy, rms_mean, rms_std
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            file_id,
            json.dumps(features['mfcc_mean']),
            json.dumps(features['mfcc_std']),
            json.dumps(features['mel_spec_mean']),
            json.dumps(features['mel_spec_std']),
            json.dumps(features['chroma_mean']),
            json.dumps(features['chroma_std']),
            features['spectral_centroid_mean'],
            features['spectral_centroid_std'],
            json.dumps(features['spectral_contrast_mean']),
            json.dumps(features['spectral_contrast_std']),
            features['zcr_mean'],
            features['zcr_std'],
            features['energy'],
            features['rms_mean'],
            features['rms_std']
        ))
        count += 1

    conn.commit()
    conn.close()
    print(f"✓ Đã import {count} records features")

def verify_database():
    """Kiểm tra tính toàn vẹn của database"""
    conn = sqlite3.connect(str(DB_FILE))
    cursor = conn.cursor()

    # Đếm số records
    cursor.execute('SELECT COUNT(*) FROM metadata')
    metadata_count = cursor.fetchone()[0]

    cursor.execute('SELECT COUNT(*) FROM features')
    features_count = cursor.fetchone()[0]

    # Kiểm tra join
    cursor.execute('''
        SELECT COUNT(*) FROM metadata m
        INNER JOIN features f ON m.file_id = f.file_id
    ''')
    joined_count = cursor.fetchone()[0]

    print("\n📊 Kiểm tra database:")
    print(f"  - Metadata records: {metadata_count}")
    print(f"  - Features records: {features_count}")
    print(f"  - Joined records: {joined_count}")

    if metadata_count == features_count == joined_count:
        print("  ✅ Database toàn vẹn!")
    else:
        print("  ❌ Database có lỗi!")

    # Hiển thị sample
    cursor.execute('''
        SELECT m.file_id, m.duration_s, f.energy, f.rms_mean
        FROM metadata m
        INNER JOIN features f ON m.file_id = f.file_id
        LIMIT 5
    ''')
    rows = cursor.fetchall()

    print("\n📋 Sample records:")
    print(f"{'File ID':<20} {'Duration':<10} {'Energy':<12} {'RMS Mean':<12}")
    print("-" * 60)
    for row in rows:
        print(f"{row[0]:<20} {row[1]:<10.2f} {row[2]:<12.4f} {row[3]:<12.4f}")

    conn.close()

def main():
    """Chạy toàn bộ quá trình tạo và import database"""
    print("🏗️  Tạo cơ sở dữ liệu giọng nói...")

    # Tạo database
    create_database()
    print("✓ Đã tạo cấu trúc database")

    # Import dữ liệu
    import_metadata()
    import_features()

    # Kiểm tra
    verify_database()

    print(f"\n✅ Hoàn thành! Database lưu tại: {DB_FILE}")

if __name__ == "__main__":
    main()
