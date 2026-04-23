"""
Module xử lý âm thanh
"""
from backend.audio.preprocessing import (
    find_audio_files,
    load_audio,
    normalize_audio,
    pad_or_trim,
    preprocess_audio
)
from backend.audio.processor import (
    extract_features,
    process_audio_files,
    save_features_and_metadata
)

__all__ = [
    'find_audio_files',
    'load_audio',
    'normalize_audio',
    'pad_or_trim',
    'preprocess_audio',
    'extract_features',
    'process_audio_files',
    'save_features_and_metadata'
]
