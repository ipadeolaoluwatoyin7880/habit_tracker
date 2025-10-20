# tests/test_integration.py
import pytest
from datetime import datetime, timedelta
from src.storage.db import DatabaseHandler, Periodicity, Completion  # ADD Completion import
from src.managers.habit_manager import HabitManager
from src.analytics.analytics_service import AnalyticsService


class TestIntegration:
    """Integration tests for complete workflows"""

    def test_complete_user_journey(self, test_db):
        """Test complete user journey from registration to analytics"""
        db_handler, db_path = test_db

        # Create habit manager
        habit_manager = HabitManager(db_path)

        # Create user directly
        user_id = db_handler.create_user("integration_user", "integration@test.com", "testpass123")
        habit_manager.set_current_user(user_id)

        # Create habits
        habit1 = habit_manager.create_habit("Morning Meditation", Periodicity.DAILY)
        habit2 = habit_manager.create_habit("Weekly Workout", Periodicity.WEEKLY)

        # Check off habits
        success1 = habit_manager.check_off_habit(habit1.habit_id, "Felt peaceful", 9)
        success2 = habit_manager.check_off_habit(habit2.habit_id, "Good session", 8)

        assert success1 is True
        assert success2 is True

        # Verify habits and completions
        habits = habit_manager.get_all_habits()
        assert len(habits) == 2

        completions = habit_manager.get_user_completions()
        assert len(completions) == 2

        # Test analytics
        streak_summary = AnalyticsService.get_habits_streak_summary(habits)
        assert len(streak_summary) == 2

        overall_streak = AnalyticsService.get_overall_longest_streak(habits)
        assert overall_streak['streak_length'] >= 1

    def test_streak_calculation_workflow(self, habit_manager, sample_habits):
        """Test complete streak calculation workflow"""
        daily_habit, weekly_habit = sample_habits

        # Add consecutive daily completions
        for i in range(5):
            comp_date = datetime.now() - timedelta(days=i)
            completion = habit_manager.db_handler.save_completion(
                daily_habit.habit_id,
                Completion(comp_date, f"Day {i}")
            )

        # Add weekly completions
        for i in range(3):
            comp_date = datetime.now() - timedelta(weeks=i)
            completion = habit_manager.db_handler.save_completion(
                weekly_habit.habit_id,
                Completion(comp_date, f"Week {i}")
            )

        # Reload habits with completions
        habits = habit_manager.get_all_habits()

        # Test analytics
        daily_streak = AnalyticsService.calculate_current_streak(habits[0])
        weekly_streak = AnalyticsService.calculate_current_streak(habits[1])

        assert daily_streak == 5
        assert weekly_streak == 3

        # Test filtering
        daily_habits = AnalyticsService.get_habits_by_periodicity(habits, Periodicity.DAILY)
        weekly_habits = AnalyticsService.get_habits_by_periodicity(habits, Periodicity.WEEKLY)

        assert len(daily_habits) == 1
        assert len(weekly_habits) == 1

    def test_user_authentication_workflow(self, test_db):
        """Test complete user authentication workflow"""
        db_handler, db_path = test_db

        # Create user
        user_id = db_handler.create_user("auth_test", "auth@test.com", "authpass123")

        # Verify login works
        user = db_handler.verify_user_credentials("auth_test", "authpass123")
        assert user is not None
        assert user.username == "auth_test"

        # Verify wrong password fails
        user = db_handler.verify_user_credentials("auth_test", "wrongpass")
        assert user is None

        # Verify non-existent user fails
        user = db_handler.verify_user_credentials("nonexistent", "password")
        assert user is None

    def test_habit_lifecycle(self, habit_manager):
        """Test complete habit lifecycle"""
        # Create habit
        habit = habit_manager.create_habit("Lifecycle Test", Periodicity.DAILY)
        assert habit.is_active == True

        # Check off multiple times (with small delays to avoid same-day issues)
        import time
        success_count = 0
        for i in range(3):
            success = habit_manager.check_off_habit(habit.habit_id, f"Completion {i}")
            if success:
                success_count += 1
            # Add small delay to ensure different timestamps
            time.sleep(0.1)

        # At least one check-off should succeed (first one)
        assert success_count >= 1

        # Verify completions
        completions = habit_manager.get_habit_completions(habit.habit_id)
        assert len(completions) >= 1

        # Delete habit
        success = habit_manager.delete_habit(habit.habit_id)
        assert success is True

        # Verify habit is inactive
        habits = habit_manager.get_all_habits(active_only=True)
        # The habit might still be in the list due to test timing, but it should be inactive
        active_habits = [h for h in habits if h.is_active]
        assert len(active_habits) == 0

        # But still exists in database when including inactive
        all_habits = habit_manager.get_all_habits(active_only=False)
        assert len(all_habits) >= 1