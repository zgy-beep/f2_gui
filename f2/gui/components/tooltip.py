# -*- coding:utf-8 -*-
# @Information  : 浮动提示组件
# @Author       : ZGY
# @Date         : 2025-12-03
# @FilePath     : /f2_gui/f2/gui/components/tooltip.py
# @LastEditTime : 2025-12-03

"""
浮动提示组件
~~~~~~~~~~~~

自定义卡片式浮动提示组件。

功能：
1. FloatingTooltip - 悬停提示（跟随鼠标）
2. show_click_tooltip - Toast 点击反馈（窗口底部）

特性：
- 卡片式设计，真正的圆角边框
- 支持多屏幕显示
- 支持主题切换
- 延迟显示，防止频繁触发
- Toast 带淡出动画
"""

from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QColor, QCursor, QLinearGradient, QPainter, QPainterPath, QPen
from PyQt6.QtWidgets import QApplication, QHBoxLayout, QLabel, QWidget


def _get_current_theme() -> str:
    """获取当前主题"""
    try:
        from f2.gui.themes.theme_manager import ThemeManager

        return ThemeManager().get_theme()
    except Exception:
        return "dark"


# ===================== 主题样式定义 =====================
# 深色主题 - 蓝紫色渐变风格
DARK_STYLES = {
    "bg_start": QColor(42, 42, 53),
    "bg_end": QColor(30, 30, 40),
    "border": QColor(99, 102, 241),
    "text": "#F3F4F6",
    "icon_color": "#A5B4FC",
}

# 浅色主题 - 绿色渐变风格
LIGHT_STYLES = {
    "bg_start": QColor(255, 255, 255),
    "bg_end": QColor(240, 253, 244),
    "border": QColor(34, 197, 94),
    "text": "#1F2937",
    "icon_color": "#059669",
}


class FloatingTooltip(QWidget):
    """卡片式浮动提示组件 - 手动绘制圆角背景"""

    _active_tooltip = None

    def __init__(self, parent=None):
        super().__init__(parent)
        self._text = ""
        self._icon = ""
        self._radius = 8
        self._setup_ui()

        # 窗口属性
        self.setWindowFlags(
            Qt.WindowType.ToolTip
            | Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.NoDropShadowWindowHint
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating)
        # 设置删除时自动清理
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)

        # 连接主题信号 - 使用安全的方式
        self._theme_connection = None
        try:
            from f2.gui.themes.theme_manager import ThemeManager

            self._theme_manager = ThemeManager()
            self._theme_connection = self._theme_manager.theme_changed.connect(
                self._on_theme_changed
            )
        except Exception:
            pass

    def _on_theme_changed(self, _):
        """主题变化回调 - 安全检查"""
        try:
            if not self.isVisible():
                return
            self.update()
        except RuntimeError:
            # 对象已被删除
            pass

    def closeEvent(self, event):
        """关闭事件 - 断开主题信号连接"""
        try:
            if self._theme_connection and hasattr(self, "_theme_manager"):
                self._theme_manager.theme_changed.disconnect(self._on_theme_changed)
        except (RuntimeError, TypeError):
            pass
        super().closeEvent(event)

    def _setup_ui(self):
        """设置 UI"""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(14, 10, 14, 10)
        layout.setSpacing(6)

        # 图标
        self._icon_label = QLabel()
        self._icon_label.hide()
        layout.addWidget(self._icon_label)

        # 文本
        self._text_label = QLabel()
        self._text_label.setWordWrap(True)
        self._text_label.setMaximumWidth(350)
        layout.addWidget(self._text_label)

        self._update_label_style()

    def _update_label_style(self):
        """更新标签样式"""
        styles = DARK_STYLES if _get_current_theme() == "dark" else LIGHT_STYLES
        self._icon_label.setStyleSheet(
            f"color: {styles['icon_color']}; font-size: 13px; background: transparent;"
        )
        self._text_label.setStyleSheet(
            f"color: {styles['text']}; font-size: 12px; font-weight: 500; background: transparent;"
        )

    def paintEvent(self, event):
        """绘制圆角背景和边框"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        styles = DARK_STYLES if _get_current_theme() == "dark" else LIGHT_STYLES

        # 创建圆角路径
        path = QPainterPath()
        path.addRoundedRect(
            0.5, 0.5, self.width() - 1, self.height() - 1, self._radius, self._radius
        )

        # 绘制渐变背景
        gradient = QLinearGradient(0, 0, self.width(), self.height())
        gradient.setColorAt(0, styles["bg_start"])
        gradient.setColorAt(1, styles["bg_end"])

        painter.fillPath(path, gradient)

        # 绘制边框
        pen = QPen(styles["border"], 1.5)
        painter.setPen(pen)
        painter.drawPath(path)

    def set_content(self, text: str, icon: str = ""):
        """设置提示内容"""
        self._text = text
        self._icon = icon
        self._text_label.setText(text)
        self._update_label_style()

        if icon:
            self._icon_label.setText(icon)
            self._icon_label.show()
        else:
            self._icon_label.hide()

        self.adjustSize()

    def show_at_cursor(self):
        """在鼠标正下方显示"""
        # 安全隐藏之前的 tooltip
        if FloatingTooltip._active_tooltip and FloatingTooltip._active_tooltip != self:
            try:
                FloatingTooltip._active_tooltip.hide()
            except RuntimeError:
                # 对象已被删除，忽略
                pass
        FloatingTooltip._active_tooltip = self

        cursor_pos = QCursor.pos()
        self.adjustSize()

        # 获取鼠标所在屏幕（支持多屏幕）
        screen = QApplication.screenAt(cursor_pos)
        if screen is None:
            screen = QApplication.primaryScreen()
        screen_geo = screen.geometry()

        # 计算位置（鼠标正下方居中）
        x = cursor_pos.x() - self.width() // 2
        y = cursor_pos.y() + 18

        # 边界检测
        if x + self.width() > screen_geo.right() - 10:
            x = screen_geo.right() - self.width() - 10
        if x < screen_geo.left() + 10:
            x = screen_geo.left() + 10
        if y + self.height() > screen_geo.bottom() - 10:
            y = cursor_pos.y() - self.height() - 10

        self.move(x, y)
        self.show()

    @classmethod
    def hide_active(cls):
        """隐藏当前激活的提示"""
        if cls._active_tooltip:
            try:
                cls._active_tooltip.hide()
            except RuntimeError:
                pass
            cls._active_tooltip = None


def install_tooltip(widget, text: str, icon: str = "", delay: int = 400):
    """为组件安装卡片式浮动提示

    在鼠标悬停时显示卡片式提示，跟随鼠标位置。

    Args:
        widget: 要安装提示的组件
        text: 提示文本
        icon: 图标（可选，emoji 字符）
        delay: 延迟显示时间（毫秒）

    示例：
        install_tooltip(button, "点击开始下载", "▶")
        install_tooltip(checkbox, "启用此选项后...")
    """
    # 如果文本为空，不安装
    if not text:
        return

    # 确保 delay 是整数
    _delay = int(delay) if delay else 400

    # 保存原始事件处理器
    original_enter = widget.enterEvent
    original_leave = widget.leaveEvent
    original_move = widget.mouseMoveEvent

    # 创建专用的提示实例和定时器
    tooltip = FloatingTooltip(widget.window() if widget.window() else None)
    tooltip.set_content(text, icon)

    timer = QTimer()
    timer.setSingleShot(True)

    # 记录是否已显示
    widget._tooltip_shown = False

    def on_timeout():
        """延迟后显示提示"""
        try:
            # 检查 widget 是否仍然有效
            if widget is None:
                return
            # 尝试访问 widget，如果已删除会抛出异常
            if widget.underMouse():
                tooltip.show_at_cursor()
                widget._tooltip_shown = True
        except RuntimeError:
            # widget 已被删除，忽略
            pass

    timer.timeout.connect(on_timeout)

    def new_enter_event(event):
        """鼠标进入"""
        timer.start(_delay)
        if original_enter:
            original_enter(event)

    def new_leave_event(event):
        """鼠标离开"""
        timer.stop()
        tooltip.hide()
        try:
            widget._tooltip_shown = False
        except RuntimeError:
            pass
        if original_leave:
            original_leave(event)

    def new_move_event(event):
        """鼠标移动 - 更新提示位置"""
        try:
            if widget._tooltip_shown:
                tooltip.show_at_cursor()
        except RuntimeError:
            pass
        if original_move:
            original_move(event)

    # 替换事件处理器
    widget.enterEvent = new_enter_event
    widget.leaveEvent = new_leave_event
    widget.mouseMoveEvent = new_move_event

    # 提供更新方法
    def update_tooltip_text(new_text: str, new_icon: str = None):
        """更新提示内容"""
        tooltip.set_content(new_text, new_icon if new_icon is not None else icon)

    widget.update_tooltip = update_tooltip_text

    # 存储引用防止垃圾回收
    widget._tooltip_instance = tooltip
    widget._tooltip_timer = timer


# ===================== Toast 样式定义 =====================
TOAST_STYLES = {
    "success": {
        "dark": {"bg": "rgba(16, 185, 129, 0.95)", "border": "#34D399"},
        "light": {"bg": "rgba(16, 185, 129, 0.95)", "border": "#10B981"},
    },
    "info": {
        "dark": {"bg": "rgba(99, 102, 241, 0.95)", "border": "#818CF8"},
        "light": {"bg": "rgba(59, 130, 246, 0.95)", "border": "#3B82F6"},
    },
    "warning": {
        "dark": {"bg": "rgba(245, 158, 11, 0.95)", "border": "#FBBF24"},
        "light": {"bg": "rgba(245, 158, 11, 0.95)", "border": "#F59E0B"},
    },
    "error": {
        "dark": {"bg": "rgba(239, 68, 68, 0.95)", "border": "#F87171"},
        "light": {"bg": "rgba(239, 68, 68, 0.95)", "border": "#EF4444"},
    },
}

# 图标到样式类型的映射
ICON_STYLE_MAP = {
    "✅": "success",
    "✓": "success",
    "🗑️": "info",
    "📂": "info",
    "📁": "info",
    "🔄": "info",
    "⏸️": "info",
    "☀️": "info",
    "🌙": "info",
    "⚠️": "warning",
    "❌": "error",
    "🚫": "error",
}


def show_click_tooltip(
    widget, text: str, icon: str = "", duration: int = 1200, style: str = None
):
    """显示 Toast 风格的点击反馈提示

    在窗口底部中央显示卡片式提示，带淡出动画。

    Args:
        widget: 触发提示的组件（用于获取窗口）
        text: 提示文本
        icon: 图标（可选，会自动根据图标选择样式）
        duration: 显示时长（毫秒），默认 1200ms
        style: 样式类型 ("success", "info", "warning", "error")，可选

    示例：
        show_click_tooltip(self, "已复制", "✅")
        show_click_tooltip(self, "操作失败", "❌", style="error")
    """
    from PyQt6.QtCore import QEasingCurve, QPropertyAnimation
    from PyQt6.QtWidgets import QGraphicsOpacityEffect

    # 获取窗口
    window = widget.window() if widget.window() else widget

    # 自动确定样式
    if style is None:
        style = ICON_STYLE_MAP.get(icon, "info")

    theme = _get_current_theme()
    toast_style = TOAST_STYLES.get(style, TOAST_STYLES["info"])[theme]

    # 创建 Toast 标签
    toast = QLabel(window)
    content = f"{icon} {text}".strip() if icon else text
    toast.setText(content)
    toast.setStyleSheet(
        f"""
        QLabel {{
            background-color: {toast_style['bg']};
            color: white;
            padding: 10px 20px;
            border-radius: 8px;
            border: 1px solid {toast_style['border']};
            font-size: 13px;
            font-weight: 500;
        }}
    """
    )
    toast.adjustSize()

    # 定位到窗口底部中央
    toast.move(
        (window.width() - toast.width()) // 2,
        window.height() - toast.height() - 30,
    )
    toast.show()
    toast.raise_()

    # 设置透明度效果
    opacity_effect = QGraphicsOpacityEffect(toast)
    toast.setGraphicsEffect(opacity_effect)

    # 延迟后淡出并销毁
    def fade_out():
        try:
            animation = QPropertyAnimation(opacity_effect, b"opacity")
            animation.setDuration(300)
            animation.setStartValue(1.0)
            animation.setEndValue(0.0)
            animation.setEasingCurve(QEasingCurve.Type.OutQuad)
            animation.finished.connect(toast.deleteLater)
            animation.start()
            # 保持引用防止被垃圾回收
            toast._animation = animation
        except RuntimeError:
            pass

    fade_timer = QTimer()
    fade_timer.setSingleShot(True)
    fade_timer.timeout.connect(fade_out)
    fade_timer.start(duration)

    # 存储引用防止垃圾回收
    toast._fade_timer = fade_timer
