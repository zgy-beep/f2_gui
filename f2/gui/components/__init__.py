# -*- coding:utf-8 -*-
# @Information  :
# @Author       : ZGY
# @Date         : 2025-12-01 13:43:20
# @FilePath     : /f2_gui/f2/gui/components/__init__.py
# @LastEditTime : 2025-12-02 17:06:48

"""
组件模块
~~~~~~~

可复用的UI组件。
"""

from .base_card import BaseCard
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
from .collapsible_card import (
    CollapsibleCard,
    CollapsibleSection,
    CompactCollapsibleCard,
)
from .download_task_card import DownloadTaskCard
from .stats_card import CompactStatsRow, GridStatsCard, HorizontalStatsCard, StatsCard
from .tooltip import FloatingTooltip, install_tooltip, show_click_tooltip

__all__ = [
    "BaseCard",
    "DownloadTaskCard",
    "CollapsibleCard",
    "CollapsibleSection",
    "CompactCollapsibleCard",
    "StatsCard",
    "HorizontalStatsCard",
    "GridStatsCard",
    "CompactStatsRow",
    "GradientButton",
    "PrimaryButton",
    "DangerButton",
    "SuccessButton",
    "WarningButton",
    "SecondaryButton",
    "GhostButton",
    "TextButton",
    "create_button",
    "FloatingTooltip",
    "install_tooltip",
    "show_click_tooltip",
]
