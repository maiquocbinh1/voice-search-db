"""
Command-line interface cho ứng dụng Voice Search
"""
import sys
from pathlib import Path
from typing import Optional

from backend.audio.processor import process_audio_files, save_features_and_metadata
from backend.database import DatabaseManager
from backend.search.voice_search import VoiceSearchEngine
from backend.config import RAW_AUDIO_DIR, PROCESSED_AUDIO_DIR
from utils.helpers import print_table, format_size

try:
    from main.web import run_web
    WEB_AVAILABLE = True
except ImportError:
    WEB_AVAILABLE = False


class CLI:
    """Command-line interface"""
    
    def __init__(self):
        self.db_manager = DatabaseManager()
        self.search_engine = VoiceSearchEngine()
    
    def extract_features_command(self) -> None:
        """Trích xuất đặc trưng từ file audio"""
        print("🎵 Bắt đầu trích xuất đặc trưng từ audio...")
        print(f"📁 Đầu vào: {RAW_AUDIO_DIR}")
        print(f"📁 Đầu ra:  {PROCESSED_AUDIO_DIR}")
        
        # Xử lý
        all_features, metadata_list = process_audio_files(RAW_AUDIO_DIR, PROCESSED_AUDIO_DIR)
        
        if not all_features:
            print("❌ Không xử lý được file nào")
            return
        
        # Lưu
        save_features_and_metadata(all_features, metadata_list)
    
    def create_database_command(self) -> None:
        """Tạo cơ sở dữ liệu"""
        print("🏗️  Tạo cơ sở dữ liệu...")
        
        try:
            self.db_manager.create_tables()
            self.db_manager.import_metadata()
            self.db_manager.import_features()
            self.db_manager.get_statistics()
            print("\n✅ Tạo database hoàn thành!")
        except Exception as e:
            print(f"❌ Lỗi: {e}")
    
    def search_command(self, query_path: str) -> None:
        """Tìm kiếm giọng nói tương tự"""
        query_path = Path(query_path)
        
        if not query_path.exists():
            print(f"❌ File không tồn tại: {query_path}")
            return
        
        print(f"🔍 Tìm kiếm giọng nói tương tự: {query_path}")
        print("-" * 70)
        
        try:
            results = self.search_engine.search(str(query_path))
            
            # Lấy metadata
            from backend.database.queries import DatabaseQueries
            db_queries = DatabaseQueries()
            metadata_df = db_queries.load_metadata_from_db()
            metadata_dict = {row['file_id']: row for _, row in metadata_df.iterrows()}
            
            # In kết quả
            print(f"{'Rank':<6} {'File ID':<25} {'Similarity':<15} {'Source':<30}")
            print("-" * 70)
            
            for rank, (file_id, similarity) in enumerate(results, 1):
                source = metadata_dict.get(file_id, {}).get('source_path', 'N/A')
                print(f"{rank:<6} {file_id:<25} {similarity:.4f}         {source:<30}")
            
        except Exception as e:
            print(f"❌ Lỗi tìm kiếm: {e}")
    
    def info_command(self) -> None:
        """Hiển thị thông tin database"""
        try:
            from backend.database.queries import DatabaseQueries
            db_queries = DatabaseQueries()
            
            count = db_queries.count_files()
            print(f"\n📊 Thông tin Database:")
            print(f"  - Tổng file:  {count}")
            
            status = self.db_manager.verify_integrity()
            print(f"  - Status:     {'✅ OK' if status['is_valid'] else '❌ Error'}")
            
        except Exception as e:
            print(f"❌ Lỗi: {e}")
    
    def show_help(self) -> None:
        """Hiển thị trợ giúp"""
        help_text = """
╔════════════════════════════════════════════════════════════╗
║           Voice Search System - Command Line Interface      ║
╚════════════════════════════════════════════════════════════╝

📋 Lệnh có sẵn:

1. Trích xuất đặc trưng âm thanh:
   python main.py extract
   
   → Xử lý tất cả file audio trong raw_audio/
   → Trích xuất 15 loại đặc trưng
   → Lưu kết quả vào processed_audio/

2. Tạo cơ sở dữ liệu:
   python main.py create-db
   
   → Tạo cấu trúc SQLite database
   → Import metadata và features
   → Kiểm tra tính toàn vẹn dữ liệu

3. Tìm kiếm giọng nói:
   python main.py search <đường_dẫn_file_audio>
   
   Ví dụ:
   python main.py search raw_audio/male_000.wav
   python main.py search ./query_voice.wav
   
   → Tìm top-5 giọng nói giống nhất
   → Hiển thị similarity score

4. Giao diện web demo:
   python main.py web
   
   → Mở trình duyệt tại http://127.0.0.1:5000
   → Chọn file dữ liệu hoặc upload file truy vấn mới

5. Xem thông tin:
   python main.py info
   
   → Hiển thị thống kê database
   → Kiểm tra status

6. Trợ giúp:
   python main.py help
   python main.py -h / --help

📂 Cấu trúc thư mục:
   - backend/        → Lõi ứng dụng
   - main/           → CLI & web interface
   - utils/          → Hàm tiện ích
   - raw_audio/      → File âm thanh thô
   - processed_audio/ → Kết quả xử lý & database

🔧 Quy trình đầy đủ:
   1. Đặt file audio vào raw_audio/
   2. python main.py extract
   3. python main.py create-db
   4. python main.py search <file>
   5. python main.py web
"""
        print(help_text)


def main():
    """Main entry point"""
    cli = CLI()
    
    if len(sys.argv) < 2:
        cli.show_help()
        return
    
    command = sys.argv[1].lower()
    
    if command in ['help', '-h', '--help']:
        cli.show_help()
    elif command == 'extract':
        cli.extract_features_command()
    elif command == 'create-db':
        cli.create_database_command()
    elif command == 'search':
        if len(sys.argv) < 3:
            print("❌ Cần cung cấp đường dẫn file audio")
            print("Cách sử dụng: python main.py search <đường_dẫn_file>")
            return
        cli.search_command(sys.argv[2])
    elif command == 'web':
        if not WEB_AVAILABLE:
            print('❌ Lỗi: Flask chưa được cài đặt. Chạy `pip install flask` để sử dụng giao diện web.')
            return
        run_web()
    elif command == 'info':
        cli.info_command()
    else:
        print(f"❌ Lệnh không hợp lệ: {command}")
        print("\nGõ 'python main.py help' để xem hướng dẫn")


if __name__ == '__main__':
    main()
