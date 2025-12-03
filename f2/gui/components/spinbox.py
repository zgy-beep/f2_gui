"""
数字输入框组件
~~~~~~~~~~~~~~

自定义样式的 QSpinBox 和 QDoubleSpinBox，支持主题切换。
"""

import os

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QDoubleSpinBox, QSpinBox

# 获取资源路径
_ASSETS_PATH = os.path.join(
    os.path.dirname(os.path.dirname(__file__)), "assets", "icon"
)

# ===================== 主题样式定义 =====================
# 夜间模式 - 透明背景，蓝紫色边框
DARK_STYLES = {
    "bg": "transparent",
    "bg_hover": "rgba(99, 102, 241, 0.05)",
    "bg_focus": "rgba(99, 102, 241, 0.08)",
    "border": "rgba(99, 102, 241, 0.3)",
    "border_hover": "rgba(139, 92, 246, 0.45)",
    "border_focus": "rgba(139, 92, 246, 0.7)",
    "text": "#E5E7EB",
    "text_disabled": "#6B7280",
    "button_bg": "rgba(99, 102, 241, 0.1)",
    "button_bg_hover": "rgba(99, 102, 241, 0.2)",
    "button_bg_pressed": "rgba(99, 102, 241, 0.3)",
    "arrow_color": "#A5B4FC",
    "selection_bg": "rgba(99, 102, 241, 0.4)",
    "up_arrow": "Dark_Arrow_Up.png",
    "down_arrow": "Dark_Arrow_Down.png",
}

# 日间模式 - 透明背景，绿色边框
LIGHT_STYLES = {
    "bg": "transparent",
    "bg_hover": "rgba(74, 222, 128, 0.05)",
    "bg_focus": "rgba(74, 222, 128, 0.08)",
    "border": "rgba(74, 222, 128, 0.4)",
    "border_hover": "rgba(34, 197, 94, 0.5)",
    "border_focus": "rgba(34, 197, 94, 0.7)",
    "text": "#1F2937",
    "text_disabled": "#9CA3AF",
    "button_bg": "rgba(74, 222, 128, 0.1)",
    "button_bg_hover": "rgba(74, 222, 128, 0.2)",
    "button_bg_pressed": "rgba(74, 222, 128, 0.3)",
    "arrow_color": "#22C55E",
    "selection_bg": "rgba(74, 222, 128, 0.35)",
    "up_arrow": "Light_Arrow_Up.png",
    "down_arrow": "Light_Arrow_Down.png",
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


class StyledSpinBox(QSpinBox):
    """自定义样式数字输入框 - 支持主题切换"""

    def __init__(
        self,
        parent=None,
        min_value: int = 0,
        max_value: int = 100,
        default_value: int = 0,
        fixed_width: int = None,
        fixed_height: int = 28,
        border_radius: int = 6,
    ):
        super().__init__(parent)

        self._border_radius = border_radius

        # 设置范围和默认值
        self.setRange(min_value, max_value)
        self.setValue(default_value)

        # 设置尺寸
        if fixed_width:
            self.setFixedWidth(fixed_width)
        if fixed_height:
            self.setFixedHeight(fixed_height)

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

        # 获取箭头图标路径（使用正斜杠，QSS 需要）
        up_arrow_path = os.path.join(_ASSETS_PATH, styles["up_arrow"]).replace(
            "\\", "/"
        )
        down_arrow_path = os.path.join(_ASSETS_PATH, styles["down_arrow"]).replace(
            "\\", "/"
        )

        self.setStyleSheet(
            f"""
            QSpinBox {{
                background-color: {styles['bg']};
                border: 1px solid {styles['border']};
                border-radius: {self._border_radius}px;
                padding: 2px 6px;
                padding-right: 20px;
                color: {styles['text']};
                font-size: 12px;
                selection-background-color: {styles['selection_bg']};
            }}
            
            QSpinBox:hover {{
                background-color: {styles['bg_hover']};
                border-color: {styles['border_hover']};
            }}
            
            QSpinBox:focus {{
                background-color: {styles['bg_focus']};
                border-color: {styles['border_focus']};
            }}
            
            QSpinBox:disabled {{
                color: {styles['text_disabled']};
                border-color: rgba(107, 114, 128, 0.3);
            }}
            
            QSpinBox::up-button {{
                subcontrol-origin: border;
                subcontrol-position: top right;
                width: 18px;
                height: 13px;
                border: none;
                border-left: 1px solid {styles['border']};
                border-top-right-radius: {self._border_radius}px;
                background-color: {styles['button_bg']};
            }}
            
            QSpinBox::up-button:hover {{
                background-color: {styles['button_bg_hover']};
            }}
            
            QSpinBox::up-button:pressed {{
                background-color: {styles['button_bg_pressed']};
            }}
            
            QSpinBox::up-arrow {{
                image: url({up_arrow_path});
                width: 10px;
                height: 10px;
            }}
            
            QSpinBox::down-button {{
                subcontrol-origin: border;
                subcontrol-position: bottom right;
                width: 18px;
                height: 13px;
                border: none;
                border-left: 1px solid {styles['border']};
                border-top: 1px solid {styles['border']};
                border-bottom-right-radius: {self._border_radius}px;
                background-color: {styles['button_bg']};
            }}
            
            QSpinBox::down-button:hover {{
                background-color: {styles['button_bg_hover']};
            }}
            
            QSpinBox::down-button:pressed {{
                background-color: {styles['button_bg_pressed']};
            }}
            
            QSpinBox::down-arrow {{
                image: url({down_arrow_path});
                width: 10px;
                height: 10px;
            }}
        """
        )


class StyledDoubleSpinBox(QDoubleSpinBox):
    """自定义样式小数输入框 - 支持主题切换"""

    def __init__(
        self,
        parent=None,
        min_value: float = 0.0,
        max_value: float = 100.0,
        default_value: float = 0.0,
        decimals: int = 2,
        fixed_width: int = None,
        fixed_height: int = 28,
        border_radius: int = 6,
    ):
        super().__init__(parent)

        self._border_radius = border_radius

        # 设置范围、精度和默认值
        self.setRange(min_value, max_value)
        self.setDecimals(decimals)
        self.setValue(default_value)

        # 设置尺寸
        if fixed_width:
            self.setFixedWidth(fixed_width)
        if fixed_height:
            self.setFixedHeight(fixed_height)

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

        # 获取箭头图标路径
        up_arrow_path = os.path.join(_ASSETS_PATH, styles["up_arrow"]).replace(
            "\\", "/"
        )
        down_arrow_path = os.path.join(_ASSETS_PATH, styles["down_arrow"]).replace(
            "\\", "/"
        )

        self.setStyleSheet(
            f"""
            QDoubleSpinBox {{
                background-color: {styles['bg']};
                border: 1px solid {styles['border']};
                border-radius: {self._border_radius}px;
                padding: 2px 6px;
                padding-right: 20px;
                color: {styles['text']};
                font-size: 12px;
                selection-background-color: {styles['selection_bg']};
            }}
            
            QDoubleSpinBox:hover {{
                background-color: {styles['bg_hover']};
                border-color: {styles['border_hover']};
            }}
            
            QDoubleSpinBox:focus {{
                background-color: {styles['bg_focus']};
                border-color: {styles['border_focus']};
            }}
            
            QDoubleSpinBox:disabled {{
                color: {styles['text_disabled']};
                border-color: rgba(107, 114, 128, 0.3);
            }}
            
            QDoubleSpinBox::up-button {{
                subcontrol-origin: border;
                subcontrol-position: top right;
                width: 18px;
                height: 13px;
                border: none;
                border-left: 1px solid {styles['border']};
                border-top-right-radius: {self._border_radius}px;
                background-color: {styles['button_bg']};
            }}
            
            QDoubleSpinBox::up-button:hover {{
                background-color: {styles['button_bg_hover']};
            }}
            
            QDoubleSpinBox::up-button:pressed {{
                background-color: {styles['button_bg_pressed']};
            }}
            
            QDoubleSpinBox::up-arrow {{
                image: url({up_arrow_path});
                width: 10px;
                height: 10px;
            }}
            
            QDoubleSpinBox::down-button {{
                subcontrol-origin: border;
                subcontrol-position: bottom right;
                width: 18px;
                height: 13px;
                border: none;
                border-left: 1px solid {styles['border']};
                border-top: 1px solid {styles['border']};
                border-bottom-right-radius: {self._border_radius}px;
                background-color: {styles['button_bg']};
            }}
            
            QDoubleSpinBox::down-button:hover {{
                background-color: {styles['button_bg_hover']};
            }}
            
            QDoubleSpinBox::down-button:pressed {{
                background-color: {styles['button_bg_pressed']};
            }}
            
            QDoubleSpinBox::down-arrow {{
                image: url({down_arrow_path});
                width: 10px;
                height: 10px;
            }}
        """
        )
