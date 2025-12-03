# -*- coding:utf-8 -*-
# @Information  :
# @Author       : ZGY
# @Date         : 2025-12-01 13:43:21
# @FilePath     : /f2_gui/f2/gui/views/home_page.py
# @LastEditTime : 2025-12-03 10:02:21

"""
首页
~~~

下载管理首页，包含下载任务管理和统计信息。
支持批量添加用户和批量下载功能。
样式由 ThemeManager 统一管理。
"""

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QCheckBox,
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from f2.gui.components.buttons import (
    DangerButton,
    GhostButton,
    PrimaryButton,
    SecondaryButton,
    SuccessButton,
)
from f2.gui.components.collapsible_card import CollapsibleCard
from f2.gui.components.combobox import StyledComboBox
from f2.gui.components.download_task_card import DownloadTaskCard
from f2.gui.components.inputs import BatchTextEdit, UrlLineEdit
from f2.gui.components.separator import GradientSeparator, SimpleSeparator
from f2.gui.components.stats_card import HorizontalStatsCard
from f2.gui.components.tooltip import install_tooltip, show_click_tooltip
from f2.gui.components.user_card import TaskItemCard
from f2.gui.config import MODE_NAMES, PLATFORM_CONFIG


class HomePage(QWidget):
    """首页"""

    # 信号
    add_to_queue = pyqtSignal(str, str, list)  # platform, mode, urls - 添加到队列
    start_all_downloads = pyqtSignal()  # 开始所有下载
    start_download = pyqtSignal(str, str, list)  # platform, mode, urls - 兼容旧接口
    batch_download = pyqtSignal(str, str, list)  # platform, mode, urls - 兼容旧接口

    def __init__(self):
        super().__init__()
        self._setup_ui()

    def _setup_ui(self):
        """设置UI"""
        # 主布局
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # 整个页面使用滚动区域
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.Shape.NoFrame)
        scroll_area.setObjectName("homeScrollArea")

        # 滚动内容容器
        scroll_content = QWidget()
        layout = QVBoxLayout(scroll_content)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)  # 所有内容顶部对齐，不拉伸

        # 顶部区域：统计卡片（水平排列）
        stats_section = self._create_stats_section()
        layout.addWidget(stats_section)

        # 任务创建面板
        task_panel = self._create_task_panel()
        layout.addWidget(task_panel)

        # 任务列表区域（下载队列）
        tasks_section = self._create_tasks_section()
        layout.addWidget(tasks_section)

        # 已完成下载区域（折叠卡片）
        completed_section = self._create_completed_section()
        layout.addWidget(completed_section)

        scroll_area.setWidget(scroll_content)
        main_layout.addWidget(scroll_area)

    def _create_stats_section(self) -> QWidget:
        """创建统计卡片区域 - 使用 HorizontalStatsCard 基类"""
        self.stats_card = HorizontalStatsCard(
            title="任务概览",
            icon="📊",
            subtitle="实时下载任务统计",
            collapsed_by_default=False,
            card_id="home_task_stats",
            stat_item_width=70,  # 固定统计项宽度
            spacing=16,  # 统计项间距
        )

        # 添加统计项
        self.stats_card.add_stat_item("total", "总任务", "0", "📋")
        self.stats_card.add_separator()
        self.stats_card.add_stat_item("downloading", "下载中", "0", "⏬")
        self.stats_card.add_separator()
        self.stats_card.add_stat_item("completed", "已完成", "0", "✅")
        self.stats_card.add_separator()
        self.stats_card.add_stat_item("failed", "失败", "0", "❌")
        self.stats_card.add_stretch()

        return self.stats_card

    def _create_task_panel(self) -> QWidget:
        """创建任务面板 - 使用可折叠卡片"""
        self.task_card = CollapsibleCard(
            title="新建下载任务",
            icon="➕",
            subtitle="",
            collapsed_by_default=False,
            card_id="home_task_panel",
        )
        # 添加折叠时显示的标签
        self.task_card.add_collapsed_tag(text="添加链接开始下载", tag_type="info")

        content_layout = self.task_card.get_content_layout()
        content_layout.setContentsMargins(14, 0, 14, 14)
        content_layout.setSpacing(10)

        # 配置区 - 两列布局
        config_widget = QWidget()
        config_layout = QHBoxLayout(config_widget)
        config_layout.setContentsMargins(0, 0, 0, 0)
        config_layout.setSpacing(12)

        # 左列：平台和模式
        left_col = QVBoxLayout()
        left_col.setSpacing(8)

        # 平台选择
        platform_row = QHBoxLayout()
        platform_row.setSpacing(8)
        platform_label = QLabel("平台")
        platform_label.setObjectName("subtitle")
        platform_label.setFixedWidth(36)
        platform_row.addWidget(platform_label)

        self.platform_combo = StyledComboBox(min_width=130, fixed_height=32)
        for platform_id, platform_info in PLATFORM_CONFIG.items():
            self.platform_combo.addItem(platform_info["name"], platform_id)
        platform_row.addWidget(self.platform_combo)
        platform_row.addStretch()
        left_col.addLayout(platform_row)

        # 模式选择
        mode_row = QHBoxLayout()
        mode_row.setSpacing(8)
        mode_label = QLabel("模式")
        mode_label.setObjectName("subtitle")
        mode_label.setFixedWidth(36)
        mode_row.addWidget(mode_label)

        self.mode_combo = StyledComboBox(min_width=130, fixed_height=32)
        self._update_mode_combo()
        mode_row.addWidget(self.mode_combo)
        mode_row.addStretch()
        left_col.addLayout(mode_row)

        config_layout.addLayout(left_col)

        # 分隔线 - 使用渐变分割线（垂直方向）
        divider = GradientSeparator(
            height=1,
            orientation=Qt.Orientation.Vertical,
            margin_h=0,
            margin_v=8,
        )
        divider.setFixedWidth(16)
        config_layout.addWidget(divider)

        # 右列：链接输入
        right_col = QHBoxLayout()  # 改为水平布局
        right_col.setSpacing(10)

        # 左侧：竖向标签按钮（垂直居中）
        tab_buttons_widget = QWidget()
        tab_buttons_layout = QVBoxLayout(tab_buttons_widget)
        tab_buttons_layout.setContentsMargins(0, 0, 0, 0)
        tab_buttons_layout.setSpacing(6)

        tab_buttons_layout.addStretch()  # 上方弹性空间

        self.single_tab_btn = QPushButton("单个")
        self.single_tab_btn.setObjectName("tabButton")
        self.single_tab_btn.setCheckable(True)
        self.single_tab_btn.setChecked(True)
        self.single_tab_btn.setFixedSize(50, 28)
        self.single_tab_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        install_tooltip(self.single_tab_btn, "单个链接输入模式", "📝")
        self.single_tab_btn.clicked.connect(lambda: self._switch_input_tab(0))
        tab_buttons_layout.addWidget(self.single_tab_btn)

        self.batch_tab_btn = QPushButton("批量")
        self.batch_tab_btn.setObjectName("tabButton")
        self.batch_tab_btn.setCheckable(True)
        self.batch_tab_btn.setFixedSize(50, 28)
        self.batch_tab_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        install_tooltip(self.batch_tab_btn, "批量链接输入，每行一个", "📋")
        self.batch_tab_btn.clicked.connect(lambda: self._switch_input_tab(1))
        tab_buttons_layout.addWidget(self.batch_tab_btn)

        tab_buttons_layout.addStretch()  # 下方弹性空间
        right_col.addWidget(tab_buttons_widget)

        # 右侧：输入区域（堆叠）
        self.input_stack = QStackedWidget()
        self.input_stack.setObjectName("inputStack")
        self.input_stack.setFixedHeight(80)  # 固定输入区域高度

        # 单个链接输入 - 使用 UrlLineEdit 基类
        self.url_input = UrlLineEdit(placeholder="粘贴用户主页链接或作品链接...")
        self.input_stack.addWidget(self.url_input)

        # 批量链接输入 - 使用 BatchTextEdit 基类
        self.batch_input = BatchTextEdit(placeholder="每行一个链接...")
        self.input_stack.addWidget(self.batch_input)

        right_col.addWidget(self.input_stack, 1)
        config_layout.addLayout(right_col, 1)

        config_widget.setFixedHeight(100)  # 固定配置区域高度
        content_layout.addWidget(config_widget)

        # 分隔线 - 使用渐变分割线（水平方向）
        bottom_divider = GradientSeparator(height=1, margin_v=4)
        content_layout.addWidget(bottom_divider)

        # 底部操作栏
        action_widget = QWidget()
        action_widget.setFixedHeight(42)  # 操作栏高度
        action_bar = QHBoxLayout(action_widget)
        action_bar.setContentsMargins(0, 6, 0, 6)
        action_bar.setSpacing(10)

        self.auto_parse_check = QCheckBox("智能解析链接")
        self.auto_parse_check.setChecked(True)
        install_tooltip(
            self.auto_parse_check, "自动识别并提取链接中的用户/作品信息", "🔍"
        )
        action_bar.addWidget(self.auto_parse_check)

        action_bar.addStretch()

        clear_btn = SecondaryButton("清空", fixed_height=28, min_width=60)
        install_tooltip(clear_btn, "清空当前输入的链接", "🗑️")
        clear_btn.clicked.connect(self._clear_inputs)
        action_bar.addWidget(clear_btn)

        self.add_queue_button = PrimaryButton(
            "添加队列", fixed_height=28, min_width=90, icon="➕"
        )
        install_tooltip(self.add_queue_button, "将链接添加到下载队列", "➕")
        self.add_queue_button.clicked.connect(self._on_add_to_queue)
        action_bar.addWidget(self.add_queue_button)

        content_layout.addWidget(action_widget)

        # 连接信号
        self.platform_combo.currentIndexChanged.connect(self._update_mode_combo)

        return self.task_card

    def _create_tasks_section(self) -> QWidget:
        """创建任务列表区域 - 使用可折叠卡片"""
        self.tasks_card = CollapsibleCard(
            title="下载队列",
            icon="📥",
            subtitle="",
            collapsed_by_default=False,
            card_id="home_download_queue",
        )
        # 添加折叠时显示的标签 - 任务计数
        self._queue_count_tag = self.tasks_card.add_collapsed_tag(
            text="0 个任务", tag_type="info"
        )

        content_layout = self.tasks_card.get_content_layout()
        content_layout.setContentsMargins(14, 0, 14, 14)
        content_layout.setSpacing(8)

        # 工具栏
        toolbar = QWidget()
        toolbar.setFixedHeight(42)  # 工具栏高度
        toolbar_layout = QHBoxLayout(toolbar)
        toolbar_layout.setContentsMargins(0, 6, 0, 6)
        toolbar_layout.setSpacing(10)

        # 全选
        self.select_all_check = QCheckBox("全选")
        install_tooltip(self.select_all_check, "选中/取消选中所有任务", "☑️")
        self.select_all_check.stateChanged.connect(self._on_select_all_changed)
        toolbar_layout.addWidget(self.select_all_check)

        # 分隔 - 使用渐变分割线
        sep = GradientSeparator(
            height=1,
            orientation=Qt.Orientation.Vertical,
            margin_h=0,
            margin_v=2,
        )
        sep.setFixedSize(12, 20)
        toolbar_layout.addWidget(sep)

        # 批量操作按钮 - 卡片风格
        batch_pause_btn = SecondaryButton("暂停", fixed_height=28, min_width=60)
        install_tooltip(batch_pause_btn, "暂停选中的下载任务", "⏸️")
        batch_pause_btn.clicked.connect(self._pause_selected)
        toolbar_layout.addWidget(batch_pause_btn)

        batch_delete_btn = DangerButton("删除", fixed_height=28, min_width=60)
        install_tooltip(batch_delete_btn, "删除选中的下载任务", "🗑️")
        batch_delete_btn.clicked.connect(self._delete_selected)
        toolbar_layout.addWidget(batch_delete_btn)

        # 分隔 - 使用渐变分割线
        sep2 = GradientSeparator(
            height=1,
            orientation=Qt.Orientation.Vertical,
            margin_h=0,
            margin_v=2,
        )
        sep2.setFixedSize(12, 20)
        toolbar_layout.addWidget(sep2)

        # 开始下载按钮 - 卡片风格
        self.start_download_btn = SuccessButton(
            "开始下载", fixed_height=28, min_width=100, icon="▶"
        )
        install_tooltip(self.start_download_btn, "开始下载所有队列中的任务", "▶️")
        self.start_download_btn.clicked.connect(self._on_start_all_downloads)
        toolbar_layout.addWidget(self.start_download_btn)

        toolbar_layout.addStretch()
        content_layout.addWidget(toolbar)

        # 滚动区域显示任务列表
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.Shape.NoFrame)
        scroll_area.setObjectName("tasksScrollArea")
        scroll_area.setMinimumHeight(280)  # 设置最小高度让卡片更大

        # 任务容器
        self.tasks_container = QWidget()
        self.tasks_layout = QVBoxLayout(self.tasks_container)
        self.tasks_layout.setContentsMargins(0, 0, 0, 0)
        self.tasks_layout.setSpacing(10)  # 增加间距

        # 空状态提示
        self.empty_hint = QLabel("暂无下载任务，添加链接开始下载")
        self.empty_hint.setObjectName("subtitle")
        self.empty_hint.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.tasks_layout.addWidget(self.empty_hint)

        self.tasks_layout.addStretch()

        scroll_area.setWidget(self.tasks_container)
        content_layout.addWidget(scroll_area)

        return self.tasks_card

    def _create_completed_section(self) -> QWidget:
        """创建已完成下载区域 - 使用可折叠卡片"""
        self.completed_card = CollapsibleCard(
            title="已完成下载",
            icon="✅",
            subtitle="",
            collapsed_by_default=True,
            card_id="home_completed",
        )

        # 添加折叠时显示的标签 - 使用 success 类型
        self._completed_count_tag = self.completed_card.add_collapsed_tag(
            text="0 个任务",
            tag_type="success",
        )

        content_layout = self.completed_card.get_content_layout()
        content_layout.setContentsMargins(14, 0, 14, 14)
        content_layout.setSpacing(8)

        # 工具栏
        toolbar = QWidget()
        toolbar.setFixedHeight(36)  # 固定工具栏高度
        toolbar_layout = QHBoxLayout(toolbar)
        toolbar_layout.setContentsMargins(0, 4, 0, 4)
        toolbar_layout.setSpacing(8)

        toolbar_layout.addStretch()

        # 清空全部按钮
        clear_all_btn = DangerButton(
            "清空全部", fixed_height=28, fixed_width=100, icon="🗑️"
        )
        install_tooltip(clear_all_btn, "清空所有已完成的下载记录", "🗑️")
        clear_all_btn.clicked.connect(self._clear_all_completed)
        toolbar_layout.addWidget(clear_all_btn)

        content_layout.addWidget(toolbar)

        # 已完成任务滚动区域
        completed_scroll = QScrollArea()
        completed_scroll.setWidgetResizable(True)
        completed_scroll.setFrameShape(QFrame.Shape.NoFrame)
        completed_scroll.setObjectName("completedScrollArea")
        completed_scroll.setMinimumHeight(200)  # 设置最小高度

        # 已完成任务容器
        self.completed_container = QWidget()
        self.completed_layout = QVBoxLayout(self.completed_container)
        self.completed_layout.setContentsMargins(0, 0, 0, 0)
        self.completed_layout.setSpacing(8)  # 增加间距

        # 空状态提示
        self.completed_empty_hint = QLabel("暂无已完成的下载任务")
        self.completed_empty_hint.setObjectName("subtitle")
        self.completed_empty_hint.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.completed_layout.addWidget(self.completed_empty_hint)

        self.completed_layout.addStretch()
        completed_scroll.setWidget(self.completed_container)
        content_layout.addWidget(completed_scroll)

        # 存储已完成任务数据
        self._completed_tasks = []

        return self.completed_card

    def _create_compact_completed_item(self, task_data: dict) -> TaskItemCard:
        """创建紧凑的已完成任务项 - 使用 TaskItemCard 组件"""
        platform = task_data.get("platform", "douyin")
        mode = task_data.get("mode", "post")

        item = TaskItemCard(
            task_id=task_data.get("task_id", ""),
            platform=platform,
            mode=mode,
            nickname=task_data.get("nickname", "未知用户"),
            status=task_data.get("status", "completed"),
        )

        # 连接删除信号
        item.delete_clicked.connect(
            lambda: self._remove_completed_item(item, task_data)
        )

        return item

    def _remove_completed_item(self, item: QWidget, task_data: dict):
        """删除单个已完成任务项"""
        if task_data in self._completed_tasks:
            self._completed_tasks.remove(task_data)
        self.completed_layout.removeWidget(item)
        item.deleteLater()
        self._update_completed_count()

    def _on_select_all_completed_changed(self, state):
        """全选已完成任务状态变化"""
        checked = state == Qt.CheckState.Checked.value
        for i in range(self.completed_layout.count()):
            widget = self.completed_layout.itemAt(i).widget()
            if isinstance(widget, TaskItemCard):
                widget.set_selected(checked)

    def _delete_selected_completed(self):
        """删除选中的已完成任务"""
        to_delete = []
        task_ids_to_remove = []

        for i in range(self.completed_layout.count()):
            widget = self.completed_layout.itemAt(i).widget()
            if isinstance(widget, TaskItemCard) and widget.is_selected():
                to_delete.append(widget)
                task_ids_to_remove.append(widget.get_task_id())

        # 从 _completed_tasks 列表中移除对应的任务数据
        self._completed_tasks = [
            task
            for task in self._completed_tasks
            if task.get("task_id") not in task_ids_to_remove
        ]

        for widget in to_delete:
            self.completed_layout.removeWidget(widget)
            widget.deleteLater()

        self._update_completed_count()

    def _clear_all_completed(self):
        """清空所有已完成任务"""
        count = len(self._completed_tasks)
        self._completed_tasks.clear()
        # 清除除了空提示和stretch之外的所有项
        to_delete = []
        for i in range(self.completed_layout.count()):
            item = self.completed_layout.itemAt(i)
            if item and item.widget() and item.widget() != self.completed_empty_hint:
                to_delete.append(item.widget())

        for widget in to_delete:
            self.completed_layout.removeWidget(widget)
            widget.deleteLater()

        if count > 0:
            show_click_tooltip(self, f"已清空 {count} 个已完成任务", "🗑️")

        self._update_completed_count()

    def _update_completed_count(self):
        """更新已完成计数"""
        count = len(self._completed_tasks)
        # 更新折叠时显示的标签
        if hasattr(self, "_completed_count_tag"):
            self._completed_count_tag.setText(f"{count} 个任务")
        # 更新副标题
        if hasattr(self, "completed_card"):
            self.completed_card.set_subtitle(f"已完成 {count} 个下载任务")
        self.completed_empty_hint.setVisible(count == 0)

    def _update_queue_count(self):
        """更新下载队列计数"""
        count = 0
        for i in range(self.tasks_layout.count()):
            widget = self.tasks_layout.itemAt(i).widget()
            if isinstance(widget, DownloadTaskCard):
                count += 1
        # 更新折叠时显示的标签
        if hasattr(self, "_queue_count_tag"):
            self._queue_count_tag.setText(f"{count} 个任务")
        # 更新副标题
        if hasattr(self, "tasks_card"):
            self.tasks_card.set_subtitle(f"队列中 {count} 个任务" if count > 0 else "")

    def move_to_completed(self, task_card: DownloadTaskCard):
        """将任务卡片转换为紧凑的已完成项并添加到已完成区域"""
        # 提取任务信息
        task_data = {
            "task_id": task_card.task_id,
            "platform": task_card._platform,
            "mode": task_card._mode,
            "nickname": task_card._nickname or "未知用户",
            "user_id": task_card._user_id,
            "url": task_card._url,
            "status": task_card._status,
        }

        # 添加到已完成任务列表
        self._completed_tasks.append(task_data)

        # 创建紧凑的已完成项
        compact_item = self._create_compact_completed_item(task_data)

        # 隐藏空状态提示
        self.completed_empty_hint.hide()

        # 在 stretch 之前插入
        self.completed_layout.insertWidget(
            self.completed_layout.count() - 1, compact_item
        )

        # 从下载队列中移除原卡片
        if task_card.parent():
            parent_layout = task_card.parent().layout()
            if parent_layout:
                parent_layout.removeWidget(task_card)
        task_card.deleteLater()

        # 更新计数
        self._update_completed_count()

        # 检查下载队列是否为空
        self._check_queue_empty()

    def _update_mode_combo(self):
        """更新模式下拉框"""
        platform_id = self.platform_combo.currentData()
        if platform_id and platform_id in PLATFORM_CONFIG:
            modes = PLATFORM_CONFIG[platform_id]["modes"]
            self.mode_combo.clear()
            for mode in modes:
                # 使用中文名称显示，但存储英文值
                display_name = MODE_NAMES.get(mode, mode)
                self.mode_combo.addItem(display_name, mode)

    def _switch_input_tab(self, index: int):
        """切换输入标签页"""
        self.input_stack.setCurrentIndex(index)
        self.single_tab_btn.setChecked(index == 0)
        self.batch_tab_btn.setChecked(index == 1)

    def _clear_inputs(self):
        """清空输入"""
        self.url_input.clear()
        self.batch_input.clear()
        show_click_tooltip(self, "已清空", "🗑️")

    def _on_add_to_queue(self):
        """添加到队列（不立即下载）"""
        platform_id = self.platform_combo.currentData()
        mode = self.mode_combo.currentData()  # 获取英文模式值

        # 根据当前输入页获取URL
        current_tab = self.input_stack.currentIndex()

        if current_tab == 0:
            # 单个链接
            url = self.url_input.text().strip()
            if url:
                self.add_to_queue.emit(platform_id, mode, [url])
                # 隐藏空状态提示
                self.empty_hint.hide()
                # 清空输入
                self.url_input.clear()
                show_click_tooltip(self, "已添加到队列", "✅")
        else:
            # 批量链接
            text = self.batch_input.toPlainText().strip()
            if text:
                urls = [line.strip() for line in text.split("\n") if line.strip()]
                if urls:
                    self.add_to_queue.emit(platform_id, mode, urls)
                    self.empty_hint.hide()
                    # 清空输入
                    self.batch_input.clear()
                    show_click_tooltip(self, f"已添加 {len(urls)} 个链接", "✅")

    def _on_start_all_downloads(self):
        """开始下载队列中所有待下载的任务"""
        self.start_all_downloads.emit()

    def _on_select_all_changed(self, state):
        """全选状态变化"""
        checked = state == Qt.CheckState.Checked.value
        for i in range(self.tasks_layout.count() - 1):  # -1 排除stretch
            widget = self.tasks_layout.itemAt(i).widget()
            if isinstance(widget, DownloadTaskCard):
                widget.set_selected(checked)

    def _pause_selected(self):
        """暂停选中任务"""
        count = 0
        for i in range(self.tasks_layout.count() - 1):
            widget = self.tasks_layout.itemAt(i).widget()
            if isinstance(widget, DownloadTaskCard) and widget.is_selected():
                widget.pause()
                count += 1
        if count > 0:
            show_click_tooltip(self, f"已暂停 {count} 个任务", "⏸️")

    def _delete_selected(self):
        """删除选中任务"""
        to_delete = []
        for i in range(self.tasks_layout.count() - 1):
            widget = self.tasks_layout.itemAt(i).widget()
            if isinstance(widget, DownloadTaskCard) and widget.is_selected():
                to_delete.append(widget)

        for widget in to_delete:
            self.tasks_layout.removeWidget(widget)
            widget.deleteLater()

        if to_delete:
            show_click_tooltip(self, f"已删除 {len(to_delete)} 个任务", "🗑️")

        self._check_queue_empty()
        self._update_queue_count()

    def add_task_card(self, task_card: DownloadTaskCard):
        """添加任务卡片"""
        # 隐藏空状态提示
        self.empty_hint.hide()
        # 在stretch之前插入
        self.tasks_layout.insertWidget(self.tasks_layout.count() - 1, task_card)

        # 连接删除信号
        task_card.delete_clicked.connect(lambda: self._remove_task_card(task_card))

        # 更新队列计数
        self._update_queue_count()

    def _remove_task_card(self, task_card: DownloadTaskCard):
        """从队列中删除任务卡片"""
        self.tasks_layout.removeWidget(task_card)
        task_card.deleteLater()
        self._check_queue_empty()
        self._update_queue_count()

    def _check_queue_empty(self):
        """检查下载队列是否为空"""
        has_tasks = False
        for i in range(self.tasks_layout.count()):
            widget = self.tasks_layout.itemAt(i).widget()
            if isinstance(widget, DownloadTaskCard):
                has_tasks = True
                break

        if not has_tasks:
            self.empty_hint.show()

    def update_stats(self, total: int, downloading: int, completed: int, failed: int):
        """更新统计数据"""
        self.stats_card.set_stat_value("total", str(total))
        self.stats_card.set_stat_value("downloading", str(downloading))
        self.stats_card.set_stat_value("completed", str(completed))
        self.stats_card.set_stat_value("failed", str(failed))
