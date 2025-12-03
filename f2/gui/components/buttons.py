"""
按钮组件
~~~~~~~~

提供统一样式的按钮组件，支持渐变色和主题切换。
所有按钮样式由 ThemeManager 统一管理。
"""

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QCursor
from PyQt6.QtWidgets import QPushButton


class GradientButton(QPushButton):
    """渐变按钮基类

    提供统一的渐变按钮样式，通过 button_type 参数指定不同的渐变色。
    样式配置支持明暗主题切换。
    """

    # 暗色主题按钮样式配置 - 低饱和度柔和色调
    DARK_STYLES = {
        "primary": {
            # 柔和蓝紫渐变
            "normal": "qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #5B5FC7, stop:1 #7B6BB8)",
            "hover": "qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #6E72D5, stop:1 #8E7EC8)",
            "pressed": "qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #4A4EB0, stop:1 #6A5AA8)",
            "text": "#FFFFFF",
            "disabled_bg": "#3D3D52",
            "disabled_text": "#6B7280",
        },
        "danger": {
            # 柔和玫红渐变
            "normal": "qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #C75B5B, stop:1 #B85B7B)",
            "hover": "qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #D56E6E, stop:1 #C86E8E)",
            "pressed": "qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #B04A4A, stop:1 #A84A6A)",
            "text": "#FFFFFF",
            "disabled_bg": "#3D3D52",
            "disabled_text": "#6B7280",
        },
        "success": {
            # 柔和青绿渐变
            "normal": "qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #4A9B7C, stop:1 #3D8B8B)",
            "hover": "qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #5AAB8C, stop:1 #4D9B9B)",
            "pressed": "qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #3A8B6C, stop:1 #2D7B7B)",
            "text": "#FFFFFF",
            "disabled_bg": "#3D3D52",
            "disabled_text": "#6B7280",
        },
        "warning": {
            # 柔和琥珀渐变
            "normal": "qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #C9A04A, stop:1 #B8944A)",
            "hover": "qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #D9B05A, stop:1 #C8A45A)",
            "pressed": "qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #B9903A, stop:1 #A8843A)",
            "text": "#1A1A2E",
            "disabled_bg": "#3D3D52",
            "disabled_text": "#6B7280",
        },
        "secondary": {
            # 柔和灰蓝渐变
            "normal": "qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #454560, stop:1 #505068)",
            "hover": "qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #505070, stop:1 #5A5A78)",
            "pressed": "qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #3A3A50, stop:1 #454558)",
            "text": "#D4D4E0",
            "disabled_bg": "#2D2D40",
            "disabled_text": "#5A5A70",
        },
        "ghost": {
            # 透明背景 - 暗色调
            "normal": "transparent",
            "hover": "rgba(91, 95, 199, 0.12)",
            "pressed": "rgba(91, 95, 199, 0.18)",
            "text": "#9CA3C0",
            "disabled_bg": "transparent",
            "disabled_text": "#5A5A70",
        },
        "text": {
            # 纯文本按钮
            "normal": "transparent",
            "hover": "rgba(255, 255, 255, 0.05)",
            "pressed": "rgba(255, 255, 255, 0.08)",
            "text": "#8B8BA0",
            "disabled_bg": "transparent",
            "disabled_text": "#4A4A60",
        },
    }

    # 亮色主题按钮样式配置 - 清新明亮色调
    LIGHT_STYLES = {
        "primary": {
            # 清新蓝紫渐变
            "normal": "qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #7C7FE8, stop:1 #9B8BD8)",
            "hover": "qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #8B8EF0, stop:1 #AA9AE8)",
            "pressed": "qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #6B6ED8, stop:1 #8A7AC8)",
            "text": "#FFFFFF",
            "disabled_bg": "#E0E0E8",
            "disabled_text": "#9090A0",
        },
        "danger": {
            # 清新珊瑚渐变
            "normal": "qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #E87C7C, stop:1 #D87C9C)",
            "hover": "qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #F08B8B, stop:1 #E88BAB)",
            "pressed": "qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #D86C6C, stop:1 #C86C8C)",
            "text": "#FFFFFF",
            "disabled_bg": "#E0E0E8",
            "disabled_text": "#9090A0",
        },
        "success": {
            # 清新薄荷渐变
            "normal": "qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #5CB89C, stop:1 #4DA8A8)",
            "hover": "qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #6CC8AC, stop:1 #5DB8B8)",
            "pressed": "qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #4CA88C, stop:1 #3D9898)",
            "text": "#FFFFFF",
            "disabled_bg": "#E0E0E8",
            "disabled_text": "#9090A0",
        },
        "warning": {
            # 清新蜂蜜渐变
            "normal": "qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #E8B85C, stop:1 #D8AC5C)",
            "hover": "qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #F0C86C, stop:1 #E8BC6C)",
            "pressed": "qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #D8A84C, stop:1 #C89C4C)",
            "text": "#3A3A4A",
            "disabled_bg": "#E0E0E8",
            "disabled_text": "#9090A0",
        },
        "secondary": {
            # 清新灰蓝渐变
            "normal": "qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #EAEAF0, stop:1 #E0E0E8)",
            "hover": "qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #E0E0E8, stop:1 #D6D6E0)",
            "pressed": "qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #D6D6E0, stop:1 #CCCCD8)",
            "text": "#3A3A50",
            "disabled_bg": "#F0F0F4",
            "disabled_text": "#B0B0C0",
        },
        "ghost": {
            # 透明背景 - 亮色调
            "normal": "transparent",
            "hover": "rgba(124, 127, 232, 0.1)",
            "pressed": "rgba(124, 127, 232, 0.15)",
            "text": "#6B6ED8",
            "disabled_bg": "transparent",
            "disabled_text": "#B0B0C0",
        },
        "text": {
            # 纯文本按钮
            "normal": "transparent",
            "hover": "rgba(0, 0, 0, 0.04)",
            "pressed": "rgba(0, 0, 0, 0.06)",
            "text": "#6A6A80",
            "disabled_bg": "transparent",
            "disabled_text": "#C0C0D0",
        },
    }

    # 当前主题（类变量）
    _current_theme = "dark"
    # 所有按钮实例的弱引用列表，用于主题切换时更新
    _instances = []

    @classmethod
    def set_theme(cls, theme: str):
        """设置当前主题并更新所有按钮实例

        Args:
            theme: 主题名称 ("dark" 或 "light")
        """
        cls._current_theme = theme
        # 更新所有存活的按钮实例
        for btn in cls._instances[:]:
            try:
                btn.update_theme()
            except RuntimeError:
                # 按钮已被销毁，从列表中移除
                cls._instances.remove(btn)

    @classmethod
    def get_styles(cls):
        """获取当前主题的样式配置"""
        if cls._current_theme == "light":
            return cls.LIGHT_STYLES
        return cls.DARK_STYLES

    def __init__(
        self,
        text: str = "",
        button_type: str = "primary",
        parent=None,
        fixed_height: int = 26,
        fixed_width: int = None,
        min_width: int = 50,
        icon: str = None,
    ):
        """初始化渐变按钮

        Args:
            text: 按钮文本
            button_type: 按钮类型 ("primary", "danger", "success", "warning", "secondary", "ghost", "text")
            parent: 父组件
            fixed_height: 固定高度
            fixed_width: 固定宽度（可选）
            min_width: 最小宽度
            icon: 图标文本（emoji 或字符）
        """
        display_text = f"{icon} {text}" if icon else text
        super().__init__(display_text, parent)

        self._button_type = button_type
        self._text = text
        self._icon = icon
        self._fixed_width = fixed_width  # 保存以便样式应用时使用

        # 注册实例以便主题切换时更新
        GradientButton._instances.append(self)

        # 设置尺寸
        self.setFixedHeight(fixed_height)
        if fixed_width is not None:
            # 强制设置固定宽度，覆盖所有尺寸限制
            self.setMinimumWidth(fixed_width)
            self.setMaximumWidth(fixed_width)
            self.setFixedWidth(fixed_width)
        else:
            self.setMinimumWidth(min_width)

        # 设置光标
        self.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))

        # 应用样式
        self._apply_style()

    def _get_style_config(self):
        """获取当前按钮类型的样式配置"""
        styles = self.get_styles()
        return styles.get(self._button_type, styles["primary"])

    def _apply_style(self):
        """应用按钮样式"""
        style = self._get_style_config()
        # 如果设置了固定宽度，减小 padding 以适应
        padding = "4px 4px" if self._fixed_width is not None else "4px 12px"
        self.setStyleSheet(
            f"""
            QPushButton {{
                background: {style['normal']};
                color: {style['text']};
                border: none;
                border-radius: 4px;
                padding: {padding};
                font-size: 12px;
                font-weight: 500;
            }}
            QPushButton:hover {{
                background: {style['hover']};
            }}
            QPushButton:pressed {{
                background: {style['pressed']};
            }}
            QPushButton:disabled {{
                background: {style['disabled_bg']};
                color: {style['disabled_text']};
            }}
        """
        )

    def update_theme(self):
        """更新主题样式（响应主题切换）"""
        self._apply_style()

    def set_button_type(self, button_type: str):
        """切换按钮类型

        Args:
            button_type: 按钮类型
        """
        styles = self.get_styles()
        if button_type in styles:
            self._button_type = button_type
            self._apply_style()

    def set_icon(self, icon: str):
        """设置图标

        Args:
            icon: 图标文本（emoji 或字符）
        """
        self._icon = icon
        display_text = f"{icon} {self._text}" if icon else self._text
        self.setText(display_text)


class PrimaryButton(GradientButton):
    """主要按钮 - 蓝紫渐变"""

    def __init__(self, text: str = "", parent=None, **kwargs):
        super().__init__(text, button_type="primary", parent=parent, **kwargs)


class DangerButton(GradientButton):
    """危险按钮 - 橙红渐变"""

    def __init__(self, text: str = "", parent=None, **kwargs):
        super().__init__(text, button_type="danger", parent=parent, **kwargs)


class SuccessButton(GradientButton):
    """成功按钮 - 绿色渐变"""

    def __init__(self, text: str = "", parent=None, **kwargs):
        super().__init__(text, button_type="success", parent=parent, **kwargs)


class WarningButton(GradientButton):
    """警告按钮 - 黄橙渐变"""

    def __init__(self, text: str = "", parent=None, **kwargs):
        super().__init__(text, button_type="warning", parent=parent, **kwargs)


class SecondaryButton(GradientButton):
    """次要按钮 - 灰色渐变"""

    def __init__(self, text: str = "", parent=None, **kwargs):
        super().__init__(text, button_type="secondary", parent=parent, **kwargs)


class GhostButton(GradientButton):
    """幽灵按钮 - 透明背景"""

    def __init__(self, text: str = "", parent=None, **kwargs):
        super().__init__(text, button_type="ghost", parent=parent, **kwargs)


class TextButton(GradientButton):
    """文本按钮 - 纯文本样式"""

    def __init__(self, text: str = "", parent=None, **kwargs):
        super().__init__(text, button_type="text", parent=parent, **kwargs)


# 便捷函数
def create_button(
    text: str,
    button_type: str = "primary",
    fixed_height: int = 26,
    fixed_width: int = None,
    min_width: int = 50,
    icon: str = None,
    parent=None,
) -> GradientButton:
    """创建渐变按钮的便捷函数

    Args:
        text: 按钮文本
        button_type: 按钮类型
        fixed_height: 固定高度
        fixed_width: 固定宽度（可选）
        min_width: 最小宽度
        icon: 图标文本（emoji 或字符）
        parent: 父组件

    Returns:
        GradientButton: 渐变按钮实例
    """
    return GradientButton(
        text=text,
        button_type=button_type,
        parent=parent,
        fixed_height=fixed_height,
        fixed_width=fixed_width,
        min_width=min_width,
        icon=icon,
    )
