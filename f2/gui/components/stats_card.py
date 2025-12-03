"""
统计卡片组件
~~~~~~~~~~~

继承自可折叠卡片的统计卡片基类。
支持多种统计数据展示、主题切换和折叠功能。
"""

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QColor, QFont
from PyQt6.QtWidgets import (
    QFrame,
    QGraphicsDropShadowEffect,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from f2.gui.components.collapsible_card import CollapsibleCard
from f2.gui.components.separator import GradientSeparator
from f2.gui.themes.theme_manager import ThemeManager


class StatsCard(CollapsibleCard):
    """统计卡片基类 - 继承可折叠卡片

    支持以下功能：
    - 折叠/展开功能
    - 多统计项显示
    - 主题切换支持
    - 图标和标签
    """

    # 暗色主题样式
    DARK_STYLES = {
        "card_bg": "qlineargradient(x1:0, y1:0, x2:1, y2:1, "
        "stop:0 rgba(91, 95, 199, 0.12), "
        "stop:0.5 rgba(123, 107, 184, 0.08), "
        "stop:1 rgba(91, 95, 199, 0.06))",
        "card_border": "rgba(91, 95, 199, 0.25)",
        "card_hover_bg": "qlineargradient(x1:0, y1:0, x2:1, y2:1, "
        "stop:0 rgba(91, 95, 199, 0.18), "
        "stop:0.5 rgba(123, 107, 184, 0.12), "
        "stop:1 rgba(91, 95, 199, 0.10))",
        "card_hover_border": "rgba(123, 107, 184, 0.35)",
        "title_color": "#D4D4E0",
        "value_color": "#FFFFFF",
        "subtitle_color": "#8B8BA0",
        "icon_color": "#9CA3C0",
        "badge_bg": "rgba(91, 95, 199, 0.2)",
        "badge_text": "#A5B4FC",
    }

    # 亮色主题样式
    LIGHT_STYLES = {
        "card_bg": "qlineargradient(x1:0, y1:0, x2:1, y2:1, "
        "stop:0 rgba(124, 127, 232, 0.1), "
        "stop:0.5 rgba(155, 139, 216, 0.07), "
        "stop:1 rgba(124, 127, 232, 0.05))",
        "card_border": "rgba(124, 127, 232, 0.2)",
        "card_hover_bg": "qlineargradient(x1:0, y1:0, x2:1, y2:1, "
        "stop:0 rgba(124, 127, 232, 0.15), "
        "stop:0.5 rgba(155, 139, 216, 0.1), "
        "stop:1 rgba(124, 127, 232, 0.08))",
        "card_hover_border": "rgba(155, 139, 216, 0.3)",
        "title_color": "#4A4A60",
        "value_color": "#2A2A40",
        "subtitle_color": "#6A6A80",
        "icon_color": "#6B6ED8",
        "badge_bg": "rgba(124, 127, 232, 0.15)",
        "badge_text": "#6B6ED8",
    }

    def __init__(
        self,
        parent=None,
        title: str = "",
        icon: str = "",
        subtitle: str = "",
        collapsed_by_default: bool = False,
        card_id: str = None,
        save_state: bool = True,
    ):
        """初始化统计卡片

        Args:
            parent: 父组件
            title: 卡片标题
            icon: 图标（emoji）
            subtitle: 副标题
            collapsed_by_default: 是否默认折叠
            card_id: 卡片ID（用于保存状态）
            save_state: 是否保存折叠状态
        """
        super().__init__(
            parent=parent,
            title=title,
            icon=icon,
            subtitle=subtitle,
            collapsed_by_default=collapsed_by_default,
            show_toggle_button=True,
            card_id=card_id,
            save_state=save_state,
        )

        # 统计项存储
        self._stat_items = {}
        self._stat_widgets = {}

        # 设置卡片样式
        self.setObjectName("StatsCard")
        self._apply_card_style()

        # 连接主题切换信号
        ThemeManager().theme_changed.connect(self._on_theme_changed)

    def _get_styles(self):
        """获取当前主题的样式"""
        theme = ThemeManager().current_theme
        if theme == "light":
            return self.LIGHT_STYLES
        return self.DARK_STYLES

    def _apply_card_style(self):
        """应用卡片样式"""
        styles = self._get_styles()
        self.setStyleSheet(
            f"""
            QFrame#StatsCard {{
                background: {styles['card_bg']};
                border: 1px solid {styles['card_border']};
                border-radius: 10px;
            }}
            QFrame#StatsCard:hover {{
                background: {styles['card_hover_bg']};
                border-color: {styles['card_hover_border']};
            }}
        """
        )

        # 更新标题颜色
        if hasattr(self, "_title_label"):
            self._title_label.setStyleSheet(
                f"""
                color: {styles['title_color']};
                font-size: 13px;
                font-weight: 600;
                background: transparent;
            """
            )

        # 更新副标题颜色
        if hasattr(self, "_subtitle_label"):
            self._subtitle_label.setStyleSheet(
                f"""
                color: {styles['subtitle_color']};
                font-size: 11px;
                background: transparent;
            """
            )

        # 更新提示标签颜色
        if hasattr(self, "_hint_label"):
            self._hint_label.setStyleSheet(
                f"""
                color: {styles['subtitle_color']};
                font-size: 10px;
                background: transparent;
            """
            )

        # 更新所有统计值的颜色
        self._update_stat_colors()

    def _update_stat_colors(self):
        """更新统计项颜色"""
        styles = self._get_styles()
        for key, widgets in self._stat_widgets.items():
            if "value_label" in widgets:
                widgets["value_label"].setStyleSheet(
                    f"""
                    color: {styles['value_color']};
                    background: transparent;
                    font-weight: 700;
                    letter-spacing: 0.5px;
                """
                )
            if "title_label" in widgets:
                widgets["title_label"].setStyleSheet(
                    f"""
                    color: {styles['subtitle_color']};
                    font-size: 11px;
                    font-weight: 500;
                    background: transparent;
                """
                )
            if "icon_label" in widgets:
                widgets["icon_label"].setStyleSheet(
                    f"""
                    color: {styles['icon_color']};
                    font-size: 14px;
                    background: transparent;
                """
                )

    def _on_theme_changed(self, theme: str):
        """主题切换回调"""
        self._apply_card_style()

    def add_stat_item(
        self,
        key: str,
        title: str,
        value: str = "0",
        icon: str = "",
        value_font_size: int = 18,
    ) -> QWidget:
        """添加统计项

        Args:
            key: 统计项唯一标识
            title: 统计项标题
            value: 初始值
            icon: 图标（emoji）
            value_font_size: 数值字体大小

        Returns:
            统计项组件
        """
        styles = self._get_styles()

        # 创建统计项容器
        item_widget = QWidget()
        item_widget.setStyleSheet("background: transparent;")
        item_layout = QVBoxLayout(item_widget)
        item_layout.setContentsMargins(0, 0, 0, 0)
        item_layout.setSpacing(2)
        item_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # 图标（可选）
        icon_label = None
        if icon:
            icon_label = QLabel(icon)
            icon_label.setStyleSheet(
                f"""
                color: {styles['icon_color']};
                font-size: 14px;
                background: transparent;
            """
            )
            icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            item_layout.addWidget(icon_label)

        # 数值
        value_label = QLabel(value)
        value_label.setStyleSheet(
            f"""
            color: {styles['value_color']};
            background: transparent;
            font-size: {value_font_size}px;
            font-weight: 700;
            letter-spacing: 0.5px;
        """
        )
        value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        item_layout.addWidget(value_label)

        # 标题
        title_label = QLabel(title)
        title_label.setStyleSheet(
            f"""
            color: {styles['subtitle_color']};
            font-size: 11px;
            font-weight: 500;
            background: transparent;
        """
        )
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        item_layout.addWidget(title_label)

        # 存储引用
        self._stat_items[key] = {"title": title, "value": value, "icon": icon}
        self._stat_widgets[key] = {
            "widget": item_widget,
            "value_label": value_label,
            "title_label": title_label,
            "icon_label": icon_label,
        }

        return item_widget

    def set_stat_value(self, key: str, value: str):
        """设置统计项的值

        Args:
            key: 统计项唯一标识
            value: 新值
        """
        if key in self._stat_items:
            self._stat_items[key]["value"] = value
        if key in self._stat_widgets and "value_label" in self._stat_widgets[key]:
            self._stat_widgets[key]["value_label"].setText(value)

    def get_stat_value(self, key: str) -> str:
        """获取统计项的值

        Args:
            key: 统计项唯一标识

        Returns:
            统计项的值
        """
        return self._stat_items.get(key, {}).get("value", "0")


class HorizontalStatsCard(StatsCard):
    """水平布局统计卡片 - 统计项水平排列"""

    def __init__(
        self,
        parent=None,
        title: str = "",
        icon: str = "",
        subtitle: str = "",
        collapsed_by_default: bool = False,
        card_id: str = None,
        save_state: bool = True,
        stat_item_width: int = None,
        stat_item_min_width: int = 60,
        spacing: int = 20,
    ):
        """初始化水平统计卡片

        Args:
            stat_item_width: 统计项固定宽度（None 表示自适应）
            stat_item_min_width: 统计项最小宽度
            spacing: 统计项之间的间距
        """
        super().__init__(
            parent=parent,
            title=title,
            icon=icon,
            subtitle=subtitle,
            collapsed_by_default=collapsed_by_default,
            card_id=card_id,
            save_state=save_state,
        )

        self._stat_item_width = stat_item_width
        self._stat_item_min_width = stat_item_min_width

        # 创建统计项水平容器
        self._stats_container = QWidget()
        self._stats_container.setStyleSheet("background: transparent;")
        self._stats_layout = QHBoxLayout(self._stats_container)
        self._stats_layout.setContentsMargins(8, 8, 8, 8)
        self._stats_layout.setSpacing(spacing)

        # 添加到内容区域
        self.add_content_widget(self._stats_container)

    def add_stat_item(
        self,
        key: str,
        title: str,
        value: str = "0",
        icon: str = "",
        value_font_size: int = 18,
        fixed_width: int = None,
    ) -> QWidget:
        """添加统计项到水平布局

        Args:
            key: 统计项唯一标识
            title: 统计项标题
            value: 初始值
            icon: 图标
            value_font_size: 数值字体大小
            fixed_width: 此统计项的固定宽度（覆盖全局设置）
        """
        item_widget = super().add_stat_item(key, title, value, icon, value_font_size)

        # 设置宽度
        width = fixed_width or self._stat_item_width
        if width is not None:
            item_widget.setFixedWidth(width)
        else:
            item_widget.setMinimumWidth(self._stat_item_min_width)

        self._stats_layout.addWidget(item_widget)
        return item_widget

    def add_stretch(self):
        """添加弹性空间"""
        self._stats_layout.addStretch()

    def add_separator(self, fixed_height: int = 30):
        """添加分隔线 - 使用渐变分割线（虚-实-虚效果）

        Args:
            fixed_height: 分隔线区域高度
        """
        from PyQt6.QtCore import Qt

        separator = GradientSeparator(
            height=1,
            orientation=Qt.Orientation.Vertical,
            margin_h=0,
            margin_v=4,
        )
        separator.setFixedHeight(fixed_height)
        self._stats_layout.addWidget(separator)

    def set_container_height(self, height: int):
        """设置统计容器固定高度"""
        self._stats_container.setFixedHeight(height)

    def set_spacing(self, spacing: int):
        """设置统计项之间的间距"""
        self._stats_layout.setSpacing(spacing)


class GridStatsCard(StatsCard):
    """网格布局统计卡片 - 统计项网格排列"""

    def __init__(
        self,
        parent=None,
        title: str = "",
        icon: str = "",
        subtitle: str = "",
        columns: int = 4,
        collapsed_by_default: bool = False,
        card_id: str = None,
        save_state: bool = True,
    ):
        """初始化网格统计卡片

        Args:
            columns: 每行显示的统计项数量
        """
        super().__init__(
            parent=parent,
            title=title,
            icon=icon,
            subtitle=subtitle,
            collapsed_by_default=collapsed_by_default,
            card_id=card_id,
            save_state=save_state,
        )

        self._columns = columns
        self._current_row = 0
        self._current_col = 0

        # 创建统计项网格容器
        self._stats_container = QWidget()
        self._stats_container.setStyleSheet("background: transparent;")
        self._stats_layout = QGridLayout(self._stats_container)
        self._stats_layout.setContentsMargins(8, 8, 8, 8)
        self._stats_layout.setSpacing(16)

        # 添加到内容区域
        self.add_content_widget(self._stats_container)

    def add_stat_item(
        self,
        key: str,
        title: str,
        value: str = "0",
        icon: str = "",
        value_font_size: int = 18,
    ) -> QWidget:
        """添加统计项到网格布局"""
        item_widget = super().add_stat_item(key, title, value, icon, value_font_size)

        # 添加到网格
        self._stats_layout.addWidget(
            item_widget,
            self._current_row,
            self._current_col,
            Qt.AlignmentFlag.AlignCenter,
        )

        # 更新位置
        self._current_col += 1
        if self._current_col >= self._columns:
            self._current_col = 0
            self._current_row += 1

        return item_widget


class CompactStatsRow(QWidget):
    """紧凑统计行 - 用于在头部显示简要统计"""

    # 暗色主题样式
    DARK_STYLES = {
        "value_color": "#FFFFFF",
        "title_color": "#8B8BA0",
        "icon_color": "#9CA3C0",
    }

    # 亮色主题样式
    LIGHT_STYLES = {
        "value_color": "#2A2A40",
        "title_color": "#6A6A80",
        "icon_color": "#6B6ED8",
    }

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("background: transparent;")

        self._layout = QHBoxLayout(self)
        self._layout.setContentsMargins(0, 0, 0, 0)
        self._layout.setSpacing(12)

        self._stat_widgets = {}

        # 连接主题切换
        ThemeManager().theme_changed.connect(self._on_theme_changed)

    def _get_styles(self):
        """获取当前主题的样式"""
        theme = ThemeManager().current_theme
        if theme == "light":
            return self.LIGHT_STYLES
        return self.DARK_STYLES

    def _on_theme_changed(self, theme: str):
        """主题切换回调"""
        self._update_colors()

    def _update_colors(self):
        """更新颜色"""
        styles = self._get_styles()
        for key, widgets in self._stat_widgets.items():
            if "value_label" in widgets:
                widgets["value_label"].setStyleSheet(
                    f"""
                    color: {styles['value_color']};
                    background: transparent;
                """
                )
            if "title_label" in widgets:
                widgets["title_label"].setStyleSheet(
                    f"""
                    color: {styles['title_color']};
                    font-size: 10px;
                    background: transparent;
                """
                )
            if "icon_label" in widgets:
                widgets["icon_label"].setStyleSheet(
                    f"""
                    color: {styles['icon_color']};
                    font-size: 11px;
                    background: transparent;
                """
                )

    def add_stat(
        self,
        key: str,
        icon: str,
        value: str,
        title: str = "",
        value_font_size: int = 12,
    ):
        """添加紧凑统计项

        Args:
            key: 唯一标识
            icon: 图标
            value: 数值
            title: 标题（可选，显示在数值后）
            value_font_size: 数值字体大小
        """
        styles = self._get_styles()

        item = QWidget()
        item.setStyleSheet("background: transparent;")
        layout = QHBoxLayout(item)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)

        # 图标
        icon_label = QLabel(icon)
        icon_label.setStyleSheet(
            f"""
            color: {styles['icon_color']};
            font-size: 11px;
            background: transparent;
        """
        )
        layout.addWidget(icon_label)

        # 数值
        value_label = QLabel(value)
        value_label.setStyleSheet(
            f"""
            color: {styles['value_color']};
            background: transparent;
        """
        )
        value_font = value_label.font()
        value_font.setPointSize(value_font_size)
        value_font.setWeight(QFont.Weight.Bold)
        value_label.setFont(value_font)
        layout.addWidget(value_label)

        # 标题（可选）
        title_label = None
        if title:
            title_label = QLabel(title)
            title_label.setStyleSheet(
                f"""
                color: {styles['title_color']};
                font-size: 10px;
                background: transparent;
            """
            )
            layout.addWidget(title_label)

        self._layout.addWidget(item)
        self._stat_widgets[key] = {
            "widget": item,
            "icon_label": icon_label,
            "value_label": value_label,
            "title_label": title_label,
        }

    def set_value(self, key: str, value: str):
        """设置统计值"""
        if key in self._stat_widgets and "value_label" in self._stat_widgets[key]:
            self._stat_widgets[key]["value_label"].setText(value)

    def add_stretch(self):
        """添加弹性空间"""
        self._layout.addStretch()
