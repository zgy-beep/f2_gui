# -*- coding:utf-8 -*-
# @Information  :
# @Author       : ZGY
# @Date         : 2025-12-02 17:40:06
# @FilePath     : /f2_gui/f2/gui/components/combobox.py
# @LastEditTime : 2025-12-05 16:53:33

"""
下拉框组件
~~~~~~~~~~

自定义样式的 QComboBox，支持主题切换。
"""

import os

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QComboBox

# 获取资源路径
_ASSETS_PATH = os.path.join(
    os.path.dirname(os.path.dirname(__file__)), "assets", "icon"
)

# ===================== 主题样式定义 =====================
# 夜间模式 - 透明背景，蓝紫色边框
DARK_STYLES = {
    "bg": "transparent",
    "bg_hover": "rgba(99, 102, 241, 0.08)",
    "border": "rgba(99, 102, 241, 0.3)",
    "border_hover": "rgba(139, 92, 246, 0.5)",
    "border_focus": "rgba(139, 92, 246, 0.7)",
    "text": "#E5E7EB",
    "text_placeholder": "#6B7280",
    "dropdown_bg": "rgba(30, 32, 45, 0.98)",
    "item_hover_bg": "rgba(99, 102, 241, 0.15)",
    "item_selected_bg": "rgba(99, 102, 241, 0.25)",
    "arrow_icon": "Dark_Arrow_Down.png",
}

# 日间模式 - 透明背景，绿色边框
LIGHT_STYLES = {
    "bg": "transparent",
    "bg_hover": "rgba(74, 222, 128, 0.08)",
    "border": "rgba(74, 222, 128, 0.4)",
    "border_hover": "rgba(34, 197, 94, 0.5)",
    "border_focus": "rgba(34, 197, 94, 0.7)",
    "text": "#1F2937",
    "text_placeholder": "#9CA3AF",
    "dropdown_bg": "rgba(255, 255, 255, 0.98)",
    "item_hover_bg": "rgba(163, 230, 53, 0.15)",
    "item_selected_bg": "rgba(74, 222, 128, 0.2)",
    "arrow_icon": "Light_Arrow_Down.png",
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


class StyledComboBox(QComboBox):
    """自定义样式下拉框 - 支持主题切换"""

    def __init__(
        self,
        parent=None,
        placeholder: str = "",
        min_width: int = 120,
        fixed_height: int = 32,
    ):
        super().__init__(parent)

        self._placeholder = placeholder

        # 设置尺寸
        if min_width:
            self.setMinimumWidth(min_width)
        if fixed_height:
            self.setFixedHeight(fixed_height)

        # 设置占位符
        if placeholder:
            self.setPlaceholderText(placeholder)

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

        # 获取箭头图标路径（使用正斜杠，QSS 需要）
        arrow_path = os.path.join(_ASSETS_PATH, styles["arrow_icon"]).replace("\\", "/")

        self.setStyleSheet(
            f"""
            QComboBox {{
                background-color: {styles['bg']};
                border: 1px solid {styles['border']};
                border-radius: 6px;
                padding: 4px 28px 4px 10px;
                color: {styles['text']};
                font-size: 12px;
                font-weight: 500;
            }}
            
            QComboBox:hover {{
                background-color: {styles['bg_hover']};
                border-color: {styles['border_hover']};
            }}
            
            QComboBox:focus {{
                border-color: {styles['border_focus']};
            }}
            
            QComboBox::drop-down {{
                subcontrol-origin: padding;
                subcontrol-position: center right;
                width: 24px;
                border: none;
                border-left: 1px solid {styles['border']};
                border-top-right-radius: 6px;
                border-bottom-right-radius: 6px;
                background: transparent;
            }}
            
            QComboBox::down-arrow {{
                image: url({arrow_path});
                width: 12px;
                height: 12px;
            }}
            
            QComboBox QAbstractItemView {{
                background-color: {styles['dropdown_bg']};
                border: 1px solid {styles['border_hover']};
                border-radius: 6px;
                padding: 4px;
                selection-background-color: {styles['item_selected_bg']};
                selection-color: {styles['text']};
                outline: none;
            }}
            
            QComboBox QAbstractItemView::item {{
                height: 28px;
                padding: 4px 10px;
                border-radius: 4px;
                color: {styles['text']};
            }}
            
            QComboBox QAbstractItemView::item:hover {{
                background-color: {styles['item_hover_bg']};
            }}
            
            QComboBox QAbstractItemView::item:selected {{
                background-color: {styles['item_selected_bg']};
            }}
        """
        )


class PlatformComboBox(StyledComboBox):
    """平台选择下拉框"""

    def __init__(self, parent=None, include_all: bool = True):
        super().__init__(parent, min_width=130, fixed_height=32)

        # 平台图标映射
        platform_icons = {
            "douyin": "🎵",
            "tiktok": "🎬",
            "weibo": "📰",
            "twitter": "🐦",
        }

        if include_all:
            self.addItem("🌐 全部平台", "all")

        try:
            from f2.gui.config import PLATFORM_CONFIG

            for platform_id, platform_info in PLATFORM_CONFIG.items():
                icon = platform_icons.get(platform_id, "📦")
                self.addItem(f"{icon} {platform_info['name']}", platform_id)
        except Exception:
            pass


class SortComboBox(StyledComboBox):
    """排序方式下拉框"""

    def __init__(self, parent=None):
        super().__init__(parent, min_width=130, fixed_height=32)

        self.addItem("🕐 最近下载", "last_time")
        self.addItem("📊 下载次数", "download_count")
        self.addItem("🔤 名称排序", "name")
