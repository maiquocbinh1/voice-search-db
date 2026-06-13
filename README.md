#  Voice Search System - Male Voice Similarity Search

Hệ thống tìm kiếm giọng nói đàn ông sử dụng kỹ thuật xử lý tín hiệu âm thanh để tìm kiếm các file âm thanh có giọng nói tương tự nhất.

## Tính Năng

- **Xử lý âm thanh**: Trích xuất 15 loại đặc trưng âm thanh (MFCC, Mel, Chroma, Spectral)
- **Cơ sở dữ liệu**: SQLite database với metadata và features
- **Tìm kiếm tương tự**: So sánh cosine/euclidean distance
-  **CLI Interface**: Giao diện dòng lệnh dễ sử dụng
- **Modular Architecture**: Cấu trúc module rõ ràng, dễ mở rộng

## Cấu Trúc Dự Án (Mới)

```
voice_project/
├── main.py                          # Entry point
├── main/cli.py                      # CLI interface
├── backend/                         # Core backend
│   ├── __init__.py
│   ├── config.py                    # Configuration
│   ├── audio/                       #Audio processing
│   │   ├── __init__.py
│   │   ├── preprocessing.py         # Audio loading & normalization
│   │   └── processor.py             # Feature extraction
│   ├── database/                    # Database management
│   │   ├── __init__.py
│   │   ├── db_manager.py            # DB operations
│   │   └── queries.py               # DB queries
│   └── search/                      # Voice search
│       ├── __init__.py
│       └── voice_search.py          # Search engine
├── utils/                           # Utilities
│   ├── __init__.py
│   └── helpers.py                   # Helper functions
├── data/                            # Data files
│   ├── raw_audio/                   # Raw audio files (739 files)
│   └── processed_audio/             # Processed data
│       ├── features.json            # Extracted features
│       ├── metadata.csv             # Audio metadata
│       └── voice_database.db        # SQLite database
├── requirements.txt                 # Dependencies
├── README.md                        # This file
├── REPORT.md                        # Báo cáo
├── test_structure.py                # Structure test
├── raw_audio/                       # File âm thanh gốc
└── processed_audio/                 # features.json, metadata.csv, voice_database.db
```

##  Quick Start (5 phút)

### 1. Chuẩn Bị Dữ Liệu
```bash
# Đặt file âm thanh vào thư mục raw_audio/
# Hỗ trợ: .wav, .flac, .mp3, .ogg
```

### 2. Cài Đặt Dependencies
```bash
pip install -r requirements.txt
```

### 3. Trích Xuất Đặc Trưng
```bash
python main.py extract
```
→ Tạo `features.json` và `metadata.csv`

### 4. Tạo Database
```bash
python main.py create-db
```
→ Tạo `voice_database.db`

### 5. Tìm Kiếm Giọng Nói
```bash
python main.py search raw_audio/male_000.wav
```
→ Hiển thị top-5 giọng nói giống nhất

### 6. Mở giao diện web demo
```bash
python main.py web
```
→ Truy cập http://127.0.0.1:5000 để sử dụng giao diện demo

##  CLI Commands

| Command | Description |
|---------|-------------|
| `python main.py extract` | Trích xuất đặc trưng âm thanh |
| `python main.py create-db` | Tạo và import database |
| `python main.py search <file>` | Tìm kiếm giọng nói tương tự |
| `python main.py info` | Hiển thị thông tin database |
| `python main.py help` | Hiển thị trợ giúp |

##  Đặc Trưng Âm Thanh (15 loại)

1. **MFCC** (13 coefficients) - Mean & Std
2. **Mel Spectrogram** (64 bins) - Mean & Std
3. **Chroma STFT** (12 bins) - Mean & Std
4. **Spectral Centroid** - Mean & Std
5. **Spectral Contrast** (7 bands) - Mean & Std
6. **Zero Crossing Rate** - Mean & Std
7. **Energy** - Single value
8. **RMS Energy** - Mean & Std

## 🔧 Cấu Hình

```python
# backend/config.py
TARGET_SAMPLE_RATE = 16000    # Hz
TARGET_DURATION = 3.0         # seconds
N_MFCC = 13                   # MFCC coefficients
N_MELS = 64                   # Mel bins
TOP_K = 5                     # Search results
DISTANCE_METRIC = 'cosine'    # 'cosine' or 'euclidean'
```

##  Workflow Chi Tiết

### Bước 1: Thu Thập Dữ Liệu
- Đặt 739 file giọng nam vào `raw_audio/`
- Mỗi file: 3 giây, 16kHz, WAV 16-bit

### Bước 2: Xử Lý Âm Thanh
```bash
python main.py extract
```
- Chuẩn hóa amplitude về [-1, 1]
- Pad/trim về độ dài chuẩn 3 giây
- Trích xuất 15 đặc trưng âm thanh
- Lưu metadata và features

### Bước 3: Database Setup
```bash
python main.py create-db
```
- Tạo bảng SQLite: `metadata`, `features`
- Import dữ liệu từ CSV/JSON
- Tạo index cho tìm kiếm nhanh
- Kiểm tra tính toàn vẹn

### Bước 4: Voice Search
```bash
python main.py search path/to/query.wav
```
- Xử lý file query tương tự
- Vector hóa đặc trưng
- So sánh với toàn bộ database
- Trả về top-5 kết quả với similarity score

## 🧪 Testing

```bash
# Kiểm tra cấu trúc dự án
python test_structure.py

# Kiểm tra imports
python -c "from backend.audio import extract_features; print('✅ OK')"
```

##  Documentation

- **[PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md)** - Hướng dẫn cấu trúc chi tiết
- **[QUICK_REFERENCE.md](QUICK_REFERENCE.md)** - Tài liệu tham khảo nhanh
- **[GITHUB_PUSH_GUIDE.md](GITHUB_PUSH_GUIDE.md)** - Hướng dẫn push lên GitHub

## Git Branches

Dự án sử dụng Git Flow với các branch:

- `main` - Branch chính
- `feature/restructure-project` - Cấu trúc mới
- `feature/backend-*` - Các module backend
- `feature/main-cli` - CLI interface
- `feature/utils-helpers` - Utilities
- `feature/documentation` - Docs

##  Deployment

### Local Development
```bash
# Clone repository
git clone https://github.com/username/voice-search-project.git
cd voice-search-project

# Install dependencies
pip install -r requirements.txt

# Run tests
python test_structure.py

# Start using
python main.py help
```

### Docker (Tương Lai)
```bash
# Sẽ thêm Dockerfile trong tương lai
docker build -t voice-search .
docker run voice-search python main.py search sample.wav
```

## Contributing

1. Fork repository
2. Tạo feature branch: `git checkout -b feature/new-feature`
3. Commit changes: `git commit -m "feat: add new feature"`
4. Push branch: `git push origin feature/new-feature`
5. Tạo Pull Request

##  License

MIT License - Xem LICENSE file để biết thêm chi tiết.

##  Authors

- **Developer**: Voice Search Team
- **Contact**: voice.search.dev@example.com

---

** Happy Voice Searching!**
- Output: Top 5 file giọng nói giống nhất
- Metric: Cosine similarity

## Đặc Trưng Kỹ Thuật

### Bộ Đặc Trưng (15 loại)
- MFCC (13 coeffs): mean, std
- Mel Spectrogram (64 bins): mean, std
- Chroma (12 bins): mean, std
- Spectral Centroid: mean, std
- Spectral Contrast (7 bands): mean, std
- Zero Crossing Rate: mean, std
- Energy, RMS: mean, std

### Database Schema
```sql
-- Metadata table
CREATE TABLE metadata (
    file_id TEXT PRIMARY KEY,
    source_path TEXT,
    sample_rate INTEGER,
    duration_s REAL,
    n_samples INTEGER
);

-- Features table
CREATE TABLE features (
    file_id TEXT PRIMARY KEY,
    mfcc_mean TEXT, mfcc_std TEXT,
    mel_spec_mean TEXT, mel_spec_std TEXT,
    chroma_mean TEXT, chroma_std TEXT,
    spectral_centroid_mean REAL, spectral_centroid_std REAL,
    spectral_contrast_mean TEXT, spectral_contrast_std TEXT,
    zcr_mean REAL, zcr_std REAL,
    energy REAL, rms_mean REAL, rms_std REAL
);
```

## Kết Quả Ví Dụ
```
🔍 Tìm kiếm giọng nói tương tự: indianmale (1).wav
------------------------------------------------------------
Rank  File ID              Similarity      Source
------------------------------------------------------------
1     indianmale (1)       1.0000         indianmale (1).wav
2     threeIndMale (41)    0.9986         threeIndMale (41).wav
3     threeIndMale (44)    0.9984         threeIndMale (44).wav
4     indianmale (136)     0.9982         indianmale (136).wav
5     indianmale (47)      0.9978         indianmale (47).wav
```

## Yêu Cầu Hệ Thống
- Python 3.8+
- Thư viện: librosa, soundfile, numpy, pandas, scipy, tqdm
- Dung lượng: ~50MB (database + audio files)

## Mở Rộng
- Thêm giọng nữ hoặc đa ngôn ngữ
- Sử dụng ANN (Approximate Nearest Neighbor) cho dataset lớn
- Tích hợp machine learning để cải thiện độ chính xác
"# voice-search-project" 
