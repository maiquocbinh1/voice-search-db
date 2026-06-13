"""
Xử lý tiền xử lý âm thanh
"""
from pathlib import Path
from typing import Dict, List, Tuple

import librosa
import numpy as np
import soundfile as sf
from tqdm import tqdm

from backend.config import (
    TARGET_SAMPLE_RATE,
    TARGET_DURATION,
    RAW_AUDIO_DIR,
    STANDARDIZED_AUDIO_DIR,
)


def find_audio_files(root: Path) -> List[Path]:
    """
    Tìm tất cả các file âm thanh trong thư mục
    
    Args:
        root: Thư mục gốc để tìm kiếm
        
    Returns:
        Danh sách các file âm thanh
    """
    return sorted([
        p
        for p in root.rglob("*")
        if p.suffix.lower() in [".wav", ".flac", ".mp3", ".ogg"] and p.is_file()
    ])


def load_audio(file_path: str | Path) -> Tuple[np.ndarray, int]:
    """
    Tải file âm thanh với tần số mẫu chuẩn
    
    Args:
        file_path: Đường dẫn đến file âm thanh
        
    Returns:
        (audio_signal, sample_rate)
    """
    audio, sr = librosa.load(
        str(file_path),
        sr=TARGET_SAMPLE_RATE,
        mono=True
    )
    return audio, sr


def normalize_audio(audio: np.ndarray) -> np.ndarray:
    """
    Chuẩn hóa amplitude âm thanh về [-1, 1]
    
    Args:
        audio: Mảng tín hiệu âm thanh
        
    Returns:
        Âm thanh đã chuẩn hóa
    """
    max_val = np.max(np.abs(audio))
    if max_val <= 0:
        return audio
    return audio / max_val


def pad_or_trim(
    audio: np.ndarray,
    sample_rate: int,
    target_duration: float = TARGET_DURATION
) -> np.ndarray:
    """
    Cắt hoặc padding audio về cùng độ dài
    
    Args:
        audio: Mảng tín hiệu âm thanh
        sample_rate: Tần số mẫu
        target_duration: Độ dài mục tiêu (giây)
        
    Returns:
        Âm thanh đã được cắt/padding
    """
    target_samples = int(sample_rate * target_duration)
    
    if len(audio) > target_samples:
        # Cắt từ đầu
        return audio[:target_samples]
    elif len(audio) < target_samples:
        # Padding với zero
        padding = target_samples - len(audio)
        return np.pad(audio, (0, padding), mode='constant')
    
    return audio


def preprocess_audio(file_path: str | Path) -> np.ndarray:
    """
    Tiền xử lý đầy đủ cho một file âm thanh
    
    Args:
        file_path: Đường dẫn đến file âm thanh
        
    Returns:
        Âm thanh đã được tiền xử lý
    """
    # Tải
    audio, sr = load_audio(file_path)
    
    # Chuẩn hóa amplitude
    audio = normalize_audio(audio)
    
    # Cắt/padding
    audio = pad_or_trim(audio, sr, TARGET_DURATION)
    
    return audio


def standardize_audio_files(
    input_dir: Path = RAW_AUDIO_DIR,
    output_dir: Path = STANDARDIZED_AUDIO_DIR,
    target_duration: float = TARGET_DURATION,
) -> List[Dict]:
    """
    Chuẩn hóa tất cả file âm thanh trong thư mục về CÙNG một độ dài.

    Mỗi file được:
      1. Tải về 16kHz, mono
      2. Chuẩn hóa biên độ về [-1, 1]
      3. Cắt (nếu dài hơn) hoặc thêm khoảng lặng (nếu ngắn hơn) -> đúng target_duration giây
      4. Lưu thành file .wav trong output_dir

    Args:
        input_dir: Thư mục chứa file âm thanh gốc
        output_dir: Thư mục lưu file đã chuẩn hóa
        target_duration: Độ dài mục tiêu (giây), mặc định 3.0

    Returns:
        Danh sách thông tin từng file đã xử lý (gồm độ dài gốc và độ dài sau xử lý)
    """
    files = find_audio_files(input_dir)
    print(f"📁 Tìm thấy {len(files)} file âm thanh trong {input_dir}")

    if len(files) == 0:
        print("⚠️  Không tìm thấy file âm thanh. Hãy kiểm tra thư mục đầu vào.")
        return []

    output_dir.mkdir(parents=True, exist_ok=True)
    target_samples = int(TARGET_SAMPLE_RATE * target_duration)

    report: List[Dict] = []

    for file_path in tqdm(files, desc="🎚️  Chuẩn hóa độ dài", unit="file"):
        try:
            audio, sr = load_audio(file_path)
            original_duration = round(len(audio) / sr, 3)

            audio = normalize_audio(audio)
            audio = pad_or_trim(audio, sr, target_duration)

            out_path = output_dir / f"{file_path.stem}.wav"
            sf.write(str(out_path), audio, TARGET_SAMPLE_RATE)

            report.append({
                "file_id": file_path.stem,
                "original_duration_s": original_duration,
                "standardized_duration_s": round(len(audio) / TARGET_SAMPLE_RATE, 3),
                "n_samples": len(audio),
                "output_path": str(out_path),
            })
        except Exception as e:
            print(f"❌ Lỗi xử lý {file_path}: {e}")

    print(
        f"\n✅ Đã chuẩn hóa {len(report)}/{len(files)} file về "
        f"{target_duration} giây ({target_samples} mẫu, {TARGET_SAMPLE_RATE} Hz)"
    )
    print(f"📂 File chuẩn hóa lưu tại: {output_dir}")
    return report
