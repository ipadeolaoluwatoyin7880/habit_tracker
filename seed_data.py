# seed_data.py
"""
Database Seeding Script
Populates the database with sample data for testing and demonstration.
"""

import sys
import os

# Add src to Python path to enable imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.storage.db import DatabaseHandler, Periodicity
from src.data_model.completion import Completion
from datetime import datetime, timedelta
import random


def seed_sample_data():
    """Seed the database with sample data for testing"""
    db = DatabaseHandler()

    # Create a sample user
    try:
        user_id = db.create_user("demo", "demo@example.com", "demo123")
        print(f"✅ Created demo user with ID: {user_id}")
    except Exception as e:
        print(f"⚠️  Demo user may already exist: {e}")
        # Try to get existing user
        user = db.get_user_by_username("demo")
        if user:
            user_id = user.user_id
            print(f"✅ Using existing demo user with ID: {user_id}")
        else:
            print("❌ Failed to create or find demo user")
            return

    # Create sample habits
    habits = [
        ("Morning Meditation", Periodicity.DAILY),
        ("Evening Journal", Periodicity.DAILY),
        ("Weekly Planning", Periodicity.WEEKLY),
        ("Exercise 3x", Periodicity.WEEKLY),
        ("Read 10 Pages", Periodicity.DAILY)
    ]

    habit_ids = []
    for name, periodicity in habits:
        try:
            habit_id = db.save_habit(user_id, name, periodicity)
            habit_ids.append(habit_id)
            print(f"✅ Created habit: {name} ({periodicity})")
        except Exception as e:
            print(f"⚠️  Habit '{name}' may already exist: {e}")

    # Generate 4 weeks of sample data
    end_date = datetime.now()
    start_date = end_date - timedelta(weeks=4)

    print("\n📊 Generating sample completion data...")

    current_date = start_date
    completion_count = 0

    while current_date <= end_date:
        for i, habit_id in enumerate(habit_ids):
            habit = db.get_habit_by_id(habit_id)

            if not habit:
                continue

            # Only add completions on appropriate days
            if habit['periodicity'] == 'daily':
                # Skip some days randomly to make it realistic (70% completion rate)
                if random.random() > 0.3:
                    try:
                        completion = Completion(
                            timestamp=current_date.replace(
                                hour=random.randint(8, 20),
                                minute=random.randint(0, 59)
                            ),
                            notes=f"Completed on {current_date.strftime('%Y-%m-%d')}",
                            mood_score=random.randint(5, 10)
                        )
                        db.save_completion(habit_id, completion)
                        completion_count += 1
                    except Exception as e:
                        print(f"⚠️  Error creating completion: {e}")

            elif habit['periodicity'] == 'weekly' and current_date.weekday() == 0:  # Monday
                try:
                    completion = Completion(
                        timestamp=current_date.replace(
                            hour=random.randint(8, 20),
                            minute=random.randint(0, 59)
                        ),
                        notes=f"Weekly completion for week {current_date.strftime('%U')}",
                        mood_score=random.randint(6, 10)
                    )
                    db.save_completion(habit_id, completion)
                    completion_count += 1
                except Exception as e:
                    print(f"⚠️  Error creating weekly completion: {e}")

        current_date += timedelta(days=1)

    print(f"\n🎉 Sample data seeded successfully!")
    print(f"📈 Created {len(habit_ids)} habits with {completion_count} completion records")
    print("🔑 You can now login with:")
    print("   Username: 'demo'")
    print("   Password: 'demo123'")


if __name__ == "__main__":
    seed_sample_data()