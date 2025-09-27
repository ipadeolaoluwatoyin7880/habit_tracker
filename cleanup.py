#!/usr/bin/env python3
"""
Cleanup script to remove stray database files
"""
import os
import glob
import shutil


def cleanup_databases():
    """Remove all database files except the main production one"""
    print("🧹 Cleaning up database files...")

    # List of directories to check for stray DB files
    directories_to_clean = [
        '.',  # Current directory (project root)
        'src/analytics',
        'tests',
        'src',
        'data'  # We'll keep this one but can recreate if needed
    ]

    db_files_removed = 0

    for directory in directories_to_clean:
        if os.path.exists(directory):
            # Find all .db files
            db_pattern = os.path.join(directory, '*.db')
            db_files = glob.glob(db_pattern)

            for db_file in db_files:
                # Don't remove the main production database in data/
                if db_file.endswith('data/habits.db'):
                    continue

                try:
                    os.remove(db_file)
                    print(f"✅ Removed: {db_file}")
                    db_files_removed += 1
                except Exception as e:
                    print(f"❌ Could not remove {db_file}: {e}")

    # Clean test data directory but keep the directory structure
    test_data_dir = 'tests/test_data'
    if os.path.exists(test_data_dir):
        for item in os.listdir(test_data_dir):
            item_path = os.path.join(test_data_dir, item)
            try:
                if os.path.isfile(item_path):
                    os.remove(item_path)
                    print(f"✅ Removed test file: {item_path}")
                elif os.path.isdir(item_path):
                    shutil.rmtree(item_path)
                    print(f"✅ Removed test directory: {item_path}")
            except Exception as e:
                print(f"❌ Could not remove {item_path}: {e}")

    # Recreate necessary directories
    os.makedirs('data', exist_ok=True)
    os.makedirs('tests/test_data', exist_ok=True)

    # Create .gitkeep files if they don't exist
    with open('data/.gitkeep', 'w') as f:
        f.write('# This file ensures the data directory is tracked by git\n')

    with open('tests/test_data/.gitkeep', 'w') as f:
        f.write('# This file ensures the test_data directory is tracked by git\n')

    print(f"\n🎉 Cleanup complete! Removed {db_files_removed} database files.")
    print("💡 Main production database (data/habits.db) was preserved.")


if __name__ == "__main__":
    cleanup_databases()