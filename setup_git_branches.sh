#!/usr/bin/env bash
# Git Workflow Script for Voice Search Project
# This script creates branches and organizes commits for GitHub

echo "🚀 Voice Search Project - Git Branch Organization"
echo "================================================="

# Function to create and commit to a branch
create_branch_commit() {
    local branch_name=$1
    local commit_message=$2
    local files_to_add=$3

    echo "📋 Creating branch: $branch_name"

    # Create and switch to branch
    git checkout -b "$branch_name" 2>/dev/null || git checkout "$branch_name"

    # Add files
    if [ -n "$files_to_add" ]; then
        git add $files_to_add
    fi

    # Commit if there are changes
    if git diff --cached --quiet; then
        echo "   ℹ️  No changes to commit in $branch_name"
    else
        git commit -m "$commit_message"
        echo "   ✅ Committed to $branch_name"
    fi

    # Return to restructure branch
    git checkout feature/restructure-project
}

# Start from restructure branch
git checkout feature/restructure-project

echo "📦 Creating feature branches..."

# 1. Backend Config
create_branch_commit \
    "feature/backend-config" \
    "feat: add backend configuration module

- Add backend/config.py with all project constants
- Add backend/__init__.py for module initialization
- Configure audio processing parameters (sample rate, duration, MFCC)
- Set up database and file paths
- Define search configuration (top_k, distance metric)" \
    "backend/config.py backend/__init__.py"

# 2. Backend Audio
create_branch_commit \
    "feature/backend-audio" \
    "feat: add backend audio processing modules

- Add backend/audio/preprocessing.py: audio loading, normalization, padding
- Add backend/audio/processor.py: feature extraction (MFCC, Mel, Chroma, Spectral)
- Add backend/audio/__init__.py: module exports
- Support 15 audio features extraction
- Handle multiple audio formats (.wav, .flac, .mp3, .ogg)
- Implement audio preprocessing pipeline" \
    "backend/audio/"

# 3. Backend Database
create_branch_commit \
    "feature/backend-database" \
    "feat: add backend database management modules

- Add backend/database/db_manager.py: create tables, import data, verify integrity
- Add backend/database/queries.py: database query operations
- Add backend/database/__init__.py: module exports
- Implement SQLite database operations
- Support metadata and features storage
- Add database integrity checks" \
    "backend/database/"

# 4. Backend Search
create_branch_commit \
    "feature/backend-search" \
    "feat: add backend voice search engine

- Add backend/search/voice_search.py: similarity search algorithm
- Add backend/search/__init__.py: module exports
- Implement cosine and euclidean distance metrics
- Support vector-based voice comparison
- Return top-K similar voices with similarity scores" \
    "backend/search/"

# 5. Main CLI
create_branch_commit \
    "feature/main-cli" \
    "feat: add main CLI interface

- Add main/cli.py: command-line interface class
- Add main/__init__.py: module exports
- Add main.py: entry point script
- Support commands: extract, create-db, search, info, help
- Implement user-friendly CLI with progress indicators" \
    "main/ main.py"

# 6. Utils Helpers
create_branch_commit \
    "feature/utils-helpers" \
    "feat: add utility helper functions

- Add utils/helpers.py: common utility functions
- Add utils/__init__.py: module exports
- Implement file operations, formatting, table printing
- Add JSON/CSV file handling utilities" \
    "utils/"

# 7. Documentation
create_branch_commit \
    "feature/documentation" \
    "docs: add comprehensive project documentation

- Add PROJECT_STRUCTURE.md: detailed architecture guide
- Add QUICK_REFERENCE.md: quick start guide
- Add test_structure.py: structure validation script
- Update README.md with new structure information
- Include Mermaid diagrams and usage examples" \
    "PROJECT_STRUCTURE.md QUICK_REFERENCE.md test_structure.py"

# 8. Data Directory Structure
create_branch_commit \
    "feature/data-structure" \
    "feat: reorganize data directory structure

- Move raw_audio/ to data/raw_audio/
- Move processed_audio/ to data/processed_audio/
- Create proper data organization
- Update all path references in code" \
    "data/"

echo ""
echo "🔀 Merging all feature branches into restructure-project..."

# Merge all branches into restructure-project
git checkout feature/restructure-project

branches=(
    "feature/backend-config"
    "feature/backend-audio"
    "feature/backend-database"
    "feature/backend-search"
    "feature/main-cli"
    "feature/utils-helpers"
    "feature/documentation"
    "feature/data-structure"
)

for branch in "${branches[@]}"; do
    echo "   Merging $branch..."
    git merge "$branch" --no-edit --strategy=ours
done

echo ""
echo "📊 Branch Status:"
echo "=================="
git branch -a

echo ""
echo "✅ All branches created and merged!"
echo ""
echo "🎯 Next steps:"
echo "1. Review branches: git log --oneline --graph --all"
echo "2. Push to GitHub: git push origin --all"
echo "3. Create Pull Request from feature/restructure-project to main"
echo "4. Or merge directly: git checkout main && git merge feature/restructure-project"