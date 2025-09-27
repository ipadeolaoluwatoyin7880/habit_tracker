from abc import ABC, abstractmethod
from datetime import datetime, date
from typing import List, Optional
from enum import Enum


class Periodicity(Enum):
    DAILY = "daily"
    WEEKLY = "weekly"


class BaseHabit(ABC):
    def __init__(self, name: str, periodicity: Periodicity, created_date: datetime = None):
        self.name = name
        self.periodicity = periodicity
        self.created_date = created_date or datetime.now()
        self.completion_records: List['Completion'] = []
        self.is_active = True

    @abstractmethod
    def is_due_on(self, target_date: date) -> bool:
        pass

    def get_last_completion_date(self) -> Optional[date]:
        if not self.completion_records:
            return None
        return max(comp.timestamp.date() for comp in self.completion_records)

    def check_off(self, notes: str = "", mood_score: int = None) -> 'Completion':
        from src.data_model.completion import Completion
        completion = Completion(notes=notes, mood_score=mood_score)
        self.completion_records.append(completion)
        return completion

    def get_completion_records(self) -> List['Completion']:
        return self.completion_records.copy()

    def deactivate(self):
        self.is_active = False

    def activate(self):
        self.is_active = True

    def __str__(self):
        status = "✅" if self.is_active else "❌"
        return f"{status} {self.periodicity.value.upper()} - {self.name}"


class DailyHabit(BaseHabit):
    def __init__(self, name: str, created_date: datetime = None):
        super().__init__(name, Periodicity.DAILY, created_date)

    def is_due_on(self, target_date: date) -> bool:
        if target_date < self.created_date.date():
            return False

        last_completion = self.get_last_completion_date()
        if last_completion is None:
            return target_date >= self.created_date.date()

        return target_date > last_completion


class WeeklyHabit(BaseHabit):
    def __init__(self, name: str, created_date: datetime = None):
        super().__init__(name, Periodicity.WEEKLY, created_date)

    def is_due_on(self, target_date: date) -> bool:
        if target_date < self.created_date.date():
            return False

        last_completion = self.get_last_completion_date()
        if last_completion is None:
            creation_week = self.created_date.isocalendar()[1]
            target_week = target_date.isocalendar()[1]
            return target_week > creation_week

        last_week = last_completion.isocalendar()[1]
        target_week = target_date.isocalendar()[1]
        last_year = last_completion.isocalendar()[0]
        target_year = target_date.isocalendar()[0]

        if target_year > last_year:
            return True
        return target_week > last_week


def create_habit(name: str, periodicity: Periodicity, created_date: datetime = None) -> BaseHabit:
    if periodicity == Periodicity.DAILY:
        return DailyHabit(name, created_date)
    elif periodicity == Periodicity.WEEKLY:
        return WeeklyHabit(name, created_date)
    else:
        raise ValueError(f"Unsupported periodicity: {periodicity}")