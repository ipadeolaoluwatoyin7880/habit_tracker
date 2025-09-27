import os
import sqlite3
from datetime import datetime
from typing import List, Dict, Any

# Database paths
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATA_DIR = os.path.join(PROJECT_ROOT, 'data')
TEST_DATA_DIR = os.path.join(PROJECT_ROOT, 'tests', 'test_data')

# Create directories if they don't exist
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(TEST_DATA_DIR, exist_ok=True)

# Database file paths
PROD_DB_PATH = os.path.join(DATA_DIR, 'habits.db')


class DatabaseHandler:
    def __init__(self, db_path: str = None):
        # Use production DB by default, or custom path for testing
        if db_path is None:
            self.db_path = PROD_DB_PATH
        else:
            self.db_path = db_path

        self.init_database()

    def init_database(self):
        """Initialize database tables"""
        with sqlite3.connect(self.db_path) as conn:
            # Habits table
            conn.execute('''
                         CREATE TABLE IF NOT EXISTS habits
                         (
                             habit_id
                             INTEGER
                             PRIMARY
                             KEY
                             AUTOINCREMENT,
                             name
                             TEXT
                             NOT
                             NULL,
                             periodicity
                             TEXT
                             NOT
                             NULL
                             CHECK (
                             periodicity
                             IN
                         (
                             'daily',
                             'weekly'
                         )),
                             created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                             is_active BOOLEAN DEFAULT TRUE
                             )
                         ''')

            # Completions table
            conn.execute('''
                         CREATE TABLE IF NOT EXISTS completions
                         (
                             completion_id
                             INTEGER
                             PRIMARY
                             KEY
                             AUTOINCREMENT,
                             habit_id
                             INTEGER
                             NOT
                             NULL,
                             timestamp
                             DATETIME
                             NOT
                             NULL,
                             notes
                             TEXT,
                             mood_score
                             INTEGER
                             CHECK
                         (
                             mood_score
                             >=
                             1
                             AND
                             mood_score
                             <=
                             10
                         ),
                             FOREIGN KEY
                         (
                             habit_id
                         ) REFERENCES habits
                         (
                             habit_id
                         ) ON DELETE CASCADE
                             )
                         ''')

    def save_habit(self, name: str, periodicity: str) -> int:
        """Save a new habit to database and return its ID"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                'INSERT INTO habits (name, periodicity) VALUES (?, ?)',
                (name, periodicity)
            )
            conn.commit()
            return cursor.lastrowid

    def save_completion(self, habit_id: int, timestamp: datetime, notes: str = "", mood_score: int = None):
        """Save a completion record for a habit"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                'INSERT INTO completions (habit_id, timestamp, notes, mood_score) VALUES (?, ?, ?, ?)',
                (habit_id, timestamp, notes, mood_score)
            )
            conn.commit()

    def get_all_habits(self) -> List[Dict[str, Any]]:
        """Get all active habits from database"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                'SELECT habit_id, name, periodicity, created_at FROM habits WHERE is_active = TRUE'
            )
            columns = [column[0] for column in cursor.description]
            return [dict(zip(columns, row)) for row in cursor.fetchall()]

    def get_completions_for_habit(self, habit_id: int) -> List[Dict[str, Any]]:
        """Get all completions for a specific habit"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                'SELECT completion_id, habit_id, timestamp, notes, mood_score FROM completions WHERE habit_id = ? ORDER BY timestamp',
                (habit_id,)
            )
            columns = [column[0] for column in cursor.description]
            return [dict(zip(columns, row)) for row in cursor.fetchall()]

    def deactivate_habit(self, habit_id: int):
        """Deactivate a habit (soft delete)"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                'UPDATE habits SET is_active = FALSE WHERE habit_id = ?',
                (habit_id,)
            )
            conn.commit()

    def clear_all_data(self):
        """Clear all data (for testing)"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('DELETE FROM completions')
            conn.execute('DELETE FROM habits')
            conn.commit()

    # Alias for backward compatibility
    reset_db = clear_all_data