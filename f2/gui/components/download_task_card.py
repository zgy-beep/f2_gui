# -*- coding:utf-8 -*-
"""
下载任务卡片组件
~~~~~~~~~~~~~~

显示下载任务进度和状态的卡片。
Linear 风格设计 - 卡片式布局,精致现代。
"""

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QCheckBox,
    QFrame,
    QHBoxLayout,
    QLabel,
    QProgressBar,
    QVBoxLayout,
)

from f2.gui.components.base_card import BaseCard
from f2.gui.components.buttons import DangerButton, SecondaryButton, SuccessButton
from f2.gui.components.labels import ModeLabel, PlatformLabel, StatusLabel, TagLabel
from f2.gui.components.tooltip import install_tooltip


def _get_current_theme() -> str:
    """获取当前主题"""
    try:
        from f2.gui.themes.theme_manager import ThemeManager

        return ThemeManager().get_theme()
    except Exception:
        return "dark"


# 主题样式配置 - 与 CompactUserCard 保持一致
DARK_THEME_STYLES = {
    # 用户信息区域 - 透明背景，蓝紫色边框
    "info_bg": "transparent",
    "info_bg_hover": "rgba(99, 102, 241, 0.06)",
    "info_border": "rgba(99, 102, 241, 0.25)",
    "info_border_hover": "rgba(139, 92, 246, 0.4)",
}

LIGHT_THEME_STYLES = {
    # 用户信息区域 - 透明背景，绿色边框
    "info_bg": "transparent",
    "info_bg_hover": "rgba(74, 222, 128, 0.08)",
    "info_border": "rgba(74, 222, 128, 0.3)",
    "info_border_hover": "rgba(34, 197, 94, 0.45)",
}


class DownloadTaskCard(BaseCard):
    """下载任务卡片 - 卡片式布局设计"""

    # 信号
    cancel_requested = pyqtSignal()
    cancel_clicked = pyqtSignal()  # 取消按钮点击
    pause_requested = pyqtSignal()
    pause_clicked = pyqtSignal()  # 暂停按钮点击
    resume_requested = pyqtSignal()
    resume_clicked = pyqtSignal()  # 继续按钮点击
    start_clicked = pyqtSignal()  # 开始下载按钮点击
    delete_clicked = pyqtSignal()  # 删除按钮点击
    selection_changed = pyqtSignal(bool)

    def __init__(
        self,
        task_id: str,
        title: str,
        platform: str,
        url: str = "",
        mode: str = "",
        nickname: str = "",
        user_id: str = "",
        total: int = 0,
        parent=None,
    ):
        super().__init__(parent, elevated=True)  # 使用阴影效果
        self.task_id = task_id
        self._title = title
        self._platform = platform
        self._url = url
        self._mode = mode
        self._nickname = nickname
        self._user_id = user_id
        self._total = total
        self._current = 0
        self._status = "pending"
        self._selected = False
        self._setup_content()
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
        self._apply_info_frame_style()

    @property
    def status(self) -> str:
        """获取当前状态"""
        return self._status

    def _setup_content(self):
        """设置内容 - 卡片式布局"""
        # 设置卡片样式 - 圆角背景
        self.setStyleSheet(
            """
            QFrame#Card {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 rgba(99, 102, 241, 0.08),
                    stop:1 rgba(139, 92, 246, 0.08));
                border: 1px solid rgba(99, 102, 241, 0.15);
                border-radius: 10px;
            }
            QFrame#Card:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 rgba(99, 102, 241, 0.12),
                    stop:1 rgba(139, 92, 246, 0.12));
                border-color: rgba(139, 92, 246, 0.25);
            }
        """
        )

        self.layout.setContentsMargins(16, 16, 16, 16)
        self.layout.setSpacing(14)

        # ===== 顶部行: 选择框 + 平台/模式徽章 + 状态 =====
        top_layout = QHBoxLayout()
        top_layout.setSpacing(10)

        # 选择框
        self.select_checkbox = QCheckBox()
        self.select_checkbox.stateChanged.connect(self._on_selection_changed)
        top_layout.addWidget(self.select_checkbox)

        # 平台徽章 - 使用 PlatformLabel 组件
        self.platform_badge = PlatformLabel(platform=self._platform)
        top_layout.addWidget(self.platform_badge)

        # 模式徽章 - 使用 ModeLabel 组件
        if self._mode:
            self.mode_badge = ModeLabel(mode=self._mode)
            top_layout.addWidget(self.mode_badge)

        top_layout.addStretch()

        # 状态标签 - 使用 StatusLabel 组件
        self.status_label = StatusLabel(status="pending", text="等待中")
        top_layout.addWidget(self.status_label)

        self.layout.addLayout(top_layout)

        # ===== 中间: 用户信息卡片区域 =====
        self.info_frame = QFrame()
        self.info_frame.setObjectName("infoFrame")
        self._apply_info_frame_style()

        info_layout = QHBoxLayout(self.info_frame)
        info_layout.setContentsMargins(14, 12, 14, 12)
        info_layout.setSpacing(14)

        # 用户昵称 - 使用 TagLabel 带图标
        self.nickname_value = TagLabel(
            text=self._nickname if self._nickname else "等待获取...",
            tag_type="neutral",
            icon="👤",
            font_weight=600,
            font_size=12,
        )
        info_layout.addWidget(self.nickname_value)

        # 用户ID - 使用 TagLabel 带图标
        user_id_display = (
            self._user_id[:20] + "..." if len(self._user_id) > 20 else self._user_id
        )
        self.userid_value = TagLabel(
            text=user_id_display if self._user_id else "等待获取...",
            tag_type="info",
            icon="🆔",
            font_size=11,
        )
        install_tooltip(self.userid_value, self._user_id if self._user_id else "")
        info_layout.addWidget(self.userid_value)

        info_layout.addStretch()

        self.layout.addWidget(self.info_frame)

        # ===== 底部: 进度条 + 操作按钮 =====
        bottom_layout = QHBoxLayout()
        bottom_layout.setSpacing(12)

        # 进度条容器
        progress_container = QVBoxLayout()
        progress_container.setSpacing(4)

        # 进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(self._total if self._total > 0 else 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setFixedHeight(6)
        self.progress_bar.setStyleSheet(
            """
            QProgressBar {
                background-color: rgba(255, 255, 255, 0.1);
                border: none;
                border-radius: 3px;
            }
            QProgressBar::chunk {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, 
                    stop:0 #6366F1, stop:1 #8B5CF6);
                border-radius: 3px;
            }
        """
        )
        progress_container.addWidget(self.progress_bar)

        # 进度文本
        self.detail_label = QLabel("0%")
        self.detail_label.setStyleSheet("color: #9CA3AF; font-size: 11px;")
        progress_container.addWidget(self.detail_label)

        bottom_layout.addLayout(progress_container, 1)

        # 操作按钮容器
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(6)

        # 开始下载按钮 - 使用 SuccessButton
        self.start_button = SuccessButton(
            "开始", fixed_height=28, min_width=28, icon="▶"
        )
        install_tooltip(self.start_button, "开始下载")
        self.start_button.clicked.connect(self._on_start_clicked)
        btn_layout.addWidget(self.start_button)

        # 暂停按钮 - 使用 SecondaryButton
        self.pause_button = SecondaryButton(
            "暂停", fixed_height=28, fixed_width=28, min_width=28, icon="⏸"
        )
        install_tooltip(self.pause_button, "暂停")
        self.pause_button.clicked.connect(self._on_pause_clicked)
        self.pause_button.hide()
        btn_layout.addWidget(self.pause_button)

        # 取消按钮 - 使用 SecondaryButton
        self.cancel_button = SecondaryButton(
            "取消", fixed_height=28, fixed_width=28, min_width=28, icon="⏹"
        )
        install_tooltip(self.cancel_button, "取消下载")
        self.cancel_button.clicked.connect(self._on_cancel_clicked)
        self.cancel_button.hide()
        btn_layout.addWidget(self.cancel_button)

        # 删除按钮 - 使用 DangerButton
        self.delete_button = DangerButton(
            "删除", fixed_height=28, fixed_width=28, min_width=28, icon="✕"
        )
        install_tooltip(self.delete_button, "从队列中删除")
        self.delete_button.clicked.connect(self._on_delete_clicked)
        btn_layout.addWidget(self.delete_button)

        bottom_layout.addLayout(btn_layout)
        self.layout.addLayout(bottom_layout)

        # 设置卡片 tooltip 显示 URL
        # install_tooltip(self, f"链接: {self._url}")

    def _on_delete_clicked(self):
        """删除按钮点击"""
        self.delete_clicked.emit()

    def _on_cancel_clicked(self):
        """取消按钮点击"""
        self.cancel_requested.emit()
        self.cancel_clicked.emit()

    def _on_start_clicked(self):
        """开始下载按钮点击"""
        self.start_clicked.emit()

    def _on_selection_changed(self, state):
        """选择状态变化"""
        self._selected = state == Qt.CheckState.Checked.value
        self.selection_changed.emit(self._selected)

    def _on_pause_clicked(self):
        """暂停/继续点击"""
        if self._status == "downloading":
            self.pause_requested.emit()
            self.pause_clicked.emit()
        elif self._status == "paused":
            self.resume_requested.emit()
            self.resume_clicked.emit()

    def is_selected(self) -> bool:
        """是否被选中"""
        return self._selected

    def set_selected(self, selected: bool):
        """设置选中状态"""
        self._selected = selected
        self.select_checkbox.setChecked(selected)

    def pause(self):
        """暂停任务"""
        if self._status == "downloading":
            self.pause_requested.emit()

    def set_indeterminate(self, indeterminate: bool = True):
        """设置不确定进度模式（脉冲动画）

        Args:
            indeterminate: True 开启脉冲动画模式，False 恢复正常进度模式
        """
        if indeterminate:
            self.progress_bar.setMaximum(0)  # 设为0会显示脉冲动画
            self.detail_label.setText("处理中...")
        else:
            self.progress_bar.setMaximum(100)
            self._total = 100

    def set_progress(self, progress: int):
        """设置进度百分比

        Args:
            progress: 进度百分比 (0-100)，-1 表示不确定进度模式
        """
        if progress < 0:
            # 不确定进度模式
            self.set_indeterminate(True)
            return

        # 确保退出不确定模式
        if self.progress_bar.maximum() == 0:
            self.progress_bar.setMaximum(100)

        self.progress_bar.setValue(progress)
        self.detail_label.setText(f"{progress}%")

    def update_progress(self, current: int, total: int = None):
        """更新进度"""
        self._current = current
        if total is not None:
            self._total = total
            self.progress_bar.setMaximum(total)
        self.progress_bar.setValue(current)
        if self._total > 0:
            percent = int((current / self._total) * 100)
            self.detail_label.setText(f"{percent}%")

    def set_status(self, status: str):
        """设置状态"""
        self._status = status

        # 状态映射: (图标, 文本)
        status_display_map = {
            "pending": ("⏳", "等待中"),
            "downloading": ("🔄", "下载中"),
            "paused": ("⏸️", "已暂停"),
            "completed": ("✅", "已完成"),
            "failed": ("❌", "失败"),
            "error": ("⚠️", "错误"),
        }

        icon, text = status_display_map.get(status, ("", "未知"))

        # 直接更新 StatusLabel 的文本
        if hasattr(self, "status_label"):
            self.status_label.setText(f"{icon} {text}")

        # 更新按钮显示状态
        if status == "pending":
            # 等待状态：显示开始按钮，隐藏暂停按钮
            self.start_button.show()
            self.start_button.setEnabled(True)
            self.pause_button.hide()
            self.cancel_button.setEnabled(True)
        elif status == "downloading":
            # 下载中：隐藏开始按钮，显示暂停按钮
            self.start_button.hide()
            self.pause_button.show()
            self.pause_button.setText("⏸")
            install_tooltip(self.pause_button, "暂停")
            self.pause_button.setEnabled(True)
            self.cancel_button.setEnabled(True)
        elif status == "paused":
            # 已暂停：显示继续按钮
            self.start_button.hide()
            self.pause_button.show()
            self.pause_button.setText("▶")
            install_tooltip(self.pause_button, "继续")
            self.pause_button.setEnabled(True)
        elif status in ["completed", "failed", "error"]:
            # 完成/失败：禁用所有操作按钮
            self.start_button.hide()
            self.pause_button.hide()
            self.cancel_button.setEnabled(False)
            # 完成时进度设置为100%
            if status == "completed":
                self.progress_bar.setValue(100)
                self.detail_label.setText("100%")

    def set_detail(self, detail: str):
        """设置详细信息"""
        self.detail_label.setText(detail)

    def set_title(self, title: str):
        """设置标题 (兼容旧接口)"""
        self._title = title

    def set_user_info(self, nickname: str, user_id: str):
        """更新用户信息并刷新显示"""
        self._nickname = nickname
        self._user_id = user_id

        # 更新用户昵称显示
        if hasattr(self, "nickname_value"):
            display_text = f"👤 {nickname}" if nickname else "👤 未知用户"
            self.nickname_value.setText(display_text)

        # 更新用户ID显示
        if hasattr(self, "userid_value"):
            user_id_display = user_id[:20] + "..." if len(user_id) > 20 else user_id
            self.userid_value.setText(f"🆔 {user_id_display}" if user_id else "🆔 未知")
            install_tooltip(self.userid_value, user_id if user_id else "")

    def _apply_info_frame_style(self):
        """应用用户信息框样式 - 支持主题切换，与 CompactUserCard 保持一致"""
        styles = (
            DARK_THEME_STYLES if _get_current_theme() == "dark" else LIGHT_THEME_STYLES
        )

        self.info_frame.setStyleSheet(
            f"""
            QFrame#infoFrame {{
                background-color: {styles["info_bg"]};
                border: 1px solid {styles["info_border"]};
                border-radius: 8px;
            }}
            QFrame#infoFrame:hover {{
                background-color: {styles["info_bg_hover"]};
                border-color: {styles["info_border_hover"]};
            }}
        """
        )

    def set_url(self, url: str):
        """更新URL (存储到 tooltip)"""
        self._url = url
        install_tooltip(self, f"链接: {url}")

    def get_title(self) -> str:
        """获取标题"""
        return self._title
