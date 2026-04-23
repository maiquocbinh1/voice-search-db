"""
Trích xuất đặc trưng âm thanh từ file audio
"""
from typing import Dict, List

import librosa
import numpy as np
import pandas as pd
from pathlib import Path
from tqdm import tqdm

from backend.config import (
    TARGET_SAMPLE_RATE, N_MFCC, N_MELS,
    RAW_AUDIO_DIR, PROCESSED_AUDIO_DIR, FEATURES_FILE, METADATA_CSV
)
from backend.audio.preprocessing import (
    find_audio_files, load_audio, normalize_audio, pad_or_trim
)


def extract_features(audio: np.ndarray, sr: int) -> Dict[str, float | List]:
    """
    Trích xuất các đặc trưng âm thanh từ tín hiệu
    
    Args:
        audio: Mảng tín hiệu âm thanh
        sr: Tần số mẫu
        
    Returns:
        Dictionary chứa các đặc trưng
    """
    features = {}
    
    # MFCC (Mel-Frequency Cepstral Coefficients)
    mfcc = librosa.feature.mfcc(y=audio, sr=sr, n_mfcc=N_MFCC)
    features['mfcc_mean'] = mfcc.mean(axis=1).tolist()
    features['mfcc_std'] = mfcc.std(axis=1).tolist()
    
    # Mel Spectrogram
    mel_spec = librosa.feature.melspectrogram(y=audio, sr=sr, n_mels=N_MELS)
    features['mel_spec_mean'] = mel_spec.mean(axis=1).tolist()
    features['mel_spec_std'] = mel_spec.std(axis=1).tolist()
    
    # Chroma STFT
    chroma = librosa.feature.chroma_stft(y=audio, sr=sr)
    features['chroma_mean'] = chroma.mean(axis=1).tolist()
    features['chroma_std'] = chroma.std(axis=1).tolist()
    
    # Spectral Centroid
    spec_cent = librosa.feature.spectral_centroid(y=audio, sr=sr)[0]
    features['spectral_centroid_mean'] = float(spec_cent.mean())
    features['spectral_centroid_std'] = float(spec_cent.std())
    
    # Spectral Contrast
    spec_contrast = librosa.feature.spectral_contrast(y=audio, sr=sr)
    features['spectral_contrast_mean'] = spec_contrast.mean(axis=1).tolist()
    features['spectral_contrast_std'] = spec_contrast.std(axis=1).tolist()
    
    # Zero Crossing Rate
    zcr = librosa.feature.zero_crossing_rate(audio)[0]
    features['zcr_mean'] = float(zcr.mean())
    features['zcr_std'] = float(zcr.std())
    
    # Energy
    energy = np.sum(audio**2) / len(audio)
    features['energy'] = float(energy)
    
    # RMS Energy
    rms = librosa.feature.rms(y=audio)[0]
    features['rms_mean'] = float(rms.mean())
    features['rms_std'] = float(rms.std())
    
    return features


def process_audio_files(
    input_dir: Path = RAW_AUDIO_DIR,
    output_dir: Path = PROCESSED_AUDIO_DIR
) -> tuple[Dict, List[Dict]]:
    """
    Xử lý tất cả file audio trong thư mục
    
    Args:
        input_dir: Thư mục chứa file audio thô
        output_dir: Thư mục để lưu kết quả
        
    Returns:
        (all_features, metadata_list)
    """
    files = find_audio_files(input_dir)
    print(f"📁 Tìm thấy {len(files)} file audio")
    
    if len(files) == 0:
        print("⚠️  Không tìm thấy file audio. Hãy kiểm tra raw_audio/")
        return {}, []
    
    output_dir.mkdir(parents=True, exist_ok=True)
    
    all_features = {}
    metadata_list = []
    
    for file_path in tqdm(files, desc="🎵 Trích đặc trưng", unit="file"):
        try:
            # Tải và tiền xử lý audio
            audio, sr = load_audio(file_path)
            audio = normalize_audio(audio)
            audio = pad_or_trim(audio, sr)
            
            # Trích đặc trưng
            features = extract_features(audio, sr)
            all_features[file_path.stem] = features
            
            # Metadata
            metadata_list.append({
                'file_id': file_path.stem,
                'source_path': str(file_path.relative_to(input_dir)),
                'sample_rate': TARGET_SAMPLE_RATE,
                'duration_s': 3.0,
                'n_samples': len(audio),
            })
        except Exception as e:
            print(f"❌ Lỗi xử lý {file_path}: {e}")
    
    return all_features, metadata_list


def save_features_and_metadata(
    all_features: Dict,
    metadata_list: List[Dict],
    features_file: Path = FEATURES_FILE,
    metadata_file: Path = METADATA_CSV
) -> None:
    """
    Lưu đặc trưng và metadata
    
    Args:
        all_features: Dictionary chứa tất cả đặc trưng
        metadata_list: Danh sách metadata
        features_file: Đường dẫn lưu file đặc trưng (JSON)
        metadata_file: Đường dẫn lưu metadata (CSV)
    """
    import json
    
    # Lưu đặc trưng
    with open(features_file, 'w', encoding='utf-8') as f:
        json.dump(all_features, f, indent=2)
    print(f"✅ Lưu đặc trưng: {features_file}")
    
    # Lưu metadata
    df = pd.DataFrame(metadata_list)
    df.to_csv(metadata_file, index=False)
    print(f"✅ Lưu metadata: {metadata_file}")
    
    print(f"\n📊 Tổng cộng: {len(metadata_list)} file đã xử lý")
