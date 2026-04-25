"""
Hệ thống tìm kiếm giọng nói tương tự
"""
from typing import List, Tuple
from pathlib import Path

import numpy as np
import librosa
from scipy.spatial.distance import cosine, euclidean

from backend.config import (
    TARGET_SAMPLE_RATE, TARGET_DURATION, TOP_K, DISTANCE_METRIC
)
from backend.audio.preprocessing import normalize_audio, pad_or_trim, load_audio
from backend.audio.processor import extract_features
from backend.database.queries import DatabaseQueries


class VoiceSearchEngine:
    """Engine tìm kiếm giọng nói"""
    
    def __init__(self, distance_metric: str = DISTANCE_METRIC, top_k: int = TOP_K):
        """
        Khởi tạo engine
        
        Args:
            distance_metric: 'cosine' hoặc 'euclidean'
            top_k: Số kết quả trả về
        """
        self.distance_metric = distance_metric
        self.top_k = top_k
        self.db_queries = DatabaseQueries()
    
    @staticmethod
    def _features_to_vector(features: dict) -> np.ndarray:
        """
        Chuyển đặc trưng thành vector để so sánh
        
        Args:
            features: Dictionary chứa đặc trưng
            
        Returns:
            Vector numpy
        """
        vector = []
        
        # Scalar values
        vector.append(features['spectral_centroid_mean'])
        vector.append(features['spectral_centroid_std'])
        vector.append(features['zcr_mean'])
        vector.append(features['zcr_std'])
        vector.append(features['energy'])
        vector.append(features['rms_mean'])
        vector.append(features['rms_std'])
        
        # MFCC
        vector.extend(features['mfcc_mean'])
        vector.extend(features['mfcc_std'])
        
        # Mel spectrogram
        vector.extend(features['mel_spec_mean'])
        vector.extend(features['mel_spec_std'])
        
        # Chroma
        vector.extend(features['chroma_mean'])
        vector.extend(features['chroma_std'])
        
        # Spectral contrast
        vector.extend(features['spectral_contrast_mean'])
        vector.extend(features['spectral_contrast_std'])
        
        return np.array(vector)
    
    @staticmethod
    def _normalize_vector(vector: np.ndarray) -> np.ndarray:
        """Chuẩn hóa vector"""
        return vector / (np.linalg.norm(vector) + 1e-8)
    
    def search(self, query_audio_path: str | Path) -> List[Tuple[str, float]]:
        """
        Tìm các giọng nói giống nhất
        
        Args:
            query_audio_path: Đường dẫn file audio truy vấn
            
        Returns:
            Danh sách (file_id, similarity_score)
        """
        # Tải và tiền xử lý
        query_audio, sr = load_audio(query_audio_path)
        query_audio = normalize_audio(query_audio)
        query_audio = pad_or_trim(query_audio, sr, TARGET_DURATION)
        
        # Trích đặc trưng
        query_features = extract_features(query_audio, TARGET_SAMPLE_RATE)
        query_vector = self._features_to_vector(query_features)
        query_vector = self._normalize_vector(query_vector)
        
        # Tải tất cả đặc trưng từ database
        all_features = self.db_queries.load_features_from_db()
        
        # So sánh
        distances = []
        for file_id, features in all_features.items():
            db_vector = self._features_to_vector(features)
            db_vector = self._normalize_vector(db_vector)
            
            if self.distance_metric == 'cosine':
                distance = cosine(query_vector, db_vector)
            else:  # euclidean
                distance = euclidean(query_vector, db_vector)
            
            distances.append((file_id, distance))
        
        # Sắp xếp
        distances.sort(key=lambda x: x[1])
        
        # Chuyển thành similarity score
        results = []
        for file_id, distance in distances[:self.top_k]:
            if self.distance_metric == 'cosine':
                similarity = 1 - distance
            else:
                similarity = 1 / (1 + distance)
            
            results.append((file_id, similarity))
        
        return results
