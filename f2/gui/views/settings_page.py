# -*- coding:utf-8 -*-
# @Information  :
# @Author       : ZGY
# @Date         : 2025-12-01 13:43:21
# @FilePath     : /f2_gui/f2/gui/views/settings_page.py
# @LastEditTime : 2025-12-02 21:29:37

"""
设置页面
~~~~~~~

应用程序设置和配置页面。
整洁的表单布局，支持时间选择和自动保存。
"""

from pathlib import Path

from PyQt6.QtCore import QDate, Qt, QTime, pyqtSignal
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QCheckBox,
    QFileDialog,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from f2.gui.components.buttons import (
    DangerButton,
    GhostButton,
    PrimaryButton,
    SecondaryButton,
)
from f2.gui.components.collapsible_card import CollapsibleCard
from f2.gui.components.combobox import StyledComboBox
from f2.gui.components.datetime_edits import StyledDateEdit, StyledTimeEdit
from f2.gui.components.inputs import StyledLineEdit, StyledTextEdit
from f2.gui.components.spinbox import StyledSpinBox
from f2.gui.components.tabwidget import StyledTabWidget
from f2.gui.components.tooltip import install_tooltip, show_click_tooltip
from f2.gui.config import DEFAULT_DOWNLOAD_CONFIG, LOG_LEVELS, PLATFORM_CONFIG


class SettingsPage(QWidget):
    """设置页面 - 整洁表单布局"""

    settings_changed = pyqtSignal(dict)

    def __init__(self):
        super().__init__()
        self._auto_save = True  # 自动保存开关
        self._platform_cookies = {}  # 存储各平台cookie输入框
        self._setup_ui()

    def _setup_ui(self):
        """设置UI"""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # 滚动区域
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.Shape.NoFrame)
        scroll_area.setObjectName("settingsScrollArea")

        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)
        scroll_layout.setContentsMargins(16, 16, 16, 16)
        scroll_layout.setSpacing(12)

        # 设置区块
        scroll_layout.addWidget(self._create_download_section())
        scroll_layout.addWidget(self._create_connection_section())  # 新增连接设置
        scroll_layout.addWidget(self._create_time_section())  # 时间设置
        scroll_layout.addWidget(self._create_platform_section())  # 新增平台设置
        scroll_layout.addWidget(self._create_proxy_section())
        scroll_layout.addWidget(self._create_bark_section())  # Bark 通知设置
        scroll_layout.addWidget(self._create_advanced_section())

        scroll_layout.addStretch()

        # 底部操作栏
        bottom_bar = QHBoxLayout()
        bottom_bar.setSpacing(8)

        # 自动保存开关
        self.auto_save_check = QCheckBox("自动保存配置")
        self.auto_save_check.setChecked(True)
        self.auto_save_check.toggled.connect(self._on_auto_save_changed)
        bottom_bar.addWidget(self.auto_save_check)

        bottom_bar.addStretch()

        reset_btn = SecondaryButton("重置默认", fixed_height=28, fixed_width=76)
        reset_btn.clicked.connect(self._reset_settings)
        bottom_bar.addWidget(reset_btn)

        self.save_button = PrimaryButton("保存设置", fixed_height=28, fixed_width=76)
        self.save_button.clicked.connect(self._save_settings)
        bottom_bar.addWidget(self.save_button)

        scroll_layout.addLayout(bottom_bar)

        scroll_area.setWidget(scroll_content)
        main_layout.addWidget(scroll_area)

    def _create_section_card(
        self, title: str, collapsed_tag_text: str = "", tag_type: str = "neutral"
    ) -> tuple:
        """创建设置区块卡片 - 使用 CollapsibleCard

        Args:
            title: 卡片标题（可带图标前缀）
            collapsed_tag_text: 折叠时显示的标签文本
            tag_type: 标签类型 (default/success/warning/error/info/neutral)
        """
        # 从标题中提取图标和纯文本
        icons = ["📂", "🔗", "⚙️", "⏰", "🔑", "🕐", "🔒", "📱", "🌐"]
        icon = ""
        clean_title = title
        for i in icons:
            if title.startswith(i):
                icon = i
                clean_title = title[len(i) :].strip()
                break

        # 生成 card_id
        import re

        clean_id = re.sub(r"[^\w]", "", clean_title)
        card_id = f"settings_{clean_id}"

        card = CollapsibleCard(
            parent=self,
            title=clean_title,
            icon=icon,
            subtitle="",
            collapsed_by_default=False,
            card_id=card_id,
        )

        # 添加折叠时显示的标签
        if collapsed_tag_text:
            card.add_collapsed_tag(text=collapsed_tag_text, tag_type=tag_type)

        layout = card.get_content_layout()
        return card, layout

    def _create_form_row(
        self, label_text: str, widget: QWidget, label_width: int = 70
    ) -> QHBoxLayout:
        """创建表单行 - 统一的标签+控件布局"""
        row = QHBoxLayout()
        row.setSpacing(6)

        label = QLabel(label_text)
        label.setFixedWidth(label_width)
        label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        row.addWidget(label)
        row.addWidget(widget, 1)

        return row

    def _create_download_section(self) -> QWidget:
        """创建下载设置区块 - 整齐的表单布局"""
        card, layout = self._create_section_card(
            "📂 下载设置", "路径、命名、并发数", "info"
        )

        # 使用网格布局确保对齐
        grid = QGridLayout()
        grid.setHorizontalSpacing(10)
        grid.setVerticalSpacing(8)
        grid.setColumnMinimumWidth(0, 70)  # 标签列固定宽度

        row = 0

        # 下载路径
        path_label = QLabel("下载路径:")
        path_label.setAlignment(
            Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
        )
        grid.addWidget(path_label, row, 0)

        path_layout = QHBoxLayout()
        path_layout.setSpacing(6)
        self.path_input = StyledLineEdit(fixed_height=30, border_radius=6)
        self.path_input.setText(DEFAULT_DOWNLOAD_CONFIG["path"])
        self.path_input.textChanged.connect(self._on_setting_changed)
        path_layout.addWidget(self.path_input, 1)

        self.path_button = SecondaryButton("浏览", fixed_height=30, fixed_width=50)
        self.path_button.clicked.connect(self._browse_download_path)
        path_layout.addWidget(self.path_button)
        grid.addLayout(path_layout, row, 1)
        row += 1

        # 命名模板
        naming_label = QLabel("命名模板:")
        naming_label.setAlignment(
            Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
        )
        grid.addWidget(naming_label, row, 0)

        # 命名模板输入框
        naming_layout = QHBoxLayout()
        naming_layout.setSpacing(8)

        self.naming_input = StyledLineEdit(
            placeholder="{create}_{desc}", fixed_height=30, border_radius=6
        )
        self.naming_input.setText(DEFAULT_DOWNLOAD_CONFIG["naming_template"])
        self.naming_input.textChanged.connect(self._on_setting_changed)
        install_tooltip(self.naming_input, "使用变量组合自定义文件命名规则")
        naming_layout.addWidget(self.naming_input, 1)

        grid.addLayout(naming_layout, row, 1)
        row += 1

        # 命名模板说明（展开区域）
        naming_hint_label = QLabel("")
        grid.addWidget(naming_hint_label, row, 0)

        naming_hint_frame = self._create_naming_hint_frame()
        grid.addWidget(naming_hint_frame, row, 1)
        row += 1

        # 数值设置行
        nums_layout = QHBoxLayout()
        nums_layout.setSpacing(12)

        # 文件名长度
        nums_layout.addWidget(QLabel("文件名长度:"))
        self.name_length_spin = StyledSpinBox(
            min_value=20,
            max_value=200,
            default_value=DEFAULT_DOWNLOAD_CONFIG["file_name_length"],
            fixed_width=70,
            fixed_height=28,
        )
        install_tooltip(
            self.name_length_spin, "文件名最大字符数，超出部分将被截断", "📏"
        )
        self.name_length_spin.valueChanged.connect(self._on_setting_changed)
        nums_layout.addWidget(self.name_length_spin)

        # 并发数
        nums_layout.addWidget(QLabel("并发数:"))
        self.max_tasks_spin = StyledSpinBox(
            min_value=1,
            max_value=20,
            default_value=DEFAULT_DOWNLOAD_CONFIG["max_tasks"],
            fixed_width=60,
            fixed_height=28,
        )
        install_tooltip(self.max_tasks_spin, "同时下载的任务数量", "⚡")
        self.max_tasks_spin.valueChanged.connect(self._on_setting_changed)
        nums_layout.addWidget(self.max_tasks_spin)

        # 下载上限
        nums_layout.addWidget(QLabel("下载上限:"))
        self.max_counts_spin = StyledSpinBox(
            min_value=0,
            max_value=10000,
            default_value=DEFAULT_DOWNLOAD_CONFIG["max_counts"],
            fixed_width=100,
            fixed_height=28,
        )
        self.max_counts_spin.setSpecialValueText("不限")
        install_tooltip(
            self.max_counts_spin, "单次下载的最大作品数量，0表示不限制", "📊"
        )
        self.max_counts_spin.valueChanged.connect(self._on_setting_changed)
        nums_layout.addWidget(self.max_counts_spin)

        nums_layout.addStretch()

        nums_label = QLabel("")
        nums_label.setFixedWidth(70)
        grid.addWidget(nums_label, row, 0)
        grid.addLayout(nums_layout, row, 1)

        layout.addLayout(grid)
        return card

    def _create_naming_hint_frame(self) -> QFrame:
        """创建命名模板变量说明区域"""
        frame = QFrame()
        frame.setObjectName("namingHintFrame")

        layout = QVBoxLayout(frame)
        layout.setContentsMargins(10, 8, 10, 8)
        layout.setSpacing(6)

        # 说明标题
        hint_title = QLabel("📝 可用变量说明:")
        hint_title.setObjectName("namingHintTitle")
        layout.addWidget(hint_title)

        # 变量说明列表 - 使用流式布局展示单个变量
        variables = [
            ("{create}", "发布时间"),
            ("{desc}", "作品描述"),
            ("{nickname}", "作者昵称"),
            ("{aweme_id}", "作品ID"),
            ("{uid}", "用户ID"),
            ("{sec_uid}", "安全ID"),
            ("{mark}", "自定义标记"),
            ("{index}", "序号"),
        ]

        # 使用网格布局，每行4个变量
        vars_layout = QGridLayout()
        vars_layout.setSpacing(6)
        vars_layout.setContentsMargins(0, 4, 0, 0)

        for i, (var, desc) in enumerate(variables):
            row = i // 4
            col = i % 4

            var_widget = QFrame()
            var_widget.setObjectName("varItem")
            var_layout = QHBoxLayout(var_widget)
            var_layout.setContentsMargins(6, 3, 6, 3)
            var_layout.setSpacing(4)

            var_label = QLabel(var)
            var_label.setObjectName("varName")
            var_layout.addWidget(var_label)

            arrow_label = QLabel("→")
            arrow_label.setObjectName("varArrow")
            var_layout.addWidget(arrow_label)

            desc_label = QLabel(desc)
            desc_label.setObjectName("varDesc")
            var_layout.addWidget(desc_label)

            vars_layout.addWidget(var_widget, row, col)

        layout.addLayout(vars_layout)

        # 应用样式
        self._apply_naming_hint_style(frame)

        return frame

    def _apply_naming_hint_style(self, frame: QFrame):
        """应用命名提示样式"""
        try:
            from f2.gui.themes.theme_manager import ThemeManager

            theme = ThemeManager().get_theme()
        except Exception:
            theme = "dark"

        if theme == "dark":
            frame.setStyleSheet(
                """
                QFrame#namingHintFrame {
                    background-color: rgba(99, 102, 241, 0.08);
                    border: 1px solid rgba(99, 102, 241, 0.2);
                    border-radius: 8px;
                }
                QLabel#namingHintTitle {
                    color: #818CF8;
                    font-size: 11px;
                    font-weight: bold;
                    background: transparent;
                    border: none;
                }
                QFrame#varItem {
                    background: rgba(30, 30, 40, 0.5);
                    border: 1px solid rgba(99, 102, 241, 0.15);
                    border-radius: 6px;
                }
                QLabel#varName {
                    color: #34D399;
                    font-size: 10px;
                    font-family: monospace;
                    background: transparent;
                    border: none;
                }
                QLabel#varArrow {
                    color: #6B7280;
                    font-size: 9px;
                    background: transparent;
                    border: none;
                }
                QLabel#varDesc {
                    color: #9CA3AF;
                    font-size: 10px;
                    background: transparent;
                    border: none;
                }
            """
            )
        else:
            frame.setStyleSheet(
                """
                QFrame#namingHintFrame {
                    background-color: rgba(74, 222, 128, 0.08);
                    border: 1px solid rgba(74, 222, 128, 0.2);
                    border-radius: 8px;
                }
                QLabel#namingHintTitle {
                    color: #059669;
                    font-size: 11px;
                    font-weight: bold;
                    background: transparent;
                    border: none;
                }
                QFrame#varItem {
                    background: rgba(248, 250, 252, 0.8);
                    border: 1px solid rgba(74, 222, 128, 0.2);
                    border-radius: 6px;
                }
                QLabel#varName {
                    color: #047857;
                    font-size: 10px;
                    font-family: monospace;
                    background: transparent;
                    border: none;
                }
                QLabel#varArrow {
                    color: #6B7280;
                    font-size: 9px;
                    background: transparent;
                    border: none;
                }
                QLabel#varDesc {
                    color: #4B5563;
                    font-size: 10px;
                    background: transparent;
                    border: none;
                }
            """
            )

    def _create_connection_section(self) -> QWidget:
        """创建连接设置区块"""
        card, layout = self._create_section_card(
            "🔗 连接设置", "连接数、翻页等待", "info"
        )

        # 使用网格布局
        grid = QGridLayout()
        grid.setHorizontalSpacing(10)
        grid.setVerticalSpacing(8)
        grid.setColumnMinimumWidth(0, 80)

        row = 0

        # 第一行：连接数、每页数量、等待时间
        conn_layout = QHBoxLayout()
        conn_layout.setSpacing(12)

        # 最大连接数
        conn_layout.addWidget(QLabel("最大连接数:"))
        self.max_connections_spin = StyledSpinBox(
            min_value=1,
            max_value=20,
            default_value=DEFAULT_DOWNLOAD_CONFIG.get("max_connections", 5),
            fixed_width=65,
            fixed_height=28,
        )
        install_tooltip(self.max_connections_spin, "网络请求的最大并发连接数")
        self.max_connections_spin.valueChanged.connect(self._on_setting_changed)
        conn_layout.addWidget(self.max_connections_spin)

        # 每页数量
        conn_layout.addWidget(QLabel("每页数量:"))
        self.page_counts_spin = StyledSpinBox(
            min_value=5,
            max_value=100,
            default_value=20,
            fixed_width=65,
            fixed_height=28,
        )
        install_tooltip(self.page_counts_spin, "每次请求获取的作品数量")
        self.page_counts_spin.valueChanged.connect(self._on_setting_changed)
        conn_layout.addWidget(self.page_counts_spin)

        # 等待时间（秒）- 用于翻页等待，避免被限流
        conn_layout.addWidget(QLabel("翻页等待(秒):"))
        self.page_interval_spin = StyledSpinBox(
            min_value=0,
            max_value=300,
            default_value=DEFAULT_DOWNLOAD_CONFIG.get("page_interval", 30),
            fixed_width=65,
            fixed_height=28,
        )
        install_tooltip(
            self.page_interval_spin,
            "每次翻页后的等待时间（秒），避免请求过于频繁被限流",
        )
        self.page_interval_spin.valueChanged.connect(self._on_setting_changed)
        conn_layout.addWidget(self.page_interval_spin)

        conn_layout.addStretch()

        conn_label = QLabel("")
        conn_label.setFixedWidth(80)
        grid.addWidget(conn_label, row, 0)
        grid.addLayout(conn_layout, row, 1)
        row += 1

        # 第二行：选项
        options_layout = QHBoxLayout()
        options_layout.setSpacing(16)

        # 按用户创建文件夹
        self.folderize_check = QCheckBox("按用户创建文件夹")
        self.folderize_check.setChecked(True)
        install_tooltip(self.folderize_check, "为每个用户单独创建下载文件夹")
        self.folderize_check.toggled.connect(self._on_setting_changed)
        options_layout.addWidget(self.folderize_check)

        # 下载歌词（抖音）
        self.lyric_check = QCheckBox("下载歌词 (抖音)")
        self.lyric_check.setChecked(True)
        install_tooltip(self.lyric_check, "下载抖音视频中的原声音乐歌词")
        self.lyric_check.toggled.connect(self._on_setting_changed)
        options_layout.addWidget(self.lyric_check)

        options_layout.addStretch()

        options_label = QLabel("")
        options_label.setFixedWidth(80)
        grid.addWidget(options_label, row, 0)
        grid.addLayout(options_layout, row, 1)

        layout.addLayout(grid)
        return card

    def _create_time_section(self) -> QWidget:
        """创建时间设置区块"""
        card, layout = self._create_section_card(
            "🕐 时间筛选", "按日期范围筛选", "neutral"
        )

        # 说明文字
        hint_label = QLabel("设置下载内容的时间范围（仅下载指定时间段内的内容）")
        hint_label.setObjectName("subtitle")
        layout.addWidget(hint_label)

        # 时间设置网格
        grid = QGridLayout()
        grid.setHorizontalSpacing(12)
        grid.setVerticalSpacing(10)
        grid.setColumnMinimumWidth(0, 80)

        # 启用时间筛选
        self.enable_time_filter = QCheckBox("启用时间筛选")
        self.enable_time_filter.toggled.connect(self._on_time_filter_toggled)
        self.enable_time_filter.toggled.connect(self._on_setting_changed)
        grid.addWidget(self.enable_time_filter, 0, 0, 1, 3)

        # 快捷选项
        preset_label = QLabel("快捷选择:")
        preset_label.setAlignment(
            Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
        )
        grid.addWidget(preset_label, 1, 0)

        preset_layout = QHBoxLayout()
        preset_layout.setSpacing(8)

        self.time_preset = StyledComboBox(min_width=140, fixed_height=32)
        self.time_preset.addItem("📅 自定义时间", "custom")
        self.time_preset.addItem("📆 最近7天", "7days")
        self.time_preset.addItem("📆 最近30天", "30days")
        self.time_preset.addItem("📆 最近3个月", "3months")
        self.time_preset.addItem("📆 最近半年", "6months")
        self.time_preset.addItem("📆 最近一年", "1year")
        self.time_preset.addItem("📆 今年", "this_year")
        self.time_preset.addItem("📆 去年", "last_year")
        self.time_preset.setEnabled(False)
        self.time_preset.currentIndexChanged.connect(self._on_time_preset_changed)
        preset_layout.addWidget(self.time_preset)
        preset_layout.addStretch()

        grid.addLayout(preset_layout, 1, 1, 1, 2)

        # 开始时间
        start_label = QLabel("开始时间:")
        start_label.setAlignment(
            Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
        )
        grid.addWidget(start_label, 2, 0)

        start_layout = QHBoxLayout()
        start_layout.setSpacing(8)

        self.start_date = StyledDateEdit()
        self.start_date.setFixedWidth(149)
        self.start_date.setDate(QDate.currentDate().addMonths(-1))
        self.start_date.setDisplayFormat("yyyy-MM-dd")
        self.start_date.setEnabled(False)
        self.start_date.dateChanged.connect(self._on_time_manual_changed)
        start_layout.addWidget(self.start_date)

        self.start_time = StyledTimeEdit()
        self.start_time.setFixedWidth(120)
        self.start_time.setTime(QTime(0, 0, 0))
        self.start_time.setDisplayFormat("HH:mm:ss")
        self.start_time.setEnabled(False)
        self.start_time.timeChanged.connect(self._on_time_manual_changed)
        start_layout.addWidget(self.start_time)

        start_layout.addStretch()
        grid.addLayout(start_layout, 2, 1, 1, 2)

        # 结束时间
        end_label = QLabel("结束时间:")
        end_label.setAlignment(
            Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
        )
        grid.addWidget(end_label, 3, 0)

        end_layout = QHBoxLayout()
        end_layout.setSpacing(8)

        self.end_date = StyledDateEdit()
        self.end_date.setFixedWidth(149)
        self.end_date.setDate(QDate.currentDate())
        self.end_date.setDisplayFormat("yyyy-MM-dd")
        self.end_date.setEnabled(False)
        self.end_date.dateChanged.connect(self._on_time_manual_changed)
        end_layout.addWidget(self.end_date)

        self.end_time = StyledTimeEdit()
        self.end_time.setFixedWidth(120)
        self.end_time.setTime(QTime(23, 59, 59))
        self.end_time.setDisplayFormat("HH:mm:ss")
        self.end_time.setEnabled(False)
        self.end_time.timeChanged.connect(self._on_time_manual_changed)
        end_layout.addWidget(self.end_time)

        end_layout.addStretch()
        grid.addLayout(end_layout, 3, 1, 1, 2)

        layout.addLayout(grid)
        return card

    def _on_time_filter_toggled(self, checked: bool):
        """时间筛选开关切换"""
        self.time_preset.setEnabled(checked)
        self.start_date.setEnabled(checked)
        self.start_time.setEnabled(checked)
        self.end_date.setEnabled(checked)
        self.end_time.setEnabled(checked)

    def _on_time_preset_changed(self, index: int):
        """快捷时间选项变化"""
        preset = self.time_preset.currentData()
        today = QDate.currentDate()

        if preset == "custom":
            # 自定义，不改变当前值
            pass
        elif preset == "7days":
            self.start_date.setDate(today.addDays(-7))
            self.end_date.setDate(today)
        elif preset == "30days":
            self.start_date.setDate(today.addDays(-30))
            self.end_date.setDate(today)
        elif preset == "3months":
            self.start_date.setDate(today.addMonths(-3))
            self.end_date.setDate(today)
        elif preset == "6months":
            self.start_date.setDate(today.addMonths(-6))
            self.end_date.setDate(today)
        elif preset == "1year":
            self.start_date.setDate(today.addYears(-1))
            self.end_date.setDate(today)
        elif preset == "this_year":
            self.start_date.setDate(QDate(today.year(), 1, 1))
            self.end_date.setDate(today)
        elif preset == "last_year":
            self.start_date.setDate(QDate(today.year() - 1, 1, 1))
            self.end_date.setDate(QDate(today.year() - 1, 12, 31))

        # 重置时间为完整一天
        if preset != "custom":
            self.start_time.setTime(QTime(0, 0, 0))
            self.end_time.setTime(QTime(23, 59, 59))

        self._on_setting_changed()

    def _on_time_manual_changed(self):
        """手动修改时间时，切换到自定义模式"""
        if self.time_preset.currentData() != "custom":
            self.time_preset.blockSignals(True)
            self.time_preset.setCurrentIndex(0)  # 切换到自定义
            self.time_preset.blockSignals(False)
        self._on_setting_changed()

    def _create_platform_section(self) -> QWidget:
        """创建平台设置区块 - Cookie 配置"""
        card, layout = self._create_section_card(
            "🔑 平台设置", "登录凭证配置", "warning"
        )

        # 说明文字
        hint_label = QLabel(
            "设置各平台的 Cookie，用于访问需要登录的内容（如喜欢列表、收藏等）"
        )
        hint_label.setObjectName("subtitle")
        hint_label.setWordWrap(True)
        layout.addWidget(hint_label)

        # 创建标签页
        tab_widget = StyledTabWidget(border_radius=6)
        tab_widget.setObjectName("cookieTabWidget")

        # 为每个平台创建一个标签页
        platforms = [
            ("douyin", "抖音"),
            ("tiktok", "TikTok"),
            ("weibo", "微博"),
            ("twitter", "Twitter/X"),
        ]

        for platform_id, platform_name in platforms:
            tab = QWidget()
            tab_layout = QVBoxLayout(tab)
            tab_layout.setContentsMargins(8, 8, 8, 8)
            tab_layout.setSpacing(6)

            # Cookie 输入框
            cookie_input = StyledTextEdit(
                placeholder=f"请输入 {platform_name} 的 Cookie...\n\n提示：\n1. 登录网页版后，按 F12 打开开发者工具\n2. 切换到 Network (网络) 标签\n3. 刷新页面，点击任意请求\n4. 在 Headers 中找到 Cookie 字段并复制",
                fixed_height=100,
                border_radius=6,
            )
            cookie_input.textChanged.connect(self._on_setting_changed)
            tab_layout.addWidget(cookie_input)

            # 存储引用
            self._platform_cookies[platform_id] = cookie_input

            # 操作按钮
            btn_layout = QHBoxLayout()
            btn_layout.setSpacing(8)

            # 从配置文件加载按钮
            load_btn = SecondaryButton("从配置加载", fixed_height=26, fixed_width=90)
            load_btn.clicked.connect(
                lambda checked, p=platform_id: self._load_cookie_from_config(p)
            )
            btn_layout.addWidget(load_btn)

            # 清空按钮
            clear_btn = DangerButton("清空", fixed_height=26, fixed_width=50)
            clear_btn.clicked.connect(
                lambda checked, p=platform_id: self._clear_platform_cookie(p)
            )
            btn_layout.addWidget(clear_btn)

            btn_layout.addStretch()
            tab_layout.addLayout(btn_layout)

            tab_widget.addTab(tab, platform_name)

        layout.addWidget(tab_widget)
        return card

    def _load_cookie_from_config(self, platform: str):
        """从 F2 配置文件加载 Cookie"""
        try:
            import f2
            from f2.utils.conf_manager import ConfigManager

            main_manager = ConfigManager(f2.APP_CONFIG_FILE_PATH)
            platform_conf = main_manager.get_config(platform)

            if platform_conf and "cookie" in platform_conf:
                cookie = platform_conf.get("cookie", "")
                if cookie and platform in self._platform_cookies:
                    self._platform_cookies[platform].setPlainText(cookie)
                    show_click_tooltip(self, "Cookie 已加载", "✅")
                else:
                    show_click_tooltip(self, "未找到 Cookie 配置", "⚠️")
            else:
                show_click_tooltip(self, "未找到平台配置", "⚠️")
        except Exception as e:
            print(f"加载 Cookie 失败: {e}")
            show_click_tooltip(self, "加载失败", "❌")

    def _clear_platform_cookie(self, platform: str):
        """清空平台 Cookie"""
        if platform in self._platform_cookies:
            self._platform_cookies[platform].clear()
            show_click_tooltip(self, "Cookie 已清空", "🗑️")

    def _create_proxy_section(self) -> QWidget:
        """创建代理设置区块"""
        card, layout = self._create_section_card(
            "🌐 代理设置", "网络代理配置", "neutral"
        )

        grid = QGridLayout()
        grid.setHorizontalSpacing(10)
        grid.setVerticalSpacing(8)
        grid.setColumnMinimumWidth(0, 70)

        # 启用代理
        self.enable_proxy_check = QCheckBox("启用代理")
        self.enable_proxy_check.toggled.connect(self._on_proxy_toggled)
        self.enable_proxy_check.toggled.connect(self._on_setting_changed)
        grid.addWidget(self.enable_proxy_check, 0, 0, 1, 2)

        # 代理地址
        proxy_label = QLabel("代理地址:")
        proxy_label.setAlignment(
            Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
        )
        grid.addWidget(proxy_label, 1, 0)

        self.proxy_input = StyledLineEdit(
            placeholder="http://127.0.0.1:7890", fixed_height=30, border_radius=6
        )
        self.proxy_input.setEnabled(False)
        self.proxy_input.textChanged.connect(self._on_setting_changed)
        grid.addWidget(self.proxy_input, 1, 1)

        layout.addLayout(grid)
        return card

    def _on_proxy_toggled(self, checked: bool):
        """代理开关切换"""
        self.proxy_input.setEnabled(checked)

    def _create_bark_section(self) -> QWidget:
        """创建 Bark 通知设置区块"""
        card, layout = self._create_section_card(
            "🔔 Bark 通知", "下载完成推送通知到 iOS 设备", "neutral"
        )

        grid = QGridLayout()
        grid.setHorizontalSpacing(10)
        grid.setVerticalSpacing(8)
        grid.setColumnMinimumWidth(0, 90)

        # 启用 Bark
        self.enable_bark_check = QCheckBox("启用 Bark 通知")
        self.enable_bark_check.toggled.connect(self._on_bark_toggled)
        self.enable_bark_check.toggled.connect(self._on_setting_changed)
        install_tooltip(
            self.enable_bark_check,
            "下载完成后推送通知到 iOS 设备，需要在 App Store 下载 Bark 应用",
        )
        grid.addWidget(self.enable_bark_check, 0, 0, 1, 2)

        # Bark Token
        token_label = QLabel("Bark Token:")
        token_label.setAlignment(
            Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
        )
        grid.addWidget(token_label, 1, 0)

        self.bark_token_input = StyledLineEdit(
            placeholder="从 Bark App 获取的 Token", fixed_height=30, border_radius=6
        )
        self.bark_token_input.setEnabled(False)
        self.bark_token_input.textChanged.connect(self._on_setting_changed)
        install_tooltip(self.bark_token_input, "打开 Bark App，复制推送 URL 中的 Token")
        grid.addWidget(self.bark_token_input, 1, 1)

        # Bark Key (加密密钥)
        key_label = QLabel("加密密钥:")
        key_label.setAlignment(
            Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
        )
        grid.addWidget(key_label, 2, 0)

        self.bark_key_input = StyledLineEdit(
            placeholder="可选，用于加密推送内容", fixed_height=30, border_radius=6
        )
        self.bark_key_input.setEnabled(False)
        self.bark_key_input.textChanged.connect(self._on_setting_changed)
        install_tooltip(self.bark_key_input, "在 Bark App 设置中配置的加密密钥（可选）")
        grid.addWidget(self.bark_key_input, 2, 1)

        # 提示信息
        hint_label = QLabel("💡 需要在 App Store 下载 Bark 应用，并获取推送 Token")
        hint_label.setStyleSheet("color: #6B7280; font-size: 11px; margin-top: 4px;")
        hint_label.setWordWrap(True)
        grid.addWidget(hint_label, 3, 0, 1, 2)

        layout.addLayout(grid)

        # 尝试加载当前 Bark 配置
        self._load_bark_config()

        return card

    def _on_bark_toggled(self, checked: bool):
        """Bark 开关切换"""
        self.bark_token_input.setEnabled(checked)
        self.bark_key_input.setEnabled(checked)

    def _load_bark_config(self):
        """从 GUI 配置加载 Bark 设置"""
        try:
            from f2.gui.utils.config_manager import ConfigManager

            config_manager = ConfigManager()
            bark_conf = config_manager.get("bark") or {}

            # 设置启用状态
            enable_bark = bark_conf.get("enabled", False)
            self.enable_bark_check.setChecked(enable_bark)

            # 设置 Token 和 Key
            self.bark_token_input.setText(bark_conf.get("token", ""))
            self.bark_key_input.setText(bark_conf.get("key", ""))

        except Exception as e:
            print(f"加载 Bark 配置失败: {e}")

    def _create_advanced_section(self) -> QWidget:
        """创建高级设置区块"""
        card, layout = self._create_section_card(
            "⚙️ 高级设置", "日志、超时、重试", "neutral"
        )

        row = QHBoxLayout()
        row.setSpacing(12)

        # 日志级别
        row.addWidget(QLabel("日志级别:"))
        self.log_level_combo = StyledComboBox(min_width=80, fixed_height=28)
        self.log_level_combo.addItems(LOG_LEVELS)
        self.log_level_combo.setCurrentText("INFO")
        self.log_level_combo.currentTextChanged.connect(self._on_setting_changed)
        row.addWidget(self.log_level_combo)

        # 超时时间
        row.addWidget(QLabel("超时(秒):"))
        self.timeout_spin = StyledSpinBox(
            min_value=10,
            max_value=300,
            default_value=DEFAULT_DOWNLOAD_CONFIG["timeout"],
            fixed_width=65,
            fixed_height=28,
        )
        self.timeout_spin.valueChanged.connect(self._on_setting_changed)
        row.addWidget(self.timeout_spin)

        # 重试次数
        row.addWidget(QLabel("重试次数:"))
        self.retry_spin = StyledSpinBox(
            min_value=0,
            max_value=10,
            default_value=DEFAULT_DOWNLOAD_CONFIG["max_retries"],
            fixed_width=55,
            fixed_height=28,
        )
        self.retry_spin.valueChanged.connect(self._on_setting_changed)
        row.addWidget(self.retry_spin)

        row.addStretch()
        layout.addLayout(row)

        return card

    def _on_auto_save_changed(self, checked: bool):
        """自动保存开关变化"""
        self._auto_save = checked
        self.save_button.setEnabled(not checked)

    def _on_setting_changed(self):
        """设置变化时自动保存"""
        if self._auto_save:
            self._save_settings()

    def _browse_download_path(self):
        """浏览下载路径"""
        path = QFileDialog.getExistingDirectory(
            self, "选择下载路径", self.path_input.text()
        )
        if path:
            self.path_input.setText(path)

    def _reset_settings(self):
        """重置设置"""
        # 暂时禁用自动保存
        old_auto_save = self._auto_save
        self._auto_save = False

        self.path_input.setText(DEFAULT_DOWNLOAD_CONFIG["path"])
        self.naming_input.setText(DEFAULT_DOWNLOAD_CONFIG["naming_template"])
        self.name_length_spin.setValue(DEFAULT_DOWNLOAD_CONFIG["file_name_length"])
        self.max_tasks_spin.setValue(DEFAULT_DOWNLOAD_CONFIG["max_tasks"])
        self.max_counts_spin.setValue(DEFAULT_DOWNLOAD_CONFIG["max_counts"])
        self.timeout_spin.setValue(DEFAULT_DOWNLOAD_CONFIG["timeout"])
        self.retry_spin.setValue(DEFAULT_DOWNLOAD_CONFIG["max_retries"])
        self.enable_proxy_check.setChecked(False)
        self.proxy_input.clear()
        self.log_level_combo.setCurrentText("INFO")

        # 重置连接设置
        self.max_connections_spin.setValue(
            DEFAULT_DOWNLOAD_CONFIG.get("max_connections", 5)
        )
        self.page_counts_spin.setValue(20)
        self.page_interval_spin.setValue(
            DEFAULT_DOWNLOAD_CONFIG.get("page_interval", 30)
        )
        self.folderize_check.setChecked(True)
        self.lyric_check.setChecked(True)

        # 重置时间设置
        self.enable_time_filter.setChecked(False)
        self.start_date.setDate(QDate.currentDate().addMonths(-1))
        self.start_time.setTime(QTime(0, 0, 0))
        self.end_date.setDate(QDate.currentDate())
        self.end_time.setTime(QTime(23, 59, 59))

        # 重置 Cookie
        for platform, cookie_input in self._platform_cookies.items():
            cookie_input.clear()

        # 恢复自动保存并保存
        self._auto_save = old_auto_save
        if self._auto_save:
            self._save_settings()

        show_click_tooltip(self, "已重置为默认设置", "🔄")

    def _save_settings(self):
        """保存设置"""
        # 收集 Cookie 设置
        cookies = {}
        for platform, cookie_input in self._platform_cookies.items():
            cookie_text = cookie_input.toPlainText().strip()
            if cookie_text:
                cookies[platform] = cookie_text

        settings = {
            "download": {
                "path": self.path_input.text(),
                "naming_template": self.naming_input.text(),
                "file_name_length": self.name_length_spin.value(),
                "max_tasks": self.max_tasks_spin.value(),
                "max_counts": self.max_counts_spin.value(),
                "timeout": self.timeout_spin.value(),
                "max_retries": self.retry_spin.value(),
                "max_connections": self.max_connections_spin.value(),
                "page_counts": self.page_counts_spin.value(),
                "page_interval": self.page_interval_spin.value(),
                "folderize": self.folderize_check.isChecked(),
                "lyric": self.lyric_check.isChecked(),
            },
            "time_filter": {
                "enabled": self.enable_time_filter.isChecked(),
                "start_date": self.start_date.date().toString("yyyy-MM-dd"),
                "start_time": self.start_time.time().toString("HH:mm:ss"),
                "end_date": self.end_date.date().toString("yyyy-MM-dd"),
                "end_time": self.end_time.time().toString("HH:mm:ss"),
            },
            "proxy": {
                "enabled": self.enable_proxy_check.isChecked(),
                "address": self.proxy_input.text(),
            },
            "bark": {
                "enabled": self.enable_bark_check.isChecked(),
                "token": self.bark_token_input.text(),
                "key": self.bark_key_input.text(),
            },
            "cookies": cookies,
            "advanced": {
                "log_level": self.log_level_combo.currentText(),
            },
        }
        self.settings_changed.emit(settings)

    def load_settings(self, settings: dict):
        """加载设置"""
        # 暂时禁用自动保存避免循环
        old_auto_save = self._auto_save
        self._auto_save = False

        if "download" in settings:
            download = settings["download"]
            self.path_input.setText(download.get("path", ""))
            self.naming_input.setText(download.get("naming_template", ""))
            self.name_length_spin.setValue(download.get("file_name_length", 80))
            self.max_tasks_spin.setValue(download.get("max_tasks", 5))
            self.max_counts_spin.setValue(download.get("max_counts", 0))
            self.timeout_spin.setValue(download.get("timeout", 30))
            self.retry_spin.setValue(download.get("max_retries", 3))
            self.max_connections_spin.setValue(download.get("max_connections", 5))
            self.page_counts_spin.setValue(download.get("page_counts", 20))
            self.page_interval_spin.setValue(download.get("page_interval", 30))
            self.folderize_check.setChecked(download.get("folderize", True))
            self.lyric_check.setChecked(download.get("lyric", True))

        if "time_filter" in settings:
            tf = settings["time_filter"]
            self.enable_time_filter.setChecked(tf.get("enabled", False))
            if tf.get("start_date"):
                self.start_date.setDate(
                    QDate.fromString(tf["start_date"], "yyyy-MM-dd")
                )
            if tf.get("start_time"):
                self.start_time.setTime(QTime.fromString(tf["start_time"], "HH:mm:ss"))
            if tf.get("end_date"):
                self.end_date.setDate(QDate.fromString(tf["end_date"], "yyyy-MM-dd"))
            if tf.get("end_time"):
                self.end_time.setTime(QTime.fromString(tf["end_time"], "HH:mm:ss"))

        if "proxy" in settings:
            proxy = settings["proxy"]
            self.enable_proxy_check.setChecked(proxy.get("enabled", False))
            self.proxy_input.setText(proxy.get("address", ""))

        if "cookies" in settings:
            cookies = settings["cookies"]
            for platform, cookie in cookies.items():
                if platform in self._platform_cookies:
                    self._platform_cookies[platform].setPlainText(cookie)

        if "advanced" in settings:
            advanced = settings["advanced"]
            self.log_level_combo.setCurrentText(advanced.get("log_level", "INFO"))

        # 恢复自动保存
        self._auto_save = old_auto_save
