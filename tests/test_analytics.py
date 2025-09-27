import pytest
from datetime import datetime
from src.managers.habit_manager import HabitManager
from src.data_model.habit import Periodicity


class TestHabitManager:
    def test_manager_initialization(self, habit_manager):
        """Test habit manager initialization"""
        assert habit_manager is not None
        assert len(habit_manager.get_all_habits()) == 0

    def test_create_habit(self, habit_manager):
        """Test creating a habit through manager"""
        habit = habit_manager.create_habit("New habit", Periodicity.DAILY)

        assert habit.name == "New habit"
        assert habit.periodicity == Periodicity.DAILY
        assert len(habit_manager.get_all_habits()) == 1

    def test_check_off_habit(self, habit_manager):
        """Test checking off a habit through manager"""
        habit = habit_manager.create_habit("Test habit", Periodicity.DAILY)

        result = habit_manager.check_off_habit("Test habit", "Great!", 8)
        assert result == True

        # Verify completion was added
        habit = habit_manager.get_habit_by_name("Test habit")
        assert len(habit.completion_records) == 1

    def test_get_habit_by_name(self, habit_manager):
        """Test retrieving habit by name"""
        habit_manager.create_habit("Habit 1", Periodicity.DAILY)
        habit_manager.create_habit("Habit 2", Periodicity.WEEKLY)

        habit = habit_manager.get_habit_by_name("Habit 1")
        assert habit.name == "Habit 1"
        assert habit.periodicity == Periodicity.DAILY

        # Test non-existent habit
        habit = habit_manager.get_habit_by_name("Non-existent")
        assert habit is None

    def test_get_habits_by_periodicity(self, habit_manager):
        """Test filtering habits by periodicity"""
        habit_manager.create_habit("Daily 1", Periodicity.DAILY)
        habit_manager.create_habit("Daily 2", Periodicity.DAILY)
        habit_manager.create_habit("Weekly 1", Periodicity.WEEKLY)

        daily_habits = habit_manager.get_daily_habits()
        weekly_habits = habit_manager.get_weekly_habits()

        assert len(daily_habits) == 2
        assert len(weekly_habits) == 1
        assert all(h.periodicity == Periodicity.DAILY for h in daily_habits)
        assert all(h.periodicity == Periodicity.WEEKLY for h in weekly_habits)

    def test_deactivate_habit(self, habit_manager):
        """Test deactivating a habit"""
        habit_manager.create_habit("Test habit", Periodicity.DAILY)

        result = habit_manager.deactivate_habit("Test habit")
        assert result == True

        habit = habit_manager.get_habit_by_name("Test habit")
        assert habit.is_active == False