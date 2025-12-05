# -*- coding:utf-8 -*-
# @Information  :
# @Author       : ZGY
# @Date         : 2025-12-05 16:50:00
# @FilePath     : /f2_gui/f2/gui/components/datetime_edits.py
# @LastEditTime : 2025-12-05 18:00:00

"""
日期和时间选择组件
~~~~~~~~~~~~~~~~~

自定义样式的 QDateEdit 和 QTimeEdit，支持主题切换和自定义图标。
样式与 spinbox.py 统一。
"""

import os

from PyQt6.QtWidgets import QDateEdit, QTimeEdit

from f2.gui.themes.theme_manager import ThemeManager

# ===================== 主题样式定义 =====================

# 获取图标路径的辅助函数
_ASSETS_PATH = os.path.join(
    os.path.dirname(os.path.dirname(__file__)), "assets", "icon"
)


def _get_current_theme() -> str:
    """获取当前主题"""
    try:
        from f2.gui.themes.theme_manager import ThemeManager

        return ThemeManager().get_theme()
    except Exception:
        return "dark"


# 夜间模式 - 风格与 spinbox.py 统一
DARK_STYLES = {
    "bg": "transparent",
    "bg_hover": "rgba(99, 102, 241, 0.05)",
    "bg_focus": "rgba(99, 102, 241, 0.08)",
    "border": "rgba(99, 102, 241, 0.3)",
    "border_hover": "rgba(139, 92, 246, 0.45)",
    "border_focus": "rgba(139, 92, 246, 0.7)",
    "text": "#E5E7EB",
    "disabled_text": "#6B7280",
    "selection_bg": "rgba(99, 102, 241, 0.4)",
    "button_bg": "rgba(99, 102, 241, 0.1)",
    "button_bg_hover": "rgba(99, 102, 241, 0.2)",
    "button_bg_pressed": "rgba(99, 102, 241, 0.3)",
    "up_arrow": "Dark_Arrow_Up.png",
    "down_arrow": "Dark_Arrow_Down.png",
    "arrow_left": "Dark_Arrow_Left.png",
    "arrow_right": "Dark_Arrow_Right.png",
    # 日历样式
    "calendar_bg": "#111827",  # 使用稍暗的背景以区分
    "calendar_text": "#F9FAFB",
    "calendar_selected_bg": "#4F46E5",
    "calendar_selected_text": "#FFFFFF",
    "calendar_weekday_text": "#9CA3AF",
    "calendar_header_bg": "#1F2937",
    "calendar_border": "#374151",
}

# 日间模式 - 风格与 spinbox.py 统一
LIGHT_STYLES = {
    "bg": "transparent",
    "bg_hover": "rgba(74, 222, 128, 0.05)",
    "bg_focus": "rgba(74, 222, 128, 0.08)",
    "border": "rgba(74, 222, 128, 0.4)",
    "border_hover": "rgba(34, 197, 94, 0.5)",
    "border_focus": "rgba(34, 197, 94, 0.7)",
    "text": "#1F2937",
    "disabled_text": "#9CA3AF",
    "selection_bg": "rgba(74, 222, 128, 0.35)",
    "button_bg": "rgba(74, 222, 128, 0.1)",
    "button_bg_hover": "rgba(74, 222, 128, 0.2)",
    "button_bg_pressed": "rgba(74, 222, 128, 0.3)",
    "up_arrow": "Light_Arrow_Up.png",
    "down_arrow": "Light_Arrow_Down.png",
    "arrow_left": "Light_Arrow_Left.png",
    "arrow_right": "Light_Arrow_Right.png",
    # 日历样式
    "calendar_bg": "#FFFFFF",
    "calendar_text": "#111827",
    "calendar_selected_bg": "#4338CA",
    "calendar_selected_text": "#FFFFFF",
    "calendar_weekday_text": "#6B7280",
    "calendar_header_bg": "#F9FAFB",
    "calendar_border": "#E5E7EB",
}


def _get_styles() -> dict:
    """根据当前主题获取样式字典"""
    return DARK_STYLES if _get_current_theme() == "dark" else LIGHT_STYLES


class StyledDateEdit(QDateEdit):
    """带样式的日期选择组件

    新增可选的固定宽高参数，并提高右侧 padding 和下拉宽度，防止内容被按钮遮挡。
    """

    def __init__(self, parent=None, fixed_width: int = None, fixed_height: int = 28):
        super().__init__(parent)
        self.setCalendarPopup(True)

        # 支持外部传入固定尺寸，未传入时设定合理最小宽度
        if fixed_width:
            self.setFixedWidth(fixed_width)
        else:
            self.setMinimumWidth(120)

        if fixed_height:
            self.setFixedHeight(fixed_height)

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
        down_arrow_path = os.path.join(_ASSETS_PATH, styles["down_arrow"]).replace(
            "\\", "/"
        )
        arrow_left_path = os.path.join(_ASSETS_PATH, styles["arrow_left"]).replace(
            "\\", "/"
        )
        arrow_right_path = os.path.join(_ASSETS_PATH, styles["arrow_right"]).replace(
            "\\", "/"
        )

        self.setStyleSheet(
            f"""
            QDateEdit {{
                background-color: {styles['bg']};
                border: 1px solid {styles['border']};
                border-radius: 6px;
                padding: 4px 6px;
                padding-right: 20px;
                color: {styles['text']};
                font-size: 12px;
                selection-background-color: {styles['selection_bg']};
            }}
            
            QDateEdit:hover {{
                background-color: {styles['bg_hover']};
                border-color: {styles['border_hover']};
            }}
            
            QDateEdit:focus {{
                background-color: {styles['bg_focus']};
                border-color: {styles['border_focus']};
            }}
            
            QDateEdit:disabled {{
                color: {styles['disabled_text']};
                border-color: rgba(107, 114, 128, 0.3);
            }}
            
            QDateEdit::drop-down {{
                subcontrol-origin: padding;
                subcontrol-position: center right;
                width: 24px;
                border: none;
                border-left: 1px solid {styles['border']};
                border-top-right-radius: 6px;
                border-bottom-right-radius: 6px;
                background: transparent;
            }}
            
            
            QDateEdit::drop-down:pressed {{
                background-color: {styles['button_bg_pressed']};
            }}
            
            QDateEdit::down-arrow {{
                image: url({down_arrow_path});
                width: 12px;
                height: 12px;
            }}
            
            QCalendarWidget {{
                background-color: {styles['calendar_bg']};
                color: {styles['calendar_text']};
                border: 1px solid {styles['calendar_border']};
                border-radius: 8px;
            }}
            
            QCalendarWidget QWidget {{
                alternate-background-color: transparent;
            }}
            
            QCalendarWidget QToolButton {{
                color: {styles['calendar_text']};
                background-color: transparent;
                border: none;
                font-size: 13px;
                font-weight: 600;
                padding: 8px;
                margin: 2px;
                min-width: 32px;
                min-height: 32px;
            }}
            
            QCalendarWidget QToolButton:hover {{
                background-color: {styles['button_bg_hover']};
                border-radius: 4px;
            }}
            
            QCalendarWidget QToolButton:pressed {{
                background-color: {styles['button_bg_pressed']};
            }}
            
            QCalendarWidget QMenu {{
                background-color: {styles['calendar_bg']};
                color: {styles['calendar_text']};
                border: 1px solid {styles['calendar_border']};
            }}
            
            QCalendarWidget QSpinBox {{
                color: {styles['calendar_text']};
                background-color: transparent;
                border: 1px solid {styles['calendar_border']};
                border-radius: 4px;
                padding: 4px 8px;
                selection-background-color: {styles['calendar_selected_bg']};
                min-width: 60px;
            }}
            
            QCalendarWidget QSpinBox::up-button,
            QCalendarWidget QSpinBox::down-button {{
                subcontrol-origin: border;
                width: 16px;
                border: none;
                background-color: {styles['button_bg']};
            }}
            
            QCalendarWidget QSpinBox::up-button:hover,
            QCalendarWidget QSpinBox::down-button:hover {{
                background-color: {styles['button_bg_hover']};
            }}
            
            QCalendarWidget QAbstractItemView {{
                color: {styles['calendar_text']};
                background-color: transparent;
                selection-background-color: {styles['calendar_selected_bg']};
                selection-color: {styles['calendar_selected_text']};
                border: none;
                outline: none;
                show-decoration-selected: 1;
            }}
            
            QCalendarWidget QAbstractItemView::item {{
                padding: 8px;
                border-radius: 4px;
            }}
            
            QCalendarWidget QAbstractItemView::item:hover {{
                background-color: {styles['button_bg_hover']};
            }}
            
            QCalendarWidget QAbstractItemView::item:selected {{
                background-color: {styles['calendar_selected_bg']};
                color: {styles['calendar_selected_text']};
            }}
            
            QCalendarWidget QAbstractItemView:enabled {{
                color: {styles['calendar_text']};
                font-size: 13px;
                font-weight: 500;
            }}
            
            QCalendarWidget QAbstractItemView:disabled {{
                color: {styles['calendar_weekday_text']};
            }}
            
            QCalendarWidget #qt_calendar_navigationbar {{
                background-color: {styles['calendar_header_bg']};
                border-bottom: 1px solid {styles['calendar_border']};
                min-height: 44px;
            }}
            
            QCalendarWidget #qt_calendar_prevmonth {{
                qproperty-icon: url({arrow_left_path});
                border-radius: 4px;
                min-width: 32px;
                min-height: 32px;
            }}
            
            QCalendarWidget #qt_calendar_nextmonth {{
                qproperty-icon: url({arrow_right_path});
                border-radius: 4px;
                min-width: 32px;
                min-height: 32px;
            }}
            
            QCalendarWidget #qt_calendar_monthbutton,
            QCalendarWidget #qt_calendar_yearbutton {{
                color: {styles['calendar_text']};
                font-size: 14px;
                font-weight: 600;
                padding: 6px 12px;
                margin: 3px;
                border-radius: 4px;
                min-height: 32px;
            }}
            
            QCalendarWidget #qt_calendar_monthbutton:hover,
            QCalendarWidget #qt_calendar_yearbutton:hover {{
                background-color: {styles['button_bg_hover']};
            }}
            
            QCalendarWidget #qt_calendar_monthbutton::menu-indicator,
            QCalendarWidget #qt_calendar_yearbutton::menu-indicator {{
                width: 0px;
            }}
            
            QCalendarWidget QTableView {{
                gridline-color: transparent;
                selection-background-color: {styles['calendar_selected_bg']};
                background-color: transparent;
            }}
            
            QCalendarWidget QHeaderView::section {{
                background-color: transparent;
                color: {styles['calendar_weekday_text']};
                padding: 8px;
                border: none;
                font-size: 12px;
                font-weight: 600;
            }}
            
            QCalendarWidget #qt_calendar_calendarview {{
                border: none;
                background-color: transparent;
            }}
        """
        )


class StyledTimeEdit(QTimeEdit):
    """带样式的时间选择组件

    支持可选固定宽高参数，增大按钮尺寸以防止遮挡。
    """

    def __init__(self, parent=None, fixed_width: int = None, fixed_height: int = 28):
        super().__init__(parent)

        if fixed_width:
            self.setFixedWidth(fixed_width)
        else:
            self.setMinimumWidth(90)

        if fixed_height:
            self.setFixedHeight(fixed_height)

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
            QTimeEdit {{
                background-color: {styles['bg']};
                border: 1px solid {styles['border']};
                border-radius: 6px;
                padding: 2px 6px;
                padding-right: 20px;
                color: {styles['text']};
                font-size: 12px;
                selection-background-color: {styles['selection_bg']};
            }}
            
            QTimeEdit:hover {{
                background-color: {styles['bg_hover']};
                border-color: {styles['border_hover']};
            }}
            
            QTimeEdit:focus {{
                background-color: {styles['bg_focus']};
                border-color: {styles['border_focus']};
            }}
            
            QTimeEdit:disabled {{
                color: {styles['disabled_text']};
                border-color: rgba(107, 114, 128, 0.3);
            }}
            
            QTimeEdit::up-button {{
                subcontrol-origin: border;
                subcontrol-position: top right;
                width: 18px;
                height: 13px;
                border: none;
                border-left: 1px solid {styles['border']};
                border-top-right-radius: 6px;
                background-color: {styles['button_bg']};
            }}
            
            QTimeEdit::up-button:hover {{
                background-color: {styles['button_bg_hover']};
            }}
            
            QTimeEdit::up-button:pressed {{
                background-color: {styles['button_bg_pressed']};
            }}
            
            QTimeEdit::up-arrow {{
                image: url({up_arrow_path});
                width: 10px;
                height: 10px;
            }}
            
            QTimeEdit::down-button {{
                subcontrol-origin: border;
                subcontrol-position: bottom right;
                width: 18px;
                height: 13px;
                border: none;
                border-left: 1px solid {styles['border']};
                border-top: 1px solid {styles['border']};
                border-bottom-right-radius: 6px;
                background-color: {styles['button_bg']};
            }}
            
            QTimeEdit::down-button:hover {{
                background-color: {styles['button_bg_hover']};
            }}
            
            QTimeEdit::down-button:pressed {{
                background-color: {styles['button_bg_pressed']};
            }}
            
            QTimeEdit::down-arrow {{
                image: url({down_arrow_path});
                width: 10px;
                height: 10px;
            }}
        """
        )
