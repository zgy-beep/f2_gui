# -*- coding:utf-8 -*-
# @Information  :
# @Author       : ZGY
# @Date         : 2025-12-02 17:40:11
# @FilePath     : /f2_gui/f2/gui/components/labels.py
# @LastEditTime : 2025-12-03 10:02:32

"""
标签组件
~~~~~~~~

自定义样式的 QLabel，支持多种卡片样式和主题切换。
"""

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QHBoxLayout, QLabel, QVBoxLayout, QWidget

# ===================== 主题样式定义 =====================
# 夜间模式
DARK_STYLES = {
    # 基础文字颜色
    "title_color": "#F3F4F6",
    "subtitle_color": "#9CA3AF",
    "hint_color": "#6B7280",
    "value_color": "#FFFFFF",
    # 卡片标签 - 蓝紫色
    "tag_bg": "rgba(99, 102, 241, 0.15)",
    "tag_border": "rgba(99, 102, 241, 0.25)",
    "tag_text": "#818CF8",
    # 成功标签
    "success_bg": "rgba(16, 185, 129, 0.12)",
    "success_border": "rgba(16, 185, 129, 0.25)",
    "success_text": "#10B981",
    # 警告标签
    "warning_bg": "rgba(245, 158, 11, 0.12)",
    "warning_border": "rgba(245, 158, 11, 0.25)",
    "warning_text": "#F59E0B",
    # 错误标签
    "error_bg": "rgba(239, 68, 68, 0.12)",
    "error_border": "rgba(239, 68, 68, 0.25)",
    "error_text": "#EF4444",
    # 信息标签
    "info_bg": "rgba(99, 102, 241, 0.12)",
    "info_border": "rgba(99, 102, 241, 0.25)",
    "info_text": "#818CF8",
    # 中性标签
    "neutral_bg": "rgba(255, 255, 255, 0.08)",
    "neutral_border": "rgba(255, 255, 255, 0.15)",
    "neutral_text": "#D1D5DB",
}

# 日间模式
LIGHT_STYLES = {
    # 基础文字颜色
    "title_color": "#1F2937",
    "subtitle_color": "#6B7280",
    "hint_color": "#9CA3AF",
    "value_color": "#111827",
    # 卡片标签 - 绿色
    "tag_bg": "rgba(74, 222, 128, 0.15)",
    "tag_border": "rgba(74, 222, 128, 0.3)",
    "tag_text": "#059669",
    # 成功标签
    "success_bg": "rgba(16, 185, 129, 0.1)",
    "success_border": "rgba(16, 185, 129, 0.25)",
    "success_text": "#059669",
    # 警告标签
    "warning_bg": "rgba(245, 158, 11, 0.1)",
    "warning_border": "rgba(245, 158, 11, 0.25)",
    "warning_text": "#D97706",
    # 错误标签
    "error_bg": "rgba(239, 68, 68, 0.1)",
    "error_border": "rgba(239, 68, 68, 0.25)",
    "error_text": "#DC2626",
    # 信息标签
    "info_bg": "rgba(59, 130, 246, 0.1)",
    "info_border": "rgba(59, 130, 246, 0.25)",
    "info_text": "#2563EB",
    # 中性标签
    "neutral_bg": "rgba(0, 0, 0, 0.05)",
    "neutral_border": "rgba(0, 0, 0, 0.1)",
    "neutral_text": "#4B5563",
}


# ===================== 平台颜色配置 =====================
PLATFORM_COLORS = {
    "douyin": {
        "bg": "rgba(254, 44, 85, 0.15)",
        "text": "#FE2C55",
        "border": "rgba(254, 44, 85, 0.3)",
        "icon": "🎵",
        "name": "抖音",
    },
    "tiktok": {
        "bg": "rgba(0, 242, 234, 0.15)",
        "text": "#00F2EA",
        "border": "rgba(0, 242, 234, 0.3)",
        "icon": "🎬",
        "name": "TikTok",
    },
    "weibo": {
        "bg": "rgba(255, 140, 0, 0.15)",
        "text": "#FF8C00",
        "border": "rgba(255, 140, 0, 0.3)",
        "icon": "📰",
        "name": "微博",
    },
    "twitter": {
        "bg": "rgba(29, 161, 242, 0.15)",
        "text": "#1DA1F2",
        "border": "rgba(29, 161, 242, 0.3)",
        "icon": "🐦",
        "name": "Twitter",
    },
    "instagram": {
        "bg": "rgba(225, 48, 108, 0.15)",
        "text": "#E1306C",
        "border": "rgba(225, 48, 108, 0.3)",
        "icon": "📷",
        "name": "Instagram",
    },
    "youtube": {
        "bg": "rgba(255, 0, 0, 0.15)",
        "text": "#FF0000",
        "border": "rgba(255, 0, 0, 0.3)",
        "icon": "▶️",
        "name": "YouTube",
    },
    "bilibili": {
        "bg": "rgba(0, 174, 236, 0.15)",
        "text": "#00AEEC",
        "border": "rgba(0, 174, 236, 0.3)",
        "icon": "📺",
        "name": "哔哩哔哩",
    },
    "xiaohongshu": {
        "bg": "rgba(255, 45, 85, 0.15)",
        "text": "#FF2D55",
        "border": "rgba(255, 45, 85, 0.3)",
        "icon": "📕",
        "name": "小红书",
    },
}


# ===================== 模式颜色配置 =====================
MODE_COLORS = {
    "post": {
        "bg": "rgba(99, 102, 241, 0.15)",
        "text": "#818CF8",
        "border": "rgba(99, 102, 241, 0.3)",
        "icon": "📋",
        "name": "主页作品",
    },
    "like": {
        "bg": "rgba(236, 72, 153, 0.15)",
        "text": "#EC4899",
        "border": "rgba(236, 72, 153, 0.3)",
        "icon": "❤️",
        "name": "喜欢",
    },
    "collect": {
        "bg": "rgba(245, 158, 11, 0.15)",
        "text": "#F59E0B",
        "border": "rgba(245, 158, 11, 0.3)",
        "icon": "⭐",
        "name": "收藏",
    },
    "mix": {
        "bg": "rgba(139, 92, 246, 0.15)",
        "text": "#8B5CF6",
        "border": "rgba(139, 92, 246, 0.3)",
        "icon": "📁",
        "name": "合集",
    },
    "music": {
        "bg": "rgba(16, 185, 129, 0.15)",
        "text": "#10B981",
        "border": "rgba(16, 185, 129, 0.3)",
        "icon": "🎵",
        "name": "音乐",
    },
    "search": {
        "bg": "rgba(6, 182, 212, 0.15)",
        "text": "#06B6D4",
        "border": "rgba(6, 182, 212, 0.3)",
        "icon": "🔍",
        "name": "搜索",
    },
    "live": {
        "bg": "rgba(239, 68, 68, 0.15)",
        "text": "#EF4444",
        "border": "rgba(239, 68, 68, 0.3)",
        "icon": "📺",
        "name": "直播",
    },
    "feed": {
        "bg": "rgba(168, 85, 247, 0.15)",
        "text": "#A855F7",
        "border": "rgba(168, 85, 247, 0.3)",
        "icon": "📰",
        "name": "推荐",
    },
    "friend": {
        "bg": "rgba(34, 197, 94, 0.15)",
        "text": "#22C55E",
        "border": "rgba(34, 197, 94, 0.3)",
        "icon": "👥",
        "name": "好友",
    },
    "video": {
        "bg": "rgba(99, 102, 241, 0.15)",
        "text": "#818CF8",
        "border": "rgba(99, 102, 241, 0.3)",
        "icon": "🎬",
        "name": "视频",
    },
    "image": {
        "bg": "rgba(236, 72, 153, 0.15)",
        "text": "#EC4899",
        "border": "rgba(236, 72, 153, 0.3)",
        "icon": "🖼️",
        "name": "图片",
    },
    "story": {
        "bg": "rgba(168, 85, 247, 0.15)",
        "text": "#A855F7",
        "border": "rgba(168, 85, 247, 0.3)",
        "icon": "📖",
        "name": "故事",
    },
    "default": {
        "bg": "rgba(107, 114, 128, 0.15)",
        "text": "#9CA3AF",
        "border": "rgba(107, 114, 128, 0.3)",
        "icon": "📦",
        "name": "默认",
    },
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


class TagLabel(QLabel):
    """卡片样式标签 - 支持多种类型和主题切换

    类型:
    - default: 默认蓝紫/绿色
    - success: 成功/绿色
    - warning: 警告/橙色
    - error: 错误/红色
    - info: 信息/蓝色
    - neutral: 中性/灰色
    - custom: 自定义颜色
    """

    def __init__(
        self,
        text: str = "",
        parent=None,
        tag_type: str = "default",
        icon: str = "",
        bg_color: str = None,
        text_color: str = None,
        border_color: str = None,
        padding: str = "5px 12px",
        border_radius: int = 6,
        font_size: int = 11,
        font_weight: int = 500,
    ):
        super().__init__(parent)

        self._text = text
        self._icon = icon
        self._tag_type = tag_type
        self._custom_bg = bg_color
        self._custom_text = text_color
        self._custom_border = border_color
        self._padding = padding
        self._border_radius = border_radius
        self._font_size = font_size
        self._font_weight = font_weight

        # 设置文本
        display_text = f"{icon} {text}" if icon else text
        self.setText(display_text)

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

    def _get_type_colors(self, styles: dict) -> tuple:
        """根据类型获取颜色"""
        type_map = {
            "default": ("tag_bg", "tag_text", "tag_border"),
            "success": ("success_bg", "success_text", "success_border"),
            "warning": ("warning_bg", "warning_text", "warning_border"),
            "error": ("error_bg", "error_text", "error_border"),
            "info": ("info_bg", "info_text", "info_border"),
            "neutral": ("neutral_bg", "neutral_text", "neutral_border"),
        }

        if self._tag_type == "custom":
            return (
                self._custom_bg or styles["tag_bg"],
                self._custom_text or styles["tag_text"],
                self._custom_border or styles["tag_border"],
            )

        bg_key, text_key, border_key = type_map.get(
            self._tag_type, ("tag_bg", "tag_text", "tag_border")
        )
        return styles[bg_key], styles[text_key], styles[border_key]

    def _apply_style(self):
        """应用当前主题样式"""
        styles = _get_styles()
        bg, text, border = self._get_type_colors(styles)

        self.setStyleSheet(
            f"""
            QLabel {{
                background-color: {bg};
                color: {text};
                border: 1px solid {border};
                padding: {self._padding};
                border-radius: {self._border_radius}px;
                font-size: {self._font_size}px;
                font-weight: {self._font_weight};
            }}
        """
        )

    def set_text(self, text: str):
        """设置文本"""
        self._text = text
        display_text = f"{self._icon} {text}" if self._icon else text
        self.setText(display_text)

    def set_icon(self, icon: str):
        """设置图标"""
        self._icon = icon
        display_text = f"{icon} {self._text}" if icon else self._text
        self.setText(display_text)

    def set_type(self, tag_type: str):
        """设置类型"""
        self._tag_type = tag_type
        self._apply_style()


class BadgeLabel(TagLabel):
    """徽章标签 - 更紧凑的样式"""

    def __init__(
        self,
        text: str = "",
        parent=None,
        tag_type: str = "default",
        icon: str = "",
        **kwargs,
    ):
        # 设置更紧凑的默认值
        kwargs.setdefault("padding", "3px 8px")
        kwargs.setdefault("border_radius", 4)
        kwargs.setdefault("font_size", 10)

        super().__init__(
            text=text,
            parent=parent,
            tag_type=tag_type,
            icon=icon,
            **kwargs,
        )


class StatusLabel(TagLabel):
    """状态标签 - 预设常用状态"""

    def __init__(
        self,
        status: str = "info",
        text: str = "",
        parent=None,
        **kwargs,
    ):
        # 状态映射
        status_map = {
            "success": ("success", "✅", "成功"),
            "error": ("error", "❌", "失败"),
            "warning": ("warning", "⚠️", "警告"),
            "info": ("info", "ℹ️", "信息"),
            "pending": ("neutral", "⏳", "等待中"),
            "running": ("info", "🔄", "进行中"),
        }

        tag_type, icon, default_text = status_map.get(status, ("neutral", "", status))

        super().__init__(
            text=text or default_text,
            parent=parent,
            tag_type=tag_type,
            icon=icon,
            **kwargs,
        )


class PlatformLabel(TagLabel):
    """平台标签 - 预设平台样式"""

    def __init__(
        self,
        platform: str = "douyin",
        parent=None,
        show_name: bool = True,
        **kwargs,
    ):
        config = PLATFORM_COLORS.get(platform, PLATFORM_COLORS["douyin"])

        text = config["name"] if show_name else ""

        super().__init__(
            text=text,
            parent=parent,
            tag_type="custom",
            icon=config["icon"],
            bg_color=config["bg"],
            text_color=config["text"],
            border_color=config["border"],
            font_weight=600,
            **kwargs,
        )


class ModeLabel(TagLabel):
    """模式标签 - 预设下载模式样式"""

    def __init__(
        self,
        mode: str = "post",
        parent=None,
        show_name: bool = True,
        **kwargs,
    ):
        config = MODE_COLORS.get(mode, MODE_COLORS["default"])

        text = config["name"] if show_name else ""

        super().__init__(
            text=text,
            parent=parent,
            tag_type="custom",
            icon=config["icon"],
            bg_color=config["bg"],
            text_color=config["text"],
            border_color=config["border"],
            **kwargs,
        )


class CountBadge(BadgeLabel):
    """计数徽章 - 显示数量"""

    def __init__(
        self,
        count: int = 0,
        suffix: str = "",
        parent=None,
        tag_type: str = "info",
        icon: str = "",
        **kwargs,
    ):
        self._count = count
        self._suffix = suffix

        text = f"{count}{suffix}" if suffix else str(count)

        super().__init__(
            text=text,
            parent=parent,
            tag_type=tag_type,
            icon=icon,
            **kwargs,
        )

    def set_count(self, count: int):
        """设置计数"""
        self._count = count
        text = f"{count}{self._suffix}" if self._suffix else str(count)
        self.set_text(text)


class TextLabel(QLabel):
    """基础文字标签 - 支持主题切换"""

    def __init__(
        self,
        text: str = "",
        parent=None,
        label_type: str = "default",  # default, title, subtitle, hint
        font_size: int = None,
        font_weight: int = None,
        color: str = None,
    ):
        super().__init__(text, parent)

        self._label_type = label_type
        self._custom_font_size = font_size
        self._custom_font_weight = font_weight
        self._custom_color = color

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

        # 类型默认值
        type_defaults = {
            "default": (styles["title_color"], 13, 400),
            "title": (styles["title_color"], 14, 600),
            "subtitle": (styles["subtitle_color"], 12, 400),
            "hint": (styles["hint_color"], 11, 400),
            "value": (styles["value_color"], 16, 700),
        }

        default_color, default_size, default_weight = type_defaults.get(
            self._label_type, (styles["title_color"], 13, 400)
        )

        color = self._custom_color or default_color
        font_size = self._custom_font_size or default_size
        font_weight = self._custom_font_weight or default_weight

        self.setStyleSheet(
            f"""
            QLabel {{
                color: {color};
                font-size: {font_size}px;
                font-weight: {font_weight};
                background: transparent;
            }}
        """
        )


class CardTextLabel(QWidget):
    """卡片模式文本组件 - 带背景的文本显示

    特点:
    - 卡片式背景（带边框和圆角）
    - 支持图标 + 标签 + 值的组合
    - 支持主题切换
    - 多种预设样式
    """

    def __init__(
        self,
        label: str = "",
        value: str = "",
        parent=None,
        icon: str = "",
        card_type: str = "default",  # default, info, success, warning, error
        layout_type: str = "horizontal",  # horizontal, vertical
        label_width: int = None,
        padding: str = "8px 12px",
        border_radius: int = 8,
        spacing: int = 8,
    ):
        super().__init__(parent)

        self._label = label
        self._value = value
        self._icon = icon
        self._card_type = card_type
        self._layout_type = layout_type
        self._label_width = label_width
        self._padding = padding
        self._border_radius = border_radius
        self._spacing = spacing

        self._setup_ui()
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

    def _setup_ui(self):
        """设置UI"""
        if self._layout_type == "vertical":
            layout = QVBoxLayout(self)
        else:
            layout = QHBoxLayout(self)

        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(self._spacing)

        # 图标 + 标签
        if self._icon or self._label:
            label_text = f"{self._icon} {self._label}" if self._icon else self._label
            self._label_widget = QLabel(label_text)
            self._label_widget.setObjectName("cardLabel")
            if self._label_width:
                self._label_widget.setFixedWidth(self._label_width)
            layout.addWidget(self._label_widget)

        # 值
        self._value_widget = QLabel(self._value)
        self._value_widget.setObjectName("cardValue")
        if self._layout_type == "horizontal":
            layout.addStretch()
        layout.addWidget(self._value_widget)

    def _get_card_colors(self, styles: dict) -> tuple:
        """获取卡片颜色"""
        type_map = {
            "default": (
                "neutral_bg",
                "neutral_border",
                "subtitle_color",
                "title_color",
            ),
            "info": ("info_bg", "info_border", "info_text", "title_color"),
            "success": ("success_bg", "success_border", "success_text", "title_color"),
            "warning": ("warning_bg", "warning_border", "warning_text", "title_color"),
            "error": ("error_bg", "error_border", "error_text", "title_color"),
        }

        bg_key, border_key, label_key, value_key = type_map.get(
            self._card_type,
            ("neutral_bg", "neutral_border", "subtitle_color", "title_color"),
        )
        return styles[bg_key], styles[border_key], styles[label_key], styles[value_key]

    def _apply_style(self):
        """应用样式"""
        styles = _get_styles()
        bg, border, label_color, value_color = self._get_card_colors(styles)

        self.setStyleSheet(
            f"""
            CardTextLabel {{
                background-color: {bg};
                border: 1px solid {border};
                border-radius: {self._border_radius}px;
                padding: {self._padding};
            }}
            QLabel#cardLabel {{
                color: {label_color};
                font-size: 12px;
                font-weight: 500;
                background: transparent;
            }}
            QLabel#cardValue {{
                color: {value_color};
                font-size: 13px;
                font-weight: 600;
                background: transparent;
            }}
        """
        )

    def set_value(self, value: str):
        """设置值"""
        self._value = value
        self._value_widget.setText(value)

    def set_label(self, label: str):
        """设置标签"""
        self._label = label
        label_text = f"{self._icon} {label}" if self._icon else label
        self._label_widget.setText(label_text)

    def value(self) -> str:
        """获取值"""
        return self._value


class KeyValueLabel(QWidget):
    """键值对标签 - 简洁的标签+值显示

    适用于表单、详情页等场景
    """

    def __init__(
        self,
        key: str = "",
        value: str = "",
        parent=None,
        icon: str = "",
        key_width: int = 80,
        spacing: int = 10,
        key_color: str = None,
        value_color: str = None,
    ):
        super().__init__(parent)

        self._key = key
        self._value = value
        self._icon = icon
        self._key_width = key_width
        self._spacing = spacing
        self._custom_key_color = key_color
        self._custom_value_color = value_color

        self._setup_ui()
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

    def _setup_ui(self):
        """设置UI"""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(self._spacing)

        # 键
        key_text = f"{self._icon} {self._key}" if self._icon else self._key
        self._key_widget = QLabel(key_text)
        self._key_widget.setObjectName("kvKey")
        self._key_widget.setFixedWidth(self._key_width)
        layout.addWidget(self._key_widget)

        # 值
        self._value_widget = QLabel(self._value)
        self._value_widget.setObjectName("kvValue")
        layout.addWidget(self._value_widget, 1)

    def _apply_style(self):
        """应用样式"""
        styles = _get_styles()
        key_color = self._custom_key_color or styles["subtitle_color"]
        value_color = self._custom_value_color or styles["title_color"]

        self.setStyleSheet(
            f"""
            KeyValueLabel {{
                background: transparent;
            }}
            QLabel#kvKey {{
                color: {key_color};
                font-size: 12px;
                font-weight: 500;
                background: transparent;
            }}
            QLabel#kvValue {{
                color: {value_color};
                font-size: 12px;
                font-weight: 400;
                background: transparent;
            }}
        """
        )

    def set_value(self, value: str):
        """设置值"""
        self._value = value
        self._value_widget.setText(value)

    def set_key(self, key: str):
        """设置键"""
        self._key = key
        key_text = f"{self._icon} {key}" if self._icon else key
        self._key_widget.setText(key_text)

    def value(self) -> str:
        """获取值"""
        return self._value


class InfoCardLabel(QWidget):
    """信息卡片标签 - 带图标的信息展示卡片

    适用于显示统计数据、状态信息等
    """

    def __init__(
        self,
        title: str = "",
        value: str = "",
        parent=None,
        icon: str = "",
        subtitle: str = "",
        card_type: str = "default",
        min_width: int = 120,
    ):
        super().__init__(parent)

        self._title = title
        self._value = value
        self._icon = icon
        self._subtitle = subtitle
        self._card_type = card_type
        self._min_width = min_width

        self.setMinimumWidth(min_width)
        self._setup_ui()
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

    def _setup_ui(self):
        """设置UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 10, 12, 10)
        layout.setSpacing(4)

        # 标题行（图标 + 标题）
        title_layout = QHBoxLayout()
        title_layout.setSpacing(6)

        if self._icon:
            self._icon_widget = QLabel(self._icon)
            self._icon_widget.setObjectName("infoIcon")
            title_layout.addWidget(self._icon_widget)

        self._title_widget = QLabel(self._title)
        self._title_widget.setObjectName("infoTitle")
        title_layout.addWidget(self._title_widget)
        title_layout.addStretch()

        layout.addLayout(title_layout)

        # 值
        self._value_widget = QLabel(self._value)
        self._value_widget.setObjectName("infoValue")
        layout.addWidget(self._value_widget)

        # 副标题
        if self._subtitle:
            self._subtitle_widget = QLabel(self._subtitle)
            self._subtitle_widget.setObjectName("infoSubtitle")
            layout.addWidget(self._subtitle_widget)

    def _get_card_colors(self, styles: dict) -> tuple:
        """获取卡片颜色"""
        type_map = {
            "default": ("neutral_bg", "neutral_border", "subtitle_color"),
            "info": ("info_bg", "info_border", "info_text"),
            "success": ("success_bg", "success_border", "success_text"),
            "warning": ("warning_bg", "warning_border", "warning_text"),
            "error": ("error_bg", "error_border", "error_text"),
        }

        bg_key, border_key, accent_key = type_map.get(
            self._card_type, ("neutral_bg", "neutral_border", "subtitle_color")
        )
        return styles[bg_key], styles[border_key], styles[accent_key]

    def _apply_style(self):
        """应用样式"""
        styles = _get_styles()
        bg, border, accent = self._get_card_colors(styles)

        self.setStyleSheet(
            f"""
            InfoCardLabel {{
                background-color: {bg};
                border: 1px solid {border};
                border-radius: 10px;
            }}
            QLabel#infoIcon {{
                font-size: 14px;
                background: transparent;
            }}
            QLabel#infoTitle {{
                color: {styles["subtitle_color"]};
                font-size: 11px;
                font-weight: 500;
                background: transparent;
            }}
            QLabel#infoValue {{
                color: {styles["title_color"]};
                font-size: 20px;
                font-weight: 700;
                background: transparent;
            }}
            QLabel#infoSubtitle {{
                color: {accent};
                font-size: 10px;
                font-weight: 400;
                background: transparent;
            }}
        """
        )

    def set_value(self, value: str):
        """设置值"""
        self._value = value
        self._value_widget.setText(value)

    def set_subtitle(self, subtitle: str):
        """设置副标题"""
        self._subtitle = subtitle
        if hasattr(self, "_subtitle_widget"):
            self._subtitle_widget.setText(subtitle)

    def value(self) -> str:
        """获取值"""
        return self._value
