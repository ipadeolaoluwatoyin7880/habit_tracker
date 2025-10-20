# src/analytics/analytics_service.py
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from functools import reduce

# Import from other packages within src
from src.data_model.habit import BaseHabit
from src.storage.db import Periodicity
from src.data_model.completion import Completion


class AnalyticsService:
    """Provides analytics functionality using functional programming principles"""

    @staticmethod
    def calculate_current_streak(habit: BaseHabit, as_of_date: datetime = None) -> int:
        """
        Calculate the current streak for a habit (pure function)

        Args:
            habit: The habit to analyze
            as_of_date: Date to calculate streak as of (defaults to today)

        Returns:
            Current streak length in periods (days for daily, weeks for weekly)
        """
        as_of_date = as_of_date or datetime.now()

        if not habit.get_completion_records():
            return 0

        # Sort completions by date (newest first)
        completions = sorted(habit.get_completion_records(),
                             key=lambda x: x.timestamp, reverse=True)

        streak_count = 0
        current_date = as_of_date

        if habit.periodicity == Periodicity.DAILY:
            # For daily habits, check consecutive days
            for completion in completions:
                comp_date = completion.timestamp.date()

                # If completion is on or before current date, it's part of streak
                if comp_date <= current_date.date():
                    streak_count += 1
                    current_date = completion.timestamp - timedelta(days=1)
                else:
                    break

        else:  # Weekly habits
            # For weekly habits, check consecutive weeks
            current_year, current_week, _ = as_of_date.isocalendar()

            for completion in completions:
                comp_year, comp_week, _ = completion.timestamp.isocalendar()

                # Check if completion is in the same week or previous consecutive weeks
                if (comp_year == current_year and comp_week == current_week) or \
                        (comp_year == current_year and comp_week == current_week - 1) or \
                        (comp_year == current_year - 1 and comp_week == 52 and current_week == 1):
                    streak_count += 1
                    current_week -= 1
                    if current_week == 0:
                        current_year -= 1
                        current_week = 52
                else:
                    break

        return streak_count

    @staticmethod
    def calculate_longest_streak(habit: BaseHabit) -> int:
        """
        Calculate the longest streak for a habit (pure function)

        Args:
            habit: The habit to analyze

        Returns:
            Longest streak length in periods
        """
        completions = sorted(habit.get_completion_records(),
                             key=lambda x: x.timestamp)

        if not completions:
            return 0

        if habit.periodicity == Periodicity.DAILY:
            return AnalyticsService._calculate_daily_longest_streak(completions)
        else:
            return AnalyticsService._calculate_weekly_longest_streak(completions)

    @staticmethod
    def _calculate_daily_longest_streak(completions: List[Completion]) -> int:
        """Calculate longest streak for daily habits"""
        if not completions:
            return 0

        dates = [comp.timestamp.date() for comp in completions]
        dates.sort()

        longest_streak = 1
        current_streak = 1

        for i in range(1, len(dates)):
            if (dates[i] - dates[i - 1]).days == 1:
                current_streak += 1
                longest_streak = max(longest_streak, current_streak)
            elif dates[i] != dates[i - 1]:
                current_streak = 1

        return longest_streak

    @staticmethod
    def _calculate_weekly_longest_streak(completions: List[Completion]) -> int:
        """Calculate longest streak for weekly habits"""
        if not completions:
            return 0

        # Get unique weeks with completions
        weeks = set()
        for comp in completions:
            year, week, _ = comp.timestamp.isocalendar()
            weeks.add((year, week))

        weeks = sorted(weeks)

        longest_streak = 1
        current_streak = 1

        for i in range(1, len(weeks)):
            current_year, current_week = weeks[i]
            prev_year, prev_week = weeks[i - 1]

            # Check if weeks are consecutive
            if (current_year == prev_year and current_week == prev_week + 1) or \
                    (current_year == prev_year + 1 and current_week == 1 and prev_week == 52):
                current_streak += 1
                longest_streak = max(longest_streak, current_streak)
            else:
                current_streak = 1

        return longest_streak

    @staticmethod
    def get_habits_by_periodicity(habits: List[BaseHabit], periodicity: Periodicity) -> List[BaseHabit]:
        """
        Filter habits by periodicity (pure function)

        Args:
            habits: List of habits to filter
            periodicity: Periodicity to filter by

        Returns:
            Filtered list of habits
        """
        return [habit for habit in habits if habit.periodicity == periodicity]

    @staticmethod
    def get_overall_longest_streak(habits: List[BaseHabit]) -> Dict[str, Any]:
        """
        Find the habit with the longest streak overall (pure function)

        Args:
            habits: List of habits to analyze

        Returns:
            Dictionary with habit and streak information
        """
        if not habits:
            return {"habit_name": None, "streak_length": 0, "periodicity": None}

        streak_data = []
        for habit in habits:
            longest_streak = AnalyticsService.calculate_longest_streak(habit)
            streak_data.append({
                "habit": habit,
                "streak_length": longest_streak
            })

        # Find habit with maximum streak
        max_streak = max(streak_data, key=lambda x: x["streak_length"])

        return {
            "habit_name": max_streak["habit"].name,
            "streak_length": max_streak["streak_length"],
            "periodicity": max_streak["habit"].periodicity.value,
            "habit_id": max_streak["habit"].habit_id
        }

    @staticmethod
    def get_inactive_habits(habits: List[BaseHabit], months: int = 6) -> List[BaseHabit]:
        """
        Find habits that haven't been completed in specified months (pure function)

        Args:
            habits: List of habits to check
            months: Number of months to consider as inactive threshold

        Returns:
            List of inactive habits
        """
        cutoff_date = datetime.now() - timedelta(days=months * 30)

        def is_inactive(habit: BaseHabit) -> bool:
            last_completion = habit.get_last_completion_date()
            if not last_completion:
                return True  # Never completed
            return last_completion < cutoff_date

        return list(filter(is_inactive, habits))

    @staticmethod
    def get_habits_streak_summary(habits: List[BaseHabit]) -> List[Dict[str, Any]]:
        """
        Get streak summary for all habits (pure function)

        Args:
            habits: List of habits to analyze

        Returns:
            List of dictionaries with streak information for each habit
        """

        def create_streak_summary(habit: BaseHabit) -> Dict[str, Any]:
            return {
                "habit_id": habit.habit_id,
                "habit_name": habit.name,
                "periodicity": habit.periodicity.value,
                "current_streak": AnalyticsService.calculate_current_streak(habit),
                "longest_streak": AnalyticsService.calculate_longest_streak(habit),
                "completion_count": len(habit.get_completion_records()),
                "last_completion": habit.get_last_completion_date()
            }

        return list(map(create_streak_summary, habits))