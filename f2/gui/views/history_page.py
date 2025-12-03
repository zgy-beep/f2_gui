"""
历史记录页面
~~~~~~~~~~~~

显示下载历史记录,支持搜索和管理。
Linear 风格设计 - 用户聚合显示,精致现代。
"""

from collections import defaultdict
from datetime import datetime

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QApplication,
    QCheckBox,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from f2.gui.components.buttons import DangerButton, PrimaryButton, SecondaryButton
from f2.gui.components.collapsible_card import CollapsibleCard
from f2.gui.components.combobox import PlatformComboBox, SortComboBox
from f2.gui.components.labels import CountBadge, ModeLabel, PlatformLabel, TagLabel
from f2.gui.components.separator import GradientSeparator
from f2.gui.components.stats_card import HorizontalStatsCard
from f2.gui.components.tooltip import install_tooltip, show_click_tooltip
from f2.gui.components.user_card import CompactUserCard
from f2.gui.config import MODE_NAMES, PLATFORM_CONFIG
from f2.gui.utils.history_manager import history_manager


class UserHistoryCard(CompactUserCard):
    """用户历史记录卡片 - 聚合同一用户的所有下载记录，支持折叠/展开"""

    # 信号
    add_to_queue_clicked = pyqtSignal(dict)  # 添加到下载队列
    delete_clicked = pyqtSignal(str)  # 删除记录 (user_key)
    selected_changed = pyqtSignal(str, bool)  # 选中状态变化

    def __init__(self, user_key: str, user_data: dict, parent=None):
        """
        Args:
            user_key: 用户唯一标识 (platform_user_id 或 platform_nickname)
            user_data: 聚合后的用户数据
        """
        super().__init__(parent=parent, card_id=f"history_{user_key[:20]}")
        self.user_key = user_key
        self.user_data = user_data
        self._selected = False
        self._expanded = False  # 默认折叠状态
        self._setup_ui()

    def _setup_ui(self):
        """设置 UI - 使用 CompactUserCard 基类样式"""
        # 获取基类的主布局
        main_layout = self.get_layout()
        main_layout.setContentsMargins(14, 12, 14, 12)
        main_layout.setSpacing(0)

        # ===== 折叠状态头部（始终可见）=====
        self.header_widget = QWidget()
        header_layout = QHBoxLayout(self.header_widget)
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(10)

        # 复选框
        self.checkbox = QCheckBox()
        self.checkbox.stateChanged.connect(self._on_checkbox_changed)
        header_layout.addWidget(self.checkbox)

        # === 信息标签区域 ===
        tags_layout = QHBoxLayout()
        tags_layout.setSpacing(8)

        # 1. 平台标签卡片 - 使用 PlatformLabel 基类
        platform = self.user_data.get("platform", "douyin")
        platform_tag = PlatformLabel(platform=platform, parent=self)
        tags_layout.addWidget(platform_tag)

        # 2. 模式标签卡片 - 使用 ModeLabel 基类
        modes = self.user_data.get("modes", [])
        last_mode = self.user_data.get("last_mode", "post")
        mode_tag = ModeLabel(mode=last_mode, parent=self)
        tags_layout.addWidget(mode_tag)

        # 3. 用户昵称标签卡片 - 使用 TagLabel 基类
        nickname = self.user_data.get("nickname", "未知用户")
        nickname_tag = TagLabel(
            text=nickname,
            parent=self,
            tag_type="neutral",
            icon="👤",
            font_weight=600,
        )
        tags_layout.addWidget(nickname_tag)

        header_layout.addLayout(tags_layout)
        header_layout.addStretch()

        # === 右侧统计和操作区域 ===
        stats_layout = QHBoxLayout()
        stats_layout.setSpacing(8)

        # 下载次数徽章 - 使用 CountBadge 基类
        download_count = self.user_data.get("download_count", 0)
        count_badge = CountBadge(
            count=download_count,
            suffix="次",
            parent=self,
            tag_type="info",
            icon="📥",
        )
        stats_layout.addWidget(count_badge)

        # 成功状态徽章 - 使用 CountBadge 基类
        success_count = self.user_data.get("success_count", 0)
        if success_count > 0:
            success_badge = CountBadge(
                count=success_count,
                parent=self,
                tag_type="success",
                icon="✅",
            )
            stats_layout.addWidget(success_badge)

        # 失败状态徽章 - 使用 CountBadge 基类
        fail_count = self.user_data.get("fail_count", 0)
        if fail_count > 0:
            fail_badge = CountBadge(
                count=fail_count,
                parent=self,
                tag_type="error",
                icon="❌",
            )
            stats_layout.addWidget(fail_badge)

        header_layout.addLayout(stats_layout)

        # 添加到队列按钮（折叠状态可见）- 蓝紫渐变
        add_btn_compact = PrimaryButton("添加", fixed_width=50, fixed_height=26)
        install_tooltip(add_btn_compact, "添加到下载队列")
        add_btn_compact.clicked.connect(self._on_add_to_queue)
        header_layout.addWidget(add_btn_compact)

        # 删除按钮（折叠状态可见）- 橙红渐变
        delete_btn_compact = DangerButton("删除", fixed_width=50, fixed_height=26)
        install_tooltip(delete_btn_compact, "删除此下载记录")
        delete_btn_compact.clicked.connect(
            lambda: self.delete_clicked.emit(self.user_key)
        )
        header_layout.addWidget(delete_btn_compact)

        main_layout.addWidget(self.header_widget)

        # ===== 展开状态详情（可折叠）=====
        self.detail_widget = QWidget()
        detail_layout = QVBoxLayout(self.detail_widget)
        detail_layout.setContentsMargins(0, 12, 0, 0)
        detail_layout.setSpacing(12)

        # 分隔线 - 使用渐变分割线基类
        separator = GradientSeparator(height=1, margin_v=4)
        detail_layout.addWidget(separator)

        # 详细信息网格
        info_frame = QFrame()
        info_frame.setObjectName("historyInfoFrame")
        info_frame.setStyleSheet(
            """
            QFrame#historyInfoFrame {
                background: transparent;
                border: none;
            }
            QFrame#historyInfoFrame QLabel {
                background: transparent;
            }
        """
        )

        info_grid = QGridLayout(info_frame)
        info_grid.setContentsMargins(0, 8, 0, 8)
        info_grid.setSpacing(10)
        info_grid.setColumnStretch(1, 1)
        info_grid.setColumnStretch(3, 1)

        # 用户ID - 可点击复制
        user_id = self.user_data.get("user_id", "")
        user_id_display = user_id[:20] + "..." if len(user_id) > 20 else user_id or "-"
        if user_id:
            self._add_clickable_info_item(
                info_grid, 0, 0, "用户ID", user_id_display, copy_text=user_id
            )
        else:
            self._add_info_item(info_grid, 0, 0, "用户ID", "-")

        # 最近下载时间
        last_time = self.user_data.get("last_download_time", "")
        self._add_info_item(info_grid, 0, 2, "最近下载", self._format_time(last_time))

        # 下载模式（显示所有模式）
        mode_names_list = [MODE_NAMES.get(m, m) for m in modes[:3]]
        modes_text = " / ".join(mode_names_list) if mode_names_list else "-"
        self._add_info_item(info_grid, 1, 0, "下载模式", modes_text)

        # 首次下载时间
        first_time = self.user_data.get("first_download_time", "")
        self._add_info_item(info_grid, 1, 2, "首次下载", self._format_time(first_time))

        # URL (提取解析后的链接) - 可点击复制
        url = self.user_data.get("url", "")
        # 从分享文本中提取实际 URL
        self._parsed_url = self._extract_url(url)
        url_display = (
            self._parsed_url[:45] + "..."
            if len(self._parsed_url) > 45
            else self._parsed_url
        )
        self._add_clickable_info_item(
            info_grid,
            2,
            0,
            "链接",
            url_display or "-",
            copy_text=self._parsed_url,
            span=3,
        )

        detail_layout.addWidget(info_frame)

        # 底部操作按钮
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)
        btn_layout.addStretch()

        # 添加到队列按钮（展开状态）- 蓝紫渐变
        add_btn = PrimaryButton("+ 添加到队列", fixed_width=110, fixed_height=30)
        add_btn.clicked.connect(self._on_add_to_queue)
        btn_layout.addWidget(add_btn)

        # 删除按钮 - 橙红渐变
        delete_btn = DangerButton("删除记录", fixed_width=100, fixed_height=30)
        delete_btn.clicked.connect(lambda: self.delete_clicked.emit(self.user_key))
        btn_layout.addWidget(delete_btn)

        detail_layout.addLayout(btn_layout)

        main_layout.addWidget(self.detail_widget)

        # 默认折叠
        self.detail_widget.setVisible(False)

    def _toggle_expand(self):
        """切换展开/折叠状态"""
        self._expanded = not self._expanded
        self.detail_widget.setVisible(self._expanded)

    def mouseDoubleClickEvent(self, event):
        """双击展开/折叠 - 阻止事件冒泡到父级"""
        self._toggle_expand()
        event.accept()  # 接受事件，阻止冒泡
        # 不调用 super()，完全阻止事件传递

    def set_expanded(self, expanded: bool):
        """设置展开状态"""
        if self._expanded != expanded:
            self._toggle_expand()

    def _add_info_item(
        self,
        grid: QGridLayout,
        row: int,
        col: int,
        label: str,
        value: str,
        tooltip: str = "",
        span: int = 1,
    ):
        """添加信息项"""
        label_widget = QLabel(label)
        label_widget.setStyleSheet(
            "color: #6B7280; font-size: 11px; background: transparent;"
        )
        grid.addWidget(label_widget, row, col)

        value_widget = QLabel(value)
        value_widget.setStyleSheet(
            "color: #D1D5DB; font-size: 12px; background: transparent;"
        )
        if tooltip:
            install_tooltip(value_widget, tooltip)
            value_widget.setCursor(Qt.CursorShape.WhatsThisCursor)

        if span > 1:
            grid.addWidget(value_widget, row, col + 1, 1, span)
        else:
            grid.addWidget(value_widget, row, col + 1)

    def _add_clickable_info_item(
        self,
        grid: QGridLayout,
        row: int,
        col: int,
        label: str,
        value: str,
        copy_text: str = "",
        span: int = 1,
    ):
        """添加可点击复制的信息项"""
        label_widget = QLabel(label)
        label_widget.setStyleSheet(
            "color: #6B7280; font-size: 11px; background: transparent;"
        )
        grid.addWidget(label_widget, row, col)

        # 可点击的链接标签
        value_widget = QPushButton(value)
        value_widget.setFlat(True)
        value_widget.setCursor(Qt.CursorShape.PointingHandCursor)
        install_tooltip(value_widget, "点击复制: " + copy_text if copy_text else value)
        value_widget.setStyleSheet(
            """
            QPushButton {
                color: #818CF8;
                font-size: 12px;
                background: transparent;
                border: none;
                text-align: left;
                padding: 0;
            }
            QPushButton:hover {
                color: #A5B4FC;
                text-decoration: underline;
            }
        """
        )
        value_widget.clicked.connect(
            lambda: self._copy_to_clipboard(copy_text or value)
        )

        if span > 1:
            grid.addWidget(value_widget, row, col + 1, 1, span)
        else:
            grid.addWidget(value_widget, row, col + 1)

    def _copy_to_clipboard(self, text: str):
        """复制文本到剪贴板"""
        clipboard = QApplication.clipboard()
        clipboard.setText(text)
        # 显示复制成功提示（在鼠标位置）
        show_click_tooltip(self, "已复制", "✅")

    def _extract_url(self, text: str) -> str:
        """从分享文本中提取实际URL"""
        import re

        if not text:
            return ""
        # 如果已经是纯URL，直接返回
        if text.startswith("http://") or text.startswith("https://"):
            # 检查是否是纯URL（不含空格）
            if " " not in text:
                return text
        # 从分享文本中提取URL
        url_pattern = r'https?://[^\s<>"{}|\\^`\[\]]+'
        matches = re.findall(url_pattern, text)
        if matches:
            return matches[0]
        return text

    def _format_time(self, time_str: str) -> str:
        """格式化时间显示"""
        if not time_str:
            return "-"
        try:
            dt = datetime.strptime(time_str, "%Y-%m-%d %H:%M:%S")
            now = datetime.now()
            diff = now - dt

            if diff.days == 0:
                if diff.seconds < 60:
                    return "刚刚"
                elif diff.seconds < 3600:
                    return f"{diff.seconds // 60} 分钟前"
                else:
                    return f"{diff.seconds // 3600} 小时前"
            elif diff.days == 1:
                return "昨天"
            elif diff.days < 7:
                return f"{diff.days} 天前"
            else:
                return dt.strftime("%m-%d %H:%M")
        except:
            return time_str

    def _on_checkbox_changed(self, state):
        """复选框状态变化"""
        self._selected = state == Qt.CheckState.Checked.value
        self.selected_changed.emit(self.user_key, self._selected)

    def _on_add_to_queue(self):
        """添加到队列"""
        record = {
            "platform": self.user_data.get("platform", "douyin"),
            "mode": self.user_data.get("last_mode", "post"),
            "url": self.user_data.get("url", ""),
            "nickname": self.user_data.get("nickname", ""),
        }
        self.add_to_queue_clicked.emit(record)

    def is_selected(self) -> bool:
        """是否选中"""
        return self._selected

    def set_selected(self, selected: bool):
        """设置选中状态"""
        self.checkbox.setChecked(selected)

    def get_record_ids(self) -> list:
        """获取所有关联的记录ID"""
        return self.user_data.get("record_ids", [])


class HistoryPage(QWidget):
    """历史记录页面 - 用户聚合显示"""

    # 信号
    redownload_requested = pyqtSignal(dict)  # 重新下载请求
    add_to_download_queue = pyqtSignal(str, str, str)  # platform, mode, url

    def __init__(self):
        super().__init__()
        self._user_cards = {}  # user_key -> UserHistoryCard
        self._all_expanded = False  # 跟踪展开/折叠状态
        self._create_ui()
        self._load_history()

    def _create_ui(self):
        """创建 UI"""
        # 主布局
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # 整个页面使用滚动区域
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.Shape.NoFrame)
        scroll_area.setObjectName("historyScrollArea")

        # 滚动内容容器
        scroll_content = QWidget()
        layout = QVBoxLayout(scroll_content)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        # 统计卡片
        stats_card = self._create_stats_card()
        layout.addWidget(stats_card)

        # 工具栏
        toolbar = self._create_toolbar()
        layout.addWidget(toolbar)

        # 历史记录列表
        records_section = self._create_records_section()
        layout.addWidget(records_section)

        # 添加弹簧，确保折叠时卡片不会占据全部空间
        layout.addStretch()

        scroll_area.setWidget(scroll_content)
        main_layout.addWidget(scroll_area)

    def _create_stats_card(self) -> QWidget:
        """创建统计卡片 - 使用 HorizontalStatsCard 基类"""
        self.stats_card = HorizontalStatsCard(
            parent=self,
            title="历史概览",
            icon="📜",
            subtitle="下载历史记录统计",
            collapsed_by_default=False,
            card_id="history_stats",
            stat_item_width=70,  # 固定统计项宽度
            spacing=16,  # 统计项间距
        )

        # 添加统计项
        self.stats_card.add_stat_item("users", "用户数", "0", "👤")
        self.stats_card.add_separator()
        self.stats_card.add_stat_item("downloads", "总下载", "0", "📥")
        self.stats_card.add_separator()
        self.stats_card.add_stat_item("success", "成功", "0", "✅")
        self.stats_card.add_separator()
        self.stats_card.add_stat_item("failed", "失败", "0", "❌")
        self.stats_card.add_stretch()

        return self.stats_card

    def _create_toolbar(self) -> QWidget:
        """创建工具栏 - 使用 CollapsibleCard"""
        self.toolbar_card = CollapsibleCard(
            parent=self,
            title="筛选工具",
            icon="🔧",
            subtitle="",
            collapsed_by_default=True,
            card_id="history_toolbar",
        )
        # 添加折叠时显示的标签
        self.toolbar_card.add_collapsed_tag(
            text="搜索和筛选历史记录", tag_type="neutral"
        )

        # 获取内容布局
        content_layout = self.toolbar_card.get_content_layout()

        # 工具栏内容
        toolbar_widget = QWidget()
        toolbar_widget.setStyleSheet("background: transparent;")
        layout = QHBoxLayout(toolbar_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)

        # 搜索框
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 搜索用户昵称或链接...")
        self.search_input.setFixedWidth(220)
        self.search_input.setFixedHeight(32)
        install_tooltip(self.search_input, "输入关键词搜索历史记录")
        self.search_input.textChanged.connect(self._on_search_changed)
        layout.addWidget(self.search_input)

        # 平台筛选 - 使用 PlatformComboBox 基类
        self.platform_filter = PlatformComboBox(parent=self, include_all=True)
        install_tooltip(self.platform_filter, "按平台筛选历史记录")
        self.platform_filter.currentIndexChanged.connect(self._on_filter_changed)
        layout.addWidget(self.platform_filter)

        # 排序方式 - 使用 SortComboBox 基类
        self.sort_filter = SortComboBox(parent=self)
        install_tooltip(self.sort_filter, "选择排序方式")
        # 添加额外的排序选项
        self.sort_filter.clear()
        self.sort_filter.addItem("🕐 最近下载", "last_time")
        self.sort_filter.addItem("📊 下载次数", "download_count")
        self.sort_filter.addItem("🔤 用户名称", "nickname")
        self.sort_filter.currentIndexChanged.connect(self._on_filter_changed)
        layout.addWidget(self.sort_filter)

        layout.addStretch()

        # 刷新按钮
        refresh_btn = SecondaryButton("刷新", fixed_height=32, min_width=70, icon="🔄")
        install_tooltip(refresh_btn, "重新加载历史记录")
        refresh_btn.clicked.connect(self._on_refresh_clicked)
        layout.addWidget(refresh_btn)

        # 清空按钮
        clear_btn = DangerButton("清空全部", fixed_height=32, min_width=90, icon="🗑️")
        install_tooltip(clear_btn, "清空所有下载历史记录")
        clear_btn.clicked.connect(self._clear_history)
        layout.addWidget(clear_btn)

        content_layout.addWidget(toolbar_widget)

        return self.toolbar_card

    def _create_records_section(self) -> QWidget:
        """创建记录列表区域 - 使用 CollapsibleCard"""
        self.records_card = CollapsibleCard(
            parent=self,
            title="下载历史",
            icon="📜",
            subtitle="",
            collapsed_by_default=False,
            card_id="history_records",
        )
        # 添加折叠时显示的标签 - 记录计数
        self._records_count_tag = self.records_card.add_collapsed_tag(
            text="0 条记录", tag_type="info"
        )

        # 获取内容布局
        content_layout = self.records_card.get_content_layout()

        # 工具栏
        toolbar_widget = QWidget()
        toolbar_widget.setStyleSheet("background: transparent;")
        header_layout = QHBoxLayout(toolbar_widget)
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(10)

        # 全选
        self.select_all_check = QCheckBox("全选")
        self.select_all_check.setStyleSheet(
            "color: #9CA3AF; font-size: 12px; background: transparent;"
        )
        install_tooltip(self.select_all_check, "选中/取消选中所有记录")
        self.select_all_check.stateChanged.connect(self._on_select_all_changed)
        header_layout.addWidget(self.select_all_check)

        header_layout.addStretch()

        # 展开/折叠全部
        self.expand_all_btn = SecondaryButton("展开全部", fixed_height=26, min_width=70)
        install_tooltip(self.expand_all_btn, "展开或折叠所有卡片的详细信息")
        self.expand_all_btn.clicked.connect(self._toggle_expand_all)
        header_layout.addWidget(self.expand_all_btn)

        # 批量操作
        batch_add_btn = PrimaryButton("批量添加", fixed_height=26, min_width=70)
        install_tooltip(batch_add_btn, "将选中的记录添加到下载队列")
        batch_add_btn.clicked.connect(self._batch_add_to_queue)
        header_layout.addWidget(batch_add_btn)

        batch_delete_btn = DangerButton("批量删除", fixed_height=26, min_width=70)
        install_tooltip(batch_delete_btn, "删除选中的历史记录")
        batch_delete_btn.clicked.connect(self._batch_delete)
        header_layout.addWidget(batch_delete_btn)

        content_layout.addWidget(toolbar_widget)

        # 记录容器
        self.records_container = QWidget()
        self.records_container.setStyleSheet("background: transparent;")
        self.records_layout = QVBoxLayout(self.records_container)
        self.records_layout.setContentsMargins(0, 0, 0, 0)
        self.records_layout.setSpacing(10)

        # 空状态提示
        self.empty_hint = QLabel("📭 暂无历史记录\n\n下载内容后会在这里显示")
        self.empty_hint.setObjectName("subtitle")
        self.empty_hint.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.empty_hint.setStyleSheet(
            "color: #6B7280; font-size: 13px; padding: 40px; background: transparent;"
        )
        self.records_layout.addWidget(self.empty_hint)

        self.records_layout.addStretch()

        content_layout.addWidget(self.records_container)

        return self.records_card

    def _aggregate_records(self, records: list) -> dict:
        """
        聚合用户记录

        Returns:
            dict: {user_key: user_data}
        """
        user_map = defaultdict(
            lambda: {
                "nickname": "",
                "user_id": "",
                "platform": "",
                "url": "",
                "download_count": 0,
                "success_count": 0,
                "fail_count": 0,
                "modes": set(),
                "last_mode": "",
                "first_download_time": "",
                "last_download_time": "",
                "record_ids": [],
            }
        )

        for record in records:
            # 生成用户唯一标识
            platform = record.get("platform", "douyin")
            nickname = record.get("nickname", "")
            url = record.get("url", "")
            user_id = record.get("user_id", "")

            # 优先使用 user_id，其次 nickname，最后使用 url
            if user_id:
                user_key = f"{platform}_{user_id}"
            elif nickname:
                user_key = f"{platform}_{nickname}"
            else:
                user_key = f"{platform}_{url}"

            user = user_map[user_key]

            # 更新用户信息
            if not user["nickname"] or nickname:
                user["nickname"] = nickname or "未知用户"
            if not user["platform"]:
                user["platform"] = platform
            if not user["url"] or nickname:  # 有昵称时优先保存该URL
                user["url"] = url
            # 保存用户ID
            if user_id:
                user["user_id"] = user_id

            # 统计 - 使用记录中的 download_count 字段
            record_download_count = record.get("download_count", 1)
            user["download_count"] += record_download_count
            user["record_ids"].append(record.get("id", ""))

            status = record.get("status", "")
            if status == "成功":
                user["success_count"] += 1
            elif status == "失败":
                user["fail_count"] += 1

            # 模式
            mode = record.get("mode", "")
            if mode:
                user["modes"].add(mode)
                user["last_mode"] = mode

            # 时间
            time_str = record.get("time", "")
            if time_str:
                if (
                    not user["first_download_time"]
                    or time_str < user["first_download_time"]
                ):
                    user["first_download_time"] = time_str
                if (
                    not user["last_download_time"]
                    or time_str > user["last_download_time"]
                ):
                    user["last_download_time"] = time_str

        # 转换 modes 为 list
        for user in user_map.values():
            user["modes"] = list(user["modes"])

        return dict(user_map)

    def _load_history(self):
        """加载历史记录"""
        records = history_manager.get_all_records()
        self._display_records(records)

    def _on_refresh_clicked(self):
        """刷新按钮点击"""
        self._load_history()
        show_click_tooltip(self, "已刷新", "🔄")

    def _display_records(self, records: list):
        """显示记录"""
        # 清除现有卡片
        for card in self._user_cards.values():
            card.deleteLater()
        self._user_cards.clear()

        # 移除所有子项
        while self.records_layout.count() > 0:
            item = self.records_layout.takeAt(0)
            widget = item.widget()
            if widget and widget != self.empty_hint:
                widget.deleteLater()

        # 聚合记录
        user_map = self._aggregate_records(records)

        # 更新统计
        self._update_stats(records, user_map)

        if not user_map:
            self.empty_hint.show()
            self.records_layout.addWidget(self.empty_hint)
            self.records_layout.addStretch()
            return

        self.empty_hint.hide()

        # 排序
        sort_key = self.sort_filter.currentData()
        if sort_key == "last_time":
            sorted_users = sorted(
                user_map.items(), key=lambda x: x[1]["last_download_time"], reverse=True
            )
        elif sort_key == "download_count":
            sorted_users = sorted(
                user_map.items(), key=lambda x: x[1]["download_count"], reverse=True
            )
        elif sort_key == "nickname":
            sorted_users = sorted(user_map.items(), key=lambda x: x[1]["nickname"])
        else:
            sorted_users = list(user_map.items())

        # 创建卡片
        for user_key, user_data in sorted_users:
            card = UserHistoryCard(user_key, user_data)
            card.add_to_queue_clicked.connect(self._add_to_queue)
            card.delete_clicked.connect(self._delete_user_records)
            card.selected_changed.connect(self._on_card_selected_changed)

            self.records_layout.addWidget(card)
            self._user_cards[user_key] = card

        self.records_layout.addStretch()

    def _update_stats(self, records: list, user_map: dict):
        """更新统计信息"""
        total_users = len(user_map)
        total_downloads = len(records)
        success_count = sum(1 for r in records if r.get("status") == "成功")
        fail_count = sum(1 for r in records if r.get("status") == "失败")

        self.stats_card.set_stat_value("users", str(total_users))
        self.stats_card.set_stat_value("downloads", str(total_downloads))
        self.stats_card.set_stat_value("success", str(success_count))
        self.stats_card.set_stat_value("failed", str(fail_count))

    def _on_search_changed(self, text: str):
        """搜索变化"""
        self._apply_filters()

    def _on_filter_changed(self, *args):
        """筛选变化"""
        self._apply_filters()

    def _apply_filters(self):
        """应用筛选"""
        search_text = self.search_input.text().lower()
        platform = self.platform_filter.currentData()

        records = history_manager.get_all_records()

        # 应用搜索
        if search_text:
            records = [
                r
                for r in records
                if search_text in r.get("url", "").lower()
                or search_text in r.get("nickname", "").lower()
            ]

        # 应用平台筛选
        if platform and platform != "all":
            records = [r for r in records if r.get("platform") == platform]

        self._display_records(records)

    def _add_to_queue(self, record: dict):
        """添加到下载队列"""
        platform = record.get("platform", "douyin")
        mode = record.get("mode", "post")
        url = record.get("url", "")

        if url:
            self.add_to_download_queue.emit(platform, mode, url)

    def _delete_user_records(self, user_key: str):
        """删除用户所有记录"""
        if user_key not in self._user_cards:
            return

        card = self._user_cards[user_key]
        record_ids = card.get_record_ids()

        reply = QMessageBox.question(
            self,
            "确认删除",
            f"确定要删除该用户的 {len(record_ids)} 条下载记录吗？",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )

        if reply == QMessageBox.StandardButton.Yes:
            for record_id in record_ids:
                history_manager.delete_record(record_id)

            card = self._user_cards.pop(user_key)
            card.deleteLater()
            self._load_history()  # 重新加载以更新统计

    def _on_select_all_changed(self, state):
        """全选状态变化"""
        checked = state == Qt.CheckState.Checked.value
        for card in self._user_cards.values():
            card.set_selected(checked)

    def _on_card_selected_changed(self, user_key: str, selected: bool):
        """卡片选中状态变化"""
        pass

    def _toggle_expand_all(self):
        """展开/折叠所有卡片"""
        self._all_expanded = not self._all_expanded

        for card in self._user_cards.values():
            card.set_expanded(self._all_expanded)

        if self._all_expanded:
            self.expand_all_btn.setText("折叠全部")
            show_click_tooltip(self, "已展开全部", "📂")
        else:
            self.expand_all_btn.setText("展开全部")
            show_click_tooltip(self, "已折叠全部", "📁")

    def _batch_add_to_queue(self):
        """批量添加到队列"""
        count = 0
        for card in self._user_cards.values():
            if card.is_selected():
                record = {
                    "platform": card.user_data.get("platform", "douyin"),
                    "mode": card.user_data.get("last_mode", "post"),
                    "url": card.user_data.get("url", ""),
                }
                self._add_to_queue(record)
                count += 1

        if count > 0:
            self.select_all_check.setChecked(False)
            show_click_tooltip(self, f"已添加 {count} 个到队列", "✅")
        else:
            show_click_tooltip(self, "请先选择用户", "⚠️")

    def _batch_delete(self):
        """批量删除"""
        to_delete = [
            key for key, card in self._user_cards.items() if card.is_selected()
        ]

        if not to_delete:
            return

        # 计算总记录数
        total_records = sum(
            len(self._user_cards[key].get_record_ids()) for key in to_delete
        )

        reply = QMessageBox.question(
            self,
            "确认删除",
            f"确定要删除选中的 {len(to_delete)} 个用户的共 {total_records} 条记录吗？",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )

        if reply == QMessageBox.StandardButton.Yes:
            for user_key in to_delete:
                card = self._user_cards[user_key]
                for record_id in card.get_record_ids():
                    history_manager.delete_record(record_id)

            self.select_all_check.setChecked(False)
            show_click_tooltip(self, f"已删除 {total_records} 条记录", "🗑️")
            self._load_history()

    def _clear_history(self):
        """清空历史记录"""
        reply = QMessageBox.question(
            self,
            "确认清空",
            "确定要清空所有历史记录吗？此操作不可恢复。",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )

        if reply == QMessageBox.StandardButton.Yes:
            history_manager.clear_all()
            show_click_tooltip(self, "已清空所有记录", "🗑️")
            self._load_history()

    def refresh(self):
        """刷新页面"""
        self._load_history()
