"""
Backend - Lõi ứng dụng xử lý âm thanh và tìm kiếm
"""
from backend.config import *
from backend.audio import *
from backend.database import *
from backend.search import *

__all__ = [
    # Config
    'PROJECT_ROOT',
    'DATA_DIR',
    'RAW_AUDIO_DIR',
    'PROCESSED_AUDIO_DIR',
    'FEATURES_FILE',
    'METADATA_CSV',
    'DB_FILE',
    'TARGET_SAMPLE_RATE',
    'TARGET_DURATION',
    'N_MFCC',
    'N_MELS',
    'TOP_K',
    'DISTANCE_METRIC',
    
    # Audio
    'find_audio_files',
    'load_audio',
    'normalize_audio',
    'pad_or_trim',
    'preprocess_audio',
    'extract_features',
    'process_audio_files',
    'save_features_and_metadata',
    
    # Database
    'DatabaseManager',
    'DatabaseQueries',
    
    # Search
    'VoiceSearchEngine'
]
