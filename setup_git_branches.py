#!/usr/bin/env python
"""
Git Branch Organization Script for Voice Search Project
Creates organized branches and commits for GitHub push
"""

import subprocess
import os
from pathlib import Path

def run_git_command(command, description=""):
    """Run a git command and return success status"""
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True, cwd=os.getcwd())
        if result.returncode == 0:
            if description:
                print(f"✅ {description}")
            return True
        else:
            print(f"❌ Failed: {command}")
            print(f"Error: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Exception running: {command}")
        print(f"Error: {e}")
        return False

def create_feature_branch(branch_name, commit_message, files_to_add=None):
    """Create a feature branch and make a commit"""
    print(f"\n📋 Creating branch: {branch_name}")

    # Create and switch to branch
    run_git_command(f"git checkout -b {branch_name}", f"Switched to {branch_name}")

    # Add specific files if provided
    if files_to_add:
        for file_path in files_to_add:
            if Path(file_path).exists():
                run_git_command(f"git add {file_path}", f"Added {file_path}")
            else:
                print(f"⚠️  File not found: {file_path}")

    # Check if there are changes to commit
    result = subprocess.run("git diff --cached --quiet", shell=True, cwd=os.getcwd())
    if result.returncode != 0:  # There are staged changes
        run_git_command(f'git commit -m "{commit_message}"', f"Committed to {branch_name}")
    else:
        print(f"   ℹ️  No changes to commit in {branch_name}")

    # Return to restructure branch
    run_git_command("git checkout feature/restructure-project", "Returned to restructure branch")

def main():
    print("🚀 Voice Search Project - Git Branch Organization")
    print("=" * 55)

    # Ensure we're on restructure branch
    run_git_command("git checkout feature/restructure-project", "Switched to restructure branch")

    # Define branch configurations
    branches = [
        {
            "name": "feature/backend-config",
            "message": """feat: add backend configuration module

- Add backend/config.py with all project constants
- Add backend/__init__.py for module initialization
- Configure audio processing parameters (sample rate, duration, MFCC)
- Set up database and file paths
- Define search configuration (top_k, distance metric)""",
            "files": ["backend/config.py", "backend/__init__.py"]
        },
        {
            "name": "feature/backend-audio",
            "message": """feat: add backend audio processing modules

- Add backend/audio/preprocessing.py: audio loading, normalization, padding
- Add backend/audio/processor.py: feature extraction (MFCC, Mel, Chroma, Spectral)
- Add backend/audio/__init__.py: module exports
- Support 15 audio features extraction
- Handle multiple audio formats (.wav, .flac, .mp3, .ogg)
- Implement audio preprocessing pipeline""",
            "files": ["backend/audio/"]
        },
        {
            "name": "feature/backend-database",
            "message": """feat: add backend database management modules

- Add backend/database/db_manager.py: create tables, import data, verify integrity
- Add backend/database/queries.py: database query operations
- Add backend/database/__init__.py: module exports
- Implement SQLite database operations
- Support metadata and features storage
- Add database integrity checks""",
            "files": ["backend/database/"]
        },
        {
            "name": "feature/backend-search",
            "message": """feat: add backend voice search engine

- Add backend/search/voice_search.py: similarity search algorithm
- Add backend/search/__init__.py: module exports
- Implement cosine and euclidean distance metrics
- Support vector-based voice comparison
- Return top-K similar voices with similarity scores""",
            "files": ["backend/search/"]
        },
        {
            "name": "feature/main-cli",
            "message": """feat: add main CLI interface

- Add main/cli.py: command-line interface class
- Add main/__init__.py: module exports
- Add main.py: entry point script
- Support commands: extract, create-db, search, info, help
- Implement user-friendly CLI with progress indicators""",
            "files": ["main/", "main.py"]
        },
        {
            "name": "feature/utils-helpers",
            "message": """feat: add utility helper functions

- Add utils/helpers.py: common utility functions
- Add utils/__init__.py: module exports
- Implement file operations, formatting, table printing
- Add JSON/CSV file handling utilities""",
            "files": ["utils/"]
        },
        {
            "name": "feature/documentation",
            "message": """docs: add comprehensive project documentation

- Add PROJECT_STRUCTURE.md: detailed architecture guide
- Add QUICK_REFERENCE.md: quick start guide
- Add test_structure.py: structure validation script
- Update README.md with new structure information
- Include Mermaid diagrams and usage examples""",
            "files": ["PROJECT_STRUCTURE.md", "QUICK_REFERENCE.md", "test_structure.py"]
        }
    ]

    # Create each feature branch
    for branch_config in branches:
        create_feature_branch(
            branch_config["name"],
            branch_config["message"],
            branch_config["files"]
        )

    print("\n🔀 Merging all feature branches into restructure-project...")

    # Merge all branches into restructure-project
    run_git_command("git checkout feature/restructure-project", "Switched to restructure branch")

    for branch_config in branches:
        branch_name = branch_config["name"]
        print(f"   Merging {branch_name}...")
        run_git_command(f"git merge {branch_name} --no-edit --strategy=ours", f"Merged {branch_name}")

    print("\n📊 Final Branch Status:")
    print("-" * 30)
    run_git_command("git branch -a", "")

    print("\n✅ Git branch organization completed!")
    print("\n🎯 Next steps:")
    print("1. Review: git log --oneline --graph --all")
    print("2. Push to GitHub: git push origin --all")
    print("3. Create PR: feature/restructure-project → main")
    print("4. Or merge: git checkout main && git merge feature/restructure-project")

if __name__ == "__main__":
    main()