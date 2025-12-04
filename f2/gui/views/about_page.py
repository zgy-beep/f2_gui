"""
关于页面
~~~~~~~

展示应用信息、版本、作者和相关链接。
采用现代化卡片设计，美观整洁。
"""

from PyQt6.QtCore import Qt, QUrl
from PyQt6.QtGui import QDesktopServices, QFont, QPixmap
from PyQt6.QtWidgets import (
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from f2.gui.components.collapsible_card import CollapsibleCard
from f2.gui.config import APP_NAME, APP_VERSION, ASSETS_DIR
from f2.gui.version import get_changelog, get_latest_changes


class AboutPage(QWidget):
    """关于页面 - 现代化设计"""

    def __init__(self):
        super().__init__()
        self._setup_ui()

    def _setup_ui(self):
        """设置UI"""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # 滚动区域
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.Shape.NoFrame)
        scroll_area.setObjectName("aboutScrollArea")

        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)
        scroll_layout.setContentsMargins(16, 16, 16, 16)
        scroll_layout.setSpacing(12)

        # 顶部 Logo 和应用信息
        scroll_layout.addWidget(self._create_header_section())

        # 版本更新记录
        scroll_layout.addWidget(self._create_changelog_section())

        # 功能特性
        scroll_layout.addWidget(self._create_features_section())

        # 链接卡片行
        links_row = QHBoxLayout()
        links_row.setSpacing(12)
        links_row.addWidget(self._create_links_section(), 1)
        links_row.addWidget(self._create_tech_section(), 1)
        scroll_layout.addLayout(links_row)

        # 开源协议和致谢
        scroll_layout.addWidget(self._create_license_section())

        scroll_layout.addStretch()

        scroll_area.setWidget(scroll_content)
        main_layout.addWidget(scroll_area)

    def _create_header_section(self) -> QWidget:
        """创建头部区域 - Logo和应用信息（使用可折叠卡片）"""
        card = CollapsibleCard(
            title="F2",
            icon="📦",
            subtitle="",
            collapsed_by_default=False,
            card_id="about_header",
        )
        # 添加折叠时显示的标签
        card.add_collapsed_tag(text="多平台媒体内容下载工具", tag_type="info")

        content_layout = card.get_content_layout()
        content_layout.setContentsMargins(14, 0, 14, 14)

        # 居中容器
        center_widget = QWidget()
        center_layout = QVBoxLayout(center_widget)
        center_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        center_layout.setSpacing(12)

        # Logo 图片
        logo_label = QLabel()
        logo_path = ASSETS_DIR / "public" / "f2-logo-with-shadow.png"
        if logo_path.exists():
            pixmap = QPixmap(str(logo_path))
            # 缩放到合适大小
            scaled_pixmap = pixmap.scaled(
                96,
                96,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )
            logo_label.setPixmap(scaled_pixmap)
        else:
            # 备用文字图标
            logo_label.setText("📦")
            logo_font = logo_label.font()
            logo_font.setPointSize(48)
            logo_label.setFont(logo_font)
        logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        center_layout.addWidget(logo_label)

        # 应用名称
        name_label = QLabel("F2")
        name_font = name_label.font()
        name_font.setPointSize(28)
        name_font.setWeight(QFont.Weight.Bold)
        name_label.setFont(name_font)
        name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        center_layout.addWidget(name_label)

        # 副标题
        subtitle_label = QLabel("多平台媒体内容下载工具")
        subtitle_label.setObjectName("subtitle")
        subtitle_font = subtitle_label.font()
        subtitle_font.setPointSize(12)
        subtitle_label.setFont(subtitle_font)
        subtitle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        center_layout.addWidget(subtitle_label)

        # 版本信息
        version_label = QLabel(f"版本 {APP_VERSION}")
        version_label.setObjectName("versionBadge")
        version_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        version_label.setStyleSheet(
            """
            QLabel {
                background: rgba(79, 70, 229, 0.1);
                color: #4F46E5;
                padding: 4px 12px;
                border-radius: 12px;
                font-size: 11px;
                font-weight: 500;
            }
        """
        )
        center_layout.addWidget(version_label, alignment=Qt.AlignmentFlag.AlignCenter)

        # 描述
        desc_label = QLabel(
            "F2 是一个强大的命令行工具和图形界面应用，\n"
            "支持从抖音、TikTok、微博、Twitter/X 等平台下载媒体内容。"
        )
        desc_label.setObjectName("subtitle")
        desc_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        desc_label.setWordWrap(True)
        center_layout.addWidget(desc_label)

        content_layout.addWidget(center_widget)
        return card

    def _create_changelog_section(self) -> QWidget:
        """创建版本更新记录区域"""
        latest = get_latest_changes()
        changelog = get_changelog()

        card = CollapsibleCard(
            title=f"更新日志 v{APP_VERSION}",
            icon="📋",
            subtitle=latest.get("日期", ""),
            collapsed_by_default=False,
            card_id="about_changelog",
        )
        # 添加折叠时显示的标签
        changes_count = len(latest.get("更新内容", []))
        card.add_collapsed_tag(text=f"{changes_count} 项更新", tag_type="info")

        content_layout = card.get_content_layout()
        content_layout.setSpacing(12)

        # 当前版本更新内容
        current_section = QWidget()
        current_layout = QVBoxLayout(current_section)
        current_layout.setContentsMargins(0, 0, 0, 0)
        current_layout.setSpacing(6)

        for change in latest.get("更新内容", []):
            change_label = QLabel(f"• {change}")
            change_label.setWordWrap(True)
            change_label.setStyleSheet("font-size: 12px; padding: 2px 0;")
            current_layout.addWidget(change_label)

        content_layout.addWidget(current_section)

        # 历史版本（折叠显示）
        if len(changelog) > 1:
            # 分隔线
            separator = QFrame()
            separator.setFrameShape(QFrame.Shape.HLine)
            separator.setStyleSheet("background: rgba(128, 128, 128, 0.2);")
            separator.setFixedHeight(1)
            content_layout.addWidget(separator)

            # 历史版本标题
            history_title = QLabel("历史版本")
            history_title.setStyleSheet(
                "font-size: 11px; font-weight: 600; color: #6B7280; margin-top: 4px;"
            )
            content_layout.addWidget(history_title)

            # 历史版本内容（只显示最近3个旧版本）
            versions = list(changelog.keys())
            for version in versions[1:4]:  # 跳过当前版本，最多显示3个
                version_data = changelog[version]
                version_widget = self._create_version_item(version, version_data)
                content_layout.addWidget(version_widget)

        return card

    def _create_version_item(self, version: str, data: dict) -> QWidget:
        """创建单个版本更新项"""
        widget = QFrame()
        widget.setStyleSheet(
            """
            QFrame {
                background: rgba(128, 128, 128, 0.05);
                border-radius: 6px;
                padding: 8px;
            }
        """
        )

        layout = QVBoxLayout(widget)
        layout.setContentsMargins(10, 8, 10, 8)
        layout.setSpacing(4)

        # 版本号和日期
        header = QHBoxLayout()
        version_label = QLabel(f"v{version}")
        version_label.setStyleSheet(
            "font-size: 11px; font-weight: 600; color: #4F46E5;"
        )
        header.addWidget(version_label)

        date_label = QLabel(data.get("日期", ""))
        date_label.setStyleSheet("font-size: 10px; color: #9CA3AF;")
        header.addWidget(date_label)
        header.addStretch()
        layout.addLayout(header)

        # 更新内容（简化显示）
        changes = data.get("更新内容", [])
        if changes:
            changes_text = " · ".join(changes[:3])  # 最多显示3项
            if len(changes) > 3:
                changes_text += f" 等 {len(changes)} 项"
            changes_label = QLabel(changes_text)
            changes_label.setStyleSheet("font-size: 10px; color: #6B7280;")
            changes_label.setWordWrap(True)
            layout.addWidget(changes_label)

        return widget

    def _create_features_section(self) -> QWidget:
        """创建功能特性区域（使用可折叠卡片）"""
        card = CollapsibleCard(
            title="功能特性",
            icon="✨",
            subtitle="",
            collapsed_by_default=False,
            card_id="about_features",
        )
        # 添加折叠时显示的标签
        card.add_collapsed_tag(text="6 项核心功能", tag_type="success")

        content_layout = card.get_content_layout()

        # 特性网格
        features_grid = QGridLayout()
        features_grid.setHorizontalSpacing(16)
        features_grid.setVerticalSpacing(12)

        features = [
            ("🎬", "多平台支持", "抖音、TikTok、微博、Twitter/X"),
            ("📥", "批量下载", "支持用户主页、收藏、喜欢等批量下载"),
            ("⚡", "高速下载", "多线程并发，快速高效"),
            ("🔄", "增量更新", "智能跳过已下载内容"),
            ("📁", "灵活命名", "自定义文件命名模板"),
            ("🕐", "时间筛选", "按日期范围筛选下载内容"),
        ]

        for i, (icon, title, desc) in enumerate(features):
            row, col = divmod(i, 2)
            feature_widget = self._create_feature_item(icon, title, desc)
            features_grid.addWidget(feature_widget, row, col)

        content_layout.addLayout(features_grid)
        return card

    def _create_feature_item(self, icon: str, title: str, desc: str) -> QWidget:
        """创建单个特性项"""
        widget = QFrame()
        widget.setObjectName("featureItem")
        widget.setStyleSheet(
            """
            QFrame#featureItem {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 rgba(99, 102, 241, 0.05),
                    stop:1 rgba(139, 92, 246, 0.05));
                border: 1px solid rgba(99, 102, 241, 0.1);
                border-radius: 8px;
            }
            QFrame#featureItem:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 rgba(99, 102, 241, 0.1),
                    stop:1 rgba(139, 92, 246, 0.1));
                border-color: rgba(139, 92, 246, 0.2);
            }
        """
        )

        layout = QHBoxLayout(widget)
        layout.setContentsMargins(10, 8, 10, 8)
        layout.setSpacing(10)

        # 图标
        icon_label = QLabel(icon)
        icon_font = icon_label.font()
        icon_font.setPointSize(18)
        icon_label.setFont(icon_font)
        icon_label.setFixedWidth(30)
        layout.addWidget(icon_label)

        # 文字区域
        text_layout = QVBoxLayout()
        text_layout.setSpacing(2)

        title_label = QLabel(title)
        title_font = title_label.font()
        title_font.setWeight(QFont.Weight.DemiBold)
        title_label.setFont(title_font)
        text_layout.addWidget(title_label)

        desc_label = QLabel(desc)
        desc_label.setObjectName("subtitle")
        desc_font = desc_label.font()
        desc_font.setPointSize(9)
        desc_label.setFont(desc_font)
        text_layout.addWidget(desc_label)

        layout.addLayout(text_layout, 1)

        return widget

    def _create_links_section(self) -> QWidget:
        """创建链接区域（使用可折叠卡片）"""
        card = CollapsibleCard(
            title="相关链接",
            icon="🔗",
            subtitle="",
            collapsed_by_default=False,
            card_id="about_links",
        )
        # 添加折叠时显示的标签
        card.add_collapsed_tag(text="文档、源码、反馈", tag_type="neutral")

        content_layout = card.get_content_layout()

        links = [
            ("📚", "官方文档", "https://f2.wiki/", "查看完整使用文档"),
            (
                "💻",
                "GitHub 仓库",
                "https://github.com/Johnserf-Seed/f2",
                "查看源代码和贡献",
            ),
            (
                "🐛",
                "问题反馈",
                "https://github.com/Johnserf-Seed/f2/issues",
                "提交 Bug 或建议",
            ),
            (
                "💬",
                "讨论区",
                "https://github.com/Johnserf-Seed/f2/discussions",
                "参与社区讨论",
            ),
        ]

        for icon, title, url, desc in links:
            link_widget = self._create_link_item(icon, title, url, desc)
            content_layout.addWidget(link_widget)

        return card

    def _create_link_item(self, icon: str, title: str, url: str, desc: str) -> QWidget:
        """创建单个链接项"""
        widget = QFrame()
        widget.setStyleSheet(
            """
            QFrame {
                background: transparent;
            }
            QFrame:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 rgba(99, 102, 241, 0.08),
                    stop:1 rgba(139, 92, 246, 0.08));
                border-radius: 6px;
            }
        """
        )
        widget.setCursor(Qt.CursorShape.PointingHandCursor)

        layout = QHBoxLayout(widget)
        layout.setContentsMargins(6, 6, 6, 6)
        layout.setSpacing(10)

        # 图标
        icon_label = QLabel(icon)
        icon_font = icon_label.font()
        icon_font.setPointSize(14)
        icon_label.setFont(icon_font)
        icon_label.setFixedWidth(28)
        layout.addWidget(icon_label)

        # 文字区域
        text_layout = QVBoxLayout()
        text_layout.setSpacing(0)

        title_label = QLabel(title)
        title_font = title_label.font()
        title_font.setWeight(QFont.Weight.Medium)
        title_font.setPointSize(10)
        title_label.setFont(title_font)
        text_layout.addWidget(title_label)

        desc_label = QLabel(desc)
        desc_label.setObjectName("subtitle")
        desc_font = desc_label.font()
        desc_font.setPointSize(9)
        desc_label.setFont(desc_font)
        text_layout.addWidget(desc_label)

        layout.addLayout(text_layout, 1)

        # 箭头
        arrow_label = QLabel("→")
        arrow_label.setObjectName("subtitle")
        layout.addWidget(arrow_label)

        # 点击事件 - 使用闭包避免返回值问题
        def make_click_handler(target_url):
            def handler(event):
                QDesktopServices.openUrl(QUrl(target_url))

            return handler

        widget.mousePressEvent = make_click_handler(url)

        return widget

    def _create_tech_section(self) -> QWidget:
        """创建技术栈区域（使用可折叠卡片）"""
        card = CollapsibleCard(
            title="技术栈",
            icon="🛠️",
            subtitle="",
            collapsed_by_default=False,
            card_id="about_tech",
        )
        # 添加折叠时显示的标签
        card.add_collapsed_tag(text="Python + PyQt6", tag_type="info")

        content_layout = card.get_content_layout()

        techs = [
            ("🐍", "Python 3.10+", "核心语言"),
            ("🖼️", "PyQt6", "图形界面"),
            ("⚡", "asyncio", "异步编程"),
            ("🌐", "httpx", "网络请求"),
        ]

        for icon, name, desc in techs:
            tech_widget = self._create_tech_item(icon, name, desc)
            content_layout.addWidget(tech_widget)

        return card

    def _create_tech_item(self, icon: str, name: str, desc: str) -> QWidget:
        """创建单个技术项"""
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(6, 4, 6, 4)
        layout.setSpacing(8)

        # 图标
        icon_label = QLabel(icon)
        icon_font = icon_label.font()
        icon_font.setPointSize(12)
        icon_label.setFont(icon_font)
        icon_label.setFixedWidth(20)
        layout.addWidget(icon_label)

        # 名称
        name_label = QLabel(name)
        name_font = name_label.font()
        name_font.setWeight(QFont.Weight.Medium)
        name_font.setPointSize(10)
        name_label.setFont(name_font)
        layout.addWidget(name_label)

        layout.addStretch()

        # 描述
        desc_label = QLabel(desc)
        desc_label.setObjectName("subtitle")
        desc_font = desc_label.font()
        desc_font.setPointSize(9)
        desc_label.setFont(desc_font)
        layout.addWidget(desc_label)

        return widget

    def _create_license_section(self) -> QWidget:
        """创建开源协议和致谢区域（使用可折叠卡片）"""
        card = CollapsibleCard(
            title="开源协议",
            icon="📜",
            subtitle="",
            collapsed_by_default=False,
            card_id="about_license",
        )
        # 添加折叠时显示的标签
        card.add_collapsed_tag(text="Apache 2.0", tag_type="warning")

        content_layout = card.get_content_layout()

        # 协议信息
        license_text = QLabel(
            "F2 基于 Apache License 2.0 开源协议发布。\n"
            "您可以自由使用、修改和分发本软件，但需保留版权声明。"
        )
        license_text.setWordWrap(True)
        license_text.setObjectName("subtitle")
        content_layout.addWidget(license_text)

        # 分隔线
        separator = QFrame()
        separator.setObjectName("separator")
        separator.setFixedHeight(1)
        content_layout.addWidget(separator)

        # 致谢
        thanks_title = QLabel("🙏 致谢")
        thanks_title.setObjectName("sectionTitle")
        content_layout.addWidget(thanks_title)

        thanks_text = QLabel(
            "感谢所有贡献者和用户的支持！\n" "特别感谢开源社区提供的优秀工具和库。"
        )
        thanks_text.setWordWrap(True)
        thanks_text.setObjectName("subtitle")
        content_layout.addWidget(thanks_text)

        # 作者信息
        author_widget = QWidget()
        author_layout = QHBoxLayout(author_widget)
        author_layout.setContentsMargins(0, 8, 0, 0)
        author_layout.setSpacing(8)

        author_label = QLabel("👨‍💻 作者:")
        author_layout.addWidget(author_label)

        author_name = QLabel("Johnserf-Seed")
        author_name.setStyleSheet(
            """
            QLabel {
                color: #4F46E5;
                font-weight: 500;
            }
            QLabel:hover {
                text-decoration: underline;
            }
        """
        )
        author_name.setCursor(Qt.CursorShape.PointingHandCursor)

        def open_author_page(event):
            QDesktopServices.openUrl(QUrl("https://github.com/Johnserf-Seed"))

        author_name.mousePressEvent = open_author_page
        author_layout.addWidget(author_name)

        author_layout.addStretch()

        # 版权年份
        copyright_label = QLabel("© 2023-2025 F2 Project")
        copyright_label.setObjectName("subtitle")
        author_layout.addWidget(copyright_label)

        content_layout.addWidget(author_widget)

        return card
