"""
F2 GUI v02 - 现代化图形用户界面
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

基于 PyQt6 的现代化、模块化的 F2 下载工具图形界面。

特性:
    - Material Design 3 设计风格
    - 卡片式布局
    - 支持亮色/暗色主题
    - 多平台支持 (抖音、TikTok、微博、Twitter等)
    - 模块化架构

:copyright: (c) 2025 by F2.
:license: Apache-2.0, see LICENSE for more details.
"""

__version__ = "0.2.0"
__author__ = "F2 Team"
__description__ = "F2 Modern GUI - Material Design 3"

# 支持的平台列表
SUPPORTED_PLATFORMS = [
    ("douyin", "抖音", "dy"),
    ("tiktok", "TikTok", "tk"),
    ("weibo", "微博", "wb"),
    ("twitter", "Twitter/X", "x"),
]

__all__ = [
    "__version__",
    "__author__",
    "__description__",
    "SUPPORTED_PLATFORMS",
]
