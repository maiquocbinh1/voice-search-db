# 📋 Voice Search System - Project Structure Guide

## 🎯 Tổng Quan

Dự án đã được tổ chức lại thành cấu trúc rõ ràng với ba thành phần chính:
- **Backend** - Lõi ứng dụng (xử lý âm thanh, cơ sở dữ liệu, tìm kiếm)
- **Main** - Entry points và CLI interface
- **Utils** - Hàm tiện ích chung

---

## 📂 Cấu Trúc Thư Mục

```
voice_project/
│
├── main.py                          ← 🚀 ENTRY POINT (chạy từ đây!)
│
├── main/                            ← 🖥️  MAIN (CLI & Entry Points)
│   ├── __init__.py
│   └── cli.py                       # Command-line interface
│
├── backend/                         ← 🧠 BACKEND (Lõi ứng dụng)
│   ├── __init__.py
│   ├── config.py                    # Cấu hình & hằng số
│   ├── audio/                       # Xử lý âm thanh
│   │   ├── __init__.py
│   │   ├── preprocessing.py         # Hàm tiền xử lý (load, normalize, pad/trim)
│   │   └── processor.py             # Trích xuất đặc trưng (MFCC, Mel, Chroma, v.v)
│   ├── database/                    # Quản lý cơ sở dữ liệu
│   │   ├── __init__.py
│   │   ├── db_manager.py            # Tạo DB, import dữ liệu, kiểm tra
│   │   └── queries.py               # Các câu query đến database
│   └── search/                      # Tìm kiếm giọng nói
│       ├── __init__.py
│       └── voice_search.py          # Engine tìm kiếm (so sánh vector)
│
├── utils/                           ← 🛠️  UTILS (Tiện ích chung)
│   ├── __init__.py
│   └── helpers.py                   # Format, file I/O, print bảng
│
├── data/                            ← 📊 DATA (Dữ liệu)
│   ├── raw_audio/                   # File âm thanh thô
│   └── processed_audio/             # Kết quả xử lý
│       ├── features.json            # Backup đặc trưng
│       ├── metadata.csv             # Siêu dữ liệu
│       └── voice_database.db        # SQLite database
│
├── requirements.txt                 ← 📦 Dependencies
├── README.md                        ← 📖 Documentation gốc
└── REPORT.md                        ← 📋 Báo cáo
```

---

## 🏗️ Chi Tiết Từng Thành Phần

### **1️⃣ MAIN - Entry Points & CLI**

**Vị trí:** `main/` folder

**Chức năng:** Giao diện dòng lệnh (CLI) để người dùng tương tác

**Modules:**
- `main/cli.py` - Class `CLI` với các lệnh:
  - `extract` - Trích xuất đặc trưng
  - `create-db` - Tạo database
  - `search <file>` - Tìm kiếm giọng nói
  - `info` - Xem thông tin
  - `help` - Trợ giúp

**Sử dụng:**
```bash
python main.py extract
python main.py create-db
python main.py search raw_audio/male_000.wav
python main.py info
```

---

### **2️⃣ BACKEND - Lõi Ứng Dụng**

**Vị trí:** `backend/` folder

**Cấu trúc phân cấp:**

#### **A. Backend/Audio** - Xử Lý Âm Thanh
- **preprocessing.py**
  - `load_audio()` - Tải file với sr chuẩn
  - `normalize_audio()` - Chuẩn hóa amplitude
  - `pad_or_trim()` - Điều chỉnh độ dài
  - `preprocess_audio()` - Tiền xử lý hoàn chỉnh

- **processor.py**
  - `extract_features()` - Trích 15 loại đặc trưng (MFCC, Mel, Chroma, Spectral, RMS, v.v)
  - `process_audio_files()` - Xử lý tất cả file
  - `save_features_and_metadata()` - Lưu kết quả

#### **B. Backend/Database** - Quản Lý Cơ Sở Dữ Liệu
- **db_manager.py** - Class `DatabaseManager`
  - `create_tables()` - Tạo bảng metadata & features
  - `import_metadata()` - Import từ CSV
  - `import_features()` - Import từ JSON
  - `verify_integrity()` - Kiểm tra dữ liệu
  - `get_statistics()` - In thống kê

- **queries.py** - Class `DatabaseQueries`
  - `load_features_from_db()` - Tải tất cả features
  - `load_metadata_from_db()` - Tải tất cả metadata
  - `get_features_by_id()` - Lấy features của 1 file
  - `get_metadata_by_id()` - Lấy metadata của 1 file
  - `count_files()` - Đếm file
  - `get_all_file_ids()` - Lấy danh sách ID

#### **C. Backend/Search** - Tìm Kiếm Giọng Nói
- **voice_search.py** - Class `VoiceSearchEngine`
  - `search(query_path)` - Tìm giọng nói giống nhất
  - `_features_to_vector()` - Chuyển đặc trưng → vector
  - `_normalize_vector()` - Chuẩn hóa vector

#### **D. Backend/Config** - Cấu Hình
- Đường dẫn dữ liệu
- Hằng số audio (sample_rate, duration, MFCC, Mel, v.v)
- Cấu hình tìm kiếm (top_k, distance_metric)

---

### **3️⃣ UTILS - Tiện Ích Chung**

**Vị trí:** `utils/` folder

**Modules:**
- `utils/helpers.py` - Các hàm tiện ích:
  - `ensure_directory()` - Tạo thư mục
  - `get_file_info()` - Lấy thông tin file
  - `format_duration()` - Format thời gian
  - `format_size()` - Format kích thước
  - `print_table()` - In bảng đẹp
  - `load_json_file()` / `save_json_file()`

---

## 🔄 Quy Trình Công Việc (Workflow)

### **Bước 1: Trích Xuất Đặc Trưng**
```bash
python main.py extract
```
- Tìm tất cả file audio trong `raw_audio/`
- Xử lý: tải → chuẩn hóa → pad/trim
- Trích 15 loại đặc trưng
- Lưu `features.json` & `metadata.csv`

### **Bước 2: Tạo Database**
```bash
python main.py create-db
```
- Tạo SQLite database
- Import metadata từ CSV
- Import features từ JSON
- Kiểm tra tính toàn vẹn

### **Bước 3: Tìm Kiếm**
```bash
python main.py search raw_audio/male_000.wav
```
- Xử lý file query
- Trích đặc trưng
- So sánh với tất cả file trong DB
- Trả về top-5 kết quả

---

## 📊 Phân Biệt Backend vs Main vs Utils

| Thành Phần | Mục Đích | Ví Dụ |
|-----------|---------|--------|
| **Backend** | Lõi xử lý (business logic) | Xử lý audio, query DB, tìm kiếm |
| **Main** | Giao diện người dùng (CLI) | Lệnh `extract`, `search`, v.v |
| **Utils** | Hàm tiện ích dùng chung | Format text, I/O file |

---

## 🔌 Cách Import Modules

```python
# Từ main/cli.py
from main.cli import CLI

# Từ backend
from backend.audio import extract_features, preprocess_audio
from backend.database import DatabaseManager, DatabaseQueries
from backend.search import VoiceSearchEngine
from backend.config import TOP_K, TARGET_SAMPLE_RATE

# Từ utils
from utils.helpers import format_duration, print_table
```

---

## ✅ Lợi Ích Của Cấu Trúc Mới

✨ **Tính rõ ràng:**
- Dễ phân biệt main/backend/frontend/utils
- Mỗi module có vai trò cụ thể

✨ **Khả năng mở rộng:**
- Dễ thêm tính năng mới
- Có thể tách backend thành API

✨ **Dễ bảo trì:**
- Tìm code dễ dàng
- Giảm lỗi phụ thuộc

✨ **Có thể tái sử dụng:**
- Backend độc lập → dùng cho web API
- Utils dùng được mọi nơi

✨ **Chuẩn công nghiệp:**
- Theo chuẩn Python project structure
- Dễ làm việc nhóm

---

## 🚀 Tiếp Theo

Bạn có thể:
1. ✅ Thêm **API (Flask/FastAPI)** dùng backend
2. ✅ Thêm **Web UI (HTML/React)** gọi API
3. ✅ Thêm **Tests** cho mỗi module
4. ✅ Thêm **Logging** toàn hệ thống
5. ✅ Docker containerize

---

**Chúc bạn thành công! 🎉**
