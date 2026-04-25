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
  <style>
    body { font-family: Arial, sans-serif; margin: 0; padding: 0; background: #f5f5f9; color: #222; }
    header { background: #0b3d91; color: white; padding: 18px 28px; }
    .container { max-width: 960px; margin: 24px auto; padding: 0 18px; }
    .panel { background: white; border-radius: 12px; box-shadow: 0 10px 28px rgba(0,0,0,0.08); padding: 22px; margin-bottom: 24px; }
    h1 { margin-top: 0; }
    label { font-weight: 700; display: block; margin-top: 16px; }
    select, input[type=file], button { width: 100%; font-size: 1rem; padding: 10px 12px; border-radius: 8px; border: 1px solid #d1d5db; }
    button { background: #0b3d91; color: white; border: none; cursor: pointer; }
    button:hover { background: #0d3f9c; }
    table { width: 100%; border-collapse: collapse; margin-top: 20px; }
    th, td { padding: 12px 10px; text-align: left; border-bottom: 1px solid #e5e7eb; }
    th { background: #eef2ff; }
    .note { color: #6b7280; font-size: 0.95rem; margin-top: 8px; }
    .error { color: #b91c1c; font-weight: 700; }
    .audio-row audio { width: 100%; }
    .stats { display: flex; gap: 20px; flex-wrap: wrap; margin-top: 16px; }
    .metric { background: #eef2ff; padding: 14px 18px; border-radius: 12px; flex: 1; min-width: 180px; }
  </style>
</head>
<body>
  <header>
    <h1>Voice Search Demo</h1>
    <p>Chọn một file giọng nam hoặc tải file truy vấn mới để tìm 5 file tương tự nhất.</p>
  </header>
  <div class="container">
    <div class="panel">
      <form method="post" enctype="multipart/form-data">
        <label for="dataset_file">1. Chọn file trong dữ liệu hiện có</label>
        <select id="dataset_file" name="dataset_file">
          <option value="">-- Chọn file giọng đầu vào --</option>
          {% for filename in dataset_files %}
          <option value="{{ filename }}" {% if filename == selected_dataset_file %}selected{% endif %}>{{ filename }}</option>
          {% endfor %}
        </select>

        <label for="upload_file">Hoặc tải file truy vấn mới</label>
        <input id="upload_file" type="file" name="upload_file" accept=".wav,.flac,.mp3,.ogg">

        <label for="metric">Khoảng cách so sánh</label>
        <select id="metric" name="metric">
          <option value="cosine" {% if metric == 'cosine' %}selected{% endif %}>Cosine Similarity</option>
          <option value="euclidean" {% if metric == 'euclidean' %}selected{% endif %}>Euclidean Distance</option>
        </select>

        <button type="submit">Tìm kiếm</button>
      </form>
      <p class="note">Bạn có thể chọn file trong bộ dữ liệu hoặc tải lên file âm thanh mới. Nếu cả hai đều có, hệ thống ưu tiên file tải lên.</p>
      {% if error_message %}
      <p class="error">{{ error_message }}</p>
      {% endif %}
    </div>

    <div class="panel stats">
      <div class="metric">
        <strong>Dataset Files</strong>
        <div>{{ dataset_count }}</div>
      </div>
      <div class="metric">
        <strong>Database</strong>
        <div>{{ db_status }}</div>
      </div>
      <div class="metric">
        <strong>Hiện tại</strong>
        <div>{{ query_label }}</div>
      </div>
    </div>

    {% if results %}
    <div class="panel">
      <h2>Kết quả Top {{ results|length }}</h2>
      <table>
        <thead>
          <tr>
            <th>#</th>
            <th>File ID</th>
            <th>Similarity</th>
            <th>Tên nguồn</th>
          </tr>
        </thead>
        <tbody>
          {% for row in results %}
          <tr>
            <td>{{ loop.index }}</td>
            <td>{{ row.file_id }}</td>
            <td>{{ row.similarity }}</td>
            <td>{{ row.source_path }}</td>
          </tr>
          {% endfor %}
        </tbody>
      </table>
    </div>
    {% endif %}
  </div>
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
            elif selected_dataset_file:
                query_path = RAW_AUDIO_DIR / Path(selected_dataset_file).name
                query_label = f'Dữ liệu: {selected_dataset_file}'

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
