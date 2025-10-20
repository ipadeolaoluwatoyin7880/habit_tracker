# src/managers/habit_manager.py
from typing import List, Optional, Dict, Any
from datetime import datetime

# Import from other packages within src
from src.storage.db import DatabaseHandler, Periodicity
from src.data_model.completion import Completion
from src.data_model.habit import BaseHabit, DailyHabit, WeeklyHabit, HabitFactory


class HabitManager:
    """Manages habit operations and business logic"""

    def __init__(self, db_path: str = "habits.db"):
        """
        Initialize HabitManager with database connection

        Args:
            db_path: Path to SQLite database file
        """
        self.db_handler = DatabaseHandler(db_path)
        self.current_user_id = None

    def set_current_user(self, user_id: int):
        """Set the current user for all operations"""
        self.current_user_id = user_id

    def create_habit(self, name: str, periodicity: Periodicity) -> BaseHabit:
        """
        Create a new habit for the current user

        Args:
            name: Name of the habit
            periodicity: Periodicity (DAILY or WEEKLY)

        Returns:
            Created habit object

        Raises:
            ValueError: If no user is logged in or habit name is empty
        """
        if not self.current_user_id:
            raise ValueError("No user logged in. Please login first.")

        if not name or not name.strip():
            raise ValueError("Habit name cannot be empty")

        # Save to database
        habit_id = self.db_handler.save_habit(self.current_user_id, name.strip(), periodicity)

        # Create habit object
        created_date = datetime.now()
        if periodicity == Periodicity.DAILY:
            return DailyHabit(habit_id, name, created_date)
        else:
            return WeeklyHabit(habit_id, name, created_date)

    def get_all_habits(self, active_only: bool = True) -> List[BaseHabit]:
        """
        Get all habits for the current user

        Args:
            active_only: If True, only return active habits

        Returns:
            List of habit objects
        """
        if not self.current_user_id:
            raise ValueError("No user logged in")

        habits_data = self.db_handler.get_habits_for_user(self.current_user_id, active_only)
        habits = []

        for habit_data in habits_data:
            # Load completions for this habit
            completions = self.db_handler.get_completions_for_habit(habit_data['habit_id'])
            # Create habit object
            habit = HabitFactory.create_habit_from_db(habit_data, completions)
            habits.append(habit)

        return habits

    def get_habit_by_id(self, habit_id: int) -> Optional[BaseHabit]:
        """
        Get a specific habit by ID

        Args:
            habit_id: ID of the habit to retrieve

        Returns:
            Habit object if found, None otherwise
        """
        habit_data = self.db_handler.get_habit_by_id(habit_id)
        if not habit_data:
            return None

        # Verify the habit belongs to current user
        if habit_data['user_id'] != self.current_user_id:
            return None

        completions = self.db_handler.get_completions_for_habit(habit_id)
        return HabitFactory.create_habit_from_db(habit_data, completions)

    def delete_habit(self, habit_id: int) -> bool:
        """
        Soft delete a habit (set is_active to False)

        Args:
            habit_id: ID of the habit to delete

        Returns:
            True if successful, False otherwise
        """
        # Verify the habit belongs to current user
        habit = self.get_habit_by_id(habit_id)
        if not habit:
            return False

        return self.db_handler.delete_habit(habit_id)

    def check_off_habit(self, habit_id: int, notes: str = None, mood_score: int = None) -> bool:
        """
        Check off a habit (create completion record)

        Args:
            habit_id: ID of the habit to check off
            notes: Optional notes about the completion
            mood_score: Optional mood score (1-10)

        Returns:
            True if successful, False otherwise
        """
        habit = self.get_habit_by_id(habit_id)
        if not habit or not habit.is_active:
            return False

        # Check if habit is due
        if not habit.is_due_on(datetime.now()):
            return False

        # Create completion
        completion = habit.check_off(notes, mood_score)

        # Save to database
        try:
            self.db_handler.save_completion(habit_id, completion)
            return True
        except Exception as e:
            print(f"Error saving completion: {e}")
            return False

    def get_habit_completions(self, habit_id: int, limit: int = None) -> List[Completion]:
        """
        Get completion records for a specific habit

        Args:
            habit_id: ID of the habit
            limit: Optional limit on number of completions to return

        Returns:
            List of completion records
        """
        return self.db_handler.get_completions_for_habit(habit_id, limit)

    def get_user_completions(self, days: int = None) -> List[dict]:
        """
        Get all completions for the current user

        Args:
            days: Optional number of days to look back

        Returns:
            List of completion records with habit information
        """
        if not self.current_user_id:
            return []

        return self.db_handler.get_completions_for_user(self.current_user_id, days)