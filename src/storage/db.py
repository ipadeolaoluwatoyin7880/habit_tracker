# src/storage/db.py
import sqlite3
import hashlib
import secrets
from datetime import datetime
from typing import List, Optional, Tuple
from enum import Enum

# Import from other packages within src
from src.data_model.completion import Completion


# Fix for Python 3.12 datetime adapter deprecation
def adapt_datetime(dt):
    return dt.isoformat()


def convert_datetime(timestamp):
    if isinstance(timestamp, bytes):
        return datetime.fromisoformat(timestamp.decode())
    else:
        return datetime.fromisoformat(timestamp)


# Register the adapter and converter
sqlite3.register_adapter(datetime, adapt_datetime)
sqlite3.register_converter("DATETIME", convert_datetime)


class Periodicity(Enum):
    DAILY = "daily"
    WEEKLY = "weekly"

    def __str__(self):
        return self.value


class User:
    """User entity class with authentication support"""

    def __init__(self, user_id: int, username: str, email: str, password_hash: str, created_at: datetime):
        self.user_id = user_id
        self.username = username
        self.email = email
        self.password_hash = password_hash
        self.created_at = created_at

    @classmethod
    def create(cls, username: str, email: str, password: str) -> 'User':
        """Create a new user with hashed password"""
        salt = secrets.token_hex(16)
        password_hash = cls._hash_password(password, salt)
        created_at = datetime.now()
        return cls(None, username, email, f"{salt}${password_hash}", created_at)

    def verify_password(self, password: str) -> bool:
        """Verify password against stored hash"""
        try:
            salt, stored_hash = self.password_hash.split('$')
            return self._hash_password(password, salt) == stored_hash
        except:
            return False

    @staticmethod
    def _hash_password(password: str, salt: str) -> str:
        """Hash password with salt using SHA-256"""
        return hashlib.sha256(f"{salt}{password}".encode()).hexdigest()

    def to_dict(self) -> dict:
        """Convert user to dictionary (without password)"""
        return {
            'user_id': self.user_id,
            'username': self.username,
            'email': self.email,
            'created_at': self.created_at.isoformat()
        }


class DatabaseHandler:
    """Enhanced database handler with user support and proper error handling"""

    def __init__(self, db_path: str = "habits.db"):
        self.db_path = db_path
        self.init_database()

    def _get_connection(self) -> sqlite3.Connection:
        """Get database connection with proper settings"""
        # Use detect_types for proper datetime handling
        conn = sqlite3.connect(self.db_path, detect_types=sqlite3.PARSE_DECLTYPES)
        conn.row_factory = sqlite3.Row
        # Enable foreign keys
        conn.execute("PRAGMA foreign_keys = ON")
        return conn

    def init_database(self):
        """Initialize database with all required tables"""
        with self._get_connection() as conn:
            # Users table
            conn.execute('''
                         CREATE TABLE IF NOT EXISTS users
                         (
                             user_id
                             INTEGER
                             PRIMARY
                             KEY
                             AUTOINCREMENT,
                             username
                             TEXT
                             UNIQUE
                             NOT
                             NULL,
                             email
                             TEXT
                             UNIQUE
                             NOT
                             NULL,
                             password_hash
                             TEXT
                             NOT
                             NULL,
                             created_at
                             DATETIME
                             DEFAULT
                             CURRENT_TIMESTAMP
                         )
                         ''')

            # Habits table with foreign key to users
            conn.execute('''
                         CREATE TABLE IF NOT EXISTS habits
                         (
                             habit_id
                             INTEGER
                             PRIMARY
                             KEY
                             AUTOINCREMENT,
                             user_id
                             INTEGER
                             NOT
                             NULL,
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
                             is_active BOOLEAN DEFAULT TRUE,
                             FOREIGN KEY
                         (
                             user_id
                         ) REFERENCES users
                         (
                             user_id
                         ) ON DELETE CASCADE,
                             UNIQUE
                         (
                             user_id,
                             name
                         )
                             )
                         ''')

            # Completions table with foreign key to habits
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
                             BETWEEN
                             1
                             AND
                             10
                             OR
                             mood_score
                             IS
                             NULL
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

            # Create indexes for better performance
            conn.execute('CREATE INDEX IF NOT EXISTS idx_habits_user_id ON habits(user_id)')
            conn.execute('CREATE INDEX IF NOT EXISTS idx_completions_habit_id ON completions(habit_id)')
            conn.execute('CREATE INDEX IF NOT EXISTS idx_completions_timestamp ON completions(timestamp)')

            conn.commit()
            print(f"✅ Database initialized successfully at: {self.db_path}")

    # User management methods
    def create_user(self, username: str, email: str, password: str) -> int:
        """Create a new user and return user_id"""
        user = User.create(username, email, password)

        with self._get_connection() as conn:
            cursor = conn.execute(
                'INSERT INTO users (username, email, password_hash, created_at) VALUES (?, ?, ?, ?)',
                (user.username, user.email, user.password_hash, user.created_at)
            )
            user_id = cursor.lastrowid
            conn.commit()
            return user_id

    def get_user_by_username(self, username: str) -> Optional[User]:
        """Get user by username"""
        with self._get_connection() as conn:
            row = conn.execute(
                'SELECT * FROM users WHERE username = ?',
                (username,)
            ).fetchone()

            if row:
                return User(
                    user_id=row['user_id'],
                    username=row['username'],
                    email=row['email'],
                    password_hash=row['password_hash'],
                    created_at=datetime.fromisoformat(row['created_at']) if isinstance(row['created_at'], str) else row[
                        'created_at']
                )
            return None

    def verify_user_credentials(self, username: str, password: str) -> Optional[User]:
        """Verify user credentials and return user if valid"""
        user = self.get_user_by_username(username)
        if user and user.verify_password(password):
            return user
        return None

    # Habit management methods
    def save_habit(self, user_id: int, name: str, periodicity: Periodicity) -> int:
        """Save a new habit and return habit_id"""
        with self._get_connection() as conn:
            cursor = conn.execute(
                'INSERT INTO habits (user_id, name, periodicity) VALUES (?, ?, ?)',
                (user_id, name, periodicity.value)
            )
            habit_id = cursor.lastrowid
            conn.commit()
            return habit_id

    def get_habits_for_user(self, user_id: int, active_only: bool = True) -> List[dict]:
        """Get all habits for a specific user"""
        query = '''
                SELECT h.*,
                       COUNT(c.completion_id) as completion_count,
                       MAX(c.timestamp)       as last_completion
                FROM habits h
                         LEFT JOIN completions c ON h.habit_id = c.habit_id
                WHERE h.user_id = ? \
                '''

        if active_only:
            query += ' AND h.is_active = TRUE'

        query += ' GROUP BY h.habit_id ORDER BY h.created_at DESC'

        with self._get_connection() as conn:
            rows = conn.execute(query, (user_id,)).fetchall()
            return [dict(row) for row in rows]

    def get_habit_by_id(self, habit_id: int) -> Optional[dict]:
        """Get a specific habit by ID"""
        with self._get_connection() as conn:
            row = conn.execute(
                'SELECT * FROM habits WHERE habit_id = ?',
                (habit_id,)
            ).fetchone()
            return dict(row) if row else None

    def delete_habit(self, habit_id: int) -> bool:
        """Soft delete a habit by setting is_active to FALSE"""
        with self._get_connection() as conn:
            cursor = conn.execute(
                'UPDATE habits SET is_active = FALSE WHERE habit_id = ?',
                (habit_id,)
            )
            conn.commit()
            return cursor.rowcount > 0

    # Completion management methods
    def save_completion(self, habit_id: int, completion: Completion) -> int:
        """Save a completion record and return completion_id"""
        with self._get_connection() as conn:
            cursor = conn.execute(
                'INSERT INTO completions (habit_id, timestamp, notes, mood_score) VALUES (?, ?, ?, ?)',
                (habit_id, completion.timestamp, completion.notes, completion.mood_score)
            )
            completion_id = cursor.lastrowid
            conn.commit()
            return completion_id

    def get_completions_for_habit(self, habit_id: int, limit: int = None) -> List[Completion]:
        """Get all completions for a specific habit"""
        query = 'SELECT * FROM completions WHERE habit_id = ? ORDER BY timestamp DESC'
        params = [habit_id]

        if limit:
            query += ' LIMIT ?'
            params.append(limit)

        with self._get_connection() as conn:
            rows = conn.execute(query, params).fetchall()
            completions = []
            for row in rows:
                timestamp = row['timestamp']
                if isinstance(timestamp, str):
                    timestamp = datetime.fromisoformat(timestamp)

                completion = Completion(
                    timestamp=timestamp,
                    notes=row['notes'],
                    mood_score=row['mood_score']
                )
                completions.append(completion)
            return completions

    def get_completions_for_user(self, user_id: int, days: int = None) -> List[dict]:
        """Get all completions for a user, optionally filtered by days"""
        query = '''
                SELECT c.*, h.name as habit_name, h.periodicity
                FROM completions c
                         JOIN habits h ON c.habit_id = h.habit_id
                WHERE h.user_id = ? \
                '''
        params = [user_id]

        if days:
            query += ' AND c.timestamp >= datetime("now", ?)'
            params.append(f'-{days} days')

        query += ' ORDER BY c.timestamp DESC'

        with self._get_connection() as conn:
            rows = conn.execute(query, params).fetchall()
            return [dict(row) for row in rows]

    # Analytics helper methods
    def get_streak_data(self, habit_id: int) -> List[datetime]:
        """Get sorted completion dates for streak calculations"""
        with self._get_connection() as conn:
            rows = conn.execute(
                'SELECT timestamp FROM completions WHERE habit_id = ? ORDER BY timestamp',
                (habit_id,)
            ).fetchall()

            dates = []
            for row in rows:
                timestamp = row['timestamp']
                if isinstance(timestamp, str):
                    dates.append(datetime.fromisoformat(timestamp))
                else:
                    dates.append(timestamp)
            return dates


# Fresh database test - will create everything from scratch
if __name__ == "__main__":
    import os

    # Delete old test database if it exists
    if os.path.exists("test_habits.db"):
        os.unlink("test_habits.db")
        print("🗑️  Old test database deleted")

    # Create fresh database
    print("🚀 Creating fresh test database...")
    db = DatabaseHandler("test_habits.db")

    # Create a test user
    user_id = db.create_user("testuser", "test@example.com", "password123")
    print(f"✅ Created user with ID: {user_id}")

    # Verify login
    user = db.verify_user_credentials("testuser", "password123")
    if user:
        print(f"✅ Login successful for user: {user.username}")
    else:
        print("❌ Login failed")
        exit(1)

    # Create test habits
    habit1_id = db.save_habit(user_id, "Morning Meditation", Periodicity.DAILY)
    habit2_id = db.save_habit(user_id, "Weekly Exercise", Periodicity.WEEKLY)
    print(f"✅ Created habits with IDs: {habit1_id}, {habit2_id}")

    # Add some completions
    completion1 = Completion(datetime.now(), "Felt great!", 8)
    db.save_completion(habit1_id, completion1)
    print("✅ Added completion record")

    # Get user's habits
    habits = db.get_habits_for_user(user_id)
    print(f"✅ User has {len(habits)} habits")

    # Show habit details
    for habit in habits:
        completions = db.get_completions_for_habit(habit['habit_id'])
        print(f"   - {habit['name']} ({habit['periodicity']}): {len(completions)} completions")

    print("\n🎉 Fresh database test completed successfully!")
    print("💡 A brand new 'test_habits.db' has been created.")