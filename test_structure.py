"""
Test script để kiểm tra cấu trúc dự án mới
"""

def test_imports():
    """Kiểm tra tất cả imports hoạt động"""
    print("🔍 Kiểm tra imports...")
    
    try:
        from backend.config import TARGET_SAMPLE_RATE, TOP_K
        print("✅ backend.config")
        
        from backend.audio import load_audio, extract_features
        print("✅ backend.audio")
        
        from backend.database import DatabaseManager, DatabaseQueries
        print("✅ backend.database")
        
        from backend.search import VoiceSearchEngine
        print("✅ backend.search")
        
        from utils.helpers import format_size, ensure_directory
        print("✅ utils")
        
        from main.cli import CLI
        print("✅ main")
        
        print("\n✅ Tất cả imports thành công!")
        return True
    except ImportError as e:
        print(f"❌ Lỗi import: {e}")
        return False


def test_directory_structure():
    """Kiểm tra cấu trúc thư mục"""
    print("\n🔍 Kiểm tra cấu trúc thư mục...")
    
    from pathlib import Path
    
    required_dirs = [
        'main',
        'backend',
        'backend/audio',
        'backend/database',
        'backend/search',
        'utils'
    ]

    # Chấp nhận cấu trúc dữ liệu ở root-level hoặc trong data/
    audio_dirs = [Path('raw_audio'), Path('data/raw_audio')]
    processed_dirs = [Path('processed_audio'), Path('data/processed_audio')]

    for option in audio_dirs:
        if option.exists() and option.is_dir():
            required_dirs.append(str(option))
            break
    else:
        print(f"❌ Không tìm thấy thư mục raw_audio (root-level hoặc data/raw_audio)")
        return False

    for option in processed_dirs:
        if option.exists() and option.is_dir():
            required_dirs.append(str(option))
            break
    else:
        print(f"❌ Không tìm thấy thư mục processed_audio (root-level hoặc data/processed_audio)")
        return False

    for dir_name in required_dirs:
        dir_path = Path(dir_name)
        if dir_path.exists() and dir_path.is_dir():
            print(f"✅ {dir_name}/")
        else:
            print(f"❌ {dir_name}/ (không tồn tại)")
            return False
    
    for dir_name in required_dirs:
        dir_path = Path(dir_name)
        if dir_path.exists() and dir_path.is_dir():
            print(f"✅ {dir_name}/")
        else:
            print(f"❌ {dir_name}/ (không tồn tại)")
            return False
    
    print("\n✅ Cấu trúc thư mục hoàn tất!")
    return True


def test_config():
    """Kiểm tra cấu hình"""
    print("\n🔍 Kiểm tra cấu hình...")
    
    from backend.config import (
        TARGET_SAMPLE_RATE, TARGET_DURATION, N_MFCC, N_MELS,
        TOP_K, RAW_AUDIO_DIR, PROCESSED_AUDIO_DIR, DB_FILE
    )
    
    print(f"  Audio Sample Rate: {TARGET_SAMPLE_RATE} Hz")
    print(f"  Audio Duration: {TARGET_DURATION} s")
    print(f"  MFCC Coefficients: {N_MFCC}")
    print(f"  Mel Bins: {N_MELS}")
    print(f"  Top K Results: {TOP_K}")
    print(f"  Raw Audio Dir: {RAW_AUDIO_DIR}")
    print(f"  Processed Audio Dir: {PROCESSED_AUDIO_DIR}")
    print(f"  Database File: {DB_FILE}")
    
    print("\n✅ Cấu hình hợp lệ!")
    return True


if __name__ == '__main__':
    print("=" * 60)
    print("📋 Voice Search System - Structure Test")
    print("=" * 60)
    
    results = []
    results.append(test_directory_structure())
    results.append(test_imports())
    results.append(test_config())
    
    print("\n" + "=" * 60)
    if all(results):
        print("✅ Tất cả kiểm tra thành công!")
        print("🚀 Hệ thống sẵn sàng sử dụng!")
        print("\nCác lệnh tiếp theo:")
        print("  python main.py extract    # Trích xuất đặc trưng")
        print("  python main.py create-db  # Tạo database")
        print("  python main.py search <file>  # Tìm kiếm")
    else:
        print("❌ Có lỗi trong kiểm tra!")
    print("=" * 60)
