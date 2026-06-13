"""
Quản lý cơ sở dữ liệu SQLite
"""
import sqlite3
from pathlib import Path
from typing import List, Dict
import pandas as pd

from backend.config import DB_FILE, FEATURES_FILE, METADATA_CSV
from backend.search.vector_utils import FEATURE_VECTOR_DIM, features_to_normalized_vector


class DatabaseManager:
    """Quản lý cơ sở dữ liệu giọng nói"""
    
    def __init__(self, db_path: Path = DB_FILE):
        self.db_path = db_path
    
    def create_tables(self) -> None:
        """Tạo các bảng cần thiết trong database"""
        conn = sqlite3.connect(str(self.db_path))
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
        
        # Bảng features
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
        
        # Bảng vector đã chuẩn hóa L2 (phục vụ tìm kiếm nhanh)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS feature_vectors (
                file_id TEXT PRIMARY KEY,
                vector_dim INTEGER NOT NULL,
                vector_json TEXT NOT NULL,
                FOREIGN KEY (file_id) REFERENCES metadata (file_id)
            )
        ''')
        
        # Tạo index
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_file_id ON metadata (file_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_sample_rate ON metadata (sample_rate)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_feature_vectors_file_id ON feature_vectors (file_id)')
        
        conn.commit()
        conn.close()
        print("✅ Tạo bảng database")
    
    def import_metadata(self, csv_file: Path = METADATA_CSV) -> int:
        """
        Import metadata từ CSV
        
        Args:
            csv_file: Đường dẫn file CSV
            
        Returns:
            Số records được import
        """
        df = pd.read_csv(csv_file)
        
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        # Xóa dữ liệu cũ
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
        print(f"✅ Import {len(df)} metadata records")
        return len(df)
    
    def import_features(self, json_file: Path = FEATURES_FILE) -> int:
        """
        Import đặc trưng từ JSON
        
        Args:
            json_file: Đường dẫn file JSON
            
        Returns:
            Số features được import
        """
        import json
        
        with open(json_file, 'r', encoding='utf-8') as f:
            features_data = json.load(f)
        
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        # Xóa dữ liệu cũ
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
        print(f"✅ Import {count} features records")
        return count
    
    def import_feature_vectors(self, json_file: Path = FEATURES_FILE) -> int:
        """
        Tính vector L2 từ đặc trưng và lưu vào bảng feature_vectors.
        
        Args:
            json_file: Đường dẫn file JSON chứa đặc trưng
            
        Returns:
            Số vector được import
        """
        import json
        
        with open(json_file, 'r', encoding='utf-8') as f:
            features_data = json.load(f)
        
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        cursor.execute('DELETE FROM feature_vectors')
        
        count = 0
        for file_id, features in features_data.items():
            normalized = features_to_normalized_vector(features)
            cursor.execute('''
                INSERT INTO feature_vectors (file_id, vector_dim, vector_json)
                VALUES (?, ?, ?)
            ''', (
                file_id,
                FEATURE_VECTOR_DIM,
                json.dumps(normalized.tolist()),
            ))
            count += 1
        
        conn.commit()
        conn.close()
        print(f"✅ Import {count} normalized vectors (dim={FEATURE_VECTOR_DIM})")
        return count
    
    def verify_integrity(self) -> Dict[str, int]:
        """
        Kiểm tra tính toàn vẹn của database
        
        Returns:
            Dictionary với thông tin kiểm tra
        """
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        # Đếm records
        cursor.execute('SELECT COUNT(*) FROM metadata')
        metadata_count = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM features')
        features_count = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM feature_vectors')
        vectors_count = cursor.fetchone()[0]
        
        # Kiểm tra join
        cursor.execute('''
            SELECT COUNT(*) FROM metadata m
            INNER JOIN features f ON m.file_id = f.file_id
        ''')
        joined_count = cursor.fetchone()[0]
        
        cursor.execute('''
            SELECT COUNT(*) FROM metadata m
            INNER JOIN feature_vectors v ON m.file_id = v.file_id
        ''')
        vectors_joined_count = cursor.fetchone()[0]
        
        conn.close()
        
        status = {
            'metadata': metadata_count,
            'features': features_count,
            'feature_vectors': vectors_count,
            'joined': joined_count,
            'vectors_joined': vectors_joined_count,
            'is_valid': (
                metadata_count == features_count == joined_count
                and metadata_count == vectors_count == vectors_joined_count
            )
        }
        
        return status
    
    def get_statistics(self) -> None:
        """In thống kê database"""
        status = self.verify_integrity()
        
        print("\n📊 Kiểm tra Database:")
        print(f"  - Metadata:        {status['metadata']} records")
        print(f"  - Features:        {status['features']} records")
        print(f"  - Feature vectors: {status['feature_vectors']} records")
        print(f"  - Joined:          {status['joined']} records")
        
        if status['is_valid']:
            print("  ✅ Database toàn vẹn!")
        else:
            print("  ❌ Database có lỗi!")
