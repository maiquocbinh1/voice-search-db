# 🚀 GitHub Push Guide - Voice Search Project

## 📋 Tổng Quan Branch

Dự án đã được tổ chức thành các branch Git có cấu trúc:

```
main (branch chính)
└── feature/restructure-project (branch tổng hợp)
    ├── feature/backend-config
    ├── feature/backend-audio
    ├── feature/backend-database
    ├── feature/backend-search
    ├── feature/main-cli
    ├── feature/utils-helpers
    └── feature/documentation
```

## 🎯 Cách Push Lên GitHub

### Bước 1: Tạo Repository trên GitHub
```bash
# Truy cập https://github.com/new
# Tạo repo: voice-search-project
# KHÔNG check "Add a README file"
```

### Bước 2: Push Branch Chính
```bash
# Thêm remote origin
git remote add origin https://github.com/YOUR_USERNAME/voice-search-project.git

# Push branch main
git push -u origin main
```

### Bước 3: Push Tất Cả Branch
```bash
# Push tất cả branch cùng lúc
git push origin --all

# Hoặc push từng branch một
git push origin feature/restructure-project
git push origin feature/backend-config
git push origin feature/backend-audio
git push origin feature/backend-database
git push origin feature/backend-search
git push origin feature/main-cli
git push origin feature/utils-helpers
git push origin feature/documentation
```

### Bước 4: Tạo Pull Request (PR)
1. Truy cập GitHub repository
2. Click "Compare & pull request" cho branch `feature/restructure-project`
3. Base: `main` ← Compare: `feature/restructure-project`
4. Title: "feat: restructure project with modular architecture"
5. Description: Xem bên dưới
6. Click "Create pull request"

## 📝 Pull Request Description

```markdown
## 🎯 Project Restructuring - Modular Architecture

### ✅ Changes Made

**🏗️ New Project Structure:**
```
voice_project/
├── main.py                    # 🚀 Entry point
├── main/cli.py               # 🖥️  CLI interface
├── backend/                  # 🧠 Core backend
│   ├── config.py            # ⚙️  Configuration
│   ├── audio/               # 🎵 Audio processing
│   ├── database/            # 💾 Database management
│   └── search/              # 🔍 Voice search engine
├── utils/                   # 🛠️  Utilities
├── data/                    # 📊 Data files
└── docs/                    # 📚 Documentation
```

**📦 Modular Components:**
- **Backend/Audio**: Audio preprocessing & feature extraction (15 features)
- **Backend/Database**: SQLite management with integrity checks
- **Backend/Search**: Cosine/Euclidean similarity search
- **Main/CLI**: Command-line interface (extract, search, create-db, info)
- **Utils**: Helper functions for formatting, file I/O, tables

### 🔧 Technical Improvements

- **Separation of Concerns**: Clear main/backend/utils distinction
- **Modular Design**: Each module has single responsibility
- **Scalability**: Easy to add web API, GUI, or new features
- **Maintainability**: Organized imports and dependencies
- **Documentation**: Comprehensive guides and examples

### 📋 CLI Commands Available

```bash
python main.py extract       # Extract audio features
python main.py create-db     # Build SQLite database
python main.py search <file> # Find similar voices
python main.py info          # Show database stats
python main.py help          # Show help
```

### 🧪 Testing

- ✅ All imports working correctly
- ✅ Directory structure validated
- ✅ Configuration parameters verified
- ✅ Modular architecture confirmed

### 📚 Documentation Added

- `PROJECT_STRUCTURE.md`: Detailed architecture guide
- `QUICK_REFERENCE.md`: Quick start guide
- `README.md`: Updated with new structure
- Mermaid diagrams for visualization

---

**Ready for merge! 🎉**
```

## 🔄 Workflow Alternatives

### Option A: Merge Trực Tiếp (Đơn Giản)
```bash
git checkout main
git merge feature/restructure-project
git push origin main
```

### Option B: Pull Request (Recommended)
```bash
# Tạo PR trên GitHub
# Review code changes
# Merge khi approved
```

### Option C: Squash Merge
```bash
git checkout main
git merge --squash feature/restructure-project
git commit -m "feat: restructure project with modular architecture"
git push origin main
```

## 🧹 Dọn Dẹp (Sau Khi Merge)

```bash
# Xóa các feature branch sau khi merge
git branch -d feature/restructure-project
git branch -d feature/backend-config
git branch -d feature/backend-audio
git branch -d feature/backend-database
git branch -d feature/backend-search
git branch -d feature/main-cli
git branch -d feature/utils-helpers
git branch -d feature/documentation

# Push deletion to remote
git push origin --delete feature/restructure-project
# ... delete other branches
```

## 📊 Kiểm Tra Trạng Thái

```bash
# Xem tất cả branch
git branch -a

# Xem commit history
git log --oneline --graph --all

# Kiểm tra remote
git remote -v
```

## 🎯 Best Practices

- ✅ **Descriptive branch names**: `feature/`, `docs/`, `fix/`
- ✅ **Clear commit messages**: Start with type (feat, docs, fix)
- ✅ **Pull Requests**: Always review before merge
- ✅ **Branch cleanup**: Delete merged branches
- ✅ **Documentation**: Keep README and docs updated

---

**Happy coding! 🚀**
