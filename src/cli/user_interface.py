# src/cli/user_interface.py
import questionary
from datetime import datetime

# Import from other packages within src
from src.storage.db import DatabaseHandler, Periodicity
from src.managers.habit_manager import HabitManager
from src.analytics.analytics_service import AnalyticsService


class UserInterface:
    """Command-line interface for the Habit Tracker"""

    def __init__(self, db_path: str = "habits.db"):
        """
        Initialize the user interface

        Args:
            db_path: Path to SQLite database file
        """
        self.db_handler = DatabaseHandler(db_path)
        self.habit_manager = HabitManager(db_path)
        self.current_user = None

    def run(self):
        """Main application loop"""
        print("🚀 Welcome to the Habit Tracker!")
        print("=" * 50)

        # Authentication
        self._handle_authentication()

        # Main menu loop
        while True:
            choice = self._main_menu()

            if choice == "View All Habits":
                self._view_all_habits()
            elif choice == "Create New Habit":
                self._create_habit()
            elif choice == "Check Off Habit":
                self._check_off_habit()
            elif choice == "Analytics Dashboard":
                self._analytics_dashboard()
            elif choice == "View Completions":
                self._view_completions()
            elif choice == "Switch User":
                self._handle_authentication()
            elif choice == "Exit":
                print("👋 Thank you for using Habit Tracker! Goodbye!")
                break

    def _handle_authentication(self):
        """Handle user login/registration"""
        while True:
            choice = questionary.select(
                "How would you like to proceed?",
                choices=[
                    "Login",
                    "Register",
                    "Continue as Guest",
                    "Exit"
                ]
            ).ask()

            if choice == "Login":
                if self._login():
                    break
            elif choice == "Register":
                if self._register():
                    break
            elif choice == "Continue as Guest":
                if self._guest_mode():
                    break
            else:  # Exit
                print("Goodbye!")
                exit()

    def _login(self) -> bool:
        """Handle user login"""
        username = questionary.text("Enter your username:").ask()
        password = questionary.password("Enter your password:").ask()

        user = self.db_handler.verify_user_credentials(username, password)
        if user:
            self.current_user = user
            self.habit_manager.set_current_user(user.user_id)
            print(f"✅ Welcome back, {user.username}!")
            return True
        else:
            print("❌ Invalid username or password.")
            return False

    def _register(self) -> bool:
        """Handle user registration"""
        username = questionary.text("Choose a username:").ask()
        email = questionary.text("Enter your email:").ask()
        password = questionary.password("Choose a password:").ask()
        confirm_password = questionary.password("Confirm password:").ask()

        if password != confirm_password:
            print("❌ Passwords do not match.")
            return False

        try:
            user_id = self.db_handler.create_user(username, email, password)
            user = self.db_handler.verify_user_credentials(username, password)
            self.current_user = user
            self.habit_manager.set_current_user(user_id)
            print(f"✅ Account created successfully! Welcome, {username}!")
            return True
        except Exception as e:
            print(f"❌ Error creating account: {e}")
            return False

    def _guest_mode(self) -> bool:
        """Handle guest mode with demo account"""
        try:
            # Try to login as demo user
            user = self.db_handler.verify_user_credentials("demo", "demo123")
            if user:
                self.current_user = user
                self.habit_manager.set_current_user(user.user_id)
                print("🔸 Welcome to Guest Mode! Using demo account.")
                return True
            else:
                print("❌ Demo account not available. Please register.")
                return False
        except:
            print("❌ Demo account not available. Please register.")
            return False

    def _main_menu(self) -> str:
        """Display main menu and get user choice"""
        return questionary.select(
            f"What would you like to do? (Logged in as: {self.current_user.username})",
            choices=[
                "View All Habits",
                "Create New Habit",
                "Check Off Habit",
                "Analytics Dashboard",
                "View Completions",
                "Switch User",
                "Exit"
            ]
        ).ask()

    def _view_all_habits(self):
        """Display all habits for the current user"""
        try:
            habits = self.habit_manager.get_all_habits()

            if not habits:
                print("📝 No habits found. Create your first habit!")
                return

            print("\n📋 Your Habits:")
            print("-" * 60)

            for i, habit in enumerate(habits, 1):
                status = "✅ Active" if habit.is_active else "❌ Inactive"
                completions = len(habit.get_completion_records())
                last_completion = habit.get_last_completion_date()
                last_comp_str = last_completion.strftime("%Y-%m-%d") if last_completion else "Never"

                print(f"{i}. {habit.name}")
                print(f"   📅 Periodicity: {habit.periodicity.value.title()}")
                print(f"   📊 Completions: {completions}")
                print(f"   📍 Status: {status}")
                print(f"   🕒 Last completed: {last_comp_str}")
                print()

        except Exception as e:
            print(f"❌ Error loading habits: {e}")

    def _create_habit(self):
        """Create a new habit"""
        try:
            name = questionary.text("Enter habit name:").ask()
            if not name:
                print("❌ Habit name cannot be empty.")
                return

            periodicity = questionary.select(
                "Select periodicity:",
                choices=["Daily", "Weekly"]
            ).ask().upper()

            habit = self.habit_manager.create_habit(name, Periodicity[periodicity])
            print(f"✅ Habit '{habit.name}' created successfully!")

        except Exception as e:
            print(f"❌ Error creating habit: {e}")

    def _check_off_habit(self):
        """Check off a habit"""
        try:
            habits = self.habit_manager.get_all_habits(active_only=True)

            if not habits:
                print("❌ No active habits found. Create a habit first!")
                return

            habit_choices = [f"{habit.name} ({habit.periodicity.value})" for habit in habits]
            selected = questionary.select("Select habit to check off:", choices=habit_choices).ask()

            # Find selected habit
            selected_habit = None
            for habit in habits:
                if f"{habit.name} ({habit.periodicity.value})" == selected:
                    selected_habit = habit
                    break

            if not selected_habit:
                print("❌ Habit not found.")
                return

            # Check if habit is due
            if not selected_habit.is_due_on(datetime.now()):
                print("❌ This habit is not due yet or has already been completed for this period.")
                return

            # Get optional details
            notes = questionary.text("Add notes (optional):").ask()
            mood_score = questionary.text("Mood score 1-10 (optional):").ask()

            mood_int = None
            if mood_score:
                try:
                    mood_int = int(mood_score)
                    if not (1 <= mood_int <= 10):
                        print("❌ Mood score must be between 1 and 10.")
                        return
                except ValueError:
                    print("❌ Invalid mood score. Using None.")
                    mood_int = None

            # Check off habit
            success = self.habit_manager.check_off_habit(selected_habit.habit_id, notes, mood_int)
            if success:
                print(f"✅ '{selected_habit.name}' checked off successfully!")
            else:
                print("❌ Failed to check off habit.")

        except Exception as e:
            print(f"❌ Error checking off habit: {e}")

    def _analytics_dashboard(self):
        """Display analytics dashboard"""
        while True:
            choice = questionary.select(
                "Analytics Dashboard:",
                choices=[
                    "Current Streaks",
                    "Longest Streaks",
                    "Habits by Periodicity",
                    "Inactive Habits",
                    "Overall Summary",
                    "Back to Main Menu"
                ]
            ).ask()

            if choice == "Current Streaks":
                self._show_current_streaks()
            elif choice == "Longest Streaks":
                self._show_longest_streaks()
            elif choice == "Habits by Periodicity":
                self._show_habits_by_periodicity()
            elif choice == "Inactive Habits":
                self._show_inactive_habits()
            elif choice == "Overall Summary":
                self._show_overall_summary()
            else:  # Back to Main Menu
                break

    def _show_current_streaks(self):
        """Show current streaks for all habits"""
        try:
            habits = self.habit_manager.get_all_habits()
            summary = AnalyticsService.get_habits_streak_summary(habits)

            print("\n🔥 Current Streaks:")
            print("-" * 50)

            for habit_data in sorted(summary, key=lambda x: x['current_streak'], reverse=True):
                print(f"{habit_data['habit_name']}: {habit_data['current_streak']} {habit_data['periodicity']}(s)")

        except Exception as e:
            print(f"❌ Error loading streaks: {e}")

    def _show_longest_streaks(self):
        """Show longest streaks for all habits"""
        try:
            habits = self.habit_manager.get_all_habits()
            summary = AnalyticsService.get_habits_streak_summary(habits)

            print("\n🏆 Longest Streaks:")
            print("-" * 50)

            for habit_data in sorted(summary, key=lambda x: x['longest_streak'], reverse=True):
                print(f"{habit_data['habit_name']}: {habit_data['longest_streak']} {habit_data['periodicity']}(s)")

        except Exception as e:
            print(f"❌ Error loading streaks: {e}")

    def _show_habits_by_periodicity(self):
        """Show habits grouped by periodicity"""
        try:
            habits = self.habit_manager.get_all_habits()

            daily_habits = AnalyticsService.get_habits_by_periodicity(habits, Periodicity.DAILY)
            weekly_habits = AnalyticsService.get_habits_by_periodicity(habits, Periodicity.WEEKLY)

            print("\n📅 Daily Habits:")
            print("-" * 30)
            for habit in daily_habits:
                print(f"• {habit.name}")

            print("\n📅 Weekly Habits:")
            print("-" * 30)
            for habit in weekly_habits:
                print(f"• {habit.name}")

        except Exception as e:
            print(f"❌ Error loading habits: {e}")

    def _show_inactive_habits(self):
        """Show habits that haven't been completed recently"""
        try:
            habits = self.habit_manager.get_all_habits()
            inactive_habits = AnalyticsService.get_inactive_habits(habits, months=1)

            print("\n💤 Inactive Habits (not completed in 1 month):")
            print("-" * 50)

            if not inactive_habits:
                print("🎉 All habits are active!")
                return

            for habit in inactive_habits:
                last_comp = habit.get_last_completion_date()
                last_str = last_comp.strftime("%Y-%m-%d") if last_comp else "Never"
                print(f"• {habit.name} (Last: {last_str})")

        except Exception as e:
            print(f"❌ Error loading inactive habits: {e}")

    def _show_overall_summary(self):
        """Show overall analytics summary"""
        try:
            habits = self.habit_manager.get_all_habits()

            if not habits:
                print("❌ No habits found.")
                return

            total_habits = len(habits)
            daily_habits = len(AnalyticsService.get_habits_by_periodicity(habits, Periodicity.DAILY))
            weekly_habits = len(AnalyticsService.get_habits_by_periodicity(habits, Periodicity.WEEKLY))
            total_completions = sum(len(habit.get_completion_records()) for habit in habits)

            longest_streak_data = AnalyticsService.get_overall_longest_streak(habits)

            print("\n📊 Overall Summary:")
            print("-" * 40)
            print(f"Total Habits: {total_habits}")
            print(f"Daily Habits: {daily_habits}")
            print(f"Weekly Habits: {weekly_habits}")
            print(f"Total Completions: {total_completions}")
            print(f"Longest Streak: {longest_streak_data['streak_length']} {longest_streak_data['periodicity']}(s)")
            print(f"Best Habit: {longest_streak_data['habit_name']}")

        except Exception as e:
            print(f"❌ Error loading summary: {e}")

    def _view_completions(self):
        """View recent completions"""
        try:
            completions = self.habit_manager.get_user_completions(days=30)

            print("\n📝 Recent Completions (Last 30 days):")
            print("-" * 60)

            if not completions:
                print("No completions in the last 30 days.")
                return

            for comp in completions[:10]:  # Show last 10
                timestamp = datetime.fromisoformat(comp['timestamp'])
                mood_str = f" | Mood: {comp['mood_score']}/10" if comp['mood_score'] else ""
                notes_str = f" | Notes: {comp['notes']}" if comp['notes'] else ""
                print(f"• {comp['habit_name']} - {timestamp.strftime('%Y-%m-%d %H:%M')}{mood_str}{notes_str}")

        except Exception as e:
            print(f"❌ Error loading completions: {e}")