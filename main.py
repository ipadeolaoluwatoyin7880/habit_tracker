# main.py
"""
Habit Tracker Application
Main entry point for the habit tracking application.
"""

import sys
import os

# Add src to Python path to enable imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Import from src package
from cli.user_interface import UserInterface


def main():
    """Main function to start the Habit Tracker application"""
    try:
        app = UserInterface()
        app.run()
    except KeyboardInterrupt:
        print("\n\n👋 Application interrupted by user. Goodbye!")
    except Exception as e:
        print(f"\n❌ An unexpected error occurred: {e}")
        print("Please check your database configuration and try again.")


if __name__ == "__main__":
    main()