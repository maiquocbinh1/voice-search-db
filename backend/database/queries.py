"""
Các câu query database
"""
import sqlite3
import json
from pathlib import Path
from typing import Dict, List

import pandas as pd

from backend.config import DB_FILE


class DatabaseQueries:
    """Thực hiện các câu query database"""
    
    def __init__(self, db_path: Path = DB_FILE):
        self.db_path = db_path
    
    def load_features_from_db(self) -> Dict[str, Dict]:
        """
        Tải tất cả đặc trưng từ database
        
        Returns:
            Dictionary với file_id là key
        """
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM features')
        rows = cursor.fetchall()
        
        features = {}
        for row in rows:
            file_id = row[0]
            features[file_id] = {
                'mfcc_mean': json.loads(row[1]),
                'mfcc_std': json.loads(row[2]),
                'mel_spec_mean': json.loads(row[3]),
                'mel_spec_std': json.loads(row[4]),
                'chroma_mean': json.loads(row[5]),
                'chroma_std': json.loads(row[6]),
                'spectral_centroid_mean': row[7],
                'spectral_centroid_std': row[8],
                'spectral_contrast_mean': json.loads(row[9]),
                'spectral_contrast_std': json.loads(row[10]),
                'zcr_mean': row[11],
                'zcr_std': row[12],
                'energy': row[13],
                'rms_mean': row[14],
                'rms_std': row[15]
            }
        
        conn.close()
        return features
    
    def load_metadata_from_db(self) -> pd.DataFrame:
        """
        Tải metadata từ database
        
        Returns:
            DataFrame chứa metadata
        """
        conn = sqlite3.connect(str(self.db_path))
        df = pd.read_sql_query('SELECT * FROM metadata', conn)
        conn.close()
        return df
    
    def get_features_by_id(self, file_id: str) -> Dict | None:
        """
        Lấy đặc trưng của một file
        
        Args:
            file_id: ID của file
            
        Returns:
            Dictionary chứa đặc trưng hoặc None
        """
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM features WHERE file_id = ?', (file_id,))
        row = cursor.fetchone()
        conn.close()
        
        if row is None:
            return None
        
        return {
            'mfcc_mean': json.loads(row[1]),
            'mfcc_std': json.loads(row[2]),
            'mel_spec_mean': json.loads(row[3]),
            'mel_spec_std': json.loads(row[4]),
            'chroma_mean': json.loads(row[5]),
            'chroma_std': json.loads(row[6]),
            'spectral_centroid_mean': row[7],
            'spectral_centroid_std': row[8],
            'spectral_contrast_mean': json.loads(row[9]),
            'spectral_contrast_std': json.loads(row[10]),
            'zcr_mean': row[11],
            'zcr_std': row[12],
            'energy': row[13],
            'rms_mean': row[14],
            'rms_std': row[15]
        }
    
    def get_metadata_by_id(self, file_id: str) -> Dict | None:
        """
        Lấy metadata của một file
        
        Args:
            file_id: ID của file
            
        Returns:
            Dictionary chứa metadata hoặc None
        """
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM metadata WHERE file_id = ?', (file_id,))
        row = cursor.fetchone()
        conn.close()
        
        if row is None:
            return None
        
        return {
            'file_id': row[0],
            'source_path': row[1],
            'sample_rate': row[2],
            'duration_s': row[3],
            'n_samples': row[4]
        }
    
    def count_files(self) -> int:
        """Đếm số file trong database"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        cursor.execute('SELECT COUNT(*) FROM metadata')
        count = cursor.fetchone()[0]
        conn.close()
        
        return count
    
    def get_all_file_ids(self) -> List[str]:
        """Lấy danh sách tất cả file IDs"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        cursor.execute('SELECT file_id FROM metadata')
        rows = cursor.fetchall()
        conn.close()
        
        return [row[0] for row in rows]
