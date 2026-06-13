"""Gộp đặc trưng thành vector và chuẩn hóa L2."""
from typing import Dict

import numpy as np

FEATURE_VECTOR_DIM = 199


def features_to_vector(features: dict) -> np.ndarray:
    """Chuyển dictionary đặc trưng thành vector số học."""
    vector = [
        features['spectral_centroid_mean'],
        features['spectral_centroid_std'],
        features['zcr_mean'],
        features['zcr_std'],
        features['energy'],
        features['rms_mean'],
        features['rms_std'],
    ]
    vector.extend(features['mfcc_mean'])
    vector.extend(features['mfcc_std'])
    vector.extend(features['mel_spec_mean'])
    vector.extend(features['mel_spec_std'])
    vector.extend(features['chroma_mean'])
    vector.extend(features['chroma_std'])
    vector.extend(features['spectral_contrast_mean'])
    vector.extend(features['spectral_contrast_std'])
    return np.array(vector, dtype=np.float64)


def normalize_vector(vector: np.ndarray) -> np.ndarray:
    """Chuẩn hóa L2 vector về độ dài 1."""
    return vector / (np.linalg.norm(vector) + 1e-8)


def features_to_normalized_vector(features: dict) -> np.ndarray:
    """Gộp đặc trưng và chuẩn hóa L2 (dùng khi lưu DB / so sánh)."""
    return normalize_vector(features_to_vector(features))
