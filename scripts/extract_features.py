from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List

import librosa
import numpy as np
import pandas as pd
from tqdm import tqdm

RAW_DIR = Path(__file__).resolve().parent.parent / "raw_audio"
PROCESSED_DIR = Path(__file__).resolve().parent.parent / "processed_audio"
FEATURES_FILE = PROCESSED_DIR / "features.json"
METADATA_CSV = PROCESSED_DIR / "metadata.csv"

# Cấu hình
TARGET_SAMPLE_RATE = 16000
TARGET_DURATION = 3.0
N_MFCC = 13
N_MELS = 64

def find_audio_files(root: Path) -> List[Path]:
    return sorted([
        p
        for p in root.rglob("*")
        if p.suffix.lower() in [".wav", ".flac", ".mp3", ".ogg"] and p.is_file()
    ])

def normalize_audio(audio: np.ndarray) -> np.ndarray:
    """Chuẩn hóa amplitude âm thanh"""
    max_val = np.max(np.abs(audio))
    if max_val <= 0:
        return audio
    return audio / max_val

def pad_or_trim(audio: np.ndarray, sample_rate: int, target_duration: float) -> np.ndarray:
    """Cắt hoặc padding audio về cùng độ dài"""
    target_samples = int(sample_rate * target_duration)
    
    if len(audio) > target_samples:
        # Cắt từ đầu
        return audio[:target_samples]
    elif len(audio) < target_samples:
        # Padding với zero
        padding = target_samples - len(audio)
        return np.pad(audio, (0, padding), mode='constant')
    return audio

def extract_features(audio: np.ndarray, sr: int) -> Dict[str, float | list]:
    """Trích đặc trưng MFCC từ audio"""
    features = {}
    
    # MFCC
    mfcc = librosa.feature.mfcc(y=audio, sr=sr, n_mfcc=N_MFCC)
    features['mfcc_mean'] = mfcc.mean(axis=1).tolist()
    features['mfcc_std'] = mfcc.std(axis=1).tolist()
    
    # Mel spectrogram
    mel_spec = librosa.feature.melspectrogram(y=audio, sr=sr, n_mels=N_MELS)
    features['mel_spec_mean'] = mel_spec.mean(axis=1).tolist()
    features['mel_spec_std'] = mel_spec.std(axis=1).tolist()
    
    # Chroma
    chroma = librosa.feature.chroma_stft(y=audio, sr=sr)
    features['chroma_mean'] = chroma.mean(axis=1).tolist()
    features['chroma_std'] = chroma.std(axis=1).tolist()
    
    # Spectral features
    spec_cent = librosa.feature.spectral_centroid(y=audio, sr=sr)[0]
    features['spectral_centroid_mean'] = float(spec_cent.mean())
    features['spectral_centroid_std'] = float(spec_cent.std())
    
    spec_contrast = librosa.feature.spectral_contrast(y=audio, sr=sr)
    features['spectral_contrast_mean'] = spec_contrast.mean(axis=1).tolist()
    features['spectral_contrast_std'] = spec_contrast.std(axis=1).tolist()
    
    # Zero crossing rate
    zcr = librosa.feature.zero_crossing_rate(audio)[0]
    features['zcr_mean'] = float(zcr.mean())
    features['zcr_std'] = float(zcr.std())
    
    # Energy
    energy = np.sum(audio**2) / len(audio)
    features['energy'] = float(energy)
    
    # RMS
    rms = librosa.feature.rms(y=audio)[0]
    features['rms_mean'] = float(rms.mean())
    features['rms_std'] = float(rms.std())
    
    return features

def process_files() -> None:
    """Xử lý tất cả file audio"""
    files = find_audio_files(RAW_DIR)
    print(f"Tìm thấy {len(files)} file audio")
    
    if len(files) == 0:
        print("Không tìm thấy file audio. Hãy kiểm tra raw_audio/")
        return
    
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    
    all_features = {}
    metadata_list = []
    
    for file_path in tqdm(files, desc="Trích đặc trưng", unit="file"):
        try:
            # Tải audio
            audio, sr = librosa.load(str(file_path), sr=TARGET_SAMPLE_RATE, mono=True)
            
            # Chuẩn hóa
            audio = normalize_audio(audio)
            
            # Pad/trim
            audio = pad_or_trim(audio, TARGET_SAMPLE_RATE, TARGET_DURATION)
            
            # Trích đặc trưng
            features = extract_features(audio, TARGET_SAMPLE_RATE)
            all_features[file_path.stem] = features
            
            # Metadata
            metadata_list.append({
                'file_id': file_path.stem,
                'source_path': str(file_path.relative_to(RAW_DIR)),
                'sample_rate': TARGET_SAMPLE_RATE,
                'duration_s': TARGET_DURATION,
                'n_samples': len(audio),
            })
        except Exception as e:
            print(f"Lỗi xử lý {file_path}: {e}")
    
    # Lưu đặc trưng
    with open(FEATURES_FILE, 'w', encoding='utf-8') as f:
        json.dump(all_features, f, indent=2)
    print(f"✓ Lưu đặc trưng vào {FEATURES_FILE}")
    
    # Lưu metadata
    df = pd.DataFrame(metadata_list)
    df.to_csv(METADATA_CSV, index=False)
    print(f"✓ Lưu metadata vào {METADATA_CSV}")
    print(f"\n📊 Tổng cộng: {len(metadata_list)} file đã xử lý thành công")

if __name__ == "__main__":
    process_files()
