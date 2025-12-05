# -*- coding:utf-8 -*-
# @Information  :
# @Author       : ZGY
# @Date         : 2025-12-01 13:43:20
# @FilePath     : /f2_gui/f2/gui/components/__init__.py
# @LastEditTime : 2025-12-05

"""
组件模块
~~~~~~~

可复用的UI组件。
"""

# 基础组件
from .base_card import BaseCard

# 按钮组件
from .buttons import (
    DangerButton,
    GhostButton,
    GradientButton,
    PrimaryButton,
    SecondaryButton,
    SuccessButton,
    TextButton,
    WarningButton,
    create_button,
)

# 卡片组件
from .collapsible_card import (
    CollapsibleCard,
    CollapsibleSection,
    CompactCollapsibleCard,
)

# 输入组件
from .combobox import PlatformComboBox, SortComboBox, StyledComboBox
from .download_task_card import DownloadTaskCard
from .inputs import BatchTextEdit, StyledLineEdit, StyledTextEdit, UrlLineEdit

# 标签组件
from .labels import (
    CardTextLabel,
    CountBadge,
    InfoCardLabel,
    KeyValueLabel,
    ModeLabel,
    PlatformLabel,
    StatusLabel,
    TagLabel,
    TextLabel,
)

# 分隔线组件
from .separator import GradientSeparator, SimpleSeparator
from .spinbox import StyledSpinBox
from .stats_card import CompactStatsRow, GridStatsCard, HorizontalStatsCard, StatsCard

# Tab 组件
from .tabwidget import StyledTabWidget

# 提示组件
from .tooltip import FloatingTooltip, install_tooltip, show_click_tooltip
from .user_card import CompactUserCard, TaskItemCard, UserCard

__all__ = [
    # 基础
    "BaseCard",
    # 按钮
    "GradientButton",
    "PrimaryButton",
    "DangerButton",
    "SuccessButton",
    "WarningButton",
    "SecondaryButton",
    "GhostButton",
    "TextButton",
    "create_button",
    # 卡片
    "DownloadTaskCard",
    "CollapsibleCard",
    "CollapsibleSection",
    "CompactCollapsibleCard",
    "StatsCard",
    "HorizontalStatsCard",
    "GridStatsCard",
    "CompactStatsRow",
    "UserCard",
    "CompactUserCard",
    "TaskItemCard",
    # 输入
    "StyledComboBox",
    "PlatformComboBox",
    "SortComboBox",
    "StyledLineEdit",
    "StyledTextEdit",
    "UrlLineEdit",
    "BatchTextEdit",
    "StyledSpinBox",
    # 标签
    "TagLabel",
    "PlatformLabel",
    "ModeLabel",
    "StatusLabel",
    "CountBadge",
    "TextLabel",
    "CardTextLabel",
    "KeyValueLabel",
    "InfoCardLabel",
    # 分隔线
    "GradientSeparator",
    "SimpleSeparator",
    # Tab
    "StyledTabWidget",
    # 提示
    "FloatingTooltip",
    "install_tooltip",
    "show_click_tooltip",
]
