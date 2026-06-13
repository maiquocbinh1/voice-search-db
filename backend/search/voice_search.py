"""
Hệ thống tìm kiếm giọng nói tương tự
"""
from typing import List, Tuple
from pathlib import Path

from scipy.spatial.distance import cosine, euclidean

from backend.config import (
    TARGET_SAMPLE_RATE, TARGET_DURATION, TOP_K, DISTANCE_METRIC
)
from backend.audio.preprocessing import normalize_audio, pad_or_trim, load_audio
from backend.audio.processor import extract_features
from backend.database.queries import DatabaseQueries
from backend.search.vector_utils import (
    features_to_normalized_vector,
)


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
        query_vector = features_to_normalized_vector(query_features)
        
        # Ưu tiên vector L2 đã lưu trong bảng feature_vectors
        all_vectors = self.db_queries.load_normalized_vectors_from_db()
        if not all_vectors:
            all_features = self.db_queries.load_features_from_db()
            all_vectors = {
                file_id: features_to_normalized_vector(features)
                for file_id, features in all_features.items()
            }
        
        # So sánh
        distances = []
        for file_id, db_vector in all_vectors.items():
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
