"""
Cấu hình toàn bộ ứng dụng Voice Search
"""
from pathlib import Path

# ============ Đường dẫn ============
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
ROOT_RAW_AUDIO_DIR = PROJECT_ROOT / "raw_audio"
ROOT_PROCESSED_AUDIO_DIR = PROJECT_ROOT / "processed_audio"

# Nếu root-level directories chứa dữ liệu thực tế thì ưu tiên dùng chúng,
# ngược lại fallback về cấu trúc data/ để tương thích với tài liệu.
if ROOT_RAW_AUDIO_DIR.exists() and any(ROOT_RAW_AUDIO_DIR.iterdir()):
    RAW_AUDIO_DIR = ROOT_RAW_AUDIO_DIR
else:
    RAW_AUDIO_DIR = DATA_DIR / "raw_audio"

if ROOT_PROCESSED_AUDIO_DIR.exists() and any(ROOT_PROCESSED_AUDIO_DIR.iterdir()):
    PROCESSED_AUDIO_DIR = ROOT_PROCESSED_AUDIO_DIR
else:
    PROCESSED_AUDIO_DIR = DATA_DIR / "processed_audio"

# ============ File paths ============
FEATURES_FILE = PROCESSED_AUDIO_DIR / "features.json"
METADATA_CSV = PROCESSED_AUDIO_DIR / "metadata.csv"
DB_FILE = PROCESSED_AUDIO_DIR / "voice_database.db"

# Thư mục chứa file âm thanh đã chuẩn hóa về cùng độ dài (3 giây).
# Đây là DATASET LÀM VIỆC CHÍNH dùng cho extract / search / web.
# raw_audio/ được giữ lại làm bản gốc (backup).
AUDIO_DIR = PROJECT_ROOT / "audio"
# Giữ tên cũ để tương thích ngược (trỏ về cùng thư mục audio/)
STANDARDIZED_AUDIO_DIR = AUDIO_DIR

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
AUDIO_DIR.mkdir(parents=True, exist_ok=True)
