"""
Xử lý tiền xử lý âm thanh
"""
from pathlib import Path
from typing import List, Tuple

import librosa
import numpy as np

from backend.config import TARGET_SAMPLE_RATE, TARGET_DURATION


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
