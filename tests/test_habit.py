# tests/test_habit.py
import pytest
from datetime import datetime, timedelta
from src.data_model.habit import BaseHabit, DailyHabit, WeeklyHabit, HabitFactory
from src.storage.db import Periodicity, Completion


class TestHabitClasses:
    """Test habit class functionality"""

    def test_daily_habit_creation(self):
        """Test daily habit creation"""
        habit = DailyHabit(1, "Morning Run", datetime.now())

        assert habit.habit_id == 1
        assert habit.name == "Morning Run"
        assert habit.periodicity == Periodicity.DAILY
        assert habit.is_active == True
        assert len(habit.get_completion_records()) == 0

    def test_weekly_habit_creation(self):
        """Test weekly habit creation"""
        habit = WeeklyHabit(2, "Weekly Review", datetime.now())

        assert habit.habit_id == 2
        assert habit.name == "Weekly Review"
        assert habit.periodicity == Periodicity.WEEKLY
        assert habit.is_active == True

    def test_habit_activation_deactivation(self):
        """Test habit activation and deactivation"""
        habit = DailyHabit(1, "Test Habit", datetime.now())

        assert habit.is_active == True

        habit.deactivate()
        assert habit.is_active == False

        habit.activate()
        assert habit.is_active == True

    def test_daily_habit_is_due_on(self):
        """Test daily habit due date calculation"""
        habit = DailyHabit(1, "Daily Habit", datetime.now())
        today = datetime.now()
        yesterday = today - timedelta(days=1)
        tomorrow = today + timedelta(days=1)

        # Habit with no completions should be due
        assert habit.is_due_on(today) == True

        # Add completion for today
        completion = Completion(today, "Completed today")
        habit.set_completion_records([completion])

        # Should not be due since completed today
        assert habit.is_due_on(today) == False

        # Should be due tomorrow
        assert habit.is_due_on(tomorrow) == True

        # Inactive habit should never be due
        habit.deactivate()
        assert habit.is_due_on(today) == False

    def test_weekly_habit_is_due_on(self):
        """Test weekly habit due date calculation"""
        habit = WeeklyHabit(1, "Weekly Habit", datetime.now())

        # Get current week dates
        today = datetime.now()
        current_year, current_week, _ = today.isocalendar()

        # Create date in current week
        current_week_date = today

        # Create date in next week
        next_week_date = today + timedelta(weeks=1)

        # Habit with no completions should be due
        assert habit.is_due_on(current_week_date) == True

        # Add completion for current week
        completion = Completion(current_week_date, "Completed this week")
        habit.set_completion_records([completion])

        # Should not be due in current week
        assert habit.is_due_on(current_week_date) == False

        # Should be due in next week
        assert habit.is_due_on(next_week_date) == True

    def test_habit_check_off(self):
        """Test habit check-off functionality"""
        habit = DailyHabit(1, "Test Habit", datetime.now())

        completion = habit.check_off("Great session!", 9)

        assert isinstance(completion, Completion)
        assert completion.notes == "Great session!"
        assert completion.mood_score == 9
        assert len(habit.get_completion_records()) == 1

        # Test check-off without optional parameters
        completion2 = habit.check_off()
        assert completion2.notes is None
        assert completion2.mood_score is None
        assert len(habit.get_completion_records()) == 2

    def test_get_last_completion_date(self):
        """Test getting last completion date"""
        habit = DailyHabit(1, "Test Habit", datetime.now())

        # No completions
        assert habit.get_last_completion_date() is None

        # Add completions
        now = datetime.now()
        yesterday = now - timedelta(days=1)

        completion1 = Completion(yesterday, "Yesterday")
        completion2 = Completion(now, "Today")
        habit.set_completion_records([completion1, completion2])

        # Should return most recent completion
        assert habit.get_last_completion_date() == now

    def test_habit_factory_daily(self):
        """Test habit factory for daily habits"""
        habit_data = {
            'habit_id': 1,
            'name': 'Test Daily',
            'periodicity': 'daily',
            'created_at': datetime.now().isoformat(),
            'is_active': True
        }

        habit = HabitFactory.create_habit_from_db(habit_data)

        assert isinstance(habit, DailyHabit)
        assert habit.name == "Test Daily"
        assert habit.periodicity == Periodicity.DAILY

    def test_habit_factory_weekly(self):
        """Test habit factory for weekly habits"""
        habit_data = {
            'habit_id': 2,
            'name': 'Test Weekly',
            'periodicity': 'weekly',
            'created_at': datetime.now().isoformat(),
            'is_active': True
        }

        habit = HabitFactory.create_habit_from_db(habit_data)

        assert isinstance(habit, WeeklyHabit)
        assert habit.name == "Test Weekly"
        assert habit.periodicity == Periodicity.WEEKLY