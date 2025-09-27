import questionary
from datetime import datetime
from src.managers.habit_manager import HabitManager
from src.data_model.habit import Periodicity
from src.analytics.analytics_service import (
    calculate_current_streak,
    calculate_longest_streak,
    overall_longest_streak,
    get_completion_statistics
)


class UserInterface:
    def __init__(self):
        self.manager = HabitManager()
        self.current_user = None
        self.is_authenticated = False

    def login_menu(self):
        """Handle user authentication"""
        print("🔐 Habit Tracker Authentication")
        print("=" * 40)

        while not self.is_authenticated:
            choice = questionary.select(
                "Please choose an option:",
                choices=[
                    "👤 Login",
                    "📝 Register",
                    "🚶 Continue as Guest",
                    "❌ Exit"
                ]
            ).ask()

            if choice == "👤 Login":
                self.handle_login()
            elif choice == "📝 Register":
                self.handle_registration()
            elif choice == "🚶 Continue as Guest":
                self.handle_guest_mode()
            elif choice == "❌ Exit":
                print("Goodbye! 👋")
                exit()

    def handle_login(self):
        """Handle user login"""
        username = questionary.text("Enter your username:").ask()

        if username:
            self.current_user = username
            self.is_authenticated = True
            print(f"✅ Welcome back, {username}! 👋")
        else:
            print("❌ Username cannot be empty!")

    def handle_registration(self):
        """Handle new user registration"""
        print("\n📝 Create a New Account")
        username = questionary.text("Choose a username:").ask()

        if not username:
            print("❌ Username cannot be empty!")
            return

        self.current_user = username
        self.is_authenticated = True
        print(f"✅ Account created successfully! Welcome, {username}! 🎉")

    def handle_guest_mode(self):
        """Handle guest user access"""
        self.current_user = "Guest"
        self.is_authenticated = True
        print("👋 Welcome, Guest! You're in demo mode.")

    def main_menu(self):
        """Main application menu after authentication"""
        print(f"\n{'=' * 50}")
        print(f"🚀 HABIT TRACKER DASHBOARD")
        print(f"👤 User: {self.current_user}")
        print(f"{'=' * 50}")

        while True:
            choice = questionary.select(
                "What would you like to do?",
                choices=[
                    "📋 View All Habits",
                    "➕ Create New Habit",
                    "✅ Check Off Habit",
                    "📊 Analytics Dashboard",
                    "🔄 Load Demo Data",
                    "👤 Switch User",
                    "❌ Exit"
                ]
            ).ask()

            if choice == "📋 View All Habits":
                self.view_habits()
            elif choice == "➕ Create New Habit":
                self.create_habit()
            elif choice == "✅ Check Off Habit":
                self.check_off_habit()
            elif choice == "📊 Analytics Dashboard":
                self.show_analytics()
            elif choice == "🔄 Load Demo Data":
                self.load_demo_data()
            elif choice == "👤 Switch User":
                self.switch_user()
                break  # Restart with new user
            elif choice == "❌ Exit":
                self.exit_application()
                break

    def view_habits(self):
        """Display all habits with their current status"""
        habits = self.manager.get_all_habits()

        if not habits:
            print("\n📭 No habits found.")
            print("💡 Create your first habit to get started!")
            return

        print(f"\n📋 YOUR HABITS ({len(habits)} total)")
        print("-" * 50)

        for i, habit in enumerate(habits, 1):
            current_streak = calculate_current_streak(habit)
            longest_streak = calculate_longest_streak(habit)
            status = "✅" if habit.is_active else "❌"

            print(f"{i}. {status} {habit.name}")
            print(f"   📅 Type: {habit.periodicity.value} | 🔥 Current Streak: {current_streak} days")
            print(f"   🏆 Longest Streak: {longest_streak} days")
            print(f"   ✅ Completions: {len(habit.completion_records)}")

            # Show due status
            if habit.is_due_on(datetime.now().date()):
                print("   ⚠️  Due today!")
            print()

    def create_habit(self):
        """Create a new habit"""
        print("\n➕ CREATE NEW HABIT")
        print("-" * 30)

        name = questionary.text("Enter habit name:").ask()
        if not name:
            print("❌ Habit name cannot be empty!")
            return

        periodicity = questionary.select(
            "Select periodicity:",
            choices=[
                questionary.Choice("📅 Daily", "daily"),
                questionary.Choice("📊 Weekly", "weekly")
            ]
        ).ask()

        confirm = questionary.confirm(f"Create '{name}' as a {periodicity} habit?").ask()
        if not confirm:
            print("❌ Habit creation cancelled.")
            return

        periodicity_enum = Periodicity(periodicity)
        habit = self.manager.create_habit(name, periodicity_enum)

        print(f"✅ Habit '{habit.name}' created successfully! 🎉")
        print(f"💡 Don't forget to check it off regularly to build your streak!")

    def check_off_habit(self):
        """Check off a habit as completed"""
        habits = self.manager.get_all_habits()

        if not habits:
            print("❌ No habits available to check off!")
            return

        habit_choices = []
        for habit in habits:
            if habit.is_active:
                streak = calculate_current_streak(habit)
                status = "✅" if habit.is_due_on(datetime.now().date()) else "⏳"
                habit_choices.append(
                    questionary.Choice(
                        f"{status} {habit.name} (Streak: {streak} days)",
                        habit
                    )
                )

        selected_habit = questionary.select("Select habit to check off:", choices=habit_choices).ask()

        if not selected_habit:
            return

        notes = questionary.text("Add notes about this completion (optional):").ask()

        mood_score = questionary.select(
            "How are you feeling? (Optional):",
            choices=[
                questionary.Choice("😢 Tough (1)", 1),
                questionary.Choice("😕 Hard (2)", 2),
                questionary.Choice("😐 Okay (3)", 3),
                questionary.Choice("🙂 Good (4)", 4),
                questionary.Choice("😊 Great (5)", 5),
                questionary.Choice("Skip", None)
            ]
        ).ask()

        if self.manager.check_off_habit(selected_habit.name, notes, mood_score):
            new_streak = calculate_current_streak(selected_habit)
            print(f"✅ '{selected_habit.name}' checked off successfully! 🎉")
            print(f"🔥 Your current streak: {new_streak} days")
        else:
            print("❌ Failed to check off habit!")

    def show_analytics(self):
        """Display comprehensive analytics"""
        habits = self.manager.get_all_habits()

        if not habits:
            print("❌ No habits available for analytics!")
            return

        print("\n📊 ANALYTICS DASHBOARD")
        print("=" * 50)

        # Summary statistics
        stats = get_completion_statistics(habits)
        print(f"📈 SUMMARY:")
        print(f"   • Total Habits: {stats['total_habits']}")
        print(f"   • Daily Habits: {stats['daily_habits']}")
        print(f"   • Weekly Habits: {stats['weekly_habits']}")
        print(f"   • Total Completions: {stats['total_completions']}")

        # Current streaks
        print(f"\n🔥 CURRENT STREAKS:")
        for habit in habits:
            streak = calculate_current_streak(habit)
            status = "✅" if streak > 0 else "⏸️"
            print(f"   {status} {habit.name}: {streak} days")

        # Longest streaks
        print(f"\n🏆 LONGEST STREAKS:")
        for habit in habits:
            streak = calculate_longest_streak(habit)
            print(f"   🏅 {habit.name}: {streak} days")

        # Overall champion
        overall = overall_longest_streak(habits)
        if overall["habit"]:
            print(f"\n🎯 OVERALL CHAMPION:")
            print(f"   👑 {overall['habit'].name}: {overall['streak']} days!")

        print()

    def load_demo_data(self):
        """Load demo data for testing"""
        confirm = questionary.confirm("Load demo data? This will add sample habits.").ask()

        if confirm:
            # Create sample habits
            sample_habits = [
                ("Read 10 pages", Periodicity.DAILY),
                ("Exercise", Periodicity.DAILY),
                ("Meditate", Periodicity.DAILY),
                ("Weekly Planning", Periodicity.WEEKLY),
                ("Clean House", Periodicity.WEEKLY)
            ]

            for name, periodicity in sample_habits:
                self.manager.create_habit(name, periodicity)

            print("✅ Demo data loaded successfully!")
            print("📚 Sample habits: Read 10 pages, Exercise, Meditate, Weekly Planning, Clean House")

    def switch_user(self):
        """Switch to a different user"""
        self.is_authenticated = False
        self.current_user = None
        print("\n🔄 Switching users...")

    def exit_application(self):
        """Handle application exit"""
        print(f"\n👋 Thank you for using Habit Tracker, {self.current_user}!")
        print("💪 Keep building those good habits!")