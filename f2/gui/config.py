# -*- coding:utf-8 -*-
# @Information  :
# @Author       : ZGY
# @Date         : 2025-12-01 13:43:20
# @FilePath     : /f2_gui/f2/gui/config.py
# @LastEditTime : 2025-12-04 11:04:34

"""
GUI配置管理模块
~~~~~~~~~~~~~~

管理GUI应用的全局配置、默认值和常量。
"""

from pathlib import Path

from f2.gui.version import get_version

# 应用配置
APP_NAME = "F2 下载工具"
APP_VERSION = get_version()
ORGANIZATION_NAME = "F2"
ORGANIZATION_DOMAIN = "f2.wiki"

# 默认窗口尺寸
DEFAULT_WINDOW_WIDTH = 1400
DEFAULT_WINDOW_HEIGHT = 900
MIN_WINDOW_WIDTH = 1200
MIN_WINDOW_HEIGHT = 700

# 主题配置
DEFAULT_THEME = "light"  # light 或 dark
THEME_AUTO_DETECT = True  # 是否根据系统主题自动切换

# 文件路径配置
BASE_DIR = Path(__file__).parent
ASSETS_DIR = BASE_DIR / "assets"
THEMES_DIR = BASE_DIR / "themes"
CONFIG_FILE = BASE_DIR / "gui_config.json"
HISTORY_FILE = BASE_DIR / "download_history.json"
SECRETS_FILE = BASE_DIR / "f2_gui_secrets"  # Cookie 等敏感信息单独存储

# 下载配置默认值
DEFAULT_DOWNLOAD_CONFIG = {
    "path": str(Path.home() / "Downloads" / "F2"),
    "naming_template": "{create}_{desc}",
    "file_name_length": 80,
    "chunk_size": 1024 * 1024,  # 1MB
    "max_connections": 5,
    "max_retries": 3,
    "timeout": 30,
    "max_tasks": 5,
    "max_counts": 0,  # 0表示不限制
    "page_interval": 30,  # 翻页等待时间（秒），避免与F2核心的interval（日期区间）冲突
    "page_counts": 20,  # 单页数量
    "folderize": True,  # 是否按作者分文件夹
    "lyric": True,  # 是否保存歌词
}

# 下载模式中英文映射
MODE_NAMES = {
    "one": "单个作品",
    "post": "主页作品",
    "like": "喜欢作品",
    "collection": "收藏作品",
    "collect": "收藏作品",
    "music": "音乐作品",
    "mix": "合集作品",
    "live": "直播录制",
    "search": "搜索作品",
    "bookmark": "书签作品",
}

# 平台配置
PLATFORM_CONFIG = {
    "douyin": {
        "name": "抖音",
        "icon": "douyin.svg",
        "modes": ["one", "post", "like", "collection", "music", "mix", "live"],
        "color": "#000000",
    },
    "tiktok": {
        "name": "TikTok",
        "icon": "tiktok.svg",
        "modes": ["one", "post", "like", "collect", "mix", "search", "live"],
        "color": "#000000",
    },
    "weibo": {
        "name": "微博",
        "icon": "weibo.svg",
        "modes": ["one", "post"],
        "color": "#E6162D",
    },
    "twitter": {
        "name": "Twitter/X",
        "icon": "twitter.svg",
        "modes": ["one", "post", "like", "bookmark"],
        "color": "#1DA1F2",
    },
}

# 日志配置
LOG_LEVELS = ["DEBUG", "INFO", "WARNING", "ERROR"]
DEFAULT_LOG_LEVEL = "INFO"
MAX_LOG_LINES = 1000


# UI配置
CARD_BORDER_RADIUS = 12
CARD_SHADOW_BLUR = 16
ANIMATION_DURATION = 300  # 毫秒
SIDEBAR_WIDTH = 280
SIDEBAR_COLLAPSED_WIDTH = 80

# 颜色配置
COLORS = {
    "light": {
        # 主色调 - 紫蓝色调（更深）
        "primary": "#4F46E5",
        "on_primary": "#554A4A",
        "primary_container": "#5B6277",
        "on_primary_container": "#635AE2",
        # 次要色调
        "secondary": "#4B5563",
        "on_secondary": "#574141",
        "secondary_container": "#3E4452",
        "on_secondary_container": "#1F2937",
        # 第三色调
        "tertiary": "#7C3AED",
        "on_tertiary": "#554646",
        "tertiary_container": "#393646",
        "on_tertiary_container": "#5B21B6",
        # 错误状态
        "error": "#DC2626",
        "on_error": "#630909",
        "error_container": "#940202",
        "on_error_container": "#B91C1C",
        # 成功状态
        "success": "#059669",
        "on_success": "#FFFFFF",
        "success_container": "#D1FAE5",
        "on_success_container": "#065F46",
        # 背景和表面
        "background": "#FAFAFA",
        "on_background": "#171717",
        "surface": "#FFFFFF",
        "on_surface": "#171717",
        "surface_variant": "#F5F5F5",
        "on_surface_variant": "#6B7280",
        "surface_dim": "#EBEBEB",
        # 边框和分隔线
        "outline": "#E5E5E5",
        "outline_variant": "#F0F0F0",
        # 其他
        "shadow": "rgba(0, 0, 0, 0.08)",
        "scrim": "rgba(0, 0, 0, 0.4)",
        "inverse_surface": "#262626",
        "inverse_on_surface": "#FAFAFA",
        "inverse_primary": "#A5B4FC",
    },
    "dark": {
        # 主色调 - 紫蓝色调（更亮）
        "primary": "#8A9CF1",
        "on_primary": "#5650AA",
        "primary_container": "#6356F5",
        "on_primary_container": "#9CB1F8",
        # 次要色调
        "secondary": "#D1D5DB",
        "on_secondary": "#1F2937",
        "secondary_container": "#4B5563",
        "on_secondary_container": "#F3F4F6",
        # 第三色调
        "tertiary": "#C4B5FD",
        "on_tertiary": "#2E1065",
        "tertiary_container": "#5B21B6",
        "on_tertiary_container": "#EDE9FE",
        # 错误状态
        "error": "#FCA5A5",
        "on_error": "#7F1D1D",
        "error_container": "#991B1B",
        "on_error_container": "#FEE2E2",
        # 成功状态
        "success": "#6EE7B7",
        "on_success": "#0B6D53",
        "success_container": "#0C8A66",
        "on_success_container": "#9FF3C8",
        # 背景和表面 - 与卡片渐变色和谐
        "background": "#0D0F1A",
        "on_background": "#FAFAFA",
        "surface": "#161929",
        "on_surface": "#FAFAFA",
        "surface_variant": "#1E2235",
        "on_surface_variant": "#A3A3A3",
        "surface_dim": "#0A0C14",
        # 边框和分隔线
        "outline": "#2A2A2A",
        "outline_variant": "#1F1F1F",
        # 其他
        "shadow": "rgba(0, 0, 0, 0.3)",
        "scrim": "rgba(0, 0, 0, 0.6)",
        "inverse_surface": "#FAFAFA",
        "inverse_on_surface": "#171717",
        "inverse_primary": "#5E6AD2",
    },
}
