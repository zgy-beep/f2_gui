# -*- coding: utf-8 -*-
# File: f2/gui/themes/theme_manager.py
# Author: zgy
# Description: 主题管理器 - 统一管理所有GUI组件样式

"""
ThemeManager - 主题管理器

功能:
1. 从外部CSS文件加载样式表
2. 支持明暗主题切换
3. 单例模式，全局统一管理
4. 样式表文件位于 themes/styles/ 目录

使用方式:
    from f2.gui.themes.theme_manager import ThemeManager

    # 获取单例实例
    theme_manager = ThemeManager()

    # 设置主题
    theme_manager.set_theme("dark")  # 或 "light"

    # 获取样式表
    stylesheet = theme_manager.get_stylesheet()

    # 监听主题变化
    theme_manager.theme_changed.connect(self.on_theme_changed)
"""

from pathlib import Path
from typing import Optional

from PyQt6.QtCore import QObject, pyqtSignal


class ThemeManager(QObject):
    """主题管理器 - 单例模式

    管理应用程序的主题和样式表。
    从外部CSS文件加载样式，支持明暗主题切换。
    """

    # 单例实例
    _instance: Optional["ThemeManager"] = None

    # 主题变化信号
    theme_changed = pyqtSignal(str)

    # 可用主题列表
    AVAILABLE_THEMES = ["dark", "light"]

    # 默认主题
    DEFAULT_THEME = "dark"

    def __new__(cls) -> "ThemeManager":
        """单例模式实现"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self) -> None:
        """初始化主题管理器"""
        # 防止重复初始化
        if self._initialized:
            return

        super().__init__()

        # 当前主题
        self._current_theme: str = self.DEFAULT_THEME

        # 样式表目录
        self._styles_dir: Path = Path(__file__).parent / "styles"

        # 缓存的样式表
        self._cached_stylesheet: str = ""

        # 标记初始化完成
        self._initialized: bool = True

        # 预加载默认主题样式
        self._load_stylesheet()

    @property
    def current_theme(self) -> str:
        """获取当前主题名称"""
        return self._current_theme

    @property
    def is_dark_mode(self) -> bool:
        """判断是否为暗色主题"""
        return self._current_theme == "dark"

    @property
    def is_light_mode(self) -> bool:
        """判断是否为亮色主题"""
        return self._current_theme == "light"

    @property
    def styles_directory(self) -> Path:
        """获取样式表目录路径"""
        return self._styles_dir

    def set_theme(self, theme: str) -> bool:
        """设置主题

        Args:
            theme: 主题名称 ("dark" 或 "light")

        Returns:
            bool: 设置是否成功
        """
        if theme not in self.AVAILABLE_THEMES:
            # print(f"[ThemeManager] 无效的主题名称: {theme}")
            return False

        if theme == self._current_theme:
            return True

        old_theme = self._current_theme
        self._current_theme = theme

        # 重新加载样式表
        if self._load_stylesheet():
            # print(f"[ThemeManager] 主题已切换: {old_theme} -> {theme}")
            # 更新按钮组件的主题
            self._update_button_theme(theme)
            self.theme_changed.emit(theme)
            return True
        else:
            # 加载失败，回滚
            self._current_theme = old_theme
            return False

    def _update_button_theme(self, theme: str):
        """更新按钮组件的主题

        Args:
            theme: 主题名称
        """
        try:
            from f2.gui.components.buttons import GradientButton

            GradientButton.set_theme(theme)
        except ImportError:
            pass

    def toggle_theme(self) -> str:
        """切换明暗主题

        Returns:
            str: 切换后的主题名称
        """
        new_theme = "light" if self._current_theme == "dark" else "dark"
        self.set_theme(new_theme)
        return self._current_theme

    def get_stylesheet(self) -> str:
        """获取当前主题的样式表

        Returns:
            str: CSS样式表字符串
        """
        if not self._cached_stylesheet:
            self._load_stylesheet()
        return self._cached_stylesheet

    def _load_stylesheet(self) -> bool:
        """从文件加载样式表（基础样式 + 主题样式）

        Returns:
            bool: 加载是否成功
        """
        # 加载基础样式表
        base_qss_file = self._styles_dir / "base.qss"
        # 尝试加载新版主题样式表，如果不存在则使用旧版
        theme_qss_file = self._styles_dir / f"{self._current_theme}_new.qss"
        if not theme_qss_file.exists():
            theme_qss_file = self._styles_dir / f"{self._current_theme}.qss"

        stylesheet_parts = []

        # 加载基础样式表（如果存在）
        if base_qss_file.exists():
            try:
                with open(base_qss_file, "r", encoding="utf-8") as f:
                    stylesheet_parts.append(f.read())
            except Exception:
                pass

        # 加载主题样式表
        if not theme_qss_file.exists():
            self._cached_stylesheet = "\n".join(stylesheet_parts)
            # 替换图标路径
            self._cached_stylesheet = self._replace_icon_paths(self._cached_stylesheet)
            return len(stylesheet_parts) > 0

        try:
            with open(theme_qss_file, "r", encoding="utf-8") as f:
                stylesheet_parts.append(f.read())
            self._cached_stylesheet = "\n".join(stylesheet_parts)
            # 替换图标路径
            self._cached_stylesheet = self._replace_icon_paths(self._cached_stylesheet)
            return True
        except Exception as e:
            self._cached_stylesheet = "\n".join(stylesheet_parts)
            # 替换图标路径
            self._cached_stylesheet = self._replace_icon_paths(self._cached_stylesheet)
            return False

    def _replace_icon_paths(self, stylesheet: str) -> str:
        """替换样式表中的图标路径为绝对路径

        Args:
            stylesheet: 原始样式表

        Returns:
            str: 替换后的样式表
        """
        # 获取 icons 目录的绝对路径
        icons_dir = Path(__file__).parent.parent / "assets" / "icon"
        icons_path = icons_dir.as_posix()  # 使用正斜杠，QSS需要

        # 替换 :/icons/ 为实际路径
        stylesheet = stylesheet.replace(":/icons/", f"{icons_path}/")

        return stylesheet

    def reload_stylesheet(self) -> bool:
        """重新加载当前主题的样式表

        用于在CSS文件修改后刷新样式。

        Returns:
            bool: 加载是否成功
        """
        if self._load_stylesheet():
            self.theme_changed.emit(self._current_theme)
            return True
        return False

    def get_color(self, color_name: str) -> str:
        """获取主题颜色值

        Args:
            color_name: 颜色名称

        Returns:
            str: 颜色值 (十六进制)
        """
        colors = self.get_colors()
        return colors.get(color_name, "#FFFFFF")

    def get_colors(self) -> dict:
        """获取当前主题的所有颜色配置

        Returns:
            dict: 颜色配置字典
        """
        if self._current_theme == "dark":
            return self._get_dark_colors()
        else:
            return self._get_light_colors()

    @staticmethod
    def _get_dark_colors() -> dict:
        """获取暗色主题颜色配置"""
        return {
            # 背景色
            "bg_primary": "#1E1E2E",
            "bg_secondary": "#252536",
            "bg_tertiary": "#2D2D44",
            "bg_elevated": "#313147",
            # 卡片背景
            "card_bg": "#252536",
            "card_hover": "#2D2D44",
            "card_border": "#3D3D5C",
            # 文字颜色
            "text_primary": "#E4E4E7",
            "text_secondary": "#A1A1AA",
            "text_muted": "#71717A",
            "text_placeholder": "#52525B",
            # 主色调
            "primary": "#6366F1",
            "primary_hover": "#818CF8",
            "primary_light": "rgba(99, 102, 241, 0.1)",
            # 功能色
            "success": "#10B981",
            "success_hover": "#34D399",
            "success_light": "rgba(16, 185, 129, 0.1)",
            "danger": "#EF4444",
            "danger_hover": "#F87171",
            "danger_light": "rgba(239, 68, 68, 0.1)",
            "warning": "#F59E0B",
            "warning_hover": "#FBBF24",
            "warning_light": "rgba(245, 158, 11, 0.1)",
            "info": "#3B82F6",
            "info_hover": "#60A5FA",
            "info_light": "rgba(59, 130, 246, 0.1)",
            # 边框
            "border_primary": "#3D3D5C",
            "border_secondary": "#4D4D6D",
            "border_light": "#2D2D44",
            # 其他
            "scrollbar": "#404060",
            "scrollbar_hover": "#505080",
            "shadow": "rgba(0, 0, 0, 0.3)",
        }

    @staticmethod
    def _get_light_colors() -> dict:
        """获取亮色主题颜色配置"""
        return {
            # 背景色
            "bg_primary": "#FAFAFA",
            "bg_secondary": "#F5F5F5",
            "bg_tertiary": "#EEEEEE",
            "bg_elevated": "#FFFFFF",
            # 卡片背景
            "card_bg": "#FFFFFF",
            "card_hover": "#F5F5F5",
            "card_border": "#E5E5E5",
            # 文字颜色
            "text_primary": "#18181B",
            "text_secondary": "#52525B",
            "text_muted": "#71717A",
            "text_placeholder": "#A1A1AA",
            # 主色调
            "primary": "#4F46E5",
            "primary_hover": "#6366F1",
            "primary_light": "rgba(79, 70, 229, 0.1)",
            # 功能色
            "success": "#059669",
            "success_hover": "#10B981",
            "success_light": "rgba(5, 150, 105, 0.1)",
            "danger": "#DC2626",
            "danger_hover": "#EF4444",
            "danger_light": "rgba(220, 38, 38, 0.1)",
            "warning": "#D97706",
            "warning_hover": "#F59E0B",
            "warning_light": "rgba(217, 119, 6, 0.1)",
            "info": "#2563EB",
            "info_hover": "#3B82F6",
            "info_light": "rgba(37, 99, 235, 0.1)",
            # 边框
            "border_primary": "#E5E5E5",
            "border_secondary": "#D4D4D4",
            "border_light": "#F5F5F5",
            # 其他
            "scrollbar": "#D4D4D4",
            "scrollbar_hover": "#A3A3A3",
            "shadow": "rgba(0, 0, 0, 0.1)",
        }

    # 按钮样式类型到 objectName 的映射
    # 对应 dark.qss / light.qss 中定义的按钮样式
    BUTTON_OBJECT_NAMES = {
        "primary": "gradientPrimaryButton",
        "success": "gradientSuccessButton",
        "danger": "gradientDangerButton",
        "warning": "gradientWarningButton",
        "info": "gradientInfoButton",
        "secondary": "secondaryButton",
        "ghost": "ghostButton",
    }

    def get_button_object_name(self, style_type: str) -> str:
        """获取按钮样式对应的 objectName

        按钮样式已在 dark.qss / light.qss 中定义，
        只需设置正确的 objectName 即可应用样式。

        Args:
            style_type: 样式类型 ("primary", "success", "danger", "warning", "info", "secondary", "ghost")

        Returns:
            str: 对应的 objectName
        """
        return self.BUTTON_OBJECT_NAMES.get(style_type, "gradientPrimaryButton")

    def apply_button_style(self, button, style_type: str) -> None:
        """应用按钮样式

        通过设置 objectName 来应用 QSS 中定义的按钮样式。
        当按钮被添加到父控件后，样式会自动生效。

        Args:
            button: QPushButton 实例
            style_type: 样式类型 ("primary", "success", "danger", "warning", "info", "secondary", "ghost")
        """
        object_name = self.get_button_object_name(style_type)
        button.setObjectName(object_name)

    def apply_to_widget(self, widget) -> None:
        """将样式表应用到指定控件

        Args:
            widget: QWidget实例
        """
        stylesheet = self.get_stylesheet()
        widget.setStyleSheet(stylesheet)

    def apply_to_app(self, app) -> None:
        """将样式表应用到整个应用程序

        Args:
            app: QApplication实例
        """
        stylesheet = self.get_stylesheet()
        app.setStyleSheet(stylesheet)


# 便捷函数：获取ThemeManager单例
def get_theme_manager() -> ThemeManager:
    """获取ThemeManager单例实例

    Returns:
        ThemeManager: 主题管理器实例
    """
    return ThemeManager()


# 便捷函数：获取当前样式表
def get_stylesheet() -> str:
    """获取当前主题的样式表

    Returns:
        str: CSS样式表字符串
    """
    return ThemeManager().get_stylesheet()


# 便捷函数：设置主题
def set_theme(theme: str) -> bool:
    """设置主题

    Args:
        theme: 主题名称

    Returns:
        bool: 设置是否成功
    """
    return ThemeManager().set_theme(theme)


# 便捷函数：切换主题
def toggle_theme() -> str:
    """切换明暗主题

    Returns:
        str: 切换后的主题名称
    """
    return ThemeManager().toggle_theme()


# 便捷函数：获取颜色
def get_color(color_name: str) -> str:
    """获取主题颜色值

    Args:
        color_name: 颜色名称

    Returns:
        str: 颜色值
    """
    return ThemeManager().get_color(color_name)


# 便捷函数：判断是否为暗色主题
def is_dark_mode() -> bool:
    """判断是否为暗色主题

    Returns:
        bool: 是否为暗色主题
    """
    return ThemeManager().is_dark_mode


# 便捷函数：获取按钮对应的 objectName
def get_button_object_name(style_type: str) -> str:
    """获取按钮样式对应的 objectName

    Args:
        style_type: 样式类型 ("primary", "success", "danger", "warning", "info", "secondary", "ghost")

    Returns:
        str: 对应的 objectName
    """
    return ThemeManager().get_button_object_name(style_type)


# 便捷函数：应用按钮样式
def apply_button_style(button, style_type: str) -> None:
    """应用按钮样式

    通过设置 objectName 来应用 QSS 中定义的按钮样式。

    Args:
        button: QPushButton 实例
        style_type: 样式类型 ("primary", "success", "danger", "warning", "info", "secondary", "ghost")
    """
    ThemeManager().apply_button_style(button, style_type)
