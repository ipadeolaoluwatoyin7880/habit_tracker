# tests/conftest.py
import pytest
import os
import tempfile
import sqlite3
from datetime import datetime, timedelta

# Use absolute imports from src
from src.storage.db import DatabaseHandler, Periodicity, Completion
from src.managers.habit_manager import HabitManager
from src.analytics.analytics_service import AnalyticsService
from src.data_model.habit import BaseHabit, DailyHabit, WeeklyHabit, HabitFactory


@pytest.fixture
def test_db():
    """Create a temporary database for testing - Windows compatible"""
    # Create temporary database file with proper cleanup
    fd, db_path = tempfile.mkstemp(suffix='.db')
    os.close(fd)

    # Initialize database
    db_handler = DatabaseHandler(db_path)

    yield db_handler, db_path

    # Cleanup - close all connections first for Windows
    try:
        # Force close any remaining connections
        if hasattr(db_handler, '_get_connection'):
            conn = db_handler._get_connection()
            conn.close()

        # Wait a bit for file locks to release
        import time
        time.sleep(0.1)

        if os.path.exists(db_path):
            os.unlink(db_path)
    except (PermissionError, OSError, sqlite3.ProgrammingError) as e:
        print(f"Warning: Could not delete test database {db_path}: {e}")
        # On Windows, sometimes we can't delete the file immediately
        # This is acceptable for testing


@pytest.fixture
def test_user(test_db):
    """Create a test user"""
    db_handler, db_path = test_db
    user_id = db_handler.create_user("testuser", "test@example.com", "testpass123")
    return user_id


@pytest.fixture
def habit_manager(test_db, test_user):
    """Create habit manager with test user"""
    db_handler, db_path = test_db
    manager = HabitManager(db_path)
    manager.set_current_user(test_user)
    return manager


@pytest.fixture
def sample_habits(habit_manager):
    """Create sample habits for testing"""
    habits = []

    # Create daily habit
    daily_habit = habit_manager.create_habit("Morning Meditation", Periodicity.DAILY)
    habits.append(daily_habit)

    # Create weekly habit
    weekly_habit = habit_manager.create_habit("Weekly Exercise", Periodicity.WEEKLY)
    habits.append(weekly_habit)

    return habits


@pytest.fixture
def habits_with_completions(habit_manager, sample_habits):
    """Create habits with completion records"""
    daily_habit, weekly_habit = sample_habits

    # Add completions for daily habit (last 5 days)
    for i in range(5):
        comp_date = datetime.now() - timedelta(days=i)
        completion = Completion(comp_date, f"Completed day {i}", 8)
        habit_manager.db_handler.save_completion(daily_habit.habit_id, completion)

    # Add completions for weekly habit (last 3 weeks)
    for i in range(3):
        comp_date = datetime.now() - timedelta(weeks=i)
        completion = Completion(comp_date, f"Weekly completion {i}", 9)
        habit_manager.db_handler.save_completion(weekly_habit.habit_id, completion)

    # Reload habits with completions
    return habit_manager.get_all_habits()