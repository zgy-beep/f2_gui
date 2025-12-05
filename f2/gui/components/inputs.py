"""
输入框组件
~~~~~~~~~~

自定义样式的 QLineEdit 和 QTextEdit，支持主题切换。
"""

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QLineEdit, QTextEdit

# ===================== 主题样式定义 =====================
# 夜间模式 - 透明背景，蓝紫色边框
DARK_STYLES = {
    "bg": "transparent",
    "bg_focus": "rgba(99, 102, 241, 0.05)",
    "border": "rgba(99, 102, 241, 0.3)",
    "border_hover": "rgba(139, 92, 246, 0.45)",
    "border_focus": "rgba(139, 92, 246, 0.7)",
    "text": "#E5E7EB",
    "placeholder": "#6B7280",
    "selection_bg": "rgba(99, 102, 241, 0.4)",
}

# 日间模式 - 透明背景，绿色边框
LIGHT_STYLES = {
    "bg": "transparent",
    "bg_focus": "rgba(74, 222, 128, 0.05)",
    "border": "rgba(74, 222, 128, 0.4)",
    "border_hover": "rgba(34, 197, 94, 0.5)",
    "border_focus": "rgba(34, 197, 94, 0.7)",
    "text": "#1F2937",
    "placeholder": "#9CA3AF",
    "selection_bg": "rgba(74, 222, 128, 0.35)",
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


class StyledLineEdit(QLineEdit):
    """自定义样式单行输入框 - 支持主题切换"""

    def __init__(
        self,
        parent=None,
        placeholder: str = "",
        fixed_height: int = 36,
        min_width: int = None,
        border_radius: int = 8,
    ):
        super().__init__(parent)

        self._border_radius = border_radius

        # 设置尺寸
        if fixed_height:
            self.setFixedHeight(fixed_height)
        if min_width:
            self.setMinimumWidth(min_width)

        # 设置占位符
        if placeholder:
            self.setPlaceholderText(placeholder)

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
            QLineEdit {{
                background-color: {styles['bg']};
                border: 1px solid {styles['border']};
                border-radius: {self._border_radius}px;
                padding: 6px 12px;
                color: {styles['text']};
                font-size: 13px;
                selection-background-color: {styles['selection_bg']};
            }}
            
            QLineEdit:hover {{
                border-color: {styles['border_hover']};
            }}
            
            QLineEdit:focus {{
                background-color: {styles['bg_focus']};
                border-color: {styles['border_focus']};
            }}
            
            QLineEdit::placeholder {{
                color: {styles['placeholder']};
            }}
        """
        )


class StyledTextEdit(QTextEdit):
    """自定义样式多行输入框 - 支持主题切换"""

    def __init__(
        self,
        parent=None,
        placeholder: str = "",
        fixed_height: int = None,
        min_height: int = 80,
        min_width: int = None,
        border_radius: int = 8,
    ):
        super().__init__(parent)

        self._border_radius = border_radius

        # 设置尺寸
        if fixed_height:
            self.setFixedHeight(fixed_height)
        if min_height:
            self.setMinimumHeight(min_height)
        if min_width:
            self.setMinimumWidth(min_width)

        # 设置占位符
        if placeholder:
            self.setPlaceholderText(placeholder)

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
            QTextEdit {{
                background-color: {styles['bg']};
                border: 1px solid {styles['border']};
                border-radius: {self._border_radius}px;
                padding: 8px 12px;
                color: {styles['text']};
                font-size: 13px;
                selection-background-color: {styles['selection_bg']};
            }}
            
            QTextEdit:hover {{
                border-color: {styles['border_hover']};
            }}
            
            QTextEdit:focus {{
                background-color: {styles['bg_focus']};
                border-color: {styles['border_focus']};
            }}
        """
        )


class UrlLineEdit(StyledLineEdit):
    """URL 输入框 - 预设样式"""

    def __init__(self, parent=None, placeholder: str = "粘贴链接..."):
        super().__init__(
            parent=parent,
            placeholder=placeholder,
            fixed_height=36,
            border_radius=8,
        )


class BatchTextEdit(StyledTextEdit):
    """批量输入框 - 预设样式，粘贴时只保留纯文本"""

    def __init__(self, parent=None, placeholder: str = "每行一个链接..."):
        super().__init__(
            parent=parent,
            placeholder=placeholder,
            min_height=80,
            border_radius=8,
        )
        # 设置只接受纯文本
        self.setAcceptRichText(False)

    def insertFromMimeData(self, source):
        """重写粘贴方法，只粘贴纯文本"""
        if source.hasText():
            self.insertPlainText(source.text())
        else:
            super().insertFromMimeData(source)


class SearchLineEdit(StyledLineEdit):
    """搜索输入框 - 预设样式"""

    def __init__(self, parent=None, placeholder: str = "🔍 搜索..."):
        super().__init__(
            parent=parent,
            placeholder=placeholder,
            fixed_height=32,
            border_radius=6,
        )
