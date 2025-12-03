# -*- coding:utf-8 -*-
# @Information  :
# @Author       : ZGY
# @Date         : 2025-12-02 17:58:31
# @FilePath     : /f2_gui/f2/gui/components/user_card.py
# @LastEditTime : 2025-12-03 11:15:27

"""
用户卡片组件
~~~~~~~~~~~~

用于显示用户信息的卡片组件，支持主题切换。
"""

import re

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import QCheckBox, QFrame, QHBoxLayout, QLabel, QVBoxLayout, QWidget

from f2.gui.components.tooltip import install_tooltip


def _get_current_theme() -> str:
    """获取当前主题"""
    try:
        from f2.gui.themes.theme_manager import ThemeManager

        return ThemeManager().get_theme()
    except Exception:
        return "dark"


# ===================== 主题样式定义 =====================
# 夜间模式 - 透明背景，蓝紫色边框
DARK_STYLES = {
    "bg": "transparent",
    "bg_hover": "rgba(99, 102, 241, 0.06)",
    "border": "rgba(99, 102, 241, 0.25)",
    "border_hover": "rgba(139, 92, 246, 0.4)",
}

# 日间模式 - 透明背景，绿色边框
LIGHT_STYLES = {
    "bg": "transparent",
    "bg_hover": "rgba(74, 222, 128, 0.08)",
    "border": "rgba(74, 222, 128, 0.3)",
    "border_hover": "rgba(34, 197, 94, 0.45)",
}


def _get_styles() -> dict:
    """根据当前主题获取样式字典"""
    return DARK_STYLES if _get_current_theme() == "dark" else LIGHT_STYLES


class UserCard(QFrame):
    """用户卡片基类 - 支持主题切换和悬停效果"""

    def __init__(
        self,
        parent=None,
        card_id: str = "",
        margins: tuple = (14, 12, 14, 12),
        spacing: int = 0,
        border_radius: int = 10,
    ):
        super().__init__(parent)

        self._card_id = card_id
        self._margins = margins
        self._spacing = spacing
        self._border_radius = border_radius
        self._is_hovered = False

        # 设置 objectName - 清理特殊字符确保 CSS 选择器有效
        if card_id:
            # 只保留字母、数字和下划线
            safe_id = re.sub(r"[^a-zA-Z0-9_]", "_", card_id)
            self.setObjectName(f"UserCard_{safe_id}")
        else:
            self.setObjectName("UserCard")

        # 设置主布局
        self._main_layout = QVBoxLayout(self)
        self._main_layout.setContentsMargins(*margins)
        self._main_layout.setSpacing(spacing)

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

        if self._is_hovered:
            bg = styles["bg_hover"]
            border = styles["border_hover"]
        else:
            bg = styles["bg"]
            border = styles["border"]

        obj_name = self.objectName()
        # 使用精确的 ID 选择器，只影响卡片本身，不影响子组件
        self.setStyleSheet(
            f"""
            QFrame#{obj_name} {{
                background-color: {bg};
                border: 1px solid {border};
                border-radius: {self._border_radius}px;
            }}
        """
        )

    def enterEvent(self, event):
        """鼠标进入时的悬停效果"""
        self._is_hovered = True
        self._apply_style()
        super().enterEvent(event)

    def leaveEvent(self, event):
        """鼠标离开时恢复"""
        self._is_hovered = False
        self._apply_style()
        super().leaveEvent(event)

    def get_layout(self) -> QVBoxLayout:
        """获取主布局"""
        return self._main_layout

    def add_widget(self, widget: QWidget):
        """添加子组件"""
        self._main_layout.addWidget(widget)

    def add_layout(self, layout):
        """添加子布局"""
        self._main_layout.addLayout(layout)

    def add_stretch(self, stretch: int = 1):
        """添加弹性空间"""
        self._main_layout.addStretch(stretch)


class CompactUserCard(UserCard):
    """紧凑型用户卡片 - 更小的内边距和圆角"""

    def __init__(
        self,
        parent=None,
        card_id: str = "",
    ):
        super().__init__(
            parent=parent,
            card_id=card_id,
            margins=(12, 10, 12, 10),
            spacing=0,
            border_radius=8,
        )


class TaskItemCard(QFrame):
    """任务项卡片 - 用于已完成下载列表的紧凑卡片

    支持主题切换和悬停效果，带有复选框、平台/模式徽章、用户信息和状态显示。
    使用 labels.py 中的 PlatformLabel、ModeLabel、TagLabel、StatusLabel 组件。
    """

    # 信号
    delete_clicked = pyqtSignal()
    selection_changed = pyqtSignal(bool)

    def __init__(
        self,
        task_id: str = "",
        platform: str = "douyin",
        mode: str = "",
        nickname: str = "",
        status: str = "completed",
        parent=None,
    ):
        super().__init__(parent)

        self._task_id = task_id
        self._platform = platform  # 平台 ID，如 "douyin", "tiktok"
        self._mode = mode  # 模式 ID，如 "post", "like"
        self._nickname = nickname or "未知用户"
        self._status = status
        self._is_hovered = False
        self._is_selected = False

        # 设置 objectName
        safe_id = re.sub(r"[^a-zA-Z0-9_]", "_", task_id) if task_id else "item"
        self.setObjectName(f"TaskItemCard_{safe_id}")

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
        """设置 UI"""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(14, 12, 14, 12)
        layout.setSpacing(12)

        # 复选框
        self._checkbox = QCheckBox()
        self._checkbox.setProperty("task_id", self._task_id)
        self._checkbox.stateChanged.connect(self._on_checkbox_changed)
        layout.addWidget(self._checkbox)

        # 平台徽章 - 使用 PlatformLabel 组件
        from f2.gui.components.labels import (
            ModeLabel,
            PlatformLabel,
            StatusLabel,
            TagLabel,
        )

        # platform 是平台 ID (如 "douyin")，PlatformLabel 会自动查找对应配置
        self._platform_badge = PlatformLabel(platform=self._platform)
        layout.addWidget(self._platform_badge)

        # 模式徽章 - 使用 ModeLabel 组件
        # mode 是模式 ID (如 "post", "like")，ModeLabel 会自动查找对应配置
        if self._mode:
            self._mode_badge = ModeLabel(mode=self._mode)
            layout.addWidget(self._mode_badge)

        # 用户昵称 - 使用 TagLabel 组件，与 UserHistoryCard 保持一致
        self._nickname_label = TagLabel(
            text=self._nickname,
            tag_type="neutral",
            icon="👤",
            font_weight=600,
            font_size=12,
        )
        layout.addWidget(self._nickname_label)

        layout.addStretch()

        # 状态标签 - 使用 StatusLabel 组件
        self._status_label = StatusLabel(
            status="success" if self._status == "completed" else "error",
            text="成功" if self._status == "completed" else "失败",
        )
        layout.addWidget(self._status_label)

        # 删除按钮
        self._delete_btn = self._create_delete_button()
        layout.addWidget(self._delete_btn)

    def _create_delete_button(self) -> QWidget:
        """创建删除按钮"""
        from f2.gui.components.buttons import DangerButton

        btn = DangerButton("✕", fixed_width=24, fixed_height=24, min_width=24)
        install_tooltip(btn, "删除此任务")
        btn.clicked.connect(self.delete_clicked.emit)
        return btn

    def _on_checkbox_changed(self, state):
        """复选框状态变化"""
        self._is_selected = state == Qt.CheckState.Checked.value
        self.selection_changed.emit(self._is_selected)

    def _apply_style(self):
        """应用当前主题样式 - 与 CompactUserCard 保持一致"""
        styles = _get_styles()

        if self._is_hovered:
            bg = styles["bg_hover"]
            border = styles["border_hover"]
        else:
            bg = styles["bg"]
            border = styles["border"]

        obj_name = self.objectName()
        self.setStyleSheet(
            f"""
            QFrame#{obj_name} {{
                background-color: {bg};
                border: 1px solid {border};
                border-radius: 8px;
            }}
        """
        )

    def enterEvent(self, event):
        """鼠标进入时的悬停效果"""
        self._is_hovered = True
        self._apply_style()
        super().enterEvent(event)

    def leaveEvent(self, event):
        """鼠标离开时恢复"""
        self._is_hovered = False
        self._apply_style()
        super().leaveEvent(event)

    def is_selected(self) -> bool:
        """是否被选中"""
        return self._is_selected

    def set_selected(self, selected: bool):
        """设置选中状态"""
        self._is_selected = selected
        self._checkbox.setChecked(selected)

    def get_task_id(self) -> str:
        """获取任务ID"""
        return self._task_id

    def get_checkbox(self) -> QCheckBox:
        """获取复选框引用"""
        return self._checkbox
