"""Web interface for Voice Search demo."""
from pathlib import Path
from uuid import uuid4

try:
    from flask import Flask, render_template_string, request, send_from_directory, url_for
    from werkzeug.utils import secure_filename
except ImportError as exc:
    raise ImportError(
        "Flask is required to run the web demo. Install it with `pip install flask`."
    ) from exc

from backend.audio.preprocessing import find_audio_files
from backend.config import AUDIO_DIR, PROCESSED_AUDIO_DIR
from backend.database.queries import DatabaseQueries
from backend.search.voice_search import VoiceSearchEngine

UPLOAD_FOLDER = PROCESSED_AUDIO_DIR / "web_uploads"
UPLOAD_FOLDER.mkdir(parents=True, exist_ok=True)
ALLOWED_EXTENSIONS = {".wav", ".flac", ".mp3", ".ogg"}

PAGE_TEMPLATE = """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Tìm Kiếm Giọng Nói</title>
  <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
  <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
  <style>
    body { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
    .hero { background: rgba(255,255,255,0.1); backdrop-filter: blur(10px); border-radius: 20px; padding: 2.5rem; margin-bottom: 2rem; color: white; text-align: center; }
    .hero h1 { font-size: 2.5rem; font-weight: bold; margin-bottom: 0.5rem; }
    .hero p { font-size: 1.1rem; opacity: 0.95; }
    .card { border: none; border-radius: 20px; box-shadow: 0 15px 40px rgba(0,0,0,0.2); transition: transform 0.3s; }
    .card:hover { transform: translateY(-5px); }
    .btn-primary { background: linear-gradient(45deg, #667eea, #764ba2); border: none; font-weight: 600; font-size: 1.1rem; padding: 0.8rem 2rem; }
    .btn-primary:hover { background: linear-gradient(45deg, #5a6fd8, #6a4190); transform: scale(1.02); }
    .form-control, .form-select { border-radius: 12px; border: 2px solid #e9ecef; font-size: 1rem; padding: 0.7rem 1rem; transition: all 0.3s; }
    .form-control:focus, .form-select:focus { border-color: #667eea; box-shadow: 0 0 0 0.2rem rgba(102, 126, 234, 0.25); }
    .form-label { font-weight: 600; font-size: 1.05rem; color: #333; margin-bottom: 0.7rem; }
    .step-number { display: inline-block; width: 40px; height: 40px; background: linear-gradient(45deg, #667eea, #764ba2); color: white; border-radius: 50%; text-align: center; line-height: 40px; font-weight: bold; margin-right: 0.5rem; }
    .step-title { display: inline-block; font-weight: 600; font-size: 1.05rem; }
    .table { border-radius: 12px; overflow: hidden; }
    .table th { background: linear-gradient(45deg, #667eea, #764ba2); color: white; font-weight: 600; border: none; }
    .table td { vertical-align: middle; border-color: #e9ecef; }
    .audio-player { width: 100%; max-width: 280px; border-radius: 8px; }
    .similarity-badge { font-size: 1rem; padding: 0.5rem 1rem; border-radius: 8px; background: linear-gradient(45deg, #667eea, #764ba2); }
    .result-card { background: rgba(255,255,255,0.95); border-radius: 15px; padding: 1.5rem; margin-bottom: 1.2rem; border-left: 5px solid #667eea; transition: all 0.3s; }
    .result-card:hover { box-shadow: 0 8px 25px rgba(0,0,0,0.1); }
    .rank-badge { width: 50px; height: 50px; background: linear-gradient(45deg, #667eea, #764ba2); color: white; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: bold; font-size: 1.3rem; }
    .guide-text { color: #6c757d; font-size: 0.95rem; margin-top: 0.5rem; font-style: italic; }
    .success-message { background: #d4edda; border: 2px solid #28a745; color: #155724; padding: 1rem; border-radius: 10px; margin-bottom: 1.5rem; }
    .error-message { background: #f8d7da; border: 2px solid #dc3545; color: #721c24; padding: 1rem; border-radius: 10px; margin-bottom: 1.5rem; }
  </style>
</head>
<body>
  <div class="container py-5">
    <div class="hero">
      <h1><i class="fas fa-microphone-alt"></i> Tìm Kiếm Giọng Nói</h1>
      <p>Hãy chọn hoặc tải lên một file âm thanh để tìm những giọng nói tương tự nhất từ bộ dữ liệu</p>
    </div>

    <div class="row">
      <div class="col-lg-9 mx-auto">
        <!-- Form Section -->
        <div class="card p-5 mb-4">
          <form method="post" enctype="multipart/form-data">
            <!-- Step 1: Choose Sample -->
            <div class="mb-4">
              <div><span class="step-number">1</span><span class="step-title">Chọn một giọng nói mẫu</span></div>
              <div class="guide-text">Chọn từ những giọng nói có sẵn trong hệ thống</div>
              <select class="form-select mt-2" id="dataset_file" name="dataset_file">
                <option value="">-- Chọn file giọng nói --</option>
                {% for filename in dataset_files %}
                <option value="{{ filename }}" {% if filename == selected_dataset_file %}selected{% endif %}>{{ filename }}</option>
                {% endfor %}
              </select>
            </div>

            <div class="text-center my-3">
              <p class="text-muted"><strong>Hoặc</strong></p>
            </div>

            <!-- Step 2: Upload -->
            <div class="mb-4">
              <div><span class="step-number">2</span><span class="step-title">Tải lên giọng nói của bạn</span></div>
              <div class="guide-text">Chỉ hỗ trợ các file âm thanh: WAV, FLAC, MP3, OGG</div>
              <input class="form-control mt-2" id="upload_file" type="file" name="upload_file" accept=".wav,.flac,.mp3,.ogg">
            </div>

            <!-- Hidden field for metric (default to cosine) -->
            <input type="hidden" name="metric" value="cosine">

            <!-- Submit Button -->
            <button type="submit" class="btn btn-primary btn-lg w-100 mt-4">
              <i class="fas fa-search"></i> Tìm Kiếm Ngay
            </button>
          </form>

          <p class="guide-text mt-4 text-center">Nếu bạn chọn cả hai, hệ thống sẽ ưu tiên file tải lên</p>
          
          {% if error_message %}
          <div class="error-message mt-4">
            <i class="fas fa-exclamation-circle"></i> <strong>Lỗi:</strong> {{ error_message }}
          </div>
          {% endif %}
        </div>

        <!-- Query Audio Display -->
        {% if query_audio %}
        <div class="card p-4 mb-4">
          <h5 class="mb-3"><i class="fas fa-play-circle"></i> <strong>Giọng nói bạn đã chọn</strong></h5>
          <audio controls class="audio-player">
            <source src="{{ query_audio }}" type="audio/wav">
            Trình duyệt của bạn không hỗ trợ audio.
          </audio>
        </div>
        {% endif %}

        <!-- Results Section -->
        {% if results %}
        <div class="card p-5">
          <h2 class="mb-4"><i class="fas fa-trophy"></i> <strong>Kết Quả Tìm Kiếm</strong></h2>
          <p class="text-muted mb-4">Đây là {{ results|length }} giọng nói tương tự nhất với file bạn chọn</p>

          <div class="row">
            {% for row in results %}
            <div class="col-12">
              <div class="result-card">
                <div class="row align-items-center">
                  <div class="col-auto">
                    <div class="rank-badge">{{ loop.index }}</div>
                  </div>
                  <div class="col">
                    <div class="mb-2">
                      <strong>{{ row.source_path }}</strong>
                      <span class="similarity-badge ms-2">Độ tương tự: {{ row.similarity }}</span>
                    </div>
                    <audio controls class="audio-player mt-2">
                      <source src="{{ url_for('serve_audio', filename=row.source_path) }}" type="audio/wav">
                      Trình duyệt của bạn không hỗ trợ audio.
                    </audio>
                  </div>
                </div>
              </div>
            </div>
            {% endfor %}
          </div>
        </div>
        {% endif %}

        <!-- Empty State -->
        {% if not query_audio and not results %}
        <div class="card p-5 text-center">
          <i class="fas fa-lightbulb fa-3x text-warning mb-3"></i>
          <h4>Bắt Đầu Tìm Kiếm</h4>
          <p class="text-muted">Chọn hoặc tải lên một file giọng nói ở trên để bắt đầu tìm kiếm những giọng nói tương tự</p>
        </div>
        {% endif %}
      </div>
    </div>
  </div>
  <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>"""


def allowed_file(filename: str) -> bool:
    return Path(filename).suffix.lower() in ALLOWED_EXTENSIONS


def get_dataset_files() -> list[str]:
    return [p.name for p in sorted(find_audio_files(AUDIO_DIR))]


def build_results(query_path: Path, metric: str, top_k: int = 5) -> dict:
    engine = VoiceSearchEngine(distance_metric=metric, top_k=top_k)
    results = engine.search(query_path)

    metadata_df = DatabaseQueries().load_metadata_from_db()
    metadata_dict = {row['file_id']: row for _, row in metadata_df.iterrows()}

    enriched = []
    for file_id, score in results:
        row = metadata_dict.get(file_id, {})
        enriched.append({
            'file_id': file_id,
            'similarity': f"{score:.4f}",
            'source_path': row.get('source_path', 'N/A')
        })

    return enriched


def create_app() -> 'Flask':
    app = Flask(__name__)

    @app.route('/', methods=['GET', 'POST'])
    def index():
        dataset_files = get_dataset_files()
        error_message = ''
        results = []
        selected_dataset_file = ''
        query_label = 'Chưa chọn file'
        query_audio = None

        if request.method == 'POST':
            selected_dataset_file = request.form.get('dataset_file', '')
            upload_file = request.files.get('upload_file')
            query_path = None

            if upload_file and upload_file.filename:
                if not allowed_file(upload_file.filename):
                    error_message = 'File không hợp lệ. Chỉ hỗ trợ: WAV, FLAC, MP3, OGG'
                else:
                    safe_name = f"{uuid4().hex}_{secure_filename(upload_file.filename)}"
                    saved_path = UPLOAD_FOLDER / safe_name
                    upload_file.save(saved_path)
                    query_path = saved_path
                    query_label = f'{upload_file.filename}'
                    query_audio = url_for('serve_upload', filename=safe_name)
            elif selected_dataset_file:
                query_path = AUDIO_DIR / Path(selected_dataset_file).name
                query_label = f'{selected_dataset_file}'
                query_audio = url_for('serve_audio', filename=selected_dataset_file)

            if query_path and not error_message:
                if not query_path.exists():
                    error_message = 'Không tìm thấy file. Vui lòng thử lại.'
                else:
                    results = build_results(query_path, 'cosine')
                    if not results:
                        error_message = 'Không có kết quả tìm kiếm. Vui lòng thử file khác.'

        return render_template_string(
            PAGE_TEMPLATE,
            dataset_files=dataset_files,
            error_message=error_message,
            results=results,
            selected_dataset_file=selected_dataset_file,
            query_label=query_label,
            query_audio=query_audio,
        )

    @app.route('/audio/<path:filename>')
    def serve_audio(filename: str):
        return send_from_directory(AUDIO_DIR, filename, as_attachment=False)

    @app.route('/uploads/<path:filename>')
    def serve_upload(filename: str):
        return send_from_directory(UPLOAD_FOLDER, filename, as_attachment=False)

    return app


def run_web(host: str = '127.0.0.1', port: int = 5000) -> None:
    app = create_app()
    print(f' Web demo khởi động tại http://{host}:{port}')
    print(' Nếu bạn chưa cài Flask, hãy chạy: pip install flask')
    app.run(host=host, port=port)
