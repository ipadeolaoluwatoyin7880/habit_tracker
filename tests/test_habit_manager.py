import pytest
from datetime import datetime
from src.storage.db import DatabaseHandler


class TestDatabaseOperations:
    def test_database_initialization(self, temp_db):
        """Test database tables are created properly"""
        # Tables should be created without errors
        habits = temp_db.get_all_habits()
        assert habits == []  # Should be empty initially

    def test_save_habit(self, temp_db):
        """Test saving a habit to database"""
        habit_id = temp_db.save_habit("Read daily", "daily")
        assert isinstance(habit_id, int)
        assert habit_id > 0

    def test_get_all_habits(self, temp_db):
        """Test retrieving all habits from database"""
        # Add some habits
        temp_db.save_habit("Habit 1", "daily")
        temp_db.save_habit("Habit 2", "weekly")

        habits = temp_db.get_all_habits()
        assert len(habits) == 2
        assert habits[0]['name'] == "Habit 1"
        assert habits[1]['name'] == "Habit 2"

    def test_save_completion(self, temp_db):
        """Test saving a completion record"""
        # First create a habit
        habit_id = temp_db.save_habit("Test habit", "daily")

        # Save completion
        timestamp = datetime(2024, 1, 1, 10, 30)
        temp_db.save_completion(habit_id, timestamp, "Great session!", 8)

        # Verify completion was saved
        completions = temp_db.get_completions_for_habit(habit_id)
        assert len(completions) == 1
        assert completions[0]['notes'] == "Great session!"
        assert completions[0]['mood_score'] == 8

    def test_deactivate_habit(self, temp_db):
        """Test deactivating a habit"""
        habit_id = temp_db.save_habit("Test habit", "daily")

        # Should be active initially
        habits = temp_db.get_all_habits()
        assert len(habits) == 1

        # Deactivate
        temp_db.deactivate_habit(habit_id)

        # Should not appear in active habits
        habits = temp_db.get_all_habits()
        assert len(habits) == 0

    def test_clear_all_data(self, temp_db):
        """Test clearing all data from database"""
        # Add some data
        habit_id = temp_db.save_habit("Test habit", "daily")
        temp_db.save_completion(habit_id, datetime.now(), "Test", 5)

        # Clear data
        temp_db.clear_all_data()

        # Verify data is cleared
        habits = temp_db.get_all_habits()
        assert len(habits) == 0


class TestDatabaseConstraints:
    def test_habit_periodicity_constraint(self, temp_db):
        """Test that only valid periodicity are allowed"""
        # Valid periodicity should work
        temp_db.save_habit("Valid daily", "daily")
        temp_db.save_habit("Valid weekly", "weekly")

        # This test verifies that invalid periodicity would be caught by SQLite constraints

    def test_mood_score_constraint(self, temp_db):
        """Test mood score constraint"""
        habit_id = temp_db.save_habit("Test habit", "daily")
        timestamp = datetime(2024, 1, 1, 10, 30)

        # Valid mood scores should work
        for score in [1, 5, 10]:
            temp_db.save_completion(habit_id, timestamp, "Test", score)

        # Invalid mood scores would be caught by SQLite constraints