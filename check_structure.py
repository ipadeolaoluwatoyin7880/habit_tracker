import os


def check_data_directories():
    print("🔍 Checking data directory structure...")

    # Check for data directories in various locations
    locations = [
        '.',  # Project root
        'src',  # Source directory
        'src/analytics',  # Analytics module
        'tests',  # Tests directory
        'tests/test_data'  # Test data directory
    ]

    for location in locations:
        data_path = os.path.join(location, 'data')
        if os.path.exists(data_path):
            print(f"❌ FOUND: {data_path}/")
            # List contents
            for item in os.listdir(data_path):
                item_path = os.path.join(data_path, item)
                if os.path.isfile(item_path):
                    print(f"     📄 {item}")
                else:
                    print(f"     📁 {item}/")
        else:
            print(f"✅ OK: No data directory in {location}")

    print(f"\n🎯 Correct structure should have:")
    print(f"   📁 data/ (in project root only)")
    print(f"   📁 tests/test_data/ (for testing)")


if __name__ == "__main__":
    check_data_directories()