#!/usr/bin/env python
"""
Automated GitHub Push Script for Voice Search Project
Handles repository setup and branch pushing
"""

import subprocess
import os
import sys
from pathlib import Path

def run_command(command, description="", fail_on_error=True):
    """Run shell command with error handling"""
    try:
        print(f"🔄 {description}")
        result = subprocess.run(command, shell=True, capture_output=True, text=True, cwd=os.getcwd())

        if result.returncode == 0:
            print(f"✅ {description}")
            return True
        else:
            print(f"❌ Failed: {description}")
            print(f"Error: {result.stderr}")
            if fail_on_error:
                return False
            return True
    except Exception as e:
        print(f"❌ Exception: {description}")
        print(f"Error: {e}")
        return False

def setup_github_remote():
    """Setup GitHub remote repository"""
    print("\n🔗 GitHub Remote Setup")
    print("-" * 30)

    # Check if remote exists
    result = subprocess.run("git remote get-url origin", shell=True, capture_output=True, text=True)
    if result.returncode == 0:
        print("✅ Remote 'origin' already exists")
        print(f"   URL: {result.stdout.strip()}")
        return True

    # Ask for repository URL
    print("\n📝 Please provide your GitHub repository URL:")
    print("   Example: https://github.com/username/voice-search-project.git")
    repo_url = input("   URL: ").strip()

    if not repo_url:
        print("❌ No URL provided. Skipping remote setup.")
        return False

    return run_command(f"git remote add origin {repo_url}", "Adding GitHub remote")

def push_branches():
    """Push all branches to GitHub"""
    print("\n📤 Pushing Branches to GitHub")
    print("-" * 35)

    branches = [
        "main",
        "feature/restructure-project",
        "feature/backend-config",
        "feature/backend-audio",
        "feature/backend-database",
        "feature/backend-search",
        "feature/main-cli",
        "feature/utils-helpers",
        "feature/documentation"
    ]

    # Push main branch first
    if not run_command("git push -u origin main", "Pushing main branch"):
        return False

    # Push all feature branches
    for branch in branches[1:]:  # Skip main
        if not run_command(f"git push origin {branch}", f"Pushing {branch}"):
            print(f"⚠️  Failed to push {branch}, continuing...")

    return run_command("git push origin --all", "Pushing all branches")

def create_pull_request_info():
    """Display PR creation information"""
    print("\n📋 Pull Request Information")
    print("-" * 30)
    print("Create a Pull Request on GitHub:")
    print("1. Go to: https://github.com/YOUR_USERNAME/REPO_NAME/pull/new")
    print("2. Base: main")
    print("3. Compare: feature/restructure-project")
    print("4. Title: feat: restructure project with modular architecture")
    print("5. Copy description from GITHUB_PUSH_GUIDE.md")
    print("6. Click 'Create Pull Request'")

def show_status():
    """Show final repository status"""
    print("\n📊 Repository Status")
    print("-" * 25)

    run_command("git remote -v", "Remote repositories")
    run_command("git branch -r", "Remote branches")
    run_command("git status", "Local status")

def main():
    print("🚀 Voice Search Project - GitHub Push Automation")
    print("=" * 55)

    # Check if we're in a git repository
    if not Path(".git").exists():
        print("❌ Not a Git repository. Please run 'git init' first.")
        sys.exit(1)

    # Setup GitHub remote
    if not setup_github_remote():
        print("⚠️  Remote setup failed. You can set it up manually:")
        print("   git remote add origin https://github.com/username/repo.git")
        print("   Then run: git push origin --all")

    # Push branches
    if push_branches():
        print("\n🎉 Successfully pushed all branches to GitHub!")
    else:
        print("\n⚠️  Some branches may not have been pushed successfully.")
        print("   Try manual push: git push origin --all")

    # Show PR info
    create_pull_request_info()

    # Show final status
    show_status()

    print("\n✅ GitHub push process completed!")
    print("\n📖 Next steps:")
    print("1. Create Pull Request on GitHub")
    print("2. Review code changes")
    print("3. Merge to main branch")
    print("4. Delete feature branches if desired")

if __name__ == "__main__":
    main()