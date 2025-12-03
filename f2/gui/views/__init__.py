"""
视图模块
~~~~~~~

应用程序的主要视图和界面。
"""

from .main_window import MainWindow
from .home_page import HomePage
from .settings_page import SettingsPage
from .history_page import HistoryPage

__all__ = ["MainWindow", "HomePage", "SettingsPage", "HistoryPage"]
