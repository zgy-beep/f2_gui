# -*- coding:utf-8 -*-
# @Information  :
# @Author       : ZGY
# @Date         : 2025-12-01 13:43:21
# @FilePath     : /f2_gui/f2/gui/__main__.py
# @LastEditTime : 2025-12-02 22:26:04

"""
F2 GUI v02 主入口
~~~~~~~~~~~~~~~~

启动现代化的 F2 GUI 应用程序。
"""

import sys
from pathlib import Path

# 添加父目录到路径,以便导入f2模块
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from PyQt6.QtCore import Qt, QtMsgType, qInstallMessageHandler
from PyQt6.QtGui import QFont, QIcon
from PyQt6.QtWidgets import QApplication

from f2.gui.config import APP_NAME, APP_VERSION, ASSETS_DIR
from f2.gui.themes.theme_manager import ThemeManager
from f2.gui.views.main_window import MainWindow


def qt_message_handler(mode, context, message):
    """自定义 Qt 消息处理器，过滤已知的无害警告"""
    # 过滤 QFont::setPointSize 警告（PyQt6 内部问题，不影响功能）
    if "QFont::setPointSize" in message:
        return
    # 其他消息正常输出
    if mode == QtMsgType.QtWarningMsg:
        print(f"Qt Warning: {message}")
    elif mode == QtMsgType.QtCriticalMsg:
        print(f"Qt Critical: {message}")
    elif mode == QtMsgType.QtFatalMsg:
        print(f"Qt Fatal: {message}")


def setup_application():
    """设置应用程序属性"""
    # 启用高DPI支持
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )

    app = QApplication(sys.argv)
    app.setApplicationName(APP_NAME)
    app.setApplicationVersion(APP_VERSION)
    app.setOrganizationName("F2")
    app.setOrganizationDomain("f2.wiki")

    # 设置默认字体，避免 QFont::setPointSize 警告
    # 明确指定字体名称和大小，确保在所有系统上都有效
    default_font = QFont("Microsoft YaHei UI", 10)
    if not default_font.exactMatch():
        # 如果首选字体不存在，使用备用字体
        default_font = QFont("Segoe UI", 10)
    if not default_font.exactMatch():
        # 如果备用字体也不存在，使用系统默认字体
        default_font = app.font()
        if default_font.pointSize() <= 0:
            default_font.setPointSize(10)
    app.setFont(default_font)

    # 设置应用图标
    icon_path = ASSETS_DIR / "public" / "f2-logo.ico"
    if icon_path.exists():
        app.setWindowIcon(QIcon(str(icon_path)))

    return app


def main():
    """主函数"""
    # 安装自定义消息处理器，过滤已知的无害警告
    qInstallMessageHandler(qt_message_handler)

    app = setup_application()

    # 初始化主题管理器并加载样式
    theme_manager = ThemeManager()

    # 先应用主题样式表到整个应用
    theme_manager.apply_to_app(app)

    # 创建并显示主窗口
    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
