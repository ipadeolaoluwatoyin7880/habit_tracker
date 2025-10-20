# src/data_model/habit.py
from abc import ABC, abstractmethod
from datetime import datetime, date
from typing import List, Optional
from enum import Enum

# Import from other packages within src
from ..storage.db import Periodicity
from .completion import Completion


class BaseHabit(ABC):
    """Abstract base class for all habits"""

    def __init__(self, habit_id: int, name: str, periodicity: Periodicity,
                 created_date: datetime, is_active: bool = True):
        self.habit_id = habit_id
        self.name = name
        self.periodicity = periodicity
        self.created_date = created_date
        self.is_active = is_active
        self._completion_records: List[Completion] = []

    @abstractmethod
    def is_due_on(self, target_date: datetime) -> bool:
        """Check if habit is due on the given date"""
        pass

    def check_off(self, notes: str = None, mood_score: int = None) -> Completion:
        """
        Create a completion record for this habit

        Args:
            notes: Optional notes about the completion
            mood_score: Optional mood score (1-10)

        Returns:
            Completion object
        """
        completion = Completion(datetime.now(), notes, mood_score)
        self._completion_records.append(completion)
        return completion

    def get_last_completion_date(self) -> Optional[datetime]:
        """Get the most recent completion date"""
        if not self._completion_records:
            return None
        return max(comp.timestamp for comp in self._completion_records)

    def get_completion_records(self) -> List[Completion]:
        """Get all completion records"""
        return self._completion_records.copy()

    def set_completion_records(self, completions: List[Completion]):
        """Set completion records (used when loading from database)"""
        self._completion_records = completions

    def activate(self):
        """Activate the habit"""
        self.is_active = True

    def deactivate(self):
        """Deactivate the habit"""
        self.is_active = False

    def __str__(self):
        status = "Active" if self.is_active else "Inactive"
        return f"{self.name} ({self.periodicity.value}) - {status}"

    def __repr__(self):
        return f"{self.__class__.__name__}(id={self.habit_id}, name='{self.name}')"


class DailyHabit(BaseHabit):
    """Daily habit that needs to be completed every day"""

    def __init__(self, habit_id: int, name: str, created_date: datetime, is_active: bool = True):
        super().__init__(habit_id, name, Periodicity.DAILY, created_date, is_active)

    def is_due_on(self, target_date: datetime) -> bool:
        """
        Check if daily habit is due on target date.
        A daily habit is due if it hasn't been completed on the target date.
        """
        if not self.is_active:
            return False

        # Check if habit was already completed on target date
        target_date_only = target_date.date()
        for completion in self._completion_records:
            if completion.timestamp.date() == target_date_only:
                return False

        return True


class WeeklyHabit(BaseHabit):
    """Weekly habit that needs to be completed once per week"""

    def __init__(self, habit_id: int, name: str, created_date: datetime, is_active: bool = True):
        super().__init__(habit_id, name, Periodicity.WEEKLY, created_date, is_active)

    def is_due_on(self, target_date: datetime) -> bool:
        """
        Check if weekly habit is due on target date.
        A weekly habit is due if it hasn't been completed in the target week.
        """
        if not self.is_active:
            return False

        target_year, target_week, _ = target_date.isocalendar()

        # Check if habit was already completed in the target week
        for completion in self._completion_records:
            comp_year, comp_week, _ = completion.timestamp.isocalendar()
            if comp_year == target_year and comp_week == target_week:
                return False

        return True


class HabitFactory:
    """Factory class to create habit objects from database data"""

    @staticmethod
    def create_habit_from_db(data: dict, completions: List[Completion] = None) -> BaseHabit:
        """
        Create a habit object from database data

        Args:
            data: Dictionary containing habit data from database
            completions: List of completion records for this habit

        Returns:
            Appropriate habit object (DailyHabit or WeeklyHabit)
        """
        habit_id = data['habit_id']
        name = data['name']
        periodicity = Periodicity(data['periodicity'])

        # Handle both string and datetime objects for created_at
        created_at = data['created_at']
        if isinstance(created_at, str):
            created_date = datetime.fromisoformat(created_at)
        else:
            # It's already a datetime object
            created_date = created_at

        is_active = bool(data['is_active'])

        if completions is None:
            completions = []

        if periodicity == Periodicity.DAILY:
            habit = DailyHabit(habit_id, name, created_date, is_active)
        else:
            habit = WeeklyHabit(habit_id, name, created_date, is_active)

        habit.set_completion_records(completions)
        return habit