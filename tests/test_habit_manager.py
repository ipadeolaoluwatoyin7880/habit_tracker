# tests/test_habit_manager.py
import pytest
from datetime import datetime, timedelta
from src.managers.habit_manager import HabitManager
from src.storage.db import Periodicity, Completion


class TestHabitManager:
    """Test habit manager functionality"""

    def test_create_habit(self, habit_manager):
        """Test habit creation"""
        habit = habit_manager.create_habit("Test Habit", Periodicity.DAILY)

        assert habit is not None
        assert habit.name == "Test Habit"
        assert habit.periodicity == Periodicity.DAILY
        assert habit.is_active == True

        # Verify habit is saved in database
        habits = habit_manager.get_all_habits()
        assert len(habits) == 1
        assert habits[0].name == "Test Habit"

    def test_create_habit_validation(self, habit_manager):
        """Test habit creation validation"""
        # Test empty name
        with pytest.raises(ValueError, match="cannot be empty"):
            habit_manager.create_habit("", Periodicity.DAILY)

        # Test whitespace name
        with pytest.raises(ValueError, match="cannot be empty"):
            habit_manager.create_habit("   ", Periodicity.DAILY)

    def test_get_all_habits(self, habit_manager):
        """Test retrieving all habits"""
        # Create multiple habits
        habit1 = habit_manager.create_habit("Habit 1", Periodicity.DAILY)
        habit2 = habit_manager.create_habit("Habit 2", Periodicity.WEEKLY)

        habits = habit_manager.get_all_habits()

        assert len(habits) == 2
        habit_names = [habit.name for habit in habits]
        assert "Habit 1" in habit_names
        assert "Habit 2" in habit_names

    def test_get_habit_by_id(self, habit_manager):
        """Test retrieving habit by ID"""
        habit = habit_manager.create_habit("Test Habit", Periodicity.DAILY)

        retrieved_habit = habit_manager.get_habit_by_id(habit.habit_id)

        assert retrieved_habit is not None
        assert retrieved_habit.habit_id == habit.habit_id
        assert retrieved_habit.name == "Test Habit"

        # Test non-existent habit
        non_existent = habit_manager.get_habit_by_id(999)
        assert non_existent is None

    def test_delete_habit(self, habit_manager):
        """Test habit deletion"""
        habit = habit_manager.create_habit("Test Habit", Periodicity.DAILY)

        # Verify habit exists and is active
        habits_before = habit_manager.get_all_habits(active_only=True)
        assert len(habits_before) == 1

        # Delete habit
        success = habit_manager.delete_habit(habit.habit_id)
        assert success is True

        # Verify habit is inactive
        habits_after = habit_manager.get_all_habits(active_only=True)
        assert len(habits_after) == 0

        # But should still exist when including inactive
        all_habits = habit_manager.get_all_habits(active_only=False)
        assert len(all_habits) == 1
        assert all_habits[0].is_active == False

    def test_check_off_habit(self, habit_manager, sample_habits):
        """Test checking off a habit"""
        daily_habit, weekly_habit = sample_habits

        # Check off daily habit
        success = habit_manager.check_off_habit(daily_habit.habit_id, "Great session!", 8)
        assert success is True

        # Verify completion was recorded
        completions = habit_manager.get_habit_completions(daily_habit.habit_id)
        assert len(completions) == 1
        assert completions[0].notes == "Great session!"
        assert completions[0].mood_score == 8

        # Try to check off again same day (should fail for daily habit)
        success = habit_manager.check_off_habit(daily_habit.habit_id)
        assert success is False

    def test_check_off_inactive_habit(self, habit_manager):
        """Test checking off an inactive habit"""
        habit = habit_manager.create_habit("Test Habit", Periodicity.DAILY)
        habit_manager.delete_habit(habit.habit_id)

        success = habit_manager.check_off_habit(habit.habit_id)
        assert success is False

    def test_get_habit_completions(self, habit_manager, sample_habits):
        """Test retrieving habit completions"""
        daily_habit, weekly_habit = sample_habits

        # Add multiple completions
        for i in range(3):
            comp_date = datetime.now() - timedelta(days=i)
            completion = Completion(comp_date, f"Completion {i}")
            habit_manager.db_handler.save_completion(daily_habit.habit_id, completion)

        completions = habit_manager.get_habit_completions(daily_habit.habit_id)
        assert len(completions) == 3

        # Test with limit
        limited_completions = habit_manager.get_habit_completions(daily_habit.habit_id, limit=2)
        assert len(limited_completions) == 2

    def test_no_user_error(self, test_db):
        """Test operations without setting current user"""
        db_handler, db_path = test_db
        manager = HabitManager(db_path)
        # No user set

        with pytest.raises(ValueError, match="No user logged in"):
            manager.create_habit("Test Habit", Periodicity.DAILY)

        with pytest.raises(ValueError, match="No user logged in"):
            manager.get_all_habits()