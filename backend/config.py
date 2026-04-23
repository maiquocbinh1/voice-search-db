"""
Cấu hình toàn bộ ứng dụng Voice Search
"""
from pathlib import Path

# ============ Đường dẫn ============
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
RAW_AUDIO_DIR = DATA_DIR / "raw_audio"
PROCESSED_AUDIO_DIR = DATA_DIR / "processed_audio"

# ============ File paths ============
FEATURES_FILE = PROCESSED_AUDIO_DIR / "features.json"
METADATA_CSV = PROCESSED_AUDIO_DIR / "metadata.csv"
DB_FILE = PROCESSED_AUDIO_DIR / "voice_database.db"

# ============ Audio Configuration ============
TARGET_SAMPLE_RATE = 16000
TARGET_DURATION = 3.0

# ============ Feature Extraction ============
N_MFCC = 13
N_MELS = 64

# ============ Search Configuration ============
TOP_K = 5
DISTANCE_METRIC = 'cosine'  # 'cosine' or 'euclidean'

# ============ Directories Setup ============
# Tạo các thư mục nếu chưa tồn tại
RAW_AUDIO_DIR.mkdir(parents=True, exist_ok=True)
PROCESSED_AUDIO_DIR.mkdir(parents=True, exist_ok=True)
