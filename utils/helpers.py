"""
Các hàm tiện ích chung
"""
from pathlib import Path
from typing import List

import pandas as pd


def ensure_directory(path: Path) -> Path:
    """
    Tạo thư mục nếu chưa tồn tại
    
    Args:
        path: Đường dẫn thư mục
        
    Returns:
        Path đã được tạo
    """
    path.mkdir(parents=True, exist_ok=True)
    return path


def get_file_info(file_path: str | Path) -> dict:
    """
    Lấy thông tin file
    
    Args:
        file_path: Đường dẫn file
        
    Returns:
        Dictionary chứa thông tin file
    """
    path = Path(file_path)
    
    return {
        'name': path.name,
        'stem': path.stem,
        'suffix': path.suffix,
        'size_bytes': path.stat().st_size if path.exists() else 0,
        'exists': path.exists(),
        'is_file': path.is_file(),
        'is_dir': path.is_dir(),
    }


def format_duration(seconds: float) -> str:
    """
    Format thời gian thành chuỗi
    
    Args:
        seconds: Thời gian (giây)
        
    Returns:
        Chuỗi định dạng "HH:MM:SS"
    """
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    
    return f"{hours:02d}:{minutes:02d}:{secs:02d}"


def format_size(size_bytes: int) -> str:
    """
    Format kích thước file thành chuỗi dễ đọc
    
    Args:
        size_bytes: Kích thước (bytes)
        
    Returns:
        Chuỗi định dạng "X.XX MB"
    """
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024
    
    return f"{size_bytes:.2f} TB"


def print_table(data: List[dict], headers: List[str] | None = None) -> None:
    """
    In bảng đẹp
    
    Args:
        data: Danh sách dictionary
        headers: Danh sách header (nếu None dùng key của dict)
    """
    if not data:
        print("Không có dữ liệu")
        return
    
    df = pd.DataFrame(data)
    if headers:
        df = df[headers]
    
    print(df.to_string(index=False))


def load_json_file(file_path: str | Path) -> dict:
    """
    Tải file JSON
    
    Args:
        file_path: Đường dẫn file
        
    Returns:
        Dictionary
    """
    import json
    
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def save_json_file(data: dict, file_path: str | Path, indent: int = 2) -> None:
    """
    Lưu file JSON
    
    Args:
        data: Dictionary để lưu
        file_path: Đường dẫn file
        indent: Khoảng cách indent
    """
    import json
    
    file_path = Path(file_path)
    file_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=indent, ensure_ascii=False)
