"""
分割线组件
~~~~~~~~~~

自定义样式的分割线，支持渐变效果和主题切换。
"""

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QLinearGradient, QPainter
from PyQt6.QtWidgets import QFrame, QWidget

# ===================== 主题样式定义 =====================
# 夜间模式 - 蓝紫色渐变
DARK_STYLES = {
    "color_start": "rgba(99, 102, 241, 0)",  # 透明（虚）
    "color_middle": "rgba(99, 102, 241, 0.4)",  # 实色（实）
    "color_end": "rgba(99, 102, 241, 0)",  # 透明（虚）
    "solid_color": "rgba(255, 255, 255, 0.08)",  # 纯色分割线
}

# 日间模式 - 绿色渐变
LIGHT_STYLES = {
    "color_start": "rgba(74, 222, 128, 0)",  # 透明（虚）
    "color_middle": "rgba(74, 222, 128, 0.5)",  # 实色（实）
    "color_end": "rgba(74, 222, 128, 0)",  # 透明（虚）
    "solid_color": "rgba(0, 0, 0, 0.08)",  # 纯色分割线
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


def _parse_rgba(rgba_str: str) -> QColor:
    """解析 rgba 字符串为 QColor"""
    # 格式: rgba(r, g, b, a)
    rgba_str = rgba_str.strip()
    if rgba_str.startswith("rgba(") and rgba_str.endswith(")"):
        values = rgba_str[5:-1].split(",")
        if len(values) == 4:
            r, g, b = (
                int(values[0].strip()),
                int(values[1].strip()),
                int(values[2].strip()),
            )
            a = float(values[3].strip())
            return QColor(r, g, b, int(a * 255))
    return QColor(128, 128, 128, 50)


class GradientSeparator(QWidget):
    """渐变分割线 - 虚实虚效果，支持主题切换"""

    def __init__(
        self,
        parent=None,
        height: int = 1,
        orientation: Qt.Orientation = Qt.Orientation.Horizontal,
        margin_h: int = 0,
        margin_v: int = 8,
    ):
        super().__init__(parent)

        self._height = height
        self._orientation = orientation
        self._margin_h = margin_h
        self._margin_v = margin_v

        # 设置固定高度或宽度
        if orientation == Qt.Orientation.Horizontal:
            self.setFixedHeight(height + margin_v * 2)
            self.setMinimumWidth(50)
        else:
            self.setFixedWidth(height + margin_h * 2)
            self.setMinimumHeight(50)

        # 连接主题信号
        self._connect_theme_signal()

    def _connect_theme_signal(self):
        """连接主题变化信号"""
        try:
            from f2.gui.themes.theme_manager import ThemeManager

            ThemeManager().theme_changed.connect(self._on_theme_changed)
        except Exception:
            pass

    def _on_theme_changed(self, theme: str):
        """主题变化时重绘"""
        self.update()

    def paintEvent(self, event):
        """绘制渐变分割线"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        styles = _get_styles()

        if self._orientation == Qt.Orientation.Horizontal:
            # 水平分割线
            y = self.height() // 2
            start_x = self._margin_h
            end_x = self.width() - self._margin_h

            gradient = QLinearGradient(start_x, y, end_x, y)
            gradient.setColorAt(0.0, _parse_rgba(styles["color_start"]))
            gradient.setColorAt(0.5, _parse_rgba(styles["color_middle"]))
            gradient.setColorAt(1.0, _parse_rgba(styles["color_end"]))

            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(gradient)
            painter.drawRect(
                start_x, y - self._height // 2, end_x - start_x, self._height
            )
        else:
            # 垂直分割线
            x = self.width() // 2
            start_y = self._margin_v
            end_y = self.height() - self._margin_v

            gradient = QLinearGradient(x, start_y, x, end_y)
            gradient.setColorAt(0.0, _parse_rgba(styles["color_start"]))
            gradient.setColorAt(0.5, _parse_rgba(styles["color_middle"]))
            gradient.setColorAt(1.0, _parse_rgba(styles["color_end"]))

            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(gradient)
            painter.drawRect(
                x - self._height // 2, start_y, self._height, end_y - start_y
            )

        painter.end()


class SimpleSeparator(QFrame):
    """简单分割线 - 纯色，支持主题切换"""

    def __init__(
        self,
        parent=None,
        height: int = 1,
        orientation: Qt.Orientation = Qt.Orientation.Horizontal,
    ):
        super().__init__(parent)

        self._line_height = height
        self._orientation = orientation

        if orientation == Qt.Orientation.Horizontal:
            self.setFrameShape(QFrame.Shape.HLine)
            self.setFixedHeight(height)
        else:
            self.setFrameShape(QFrame.Shape.VLine)
            self.setFixedWidth(height)

        self.setFrameShadow(QFrame.Shadow.Plain)

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
            QFrame {{
                background-color: {styles['solid_color']};
                border: none;
            }}
        """
        )


class DashedSeparator(QWidget):
    """虚线分割线 - 支持主题切换"""

    def __init__(
        self,
        parent=None,
        height: int = 1,
        dash_length: int = 4,
        gap_length: int = 4,
        orientation: Qt.Orientation = Qt.Orientation.Horizontal,
    ):
        super().__init__(parent)

        self._height = height
        self._dash_length = dash_length
        self._gap_length = gap_length
        self._orientation = orientation

        if orientation == Qt.Orientation.Horizontal:
            self.setFixedHeight(height + 8)
            self.setMinimumWidth(50)
        else:
            self.setFixedWidth(height + 8)
            self.setMinimumHeight(50)

        self._connect_theme_signal()

    def _connect_theme_signal(self):
        """连接主题变化信号"""
        try:
            from f2.gui.themes.theme_manager import ThemeManager

            ThemeManager().theme_changed.connect(self._on_theme_changed)
        except Exception:
            pass

    def _on_theme_changed(self, theme: str):
        """主题变化时重绘"""
        self.update()

    def paintEvent(self, event):
        """绘制虚线分割线"""
        from PyQt6.QtGui import QPen

        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        styles = _get_styles()
        color = _parse_rgba(styles["color_middle"])

        pen = QPen(color)
        pen.setWidth(self._height)
        pen.setStyle(Qt.PenStyle.DashLine)
        pen.setDashPattern([self._dash_length, self._gap_length])

        painter.setPen(pen)

        if self._orientation == Qt.Orientation.Horizontal:
            y = self.height() // 2
            painter.drawLine(0, y, self.width(), y)
        else:
            x = self.width() // 2
            painter.drawLine(x, 0, x, self.height())

        painter.end()
