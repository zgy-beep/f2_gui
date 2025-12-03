"""
主题模块
~~~~~~~

统一样式管理系统，支持明暗主题切换。
样式表存储在 themes/styles/ 目录下。
"""

from .theme_manager import (
    ThemeManager,
    get_theme_manager,
    get_stylesheet,
    set_theme,
    toggle_theme,
    get_color,
    is_dark_mode,
    apply_button_style,
    get_button_object_name,
)

__all__ = [
    "ThemeManager",
    "get_theme_manager",
    "get_stylesheet",
    "set_theme",
    "toggle_theme",
    "get_color",
    "is_dark_mode",
    "apply_button_style",
    "get_button_object_name",
]
