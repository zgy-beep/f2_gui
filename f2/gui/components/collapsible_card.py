# -*- coding:utf-8 -*-
# @Information  :
# @Author       : ZGY
# @Date         : 2025-12-01 14:51:28
# @FilePath     : /f2_gui/f2/gui/components/collapsible_card.py
# @LastEditTime : 2025-12-02 22:26:31

"""
可折叠卡片组件
~~~~~~~~~~~~~

支持双击折叠/展开的卡片基类，折叠后显示紧凑的卡片式摘要。
使用内联样式，支持自动切换日间/夜间模式。
"""


from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QColor, QMouseEvent
from PyQt6.QtWidgets import (
    QFrame,
    QGraphicsDropShadowEffect,
    QHBoxLayout,
    QLabel,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from f2.gui.components.labels import TagLabel
from f2.gui.components.separator import GradientSeparator

# ===================== 主题样式定义 =====================
# 夜间模式 - 蓝紫色对角渐变（低饱和度）
DARK_STYLES = {
    # CollapsibleCard 卡片样式
    "card_bg": """
        qlineargradient(x1:0, y1:0, x2:1, y2:1,
            stop:0 rgba(99, 102, 241, 0.12),
            stop:0.5 rgba(139, 92, 246, 0.08),
            stop:1 rgba(99, 102, 241, 0.06))
    """,
    "card_bg_hover": """
        qlineargradient(x1:0, y1:0, x2:1, y2:1,
            stop:0 rgba(99, 102, 241, 0.18),
            stop:0.5 rgba(139, 92, 246, 0.12),
            stop:1 rgba(99, 102, 241, 0.1))
    """,
    "card_border": "rgba(99, 102, 241, 0.22)",
    "card_border_hover": "rgba(139, 92, 246, 0.38)",
    # CompactCollapsibleCard 紧凑卡片样式
    "compact_bg": """
        qlineargradient(x1:0, y1:0, x2:1, y2:1,
            stop:0 rgba(99, 102, 241, 0.1),
            stop:0.5 rgba(139, 92, 246, 0.06),
            stop:1 rgba(99, 102, 241, 0.05))
    """,
    "compact_bg_hover": """
        qlineargradient(x1:0, y1:0, x2:1, y2:1,
            stop:0 rgba(99, 102, 241, 0.15),
            stop:0.5 rgba(139, 92, 246, 0.1),
            stop:1 rgba(99, 102, 241, 0.08))
    """,
    "compact_border": "rgba(99, 102, 241, 0.18)",
    "compact_border_hover": "rgba(139, 92, 246, 0.32)",
    # 文字颜色
    "title_color": "#F3F4F6",
    "subtitle_color": "#9CA3AF",
    "hint_color": "#6B7280",
    # 标签样式
    "tag_bg": "rgba(99, 102, 241, 0.15)",
    "tag_color": "#818CF8",
}

# 日间模式 - 淡黄到淡绿对角渐变
LIGHT_STYLES = {
    # CollapsibleCard 卡片样式
    "card_bg": """
        qlineargradient(x1:0, y1:0, x2:1, y2:1,
            stop:0 rgba(253, 224, 71, 0.12),
            stop:0.5 rgba(163, 230, 53, 0.1),
            stop:1 rgba(74, 222, 128, 0.12))
    """,
    "card_bg_hover": """
        qlineargradient(x1:0, y1:0, x2:1, y2:1,
            stop:0 rgba(253, 224, 71, 0.18),
            stop:0.5 rgba(163, 230, 53, 0.15),
            stop:1 rgba(74, 222, 128, 0.18))
    """,
    "card_border": "rgba(163, 230, 53, 0.25)",
    "card_border_hover": "rgba(74, 222, 128, 0.4)",
    # CompactCollapsibleCard 紧凑卡片样式
    "compact_bg": """
        qlineargradient(x1:0, y1:0, x2:1, y2:1,
            stop:0 rgba(253, 224, 71, 0.1),
            stop:0.5 rgba(163, 230, 53, 0.08),
            stop:1 rgba(74, 222, 128, 0.1))
    """,
    "compact_bg_hover": """
        qlineargradient(x1:0, y1:0, x2:1, y2:1,
            stop:0 rgba(253, 224, 71, 0.15),
            stop:0.5 rgba(163, 230, 53, 0.12),
            stop:1 rgba(74, 222, 128, 0.15))
    """,
    "compact_border": "rgba(163, 230, 53, 0.2)",
    "compact_border_hover": "rgba(74, 222, 128, 0.35)",
    # 文字颜色
    "title_color": "#1F2937",
    "subtitle_color": "#6B7280",
    "hint_color": "#9CA3AF",
    # 标签样式
    "tag_bg": "rgba(74, 222, 128, 0.15)",
    "tag_color": "#059669",
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


class CollapsibleCard(QFrame):
    """可折叠卡片基类 - 支持双击折叠/展开"""

    # 信号
    expanded_changed = pyqtSignal(bool)  # 展开/折叠状态变化

    # 类变量：配置管理器引用（延迟初始化）
    _config_manager = None

    @classmethod
    def _get_config_manager(cls):
        """获取配置管理器实例（延迟加载）"""
        if cls._config_manager is None:
            from f2.gui.utils.config_manager import ConfigManager

            cls._config_manager = ConfigManager()
        return cls._config_manager

    def __init__(
        self,
        parent=None,
        title: str = "",
        icon: str = "",
        subtitle: str = "",
        collapsed_by_default: bool = False,
        show_toggle_button: bool = True,
        card_id: str = None,
        save_state: bool = True,
    ):
        super().__init__(parent)
        self._title = title
        self._icon = icon
        self._show_toggle_button = show_toggle_button
        self._card_id = card_id or self._generate_card_id(title)
        self._save_state = save_state
        self._is_hovered = False

        # 从配置加载保存的状态，如果没有则使用默认值
        if save_state:
            saved_expanded = self._load_expanded_state()
            if saved_expanded is not None:
                self._expanded = saved_expanded
            else:
                self._expanded = not collapsed_by_default
        else:
            self._expanded = not collapsed_by_default

        self._setup_base_ui()
        self._apply_style()
        self._connect_theme_signal()

        if subtitle:
            self.add_subtitle(subtitle)

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
        bg = styles["card_bg_hover"] if self._is_hovered else styles["card_bg"]
        border = (
            styles["card_border_hover"] if self._is_hovered else styles["card_border"]
        )

        # 使用动态 ObjectName 确保子类样式正确应用
        object_name = self.objectName() or "CollapsibleCard"
        self.setStyleSheet(
            f"""
            QFrame#{object_name} {{
                background: {bg};
                border: 1px solid {border};
                border-radius: 8px;
            }}
        """
        )

        # 更新内部组件样式
        self._update_internal_styles(styles)

    def _generate_card_id(self, title: str) -> str:
        """根据标题生成卡片ID"""
        # 移除特殊字符，生成简洁的ID
        import re

        clean_title = re.sub(r"[^\w\u4e00-\u9fff]", "", title)
        return f"card_{clean_title}" if clean_title else f"card_{id(self)}"

    def _setup_base_ui(self):
        """设置基础 UI"""
        self.setObjectName("CollapsibleCard")

        self._main_layout = QVBoxLayout(self)
        self._main_layout.setContentsMargins(0, 0, 0, 0)
        self._main_layout.setSpacing(0)

        # 折叠状态显示的头部（始终可见）
        self._header = self._create_header()
        self._main_layout.addWidget(self._header)

        # 分割线（展开时显示）- 横跨整个卡片宽度，与头部底边一致
        self._separator = GradientSeparator(margin_h=0, margin_v=0, height=1)
        self._main_layout.addWidget(self._separator)
        self._separator.setVisible(self._expanded)

        # 展开时显示的内容区域
        self._content = QWidget()
        self._content.setProperty("transparent", True)
        self._content.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self._content_layout = QVBoxLayout(self._content)
        self._content_layout.setContentsMargins(14, 0, 14, 14)
        self._content_layout.setSpacing(10)
        self._main_layout.addWidget(self._content)

        # 设置大小策略 - 水平方向填满，垂直方向固定为内容高度（不拉伸）
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Maximum)

        # 根据初始状态设置可见性
        self._content.setVisible(self._expanded)
        self._update_toggle_button()

    def _update_internal_styles(self, styles: dict):
        """更新内部组件样式"""
        if hasattr(self, "_title_label"):
            self._title_label.setStyleSheet(
                f"""
                color: {styles['title_color']};
                font-size: 13px;
                font-weight: 600;
                background: transparent;
            """
            )



        if hasattr(self, "_hint_label"):
            self._hint_label.setStyleSheet(
                f"""
                color: {styles['hint_color']};
                font-size: 10px;
                background: transparent;
            """
            )

    def _create_header(self) -> QWidget:
        """创建头部区域 - 折叠时作为卡片式摘要显示"""
        styles = _get_styles()

        header = QWidget()
        header.setObjectName("CollapsibleCardHeader")
        header.setStyleSheet("background: transparent;")

        layout = QHBoxLayout(header)
        layout.setContentsMargins(14, 12, 14, 12)
        layout.setSpacing(10)

        # 图标
        if self._icon:
            icon_label = QLabel(self._icon)
            icon_label.setStyleSheet("font-size: 14px; background: transparent;")
            layout.addWidget(icon_label)

        # 标题
        self._title_label = QLabel(self._title)
        self._title_label.setStyleSheet(
            f"""
            color: {styles['title_color']};
            font-size: 13px;
            font-weight: 600;
            background: transparent;
        """
        )
        layout.addWidget(self._title_label)

        # 副标题容器
        self._subtitles_container = QWidget()
        self._subtitles_container.setStyleSheet("background: transparent;")
        self._subtitles_layout = QHBoxLayout(self._subtitles_container)
        self._subtitles_layout.setContentsMargins(0, 0, 0, 0)
        self._subtitles_layout.setSpacing(6)
        self._subtitles_container.setVisible(False)  # 默认隐藏
        layout.addWidget(self._subtitles_container)

        # 折叠状态指示器
        self._collapsed_info = QWidget()
        self._collapsed_info.setStyleSheet("background: transparent;")
        collapsed_info_layout = QHBoxLayout(self._collapsed_info)
        collapsed_info_layout.setContentsMargins(0, 0, 0, 0)
        collapsed_info_layout.setSpacing(8)

        # 可以在这里添加折叠时显示的额外信息标签
        self._collapsed_tags_layout = collapsed_info_layout

        layout.addWidget(self._collapsed_info)
        self._collapsed_info.setVisible(not self._expanded)

        layout.addStretch()

        # 展开/折叠提示
        self._hint_label = QLabel("双击展开" if not self._expanded else "双击折叠")
        self._hint_label.setStyleSheet(
            f"""
            color: {styles['hint_color']};
            font-size: 10px;
            background: transparent;
        """
        )
        layout.addWidget(self._hint_label)

        return header

    def _update_toggle_button(self):
        """更新折叠状态提示"""
        if hasattr(self, "_hint_label"):
            self._hint_label.setText("双击折叠" if self._expanded else "双击展开")
        if hasattr(self, "_collapsed_info"):
            self._collapsed_info.setVisible(not self._expanded)

    def toggle(self):
        """切换展开/折叠状态"""
        self._expanded = not self._expanded
        self._content.setVisible(self._expanded)
        self._separator.setVisible(self._expanded)
        self._update_toggle_button()

        # 重置高度限制，让卡片自然伸缩
        self.setMinimumHeight(0)
        self.setMaximumHeight(16777215)

        # 保存状态到配置
        if self._save_state:
            self._save_expanded_state()

        self.expanded_changed.emit(self._expanded)

    def _load_expanded_state(self) -> bool:
        """从配置加载展开状态"""
        try:
            config = self._get_config_manager()
            return config.get_card_state(self._card_id)
        except Exception:
            return None

    def _save_expanded_state(self):
        """保存展开状态到配置"""
        try:
            config = self._get_config_manager()
            config.set_card_state(self._card_id, self._expanded)
            config.save()
        except Exception:
            pass

    def _fix_expanded_height(self):
        """固定展开时的高度 - 已弃用"""
        pass

    def set_expanded(self, expanded: bool):
        """设置展开状态"""
        if self._expanded != expanded:
            self.toggle()

    def is_expanded(self) -> bool:
        """获取展开状态"""
        return self._expanded

    def mouseDoubleClickEvent(self, event: QMouseEvent):
        """双击切换展开/折叠"""
        self.toggle()
        super().mouseDoubleClickEvent(event)

    def enterEvent(self, event):
        """鼠标进入"""
        self._is_hovered = True
        self._apply_style()
        super().enterEvent(event)

    def leaveEvent(self, event):
        """鼠标离开"""
        self._is_hovered = False
        self._apply_style()
        super().leaveEvent(event)

    def set_title(self, title: str):
        """设置标题"""
        self._title = title
        self._title_label.setText(title)

    def add_subtitle(
        self, text: str, icon: str = "", tag_type: str = "info"
    ) -> TagLabel:
        """添加一个卡片样式的副标题.

        Args:
            text (str): 副标题文本.
            icon (str, optional): 图标. Defaults to "".
            tag_type (str, optional): 标签类型. Defaults to "info".

        Returns:
            TagLabel: 创建的标签实例.
        """
        if not hasattr(self, "_subtitles_container"):
            return

        subtitle_tag = TagLabel(
            text=text,
            icon=icon,
            tag_type=tag_type,
            padding="4px 8px",
            border_radius=5,
        )
        self._subtitles_layout.addWidget(subtitle_tag)

        if not self._subtitles_container.isVisible():
            self._subtitles_container.setVisible(True)

        return subtitle_tag

    def clear_subtitles(self):
        """清除所有副标题."""
        if not hasattr(self, "_subtitles_layout"):
            return

        while self._subtitles_layout.count():
            item = self._subtitles_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

        if hasattr(self, "_subtitles_container"):
            self._subtitles_container.setVisible(False)

    def set_icon(self, icon: str):
        """设置图标"""
        self._icon = icon
        # 需要重建头部以更新图标

    def add_collapsed_tag(
        self,
        text: str,
        bg_color: str = None,
        text_color: str = None,
        border_color: str = None,
        icon: str = "",
        tag_type: str = "default",
    ):
        """添加折叠时显示的标签 - 使用 TagLabel 组件

        Args:
            text: 标签文本
            bg_color: 背景颜色（可选）
            text_color: 文字颜色（可选）
            border_color: 边框颜色（可选）
            icon: 图标（可选）
            tag_type: 标签类型 (default/success/warning/error/info/neutral)
        """
        tag = TagLabel(
            text=text,
            icon=icon,
            tag_type=tag_type if not bg_color else "custom",
            bg_color=bg_color,
            text_color=text_color,
            border_color=border_color,
            padding="3px 8px",
            border_radius=4,
            font_size=10,
            font_weight=500,
        )
        self._collapsed_tags_layout.addWidget(tag)
        return tag

    def clear_collapsed_tags(self):
        """清除所有折叠标签"""
        while self._collapsed_tags_layout.count():
            item = self._collapsed_tags_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

    def get_content_layout(self) -> QVBoxLayout:
        """获取内容区域布局，用于添加子组件"""
        return self._content_layout

    def add_content_widget(self, widget: QWidget):
        """添加内容组件"""
        self._content_layout.addWidget(widget)

    def add_shadow(self):
        """添加阴影效果"""
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(12)
        shadow.setXOffset(0)
        shadow.setYOffset(2)
        shadow.setColor(QColor(0, 0, 0, 30))
        self.setGraphicsEffect(shadow)


class CollapsibleSection(CollapsibleCard):
    """可折叠区域 - 用于页面中的各个区块"""

    def __init__(
        self,
        parent=None,
        title: str = "",
        icon: str = "",
        subtitle: str = "",
        collapsed_by_default: bool = False,
    ):
        super().__init__(
            parent=parent,
            title=title,
            icon=icon,
            subtitle=subtitle,
            collapsed_by_default=collapsed_by_default,
            show_toggle_button=True,
        )
        # 继承父类样式


class CompactCollapsibleCard(QFrame):
    """紧凑型可折叠卡片 - 用于列表项"""

    expanded_changed = pyqtSignal(bool)

    def __init__(
        self,
        parent=None,
        title: str = "",
        icon: str = "",
        tags: list = None,
    ):
        super().__init__(parent)
        self._title = title
        self._icon = icon
        self._tags = tags or []
        self._expanded = False
        self._is_hovered = False
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

    def _apply_style(self):
        """应用当前主题样式"""
        styles = _get_styles()
        bg = styles["compact_bg_hover"] if self._is_hovered else styles["compact_bg"]
        border = (
            styles["compact_border_hover"]
            if self._is_hovered
            else styles["compact_border"]
        )

        # 使用动态 ObjectName 确保子类样式正确应用
        object_name = self.objectName() or "CompactCollapsibleCard"
        self.setStyleSheet(
            f"""
            QFrame#{object_name} {{
                background: {bg};
                border: 1px solid {border};
                border-radius: 6px;
            }}
        """
        )

    def _setup_ui(self):
        """设置 UI"""
        styles = _get_styles()
        self.setObjectName("CompactCollapsibleCard")

        self._main_layout = QVBoxLayout(self)
        self._main_layout.setContentsMargins(0, 0, 0, 0)
        self._main_layout.setSpacing(0)

        # 折叠状态头部
        self._header = QWidget()
        self._header.setStyleSheet("background: transparent;")
        header_layout = QHBoxLayout(self._header)
        header_layout.setContentsMargins(12, 8, 12, 8)
        header_layout.setSpacing(8)

        # 图标
        if self._icon:
            icon_label = QLabel(self._icon)
            icon_label.setStyleSheet("font-size: 12px; background: transparent;")
            header_layout.addWidget(icon_label)

        # 标题
        self._title_label = QLabel(self._title)
        self._title_label.setStyleSheet(
            f"""
            color: {styles['title_color']};
            font-size: 12px;
            font-weight: 500;
            background: transparent;
        """
        )
        header_layout.addWidget(self._title_label)

        # 标签
        self._tag_labels = []
        for tag_info in self._tags:
            tag = QLabel(tag_info.get("text", ""))
            bg = tag_info.get("bg", styles["tag_bg"])
            color = tag_info.get("color", styles["tag_color"])
            tag.setStyleSheet(
                f"""
                QLabel {{
                    background-color: {bg};
                    color: {color};
                    padding: 2px 6px;
                    border-radius: 3px;
                    font-size: 9px;
                    font-weight: 500;
                }}
            """
            )
            header_layout.addWidget(tag)
            self._tag_labels.append(tag)

        header_layout.addStretch()
        self._main_layout.addWidget(self._header)

        # 分割线（展开时显示）- 横跨整个卡片宽度，与头部底边一致
        self._separator = GradientSeparator(margin_h=0, margin_v=0, height=1)
        self._main_layout.addWidget(self._separator)
        self._separator.setVisible(False)

        # 展开内容
        self._content = QWidget()
        self._content.setProperty("transparent", True)
        self._content.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self._content.setVisible(False)
        self._content_layout = QVBoxLayout(self._content)
        self._content_layout.setContentsMargins(12, 0, 12, 10)
        self._content_layout.setSpacing(6)
        self._main_layout.addWidget(self._content)

    def enterEvent(self, event):
        """鼠标进入"""
        self._is_hovered = True
        self._apply_style()
        super().enterEvent(event)

    def leaveEvent(self, event):
        """鼠标离开"""
        self._is_hovered = False
        self._apply_style()
        super().leaveEvent(event)

    def toggle(self):
        """切换展开/折叠"""
        self._expanded = not self._expanded
        self._content.setVisible(self._expanded)
        self._separator.setVisible(self._expanded)
        self.expanded_changed.emit(self._expanded)

    def mouseDoubleClickEvent(self, event: QMouseEvent):
        """双击切换"""
        self.toggle()
        super().mouseDoubleClickEvent(event)

    def mousePressEvent(self, event: QMouseEvent):
        """单击也可切换"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.toggle()
        super().mousePressEvent(event)

    def get_content_layout(self) -> QVBoxLayout:
        """获取内容布局"""
        return self._content_layout

    def add_content_widget(self, widget: QWidget):
        """添加内容组件"""
        self._content_layout.addWidget(widget)

    def is_expanded(self) -> bool:
        """获取展开状态"""
        return self._expanded

    def set_expanded(self, expanded: bool):
        """设置展开状态"""
        if self._expanded != expanded:
            self.toggle()
