from typing import List, Optional
from src.data_model.habit import BaseHabit, Periodicity, create_habit
from src.storage.db import DatabaseHandler, PROD_DB_PATH


class HabitManager:
    def __init__(self, db_path: str = None):
        # Use production DB by default
        if db_path is None:
            self.db_path = PROD_DB_PATH
        else:
            self.db_path = db_path

        self.db = DatabaseHandler(self.db_path)
        self.habits: List[BaseHabit] = []
        self.load_habits()

    def load_habits(self):
        """Load habits from database"""
        db_habits = self.db.get_all_habits()
        for habit_data in db_habits:
            periodicity_enum = Periodicity(habit_data['periodicity'])
            habit = create_habit(habit_data['name'], periodicity_enum, habit_data['created_at'])

            # Load completions
            completions_data = self.db.get_completions_for_habit(habit_data['habit_id'])
            for comp_data in completions_data:
                # Create completion record
                completion = habit.check_off(
                    notes=comp_data['notes'],
                    mood_score=comp_data['mood_score']
                )
                # Set the actual timestamp from database
                completion.timestamp = comp_data['timestamp']

            self.habits.append(habit)

    def create_habit(self, name: str, periodicity: Periodicity) -> BaseHabit:
        """Create a new habit and save to database"""
        # Create in-memory habit object
        habit = create_habit(name, periodicity)

        # Save to database
        habit_id = self.db.save_habit(name, periodicity.value)

        # Add to managed habits
        self.habits.append(habit)

        return habit

    def check_off_habit(self, habit_name: str, notes: str = "", mood_score: int = None) -> bool:
        """Check off a habit as completed"""
        habit = self.get_habit_by_name(habit_name)
        if not habit:
            return False

        # Create completion
        completion = habit.check_off(notes, mood_score)

        # Save to database
        self.db.save_completion(
            habit_id=self._get_habit_id(habit_name),
            timestamp=completion.timestamp,
            notes=notes,
            mood_score=mood_score
        )

        return True

    def _get_habit_id(self, habit_name: str) -> Optional[int]:
        """Get database ID for a habit by name"""
        db_habits = self.db.get_all_habits()
        for habit_data in db_habits:
            if habit_data['name'] == habit_name:
                return habit_data['habit_id']
        return None

    def get_habit_by_name(self, name: str) -> Optional[BaseHabit]:
        """Get a habit by its name"""
        for habit in self.habits:
            if habit.name == name:
                return habit
        return None

    def get_all_habits(self) -> List[BaseHabit]:
        """Get all managed habits"""
        return self.habits

    def get_habits_by_periodicity(self, periodicity: Periodicity) -> List[BaseHabit]:
        """Get habits filtered by periodicity"""
        return [habit for habit in self.habits if habit.periodicity == periodicity]

    def get_daily_habits(self) -> List[BaseHabit]:
        """Get all daily habits"""
        return self.get_habits_by_periodicity(Periodicity.DAILY)

    def get_weekly_habits(self) -> List[BaseHabit]:
        """Get all weekly habits"""
        return self.get_habits_by_periodicity(Periodicity.WEEKLY)

    def deactivate_habit(self, habit_name: str) -> bool:
        """Deactivate a habit"""
        habit = self.get_habit_by_name(habit_name)
        if habit:
            habit.deactivate()
            habit_id = self._get_habit_id(habit_name)
            if habit_id:
                self.db.deactivate_habit(habit_id)
            return True
        return False