# Voice Project

## Tổng Quan
Hệ thống tìm kiếm giọng nói đàn ông sử dụng kỹ thuật xử lý tín hiệu âm thanh để tìm kiếm các file âm thanh có giọng nói tương tự nhất.

## Cấu Trúc Thư Mục
```
voice_project/
├── raw_audio/          # File âm thanh thô (739 files)
├── processed_audio/    # File đã xử lý + database
│   ├── metadata.csv    # Siêu dữ liệu
│   ├── features.json   # Đặc trưng (backup)
│   └── voice_database.db # Cơ sở dữ liệu SQLite
└── scripts/            # Scripts xử lý
    ├── preprocess_audio.py
    ├── extract_features.py
    ├── create_database.py
    └── search_voices.py
```

## Bước Thực Hiện

### 1. Thu Thập Dữ Liệu
```bash
python scripts/download_male_voices.py
```
- Tạo 739 file giọng nam synthetic khác nhau
- Mỗi file: 3s, 16kHz, WAV 16-bit

### 2. Xử Lý Dữ Liệu
```bash
python scripts/extract_features.py
```
- Chuẩn hóa amplitude và độ dài
- Trích xuất 15 loại đặc trưng âm thanh
- Lưu metadata và features

### 3. Tạo Cơ Sở Dữ Liệu
```bash
python scripts/create_database.py
```
- Tạo SQLite database
- Import metadata và features
- Tạo index cho tìm kiếm nhanh

### 4. Tìm Kiếm Giọng Nói
```bash
python scripts/search_voices.py path/to/audio.wav
```
- Input: File âm thanh bất kỳ
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
