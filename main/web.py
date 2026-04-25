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
from backend.config import RAW_AUDIO_DIR, PROCESSED_AUDIO_DIR
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
  <title>Voice Search Demo</title>
  <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
  <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
  <style>
    body { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh; }
    .hero { background: rgba(255,255,255,0.1); backdrop-filter: blur(10px); border-radius: 15px; padding: 2rem; margin-bottom: 2rem; color: white; }
    .card { border: none; border-radius: 15px; box-shadow: 0 10px 30px rgba(0,0,0,0.2); }
    .btn-primary { background: linear-gradient(45deg, #667eea, #764ba2); border: none; }
    .btn-primary:hover { background: linear-gradient(45deg, #5a6fd8, #6a4190); }
    .form-control, .form-select { border-radius: 10px; }
    .table { border-radius: 10px; overflow: hidden; }
    .audio-player { width: 100%; max-width: 300px; }
    .metric-card { background: rgba(255,255,255,0.9); border-radius: 10px; padding: 1rem; text-align: center; }
  </style>
</head>
<body>
  <div class="container py-5">
    <div class="hero text-center mb-5">
      <h1 class="display-4"><i class="fas fa-microphone-alt"></i> Voice Search Demo</h1>
      <p class="lead">Tìm kiếm giọng nói tương tự bằng công nghệ AI</p>
    </div>

    <div class="row">
      <div class="col-lg-8 mx-auto">
        <div class="card p-4 mb-4">
          <h2 class="mb-4"><i class="fas fa-search"></i> Tìm kiếm giọng nói</h2>
          <form method="post" enctype="multipart/form-data">
            <div class="mb-3">
              <label for="dataset_file" class="form-label"><i class="fas fa-folder-open"></i> Chọn file trong dữ liệu hiện có</label>
              <select class="form-select" id="dataset_file" name="dataset_file">
                <option value="">-- Chọn file giọng đầu vào --</option>
                {% for filename in dataset_files %}
                <option value="{{ filename }}" {% if filename == selected_dataset_file %}selected{% endif %}>{{ filename }}</option>
                {% endfor %}
              </select>
            </div>

            <div class="mb-3">
              <label for="upload_file" class="form-label"><i class="fas fa-upload"></i> Hoặc tải file truy vấn mới</label>
              <input class="form-control" id="upload_file" type="file" name="upload_file" accept=".wav,.flac,.mp3,.ogg">
            </div>

            <div class="mb-3">
              <label for="metric" class="form-label"><i class="fas fa-calculator"></i> Khoảng cách so sánh</label>
              <select class="form-select" id="metric" name="metric">
                <option value="cosine" {% if metric == 'cosine' %}selected{% endif %}>Cosine Similarity</option>
                <option value="euclidean" {% if metric == 'euclidean' %}selected{% endif %}>Euclidean Distance</option>
              </select>
            </div>

            <button type="submit" class="btn btn-primary btn-lg w-100"><i class="fas fa-search"></i> Tìm kiếm</button>
          </form>
          <p class="text-muted mt-3"><small>Bạn có thể chọn file trong bộ dữ liệu hoặc tải lên file âm thanh mới. Nếu cả hai đều có, hệ thống ưu tiên file tải lên.</small></p>
          {% if error_message %}
          <div class="alert alert-danger mt-3"><i class="fas fa-exclamation-triangle"></i> {{ error_message }}</div>
          {% endif %}
        </div>

        <div class="row mb-4">
          <div class="col-md-4">
            <div class="metric-card">
              <i class="fas fa-database fa-2x text-primary mb-2"></i>
              <h5>Dataset Files</h5>
              <span class="badge bg-primary fs-6">{{ dataset_count }}</span>
            </div>
          </div>
          <div class="col-md-4">
            <div class="metric-card">
              <i class="fas fa-server fa-2x text-success mb-2"></i>
              <h5>Database</h5>
              <span class="badge {% if db_status == 'OK' %}bg-success{% else %}bg-danger{% endif %} fs-6">{{ db_status }}</span>
            </div>
          </div>
          <div class="col-md-4">
            <div class="metric-card">
              <i class="fas fa-music fa-2x text-info mb-2"></i>
              <h5>Truy vấn hiện tại</h5>
              <small>{{ query_label }}</small>
            </div>
          </div>
        </div>

        {% if query_audio %}
        <div class="card p-3 mb-4">
          <h5><i class="fas fa-play-circle"></i> File truy vấn</h5>
          <audio controls class="audio-player">
            <source src="{{ query_audio }}" type="audio/wav">
            Trình duyệt của bạn không hỗ trợ audio.
          </audio>
        </div>
        {% endif %}

        {% if results %}
        <div class="card p-4">
          <h2 class="mb-4"><i class="fas fa-list-ol"></i> Kết quả Top {{ results|length }}</h2>
          <div class="table-responsive">
            <table class="table table-hover">
              <thead class="table-dark">
                <tr>
                  <th>#</th>
                  <th>File ID</th>
                  <th>Độ tương tự</th>
                  <th>Tên file</th>
                  <th>Nghe</th>
                </tr>
              </thead>
              <tbody>
                {% for row in results %}
                <tr>
                  <td>{{ loop.index }}</td>
                  <td>{{ row.file_id }}</td>
                  <td><span class="badge bg-info">{{ row.similarity }}</span></td>
                  <td>{{ row.source_path }}</td>
                  <td>
                    <audio controls class="audio-player">
                      <source src="{{ url_for('serve_audio', filename=row.source_path) }}" type="audio/wav">
                      Trình duyệt của bạn không hỗ trợ audio.
                    </audio>
                  </td>
                </tr>
                {% endfor %}
              </tbody>
            </table>
          </div>
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
    return [p.name for p in sorted(find_audio_files(RAW_AUDIO_DIR))]


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
        metric = 'cosine'
        query_label = 'Chưa chọn file truy vấn'
        query_audio = None

        if request.method == 'POST':
            selected_dataset_file = request.form.get('dataset_file', '')
            metric = request.form.get('metric', 'cosine')
            upload_file = request.files.get('upload_file')
            query_path = None

            if upload_file and upload_file.filename:
                if not allowed_file(upload_file.filename):
                    error_message = 'File không hợp lệ. Vui lòng dùng .wav, .flac, .mp3, hoặc .ogg.'
                else:
                    safe_name = f"{uuid4().hex}_{secure_filename(upload_file.filename)}"
                    saved_path = UPLOAD_FOLDER / safe_name
                    upload_file.save(saved_path)
                    query_path = saved_path
                    query_label = f'Tải lên: {upload_file.filename}'
                    query_audio = url_for('serve_upload', filename=safe_name)
            elif selected_dataset_file:
                query_path = RAW_AUDIO_DIR / Path(selected_dataset_file).name
                query_label = f'Dữ liệu: {selected_dataset_file}'
                query_audio = url_for('serve_audio', filename=selected_dataset_file)

            if query_path and not error_message:
                if not query_path.exists():
                    error_message = 'Không tìm thấy file truy vấn.'
                else:
                    results = build_results(query_path, metric)
                    if not results:
                        error_message = 'Không có kết quả tìm kiếm.'

        db_status = 'OK' if Path(PROCESSED_AUDIO_DIR / 'voice_database.db').exists() else 'Missing'
        return render_template_string(
            PAGE_TEMPLATE,
            dataset_files=dataset_files,
            dataset_count=len(dataset_files),
            db_status=db_status,
            error_message=error_message,
            results=results,
            selected_dataset_file=selected_dataset_file,
            metric=metric,
            query_label=query_label,
            query_audio=query_audio,
        )

    @app.route('/audio/<path:filename>')
    def serve_audio(filename: str):
        return send_from_directory(RAW_AUDIO_DIR, filename, as_attachment=False)

    @app.route('/uploads/<path:filename>')
    def serve_upload(filename: str):
        return send_from_directory(UPLOAD_FOLDER, filename, as_attachment=False)

    return app


def run_web(host: str = '127.0.0.1', port: int = 5000) -> None:
    app = create_app()
    print(f'✅ Web demo khởi động tại http://{host}:{port}')
    print('⏳ Nếu bạn chưa cài Flask, hãy chạy: pip install flask')
    app.run(host=host, port=port)
