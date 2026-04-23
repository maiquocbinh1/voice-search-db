import json
import sqlite3
from pathlib import Path
from typing import List, Tuple
import numpy as np
import librosa
from scipy.spatial.distance import cosine, euclidean
import pandas as pd

PROCESSED_DIR = Path(__file__).resolve().parent.parent / "processed_audio"
DB_FILE = PROCESSED_DIR / "voice_database.db"

# Cấu hình
TARGET_SAMPLE_RATE = 16000
TARGET_DURATION = 3.0
N_MFCC = 13
N_MELS = 64
TOP_K = 5

def load_features_from_db() -> dict:
    """Tải tất cả đặc trưng từ database"""
    conn = sqlite3.connect(str(DB_FILE))
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM features')
    rows = cursor.fetchall()
    
    features = {}
    for row in rows:
        file_id = row[0]
        features[file_id] = {
            'mfcc_mean': json.loads(row[1]),
            'mfcc_std': json.loads(row[2]),
            'mel_spec_mean': json.loads(row[3]),
            'mel_spec_std': json.loads(row[4]),
            'chroma_mean': json.loads(row[5]),
            'chroma_std': json.loads(row[6]),
            'spectral_centroid_mean': row[7],
            'spectral_centroid_std': row[8],
            'spectral_contrast_mean': json.loads(row[9]),
            'spectral_contrast_std': json.loads(row[10]),
            'zcr_mean': row[11],
            'zcr_std': row[12],
            'energy': row[13],
            'rms_mean': row[14],
            'rms_std': row[15]
        }
    
    conn.close()
    return features

def load_metadata_from_db() -> pd.DataFrame:
    """Tải metadata từ database"""
    conn = sqlite3.connect(str(DB_FILE))
    df = pd.read_sql_query('SELECT * FROM metadata', conn)
    conn.close()
    return df

def extract_features_from_audio(audio: np.ndarray, sr: int) -> dict:
    """Trích đặc trưng từ file audio đầu vào"""
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

def features_to_vector(features: dict) -> np.ndarray:
    """Chuyển đặc trưng thành vector để so sánh"""
    vector = []
    
    # Lấy các giá trị scalar
    vector.append(features['spectral_centroid_mean'])
    vector.append(features['spectral_centroid_std'])
    vector.append(features['zcr_mean'])
    vector.append(features['zcr_std'])
    vector.append(features['energy'])
    vector.append(features['rms_mean'])
    vector.append(features['rms_std'])
    
    # Mảng MFCC
    vector.extend(features['mfcc_mean'])
    vector.extend(features['mfcc_std'])
    
    # Mel spec
    vector.extend(features['mel_spec_mean'])
    vector.extend(features['mel_spec_std'])
    
    # Chroma
    vector.extend(features['chroma_mean'])
    vector.extend(features['chroma_std'])
    
    # Spectral contrast
    vector.extend(features['spectral_contrast_mean'])
    vector.extend(features['spectral_contrast_std'])
    
    return np.array(vector)

def search_similar_voices(query_audio_path: str, metric: str = 'cosine') -> List[Tuple[str, float]]:
    """
    Tìm các file giọng nói giống nhất với file đầu vào
    
    Args:
        query_audio_path: Đường dẫn đến file audio đầu vào
        metric: 'cosine' hoặc 'euclidean'
    
    Returns:
        Danh sách (file_id, similarity_score)
    """
    # Tải file đầu vào
    query_audio, sr = librosa.load(query_audio_path, sr=TARGET_SAMPLE_RATE, mono=True)
    
    # Chuẩn hóa
    max_val = np.max(np.abs(query_audio))
    if max_val > 0:
        query_audio = query_audio / max_val
    
    # Pad/trim
    target_samples = int(TARGET_SAMPLE_RATE * TARGET_DURATION)
    if len(query_audio) > target_samples:
        query_audio = query_audio[:target_samples]
    elif len(query_audio) < target_samples:
        query_audio = np.pad(query_audio, (0, target_samples - len(query_audio)), mode='constant')
    
    # Trích đặc trưng
    query_features = extract_features_from_audio(query_audio, TARGET_SAMPLE_RATE)
    query_vector = features_to_vector(query_features)
    
    # Chuẩn hóa vector
    query_vector = query_vector / (np.linalg.norm(query_vector) + 1e-8)
    
    # Tải tất cả đặc trưng database
    all_features = load_features_from_db()
    
    # So sánh với tất cả file
    distances = []
    for file_id, features in all_features.items():
        db_vector = features_to_vector(features)
        # Chuẩn hóa
        db_vector = db_vector / (np.linalg.norm(db_vector) + 1e-8)
        
        if metric == 'cosine':
            distance = cosine(query_vector, db_vector)
        else:  # euclidean
            distance = euclidean(query_vector, db_vector)
        
        distances.append((file_id, distance))
    
    # Sắp xếp theo khoảng cách (nhỏ nhất = giống nhất)
    distances.sort(key=lambda x: x[1])
    
    # Trả về top K
    results = []
    for file_id, distance in distances[:TOP_K]:
        # Chuyển distance thành similarity score (0-1)
        if metric == 'cosine':
            similarity = 1 - distance  # Cosine distance: 0-2 → similarity: 1 to -1
        else:
            similarity = 1 / (1 + distance)  # Euclidean → normalize
        results.append((file_id, similarity))
    
    return results

def main():
    """Ví dụ sử dụng hệ thống tìm kiếm"""
    import sys
    
    if len(sys.argv) < 2:
        print("Cách sử dụng: python search_voices.py <query_audio_path>")
        print("\nVí dụ: python search_voices.py raw_audio/male_000.wav")
        return
    
    query_path = sys.argv[1]
    
    if not Path(query_path).exists():
        print(f"Lỗi: File {query_path} không tồn tại")
        return
    
    print(f"🔍 Tìm kiếm giọng nói tương tự: {query_path}")
    print("-" * 60)
    
    results = search_similar_voices(query_path)
    
    metadata = load_metadata_from_db()
    metadata_dict = {row['file_id']: row for _, row in metadata.iterrows()}
    
    print(f"{'Rank':<5} {'File ID':<20} {'Similarity':<15} {'Source':<30}")
    print("-" * 60)
    
    for rank, (file_id, similarity) in enumerate(results, 1):
        source = metadata_dict.get(file_id, {}).get('source_path', 'N/A')
        print(f"{rank:<5} {file_id:<20} {similarity:.4f}         {source:<30}")

if __name__ == "__main__":
    main()
