import sys
import os

# Add the src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from cli.user_interface import UserInterface


def main():
    print("🚀 Welcome to the Habit Tracker!")

    ui = UserInterface()
    ui.login_menu()
    ui.main_menu()


if __name__ == "__main__":
    main()