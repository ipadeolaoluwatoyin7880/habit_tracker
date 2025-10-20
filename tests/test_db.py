# tests/test_db.py
import pytest
from datetime import datetime, timedelta
from src.storage.db import DatabaseHandler, Periodicity, Completion, User


class TestDatabaseHandler:
    """Test database operations"""

    def test_init_database(self, test_db):
        """Test database initialization"""
        db_handler, db_path = test_db

        # Verify tables are created
        with db_handler._get_connection() as conn:
            tables = conn.execute("""
                                  SELECT name
                                  FROM sqlite_master
                                  WHERE type = 'table'
                                    AND name IN ('users', 'habits', 'completions')
                                  """).fetchall()

            table_names = [table['name'] for table in tables]
            assert 'users' in table_names
            assert 'habits' in table_names
            assert 'completions' in table_names

    def test_create_user(self, test_db):
        """Test user creation"""
        db_handler, db_path = test_db

        user_id = db_handler.create_user("testuser", "test@example.com", "password123")
        assert user_id is not None
        assert isinstance(user_id, int)

        # Verify user can be retrieved
        user = db_handler.get_user_by_username("testuser")
        assert user is not None
        assert user.username == "testuser"
        assert user.email == "test@example.com"

    def test_verify_user_credentials(self, test_db):
        """Test user credential verification"""
        db_handler, db_path = test_db

        db_handler.create_user("testuser", "test@example.com", "password123")

        # Test valid credentials
        user = db_handler.verify_user_credentials("testuser", "password123")
        assert user is not None
        assert user.username == "testuser"

        # Test invalid password
        user = db_handler.verify_user_credentials("testuser", "wrongpassword")
        assert user is None

        # Test non-existent user
        user = db_handler.verify_user_credentials("nonexistent", "password123")
        assert user is None

    def test_save_habit(self, test_db, test_user):
        """Test habit saving"""
        db_handler, db_path = test_db

        habit_id = db_handler.save_habit(test_user, "Test Habit", Periodicity.DAILY)
        assert habit_id is not None

        # Verify habit can be retrieved
        habit_data = db_handler.get_habit_by_id(habit_id)
        assert habit_data is not None
        assert habit_data['name'] == "Test Habit"
        assert habit_data['periodicity'] == 'daily'
        assert habit_data['user_id'] == test_user

    def test_get_habits_for_user(self, test_db, test_user):
        """Test retrieving habits for user"""
        db_handler, db_path = test_db

        # Create multiple habits
        habit1_id = db_handler.save_habit(test_user, "Habit 1", Periodicity.DAILY)
        habit2_id = db_handler.save_habit(test_user, "Habit 2", Periodicity.WEEKLY)

        habits = db_handler.get_habits_for_user(test_user)
        assert len(habits) == 2
        habit_names = [habit['name'] for habit in habits]
        assert "Habit 1" in habit_names
        assert "Habit 2" in habit_names

    def test_save_completion(self, test_db, test_user):
        """Test completion saving"""
        db_handler, db_path = test_db

        habit_id = db_handler.save_habit(test_user, "Test Habit", Periodicity.DAILY)
        completion = Completion(datetime.now(), "Test notes", 8)

        completion_id = db_handler.save_completion(habit_id, completion)
        assert completion_id is not None

        # Verify completion can be retrieved
        completions = db_handler.get_completions_for_habit(habit_id)
        assert len(completions) == 1
        assert completions[0].notes == "Test notes"
        assert completions[0].mood_score == 8

    def test_completion_validation(self, test_db, test_user):
        """Test completion validation"""
        db_handler, db_path = test_db

        habit_id = db_handler.save_habit(test_user, "Test Habit", Periodicity.DAILY)

        # Test future timestamp validation
        future_date = datetime.now() + timedelta(days=1)
        with pytest.raises(ValueError, match="cannot be in the future"):
            completion = Completion(future_date, "Future completion")
            db_handler.save_completion(habit_id, completion)

        # Test mood score validation
        with pytest.raises(ValueError, match="must be between 1 and 10"):
            completion = Completion(datetime.now(), "Invalid mood", 15)
            db_handler.save_completion(habit_id, completion)

    def test_soft_delete_habit(self, test_db, test_user):
        """Test habit soft deletion"""
        db_handler, db_path = test_db

        habit_id = db_handler.save_habit(test_user, "Test Habit", Periodicity.DAILY)

        # Verify habit is active initially
        habit_data = db_handler.get_habit_by_id(habit_id)
        assert habit_data['is_active'] == True

        # Soft delete habit
        success = db_handler.delete_habit(habit_id)
        assert success is True

        # Verify habit is inactive
        habit_data = db_handler.get_habit_by_id(habit_id)
        assert habit_data['is_active'] == False

        # Test getting only active habits
        active_habits = db_handler.get_habits_for_user(test_user, active_only=True)
        assert len(active_habits) == 0

        # Test getting all habits (including inactive)
        all_habits = db_handler.get_habits_for_user(test_user, active_only=False)
        assert len(all_habits) == 1

    def test_user_password_hashing(self, test_db):
        """Test password hashing and verification"""
        db_handler, db_path = test_db

        user_id = db_handler.create_user("testuser", "test@example.com", "mysecretpassword")
        user = db_handler.get_user_by_username("testuser")

        # Verify password is hashed (not stored in plain text)
        assert user.password_hash != "mysecretpassword"
        assert '$' in user.password_hash  # Should contain salt

        # Verify correct password works
        assert user.verify_password("mysecretpassword") is True

        # Verify incorrect password fails
        assert user.verify_password("wrongpassword") is False