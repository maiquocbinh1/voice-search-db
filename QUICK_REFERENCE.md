# ⚡ Quick Reference - Voice Search System

## 🚀 Quick Start (5 phút)

### 1. Đặt file âm thanh
```bash
# Copy file audio vào thư mục này:
data/raw_audio/
```

### 2. Trích xuất đặc trưng
```bash
python main.py extract
```
Output: `features.json`, `metadata.csv`

### 3. Tạo database
```bash
python main.py create-db
```
Output: `voice_database.db`

### 4. Tìm kiếm
```bash
python main.py search data/raw_audio/male_000.wav
```

---

## 📚 File Map

```
voice_project/
├── main.py                    ← Chạy từ đây!
├── main/cli.py               ← Command interface
├── backend/config.py          ← Cấu hình
├── backend/audio/             ← Xử lý âm thanh
├── backend/database/          ← Quản lý DB
├── backend/search/            ← Tìm kiếm
├── utils/helpers.py           ← Tiện ích
└── data/                      ← Dữ liệu
```

---

## 🎯 Module Purpose

| Module | Purpose | Key Class/Function |
|--------|---------|-------------------|
| **backend/audio/preprocessing.py** | Tải & xử lý audio | `load_audio()`, `normalize_audio()` |
| **backend/audio/processor.py** | Trích đặc trưng | `extract_features()` |
| **backend/database/db_manager.py** | Quản lý DB | `DatabaseManager` |
| **backend/database/queries.py** | Query DB | `DatabaseQueries` |
| **backend/search/voice_search.py** | Tìm kiếm | `VoiceSearchEngine` |
| **main/cli.py** | CLI commands | `CLI` |
| **utils/helpers.py** | Utility functions | `format_size()`, `print_table()` |

---

## 💻 Example Usage (Python)

```python
# 1. Extract features
from backend.audio.processor import process_audio_files
from backend.config import RAW_AUDIO_DIR, PROCESSED_AUDIO_DIR

features, metadata = process_audio_files(RAW_AUDIO_DIR, PROCESSED_AUDIO_DIR)

# 2. Create database
from backend.database import DatabaseManager

db = DatabaseManager()
db.create_tables()
db.import_metadata()
db.import_features()

# 3. Search
from backend.search import VoiceSearchEngine

engine = VoiceSearchEngine()
results = engine.search('data/raw_audio/query.wav')
for file_id, score in results:
    print(f"{file_id}: {score:.4f}")

# 4. Query database
from backend.database import DatabaseQueries

queries = DatabaseQueries()
all_metadata = queries.load_metadata_from_db()
features = queries.get_features_by_id('male_000')
```

---

## 🔧 Configuration (backend/config.py)

```python
# Audio settings
TARGET_SAMPLE_RATE = 16000      # Hz
TARGET_DURATION = 3.0            # seconds
N_MFCC = 13                       # MFCC coefficients
N_MELS = 64                       # Mel bins

# Search settings
TOP_K = 5                         # Top results
DISTANCE_METRIC = 'cosine'        # or 'euclidean'

# Paths
RAW_AUDIO_DIR = 'data/raw_audio'
PROCESSED_AUDIO_DIR = 'data/processed_audio'
DB_FILE = 'data/processed_audio/voice_database.db'
```

---

## 📊 Features Extracted (15 types)

1. **MFCC** (Mel-Frequency Cepstral Coefficients)
   - mean, std

2. **Mel Spectrogram**
   - mean, std

3. **Chroma STFT**
   - mean, std

4. **Spectral Centroid**
   - mean, std

5. **Spectral Contrast**
   - mean, std

6. **Zero Crossing Rate**
   - mean, std

7. **Energy**
   - single value

8. **RMS Energy**
   - mean, std

---

## 🐛 Troubleshooting

### No audio files found
```bash
# Make sure files are in:
data/raw_audio/
# Supported: .wav, .flac, .mp3, .ogg
```

### Database error
```bash
# Recreate database:
python main.py create-db
```

### Search returns no results
```bash
# Check database has data:
python main.py info
```

---

## 📝 Command Cheat Sheet

```bash
python main.py help          # Show help
python main.py extract       # Extract features
python main.py create-db     # Create database
python main.py search <file> # Search similar voices
python main.py info          # Show database info
```

---

## 🎓 Architecture Overview

```
User Input (CLI)
    ↓
main/cli.py (Command Interface)
    ↓
backend/audio/ (Process Audio)
    ↓
backend/database/ (Store/Load Data)
    ↓
backend/search/ (Search Engine)
    ↓
Output Results
```

---

**Need help?** Run: `python main.py help`
