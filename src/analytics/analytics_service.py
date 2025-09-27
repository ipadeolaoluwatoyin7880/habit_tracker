from datetime import datetime, date, timedelta
from typing import List, Dict, Any
from src.data_model.habit import BaseHabit, Periodicity


def calculate_current_streak(habit: BaseHabit, as_of_date: date = None) -> int:
    """Calculate current consecutive streak for a habit"""
    as_of_date = as_of_date or date.today()

    if not habit.completion_records:
        return 0

    # Sort completions by date (newest first)
    completions = sorted(habit.completion_records,
                         key=lambda x: x.timestamp, reverse=True)

    streak = 0

    if habit.periodicity == Periodicity.DAILY:
        # For daily habits: check consecutive days
        current_date = as_of_date

        for comp in completions:
            comp_date = comp.timestamp.date()

            if comp_date == current_date:
                streak += 1
                current_date -= timedelta(days=1)
            elif comp_date < current_date:
                # Gap found, streak ends
                break
    else:
        # For weekly habits: check consecutive weeks
        current_week = as_of_date.isocalendar()[1]
        current_year = as_of_date.isocalendar()[0]

        for comp in completions:
            comp_week = comp.timestamp.isocalendar()[1]
            comp_year = comp.timestamp.isocalendar()[0]

            if comp_year == current_year and comp_week == current_week:
                streak += 1
                current_week -= 1
                if current_week == 0:
                    current_year -= 1
                    current_week = 52
            else:
                break

    return streak


def calculate_longest_streak(habit: BaseHabit) -> int:
    """Calculate the longest streak for a habit"""
    if not habit.completion_records:
        return 0

    completions = sorted(habit.completion_records, key=lambda x: x.timestamp)

    if len(completions) == 1:
        return 1

    streaks = []
    current_streak = 1

    for i in range(1, len(completions)):
        if habit.periodicity == Periodicity.DAILY:
            # Daily habit: consecutive days
            gap = (completions[i].timestamp.date() - completions[i - 1].timestamp.date()).days
            if gap == 1:
                current_streak += 1
            else:
                streaks.append(current_streak)
                current_streak = 1
        else:
            # Weekly habit: consecutive weeks
            prev_week = completions[i - 1].timestamp.isocalendar()[1]
            curr_week = completions[i].timestamp.isocalendar()[1]
            prev_year = completions[i - 1].timestamp.isocalendar()[0]
            curr_year = completions[i].timestamp.isocalendar()[0]

            # Check if consecutive weeks (handling year boundaries)
            if (curr_year == prev_year and curr_week - prev_week == 1) or \
                    (curr_year == prev_year + 1 and curr_week == 1 and prev_week == 52):
                current_streak += 1
            else:
                streaks.append(current_streak)
                current_streak = 1

    streaks.append(current_streak)
    return max(streaks) if streaks else 1


def get_habits_by_periodicity(habits: List[BaseHabit], periodicity: Periodicity) -> List[BaseHabit]:
    """Filter habits by periodicity"""
    return [habit for habit in habits if habit.periodicity == periodicity]


def overall_longest_streak(habits: List[BaseHabit]) -> Dict[str, Any]:
    """Find the habit with the longest streak across all habits"""
    if not habits:
        return {"habit": None, "streak": 0}

    streak_data = []
    for habit in habits:
        streak = calculate_longest_streak(habit)
        streak_data.append({
            "habit": habit,
            "streak": streak
        })

    return max(streak_data, key=lambda x: x["streak"])


def get_completion_statistics(habits: List[BaseHabit]) -> Dict[str, Any]:
    """Get comprehensive completion statistics"""
    total_completions = sum(len(habit.completion_records) for habit in habits)
    daily_habits = get_habits_by_periodicity(habits, Periodicity.DAILY)
    weekly_habits = get_habits_by_periodicity(habits, Periodicity.WEEKLY)

    avg_completions = total_completions / len(habits) if habits else 0

    return {
        "total_habits": len(habits),
        "daily_habits": len(daily_habits),
        "weekly_habits": len(weekly_habits),
        "total_completions": total_completions,
        "avg_completions_per_habit": avg_completions
    }