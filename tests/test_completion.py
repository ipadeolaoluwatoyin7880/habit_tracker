import pytest
from datetime import datetime, date, timedelta
from src.data_model.habit import DailyHabit, WeeklyHabit, Periodicity, create_habit


class TestHabitCreation:
    def test_daily_habit_creation(self):
        """Test creating a daily habit"""
        habit = DailyHabit("Read daily")
        assert habit.name == "Read daily"
        assert habit.periodicity == Periodicity.DAILY
        assert habit.is_active == True
        assert len(habit.completion_records) == 0

    def test_weekly_habit_creation(self):
        """Test creating a weekly habit"""
        habit = WeeklyHabit("Exercise weekly")
        assert habit.name == "Exercise weekly"
        assert habit.periodicity == Periodicity.WEEKLY
        assert habit.is_active == True

    def test_habit_factory_function(self):
        """Test the create_habit factory function"""
        daily = create_habit("Read", Periodicity.DAILY)
        weekly = create_habit("Exercise", Periodicity.WEEKLY)

        assert daily.periodicity == Periodicity.DAILY
        assert weekly.periodicity == Periodicity.WEEKLY
        assert isinstance(daily, DailyHabit)
        assert isinstance(weekly, WeeklyHabit)


class TestHabitMethods:
    def test_check_off_habit(self, sample_daily_habit):
        """Test checking off a habit"""
        completion = sample_daily_habit.check_off("Great session!", 8)

        assert len(sample_daily_habit.completion_records) == 1
        assert completion.notes == "Great session!"
        assert completion.mood_score == 8

    def test_deactivate_habit(self, sample_daily_habit):
        """Test deactivating a habit"""
        sample_daily_habit.deactivate()
        assert sample_daily_habit.is_active == False

        sample_daily_habit.activate()
        assert sample_daily_habit.is_active == True


class TestDueDateLogic:
    def test_daily_habit_due_date(self, sample_daily_habit):
        """Test daily habit due date logic"""
        # Habit created on Jan 1, should be due on Jan 2 if not completed
        test_date = date(2024, 1, 2)
        assert sample_daily_habit.is_due_on(test_date) == True

    def test_daily_habit_not_due_if_completed(self, sample_daily_habit):
        """Test daily habit not due if completed today"""
        # Complete the habit for Jan 2
        completion = sample_daily_habit.check_off()
        completion.timestamp = datetime(2024, 1, 2)

        # Should not be due on Jan 2 since it's already completed
        test_date = date(2024, 1, 2)
        assert sample_daily_habit.is_due_on(test_date) == False

    def test_weekly_habit_due_date(self, sample_weekly_habit):
        """Test weekly habit due date logic"""
        # Habit created in week 1, should be due in week 2
        test_date = date(2024, 1, 8)  # Week 2
        assert sample_weekly_habit.is_due_on(test_date) == True

    def test_weekly_habit_not_due_same_week(self, sample_weekly_habit):
        """Test weekly habit not due in the same week as creation"""
        test_date = date(2024, 1, 3)  # Still week 1
        assert sample_weekly_habit.is_due_on(test_date) == False


class TestHabitStringRepresentation:
    def test_habit_string_representation(self, sample_daily_habit):
        """Test habit string representation"""
        expected = "✅ DAILY - Read 10 pages"
        assert str(sample_daily_habit) == expected

    def test_inactive_habit_string(self, sample_daily_habit):
        """Test inactive habit string representation"""
        sample_daily_habit.deactivate()
        expected = "❌ DAILY - Read 10 pages"
        assert str(sample_daily_habit) == expected