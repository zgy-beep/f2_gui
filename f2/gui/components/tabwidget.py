# -*- coding:utf-8 -*-
# @Information  :
# @Author       : ZGY
# @Date         : 2025-12-02 21:14:02
# @FilePath     : /f2_gui/f2/gui/components/tabwidget.py
# @LastEditTime : 2025-12-02 21:14:07

"""
标签页组件
~~~~~~~~~~

自定义样式的 QTabWidget，支持主题切换。
"""

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QTabBar, QTabWidget

# ===================== 主题样式定义 =====================
# 夜间模式 - 透明背景，蓝紫色主题
DARK_STYLES = {
    "bg": "transparent",
    "pane_bg": "rgba(30, 32, 45, 0.3)",
    "pane_border": "rgba(99, 102, 241, 0.2)",
    "tab_bg": "transparent",
    "tab_bg_hover": "rgba(99, 102, 241, 0.1)",
    "tab_bg_selected": "rgba(99, 102, 241, 0.15)",
    "tab_border": "rgba(99, 102, 241, 0.2)",
    "tab_border_selected": "rgba(139, 92, 246, 0.6)",
    "tab_text": "#9CA3AF",
    "tab_text_hover": "#C4B5FD",
    "tab_text_selected": "#E5E7EB",
    "indicator_color": "#8B5CF6",
}

# 日间模式 - 透明背景，绿色主题
LIGHT_STYLES = {
    "bg": "transparent",
    "pane_bg": "rgba(255, 255, 255, 0.3)",
    "pane_border": "rgba(74, 222, 128, 0.25)",
    "tab_bg": "transparent",
    "tab_bg_hover": "rgba(74, 222, 128, 0.1)",
    "tab_bg_selected": "rgba(74, 222, 128, 0.15)",
    "tab_border": "rgba(74, 222, 128, 0.25)",
    "tab_border_selected": "rgba(34, 197, 94, 0.6)",
    "tab_text": "#6B7280",
    "tab_text_hover": "#16A34A",
    "tab_text_selected": "#1F2937",
    "indicator_color": "#22C55E",
}


def _get_current_theme() -> str:
    """获取当前主题"""
    try:
        from f2.gui.themes.theme_manager import ThemeManager

        return ThemeManager().get_theme()
    except Exception:
        return "dark"


def _get_styles() -> dict:
    """根据当前主题获取样式字典"""
    return DARK_STYLES if _get_current_theme() == "dark" else LIGHT_STYLES


class StyledTabWidget(QTabWidget):
    """自定义样式标签页组件 - 支持主题切换"""

    def __init__(
        self,
        parent=None,
        tab_position: str = "top",
        border_radius: int = 8,
    ):
        super().__init__(parent)

        self._border_radius = border_radius

        # 设置标签位置
        position_map = {
            "top": QTabWidget.TabPosition.North,
            "bottom": QTabWidget.TabPosition.South,
            "left": QTabWidget.TabPosition.West,
            "right": QTabWidget.TabPosition.East,
        }
        self.setTabPosition(
            position_map.get(tab_position, QTabWidget.TabPosition.North)
        )

        # 设置文档模式（更简洁的外观）
        self.setDocumentMode(False)

        # 应用样式
        self._apply_style()
        self._connect_theme_signal()

    def _connect_theme_signal(self):
        """连接主题变化信号"""
        try:
            from f2.gui.themes.theme_manager import ThemeManager

            ThemeManager().theme_changed.connect(self._on_theme_changed)
        except Exception:
            pass

    def _on_theme_changed(self, theme: str):
        """主题变化时更新样式"""
        self._apply_style()

    def _apply_style(self):
        """应用当前主题样式"""
        styles = _get_styles()

        self.setStyleSheet(
            f"""
            QTabWidget {{
                background-color: {styles['bg']};
                border: none;
            }}
            
            QTabWidget::pane {{
                background-color: {styles['pane_bg']};
                border: 1px solid {styles['pane_border']};
                border-radius: {self._border_radius}px;
                padding: 8px;
                margin-top: -1px;
            }}
            
            QTabBar {{
                background-color: transparent;
            }}
            
            QTabBar::tab {{
                background-color: {styles['tab_bg']};
                border: 1px solid {styles['tab_border']};
                border-bottom: none;
                border-top-left-radius: 6px;
                border-top-right-radius: 6px;
                padding: 8px 16px;
                margin-right: 2px;
                color: {styles['tab_text']};
                font-size: 12px;
                font-weight: 500;
                min-width: 60px;
            }}
            
            QTabBar::tab:hover {{
                background-color: {styles['tab_bg_hover']};
                color: {styles['tab_text_hover']};
            }}
            
            QTabBar::tab:selected {{
                background-color: {styles['tab_bg_selected']};
                border-color: {styles['tab_border_selected']};
                border-bottom: 2px solid {styles['indicator_color']};
                color: {styles['tab_text_selected']};
            }}
            
            QTabBar::tab:!selected {{
                margin-top: 2px;
            }}
            
            /* 滚动按钮样式 */
            QTabBar::scroller {{
                width: 20px;
            }}
            
            QTabBar QToolButton {{
                background-color: {styles['tab_bg_hover']};
                border: 1px solid {styles['tab_border']};
                border-radius: 4px;
                margin: 2px;
            }}
            
            QTabBar QToolButton:hover {{
                background-color: {styles['tab_bg_selected']};
                border-color: {styles['tab_border_selected']};
            }}
        """
        )


class StyledTabBar(QTabBar):
    """自定义样式标签栏 - 支持主题切换"""

    def __init__(self, parent=None):
        super().__init__(parent)

        # 应用样式
        self._apply_style()
        self._connect_theme_signal()

    def _connect_theme_signal(self):
        """连接主题变化信号"""
        try:
            from f2.gui.themes.theme_manager import ThemeManager

            ThemeManager().theme_changed.connect(self._on_theme_changed)
        except Exception:
            pass

    def _on_theme_changed(self, theme: str):
        """主题变化时更新样式"""
        self._apply_style()

    def _apply_style(self):
        """应用当前主题样式"""
        styles = _get_styles()

        self.setStyleSheet(
            f"""
            QTabBar {{
                background-color: transparent;
            }}
            
            QTabBar::tab {{
                background-color: {styles['tab_bg']};
                border: 1px solid {styles['tab_border']};
                border-bottom: none;
                border-top-left-radius: 6px;
                border-top-right-radius: 6px;
                padding: 8px 16px;
                margin-right: 2px;
                color: {styles['tab_text']};
                font-size: 12px;
                font-weight: 500;
            }}
            
            QTabBar::tab:hover {{
                background-color: {styles['tab_bg_hover']};
                color: {styles['tab_text_hover']};
            }}
            
            QTabBar::tab:selected {{
                background-color: {styles['tab_bg_selected']};
                border-color: {styles['tab_border_selected']};
                border-bottom: 2px solid {styles['indicator_color']};
                color: {styles['tab_text_selected']};
            }}
        """
        )


class PillTabWidget(QTabWidget):
    """药丸样式标签页组件 - 圆角胶囊风格"""

    def __init__(
        self,
        parent=None,
        tab_position: str = "top",
    ):
        super().__init__(parent)

        # 设置标签位置
        position_map = {
            "top": QTabWidget.TabPosition.North,
            "bottom": QTabWidget.TabPosition.South,
            "left": QTabWidget.TabPosition.West,
            "right": QTabWidget.TabPosition.East,
        }
        self.setTabPosition(
            position_map.get(tab_position, QTabWidget.TabPosition.North)
        )
        self.setDocumentMode(True)

        # 应用样式
        self._apply_style()
        self._connect_theme_signal()

    def _connect_theme_signal(self):
        """连接主题变化信号"""
        try:
            from f2.gui.themes.theme_manager import ThemeManager

            ThemeManager().theme_changed.connect(self._on_theme_changed)
        except Exception:
            pass

    def _on_theme_changed(self, theme: str):
        """主题变化时更新样式"""
        self._apply_style()

    def _apply_style(self):
        """应用当前主题样式"""
        styles = _get_styles()

        self.setStyleSheet(
            f"""
            QTabWidget {{
                background-color: transparent;
                border: none;
            }}
            
            QTabWidget::pane {{
                background-color: transparent;
                border: none;
                padding-top: 8px;
            }}
            
            QTabBar {{
                background-color: rgba(107, 114, 128, 0.1);
                border-radius: 16px;
                padding: 2px;
            }}
            
            QTabBar::tab {{
                background-color: transparent;
                border: none;
                border-radius: 14px;
                padding: 6px 16px;
                margin: 2px;
                color: {styles['tab_text']};
                font-size: 12px;
                font-weight: 500;
                min-width: 50px;
            }}
            
            QTabBar::tab:hover {{
                background-color: {styles['tab_bg_hover']};
                color: {styles['tab_text_hover']};
            }}
            
            QTabBar::tab:selected {{
                background-color: {styles['indicator_color']};
                color: white;
            }}
        """
        )
