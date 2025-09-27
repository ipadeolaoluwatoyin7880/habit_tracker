import pytest
import tempfile
import os
import sqlite3
from datetime import datetime, date, timedelta
from src.data_model.habit import DailyHabit, WeeklyHabit, Periodicity, create_habit
from src.data_model.completion import Completion
from src.storage.db import DatabaseHandler, TEST_DATA_DIR
from src.managers.habit_manager import HabitManager

# Create test data directory
os.makedirs(TEST_DATA_DIR, exist_ok=True)


@pytest.fixture
def temp_db():
    """Create a temporary database for testing in the proper test directory"""
    fd, temp_path = tempfile.mkstemp(suffix='.db', dir=TEST_DATA_DIR)
    os.close(fd)

    db = DatabaseHandler(temp_path)

    yield db

    # Cleanup - properly close connections before deletion
    try:
        # Force close any open connections
        conn = sqlite3.connect(temp_path)
        conn.close()
        os.unlink(temp_path)
    except (PermissionError, sqlite3.Error):
        # If file is still locked, it will be cleaned up later
        pass


@pytest.fixture
def sample_daily_habit():
    """Create a sample daily habit"""
    return DailyHabit("Read 10 pages", datetime(2024, 1, 1))


@pytest.fixture
def sample_weekly_habit():
    """Create a sample weekly habit"""
    return WeeklyHabit("Exercise", datetime(2024, 1, 1))


@pytest.fixture
def habit_with_completions():
    """Create a habit with completion records"""
    habit = DailyHabit("Meditate", datetime(2024, 1, 1))

    # Add completions for consecutive days
    for i in range(5):
        completion = Completion(f"Day {i + 1}", 5)
        completion.timestamp = datetime(2024, 1, i + 1)  # Jan 1-5
        habit.completion_records.append(completion)

    return habit


@pytest.fixture
def habit_manager(temp_db):
    """Create a habit manager with temporary database"""
    return HabitManager(temp_db.db_path)