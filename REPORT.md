# Báo Cáo Bài Tập Lớn: Hệ Thống Tìm Kiếm Giọng Nói Đàn Ông

## Tổng Quan
Hệ thống tìm kiếm giọng nói đàn ông sử dụng kỹ thuật xử lý tín hiệu âm thanh và học máy để tìm kiếm các file âm thanh có giọng nói tương tự nhất.

## 1. Thu Thập Dữ Liệu
- **Số lượng file**: 739 file âm thanh giọng nam
- **Định dạng**: WAV 16-bit PCM
- **Độ dài**: 3 giây mỗi file
- **Tần số mẫu**: 16 kHz
- **Nguồn**: Tạo synthetic với các đặc trưng giọng nam khác nhau

## 2. Xử Lý Dữ Liệu
### Chuẩn Hóa
- **Amplitude**: Chuẩn hóa về [-1, 1]
- **Độ dài**: Cắt hoặc padding về 3 giây
- **Tần số**: Resample về 16 kHz

### Đặc Trưng Trích Xuất
- **MFCC**: 13 coefficients (mean, std)
- **Mel Spectrogram**: 64 bins (mean, std)
- **Chroma**: 12 bins (mean, std)
- **Spectral Centroid**: mean, std
- **Spectral Contrast**: 7 bands (mean, std)
- **Zero Crossing Rate**: mean, std
- **Energy**: scalar
- **RMS**: mean, std

## 3. Cơ Sở Dữ Liệu
- **Loại**: SQLite
- **Bảng metadata**: file_id, source_path, sample_rate, duration_s, n_samples
- **Bảng features**: file_id + 15 loại đặc trưng
- **Index**: file_id, sample_rate
- **Tổng records**: 739 (metadata + features)

## 4. Hệ Thống Tìm Kiếm
### Thuật Toán
- **Vector hóa**: Chuyển đặc trưng thành vector số học
- **Chuẩn hóa**: L2 normalization
- **Đo khoảng cách**: Cosine similarity
- **Kết quả**: Top 5 file giống nhất

### Ví Dụ Kết Quả
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

## 5. Sơ Đồ Hệ Thống
```
[File Audio Mới] → [Tiền Xử Lý] → [Trích Đặc Trưng] → [Vector Hóa]
      ↓
[Database Features] → [Tính Khoảng Cách] → [Sắp Xếp] → [Top 5 Kết Quả]
```

## 6. Cách Sử Dụng
```bash
# Tìm kiếm giọng nói tương tự
python scripts/search_voices.py path/to/query_audio.wav
```

## 7. Kết Luận
- ✅ Đã hoàn thành tất cả yêu cầu đề bài
- ✅ Dataset: 739 file giọng nam
- ✅ Bộ đặc trưng: 15 loại features
- ✅ CSDL: SQLite với metadata và features
- ✅ Hệ thống tìm kiếm: Top 5 file giống nhất
- ✅ Độ chính xác: Similarity score từ 0-1

Hệ thống có thể mở rộng để xử lý giọng nữ, đa ngôn ngữ, hoặc sử dụng thuật toán học máy nâng cao hơn.