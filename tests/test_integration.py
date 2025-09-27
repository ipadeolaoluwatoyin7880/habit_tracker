import pytest
from datetime import datetime, date
from src.managers.habit_manager import HabitManager
from src.data_model.habit import Periodicity
from src.analytics.analytics_service import calculate_current_streak, calculate_longest_streak


class TestIntegration:
    def test_end_to_end_workflow(self, habit_manager):
        """Test complete workflow: create habit → check off → analyze"""
        # Create habits
        daily_habit = habit_manager.create_habit("Daily reading", Periodicity.DAILY)
        weekly_habit = habit_manager.create_habit("Weekly exercise", Periodicity.WEEKLY)

        # Verify creation
        habits = habit_manager.get_all_habits()
        assert len(habits) == 2

        # Check off daily habit multiple times with specific timestamps
        daily_habit = habit_manager.get_habit_by_name("Daily reading")

        # Add completions for consecutive days
        for i in range(3):
            completion = daily_habit.check_off(f"Day {i + 1}", i + 7)
            completion.timestamp = datetime(2024, 1, i + 1)  # Jan 1, 2, 3

        # Verify analytics - use a specific date for testing
        test_date = date(2024, 1, 3)  # Jan 3rd
        current_streak = calculate_current_streak(daily_habit, test_date)
        longest_streak = calculate_longest_streak(daily_habit)

        # With completions on Jan 1, 2, 3, streak should be 3 on Jan 3rd
        assert current_streak == 3
        assert longest_streak == 3

        # Test filtering
        daily_habits = habit_manager.get_daily_habits()
        weekly_habits = habit_manager.get_weekly_habits()

        assert len(daily_habits) == 1
        assert len(weekly_habits) == 1

    def test_habit_persistence(self, temp_db):
        """Test that habits persist through manager instances"""
        # Create first manager instance and add habit
        manager1 = HabitManager(temp_db.db_path)
        manager1.create_habit("Persistent habit", Periodicity.DAILY)

        # Create second manager instance (should load from same DB)
        manager2 = HabitManager(temp_db.db_path)
        habits = manager2.get_all_habits()

        assert len(habits) == 1
        assert habits[0].name == "Persistent habit"