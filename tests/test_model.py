import pytest
from unittest.mock import patch, MagicMock
from src.cli.user_interface import UserInterface
from src.data_model.habit import Periodicity


class TestCLI:
    def test_user_interface_initialization(self):
        """Test that UserInterface initializes correctly"""
        ui = UserInterface()
        assert ui.current_user is None
        assert ui.is_authenticated == False
        assert ui.manager is not None

    @patch('src.cli.user_interface.questionary')
    def test_handle_guest_mode(self, mock_questionary):
        """Test guest mode authentication"""
        ui = UserInterface()
        ui.handle_guest_mode()

        assert ui.current_user == "Guest"
        assert ui.is_authenticated == True

    @patch('src.cli.user_interface.questionary')
    def test_handle_login(self, mock_questionary):
        """Test login functionality"""
        mock_questionary.text.return_value.ask.return_value = "testuser"

        ui = UserInterface()
        ui.handle_login()

        assert ui.current_user == "testuser"
        assert ui.is_authenticated == True

    def test_cli_methods_exist(self):
        """Test that all CLI methods exist"""
        ui = UserInterface()

        # Test that main methods exist
        assert hasattr(ui, 'login_menu')
        assert hasattr(ui, 'main_menu')
        assert hasattr(ui, 'view_habits')
        assert hasattr(ui, 'create_habit')
        assert hasattr(ui, 'check_off_habit')
        assert hasattr(ui, 'show_analytics')