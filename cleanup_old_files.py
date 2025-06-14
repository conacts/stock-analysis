#!/usr/bin/env python3
"""
Cleanup Script - Remove old scattered files
Organize the project with the new modular structure
"""

import os
import shutil
from pathlib import Path


def cleanup_old_files():
    """Remove old scattered files"""

    old_files = [
        "stock_analyzer.py",
        "enhanced_stock_analyzer.py",
        "ai_analysis.py",
        "stock_universe.py",
        "master_stock_analyzer.py",
        "quick_stock_picks.py",
        "nvda_deep_dive.py",
        "demo.py",
        "main.py",
    ]

    print("🧹 CLEANING UP OLD FILES")
    print("=" * 40)

    for file in old_files:
        if Path(file).exists():
            print(f"Removing: {file}")
            os.remove(file)
        else:
            print(f"Not found: {file}")

    # Create archive directory for important files
    archive_dir = Path("archive")
    archive_dir.mkdir(exist_ok=True)

    # Move important files to archive
    important_files = ["IMPROVEMENT_ROADMAP.md", "README.md"]

    for file in important_files:
        if Path(file).exists():
            shutil.move(file, archive_dir / file)
            print(f"Archived: {file}")

    print("\n✅ Cleanup completed!")
    print("📁 Old files removed, important files archived")


if __name__ == "__main__":
    cleanup_old_files()
