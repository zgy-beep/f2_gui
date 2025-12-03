"""
主窗口
~~~~~

应用程序的主窗口,包含导航栏和内容区域。
支持自动保存配置。
"""

import uuid

from PyQt6.QtCore import Qt, QThread
from PyQt6.QtGui import QCloseEvent, QFont, QIcon, QPixmap
from PyQt6.QtWidgets import (
    QApplication,
    QFrame,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QPushButton,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from f2.gui.components.download_task_card import DownloadTaskCard
from f2.gui.components.tooltip import install_tooltip, show_click_tooltip
from f2.gui.config import (
    APP_NAME,
    APP_VERSION,
    ASSETS_DIR,
    DEFAULT_WINDOW_HEIGHT,
    DEFAULT_WINDOW_WIDTH,
    MIN_WINDOW_HEIGHT,
    MIN_WINDOW_WIDTH,
    MODE_NAMES,
    PLATFORM_CONFIG,
)
from f2.gui.controllers.download_controller import DownloadController, UrlParseWorker
from f2.gui.themes import ThemeManager, get_theme_manager
from f2.gui.utils.config_manager import ConfigManager
from f2.gui.utils.history_manager import history_manager
from f2.gui.views.about_page import AboutPage
from f2.gui.views.history_page import HistoryPage
from f2.gui.views.home_page import HomePage
from f2.gui.views.settings_page import SettingsPage
from f2.log.logger import logger


class MainWindow(QMainWindow):
    """主窗口"""

    def __init__(self):
        super().__init__()
        self.nav_buttons = []
        self.theme_btn = None
        self.page_title_label = None
        self._first_show = True  # 标记是否首次显示

        # 配置管理器
        self.config_manager = ConfigManager()

        # 下载控制器
        self.download_controller = DownloadController()

        # 任务跟踪
        self._task_cards = {}  # task_id -> DownloadTaskCard

        # 预解析任务跟踪
        self._parse_workers = {}  # 用于跟踪解析工作器和线程

        self._setup_window()
        self._create_ui()
        self._connect_signals()
        self._load_config()

    def _setup_window(self):
        """设置窗口属性"""
        self.setWindowTitle(f"{APP_NAME} v{APP_VERSION}")
        self.resize(DEFAULT_WINDOW_WIDTH, DEFAULT_WINDOW_HEIGHT)
        self.setMinimumSize(MIN_WINDOW_WIDTH, MIN_WINDOW_HEIGHT)

        # 设置窗口图标
        icon_path = ASSETS_DIR / "public" / "f2-logo.ico"
        if icon_path.exists():
            self.setWindowIcon(QIcon(str(icon_path)))

    def _create_ui(self):
        """创建UI"""
        # 中心部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # 主布局
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # 创建侧边栏
        self.sidebar = self._create_sidebar()
        main_layout.addWidget(self.sidebar)

        # 创建内容区域
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)

        # 顶部栏
        self.top_bar = self._create_top_bar()
        content_layout.addWidget(self.top_bar)

        # 页面堆栈
        self.page_stack = QStackedWidget()

        # 添加页面
        self.home_page = HomePage()
        self.history_page = HistoryPage()
        self.settings_page = SettingsPage()
        self.about_page = AboutPage()

        self.page_stack.addWidget(self.home_page)
        self.page_stack.addWidget(self.history_page)
        self.page_stack.addWidget(self.settings_page)
        self.page_stack.addWidget(self.about_page)

        content_layout.addWidget(self.page_stack)

        main_layout.addWidget(content_widget, 1)

    def _create_sidebar(self) -> QWidget:
        """创建侧边栏 - 卡片式精致设计"""
        sidebar = QFrame()
        sidebar.setObjectName("sidebar")
        sidebar.setFixedWidth(180)

        layout = QVBoxLayout(sidebar)
        layout.setContentsMargins(12, 14, 12, 14)
        layout.setSpacing(6)

        # ===== 应用Logo和标题卡片 =====
        app_header = QFrame()
        app_header.setObjectName("sidebarHeaderCard")
        app_header_layout = QHBoxLayout(app_header)
        app_header_layout.setContentsMargins(12, 10, 12, 10)
        app_header_layout.setSpacing(10)

        # Logo 图标 - 使用真实图片
        logo_label = QLabel()
        logo_path = ASSETS_DIR / "public" / "f2-logo-with-shadow-mini.png"
        if logo_path.exists():
            pixmap = QPixmap(str(logo_path))
            scaled_pixmap = pixmap.scaled(
                32,
                32,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )
            logo_label.setPixmap(scaled_pixmap)
        else:
            logo_label.setText("📦")
            logo_font = logo_label.font()
            logo_font.setPointSize(16)
            logo_label.setFont(logo_font)
        logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        logo_label.setFixedSize(36, 36)
        app_header_layout.addWidget(logo_label)

        # 标题区
        title_area = QVBoxLayout()
        title_area.setSpacing(2)

        app_title = QLabel("F2")
        app_title.setObjectName("sidebarTitle")
        app_title_font = app_title.font()
        app_title_font.setPointSize(15)
        app_title_font.setWeight(QFont.Weight.Bold)
        app_title.setFont(app_title_font)
        title_area.addWidget(app_title)

        app_subtitle = QLabel("媒体下载工具")
        app_subtitle.setObjectName("sidebarSubtitle")
        subtitle_font = app_subtitle.font()
        subtitle_font.setPointSize(9)
        app_subtitle.setFont(subtitle_font)
        title_area.addWidget(app_subtitle)

        app_header_layout.addLayout(title_area)
        app_header_layout.addStretch()

        layout.addWidget(app_header)

        layout.addSpacing(8)

        # ===== 导航区域 =====
        nav_section = QFrame()
        nav_section.setObjectName("navSection")
        nav_layout = QVBoxLayout(nav_section)
        nav_layout.setContentsMargins(8, 8, 8, 8)
        nav_layout.setSpacing(4)

        # 导航标签 - 简洁风格
        nav_label = QLabel("导航菜单")
        nav_label.setObjectName("sidebarSectionLabel")
        nav_label_font = nav_label.font()
        nav_label_font.setPointSize(9)
        nav_label_font.setWeight(QFont.Weight.Medium)
        nav_label.setFont(nav_label_font)
        nav_layout.addWidget(nav_label)

        nav_layout.addSpacing(4)

        # 导航按钮
        nav_items = [
            ("🏠", "首页", 0),
            ("📜", "历史", 1),
            ("⚙️", "设置", 2),
            ("ℹ️", "关于", 3),
        ]

        for icon, text, index in nav_items:
            btn = self._create_nav_button(icon, text, index)
            self.nav_buttons.append(btn)
            nav_layout.addWidget(btn)

        layout.addWidget(nav_section)
        layout.addStretch()

        # ===== 底部区域 =====
        bottom_widget = QFrame()
        bottom_widget.setObjectName("sidebarBottomCard")
        bottom_layout = QVBoxLayout(bottom_widget)
        bottom_layout.setContentsMargins(8, 10, 8, 10)
        bottom_layout.setSpacing(8)

        # 主题切换按钮
        self.theme_btn = QPushButton("☀️ 浅色模式")
        self.theme_btn.setObjectName("themeToggleButton")
        self.theme_btn.setFixedHeight(34)
        self.theme_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        install_tooltip(self.theme_btn, "切换深色/浅色主题")
        self.theme_btn.clicked.connect(self._toggle_theme)
        bottom_layout.addWidget(self.theme_btn)

        # 版本信息 - 卡片式标签
        version_container = QFrame()
        version_container.setObjectName("versionBadge")
        version_layout = QHBoxLayout(version_container)
        version_layout.setContentsMargins(8, 4, 8, 4)
        version_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        version_icon = QLabel("🏷️")
        version_icon.setObjectName("versionIcon")
        version_layout.addWidget(version_icon)

        version_label = QLabel(f"v{APP_VERSION}")
        version_label.setObjectName("versionText")
        version_font = version_label.font()
        version_font.setPointSize(9)
        version_font.setWeight(QFont.Weight.Medium)
        version_label.setFont(version_font)
        version_layout.addWidget(version_label)

        bottom_layout.addWidget(version_container)

        layout.addWidget(bottom_widget)

        # 高亮第一个按钮
        self._highlight_nav_button(0)

        return sidebar

    def _create_nav_button(self, icon: str, text: str, page_index: int) -> QPushButton:
        """创建导航按钮 - 卡片式风格"""
        button = QPushButton(f"{icon}  {text}")
        button.setObjectName("navButton")
        button.setFixedHeight(36)
        button.setCheckable(True)
        button.setCursor(Qt.CursorShape.PointingHandCursor)
        button.clicked.connect(lambda: self._switch_page(page_index))
        return button

    def _create_top_bar(self) -> QWidget:
        """创建顶部栏 - 极简精致"""
        top_bar = QFrame()
        top_bar.setObjectName("topBar")
        top_bar.setFixedHeight(48)

        layout = QHBoxLayout(top_bar)
        layout.setContentsMargins(20, 0, 20, 0)

        # 页面标题
        self.page_title_label = QLabel("首页")
        self.page_title_label.setObjectName("pageTitle")
        title_font = self.page_title_label.font()
        title_font.setPointSize(16)
        title_font.setWeight(QFont.Weight.DemiBold)
        self.page_title_label.setFont(title_font)

        layout.addWidget(self.page_title_label)
        layout.addStretch()

        return top_bar

    def _switch_page(self, index: int):
        """切换页面"""
        self.page_stack.setCurrentIndex(index)

        # 更新标题
        titles = ["首页", "历史记录", "设置", "关于"]
        if 0 <= index < len(titles):
            self.page_title_label.setText(titles[index])

        # 更新导航按钮高亮
        self._highlight_nav_button(index)

    def _highlight_nav_button(self, index: int):
        """高亮导航按钮"""
        for i, btn in enumerate(self.nav_buttons):
            btn.setChecked(i == index)

    def _toggle_theme(self):
        """切换主题"""
        from PyQt6.QtWidgets import QApplication

        tm = get_theme_manager()
        new_theme = tm.toggle_theme()
        app = QApplication.instance()
        if app:
            tm.apply_to_app(app)

        # 更新主题按钮文本
        if tm.is_dark_mode:
            self.theme_btn.setText("☀️ 浅色模式")
            show_click_tooltip(self, "已切换到深色模式", "🌙")
        else:
            self.theme_btn.setText("🌙 深色模式")
            show_click_tooltip(self, "已切换到浅色模式", "☀️")

    def _connect_signals(self):
        """连接信号"""
        # 监听主题变化
        get_theme_manager().theme_changed.connect(self._on_theme_changed)

        # 监听设置变化并自动保存
        self.settings_page.settings_changed.connect(self._on_settings_changed)

        # 连接添加队列信号（新）
        self.home_page.add_to_queue.connect(self._on_add_to_queue)
        self.home_page.start_all_downloads.connect(self._on_start_all_downloads)

        # 连接下载信号（兼容旧接口）
        self.home_page.start_download.connect(self._on_start_download)
        self.home_page.batch_download.connect(self._on_batch_download)

        # 连接下载控制器信号
        self.download_controller.task_progress.connect(self._on_task_progress)
        self.download_controller.task_status_changed.connect(
            self._on_task_status_changed
        )
        self.download_controller.task_message.connect(self._on_task_message)
        self.download_controller.task_finished.connect(self._on_task_finished)
        self.download_controller.task_error.connect(self._on_task_error)
        self.download_controller.task_title_changed.connect(self._on_task_title_changed)
        self.download_controller.task_user_info_changed.connect(
            self._on_task_user_info_changed
        )
        self.download_controller.task_url_parsed.connect(self._on_task_url_parsed)
        self.download_controller.task_completed.connect(self._on_task_completed)

        # 连接历史记录页面信号
        self.history_page.add_to_download_queue.connect(self._on_add_from_history)

    def _on_add_to_queue(self, platform: str, mode: str, urls: list):
        """添加到下载队列（不立即下载）"""
        for url in urls:
            self._add_task_to_queue(platform, mode, url)

    def _on_start_all_downloads(self):
        """开始下载所有待下载任务"""
        for task_id, card in self._task_cards.items():
            if card.status == "pending":
                self._start_single_task(task_id)

    def _on_start_download(self, platform: str, mode: str, urls: list):
        """开始单个/多个下载（兼容旧接口）"""
        for url in urls:
            self._create_download_task(platform, mode, url)

    def _on_batch_download(self, platform: str, mode: str, urls: list):
        """批量下载（兼容旧接口）"""
        for url in urls:
            self._create_download_task(platform, mode, url)

    def _add_task_to_queue(self, platform: str, mode: str, url: str):
        """添加任务到队列（先解析信息再添加）"""
        task_id = str(uuid.uuid4())[:8]

        # 获取完整的配置（包含所有设置项）
        config = self._get_full_config()

        # 创建解析工作器
        worker = UrlParseWorker(platform, url, config)
        thread = QThread()
        worker.moveToThread(thread)

        # 连接信号
        thread.started.connect(worker.parse)
        worker.finished.connect(
            lambda parsed_url, nickname, user_id, error: self._on_parse_finished(
                task_id,
                platform,
                mode,
                url,
                parsed_url,
                nickname,
                user_id,
                error,
                config,
            )
        )
        worker.finished.connect(thread.quit)
        worker.finished.connect(worker.deleteLater)
        thread.finished.connect(thread.deleteLater)
        thread.finished.connect(lambda: self._cleanup_parse_worker(task_id))

        # 保存引用防止被垃圾回收
        self._parse_workers[task_id] = {"worker": worker, "thread": thread}

        # 开始解析
        thread.start()

    def _get_full_config(self) -> dict:
        """获取完整的配置信息"""
        config = self.config_manager.get_all()
        return {
            "download": config.get("download", {}),
            "cookies": config.get("cookies", {}),
            "proxy": config.get("proxy", {}),
            "time_filter": config.get("time_filter", {}),
            "advanced": config.get("advanced", {}),
        }

    def _on_parse_finished(
        self,
        task_id: str,
        platform: str,
        mode: str,
        original_url: str,
        parsed_url: str,
        nickname: str,
        user_id: str,
        error: str,
        config: dict,
    ):
        """URL解析完成回调 - 创建任务卡片"""
        # 获取平台和模式的显示名称
        platform_name = PLATFORM_CONFIG.get(platform, {}).get("name", platform.upper())
        mode_name = MODE_NAMES.get(mode, mode)

        # 创建任务卡片 - 使用解析后的信息
        task_card = DownloadTaskCard(
            task_id=task_id,
            title=f"{platform_name} - {mode_name}",
            platform=platform,
            mode=mode,
            url=parsed_url if parsed_url else original_url,
            nickname=nickname,
            user_id=user_id,
        )
        task_card.start_clicked.connect(
            lambda tid=task_id: self._start_single_task(tid)
        )
        task_card.pause_clicked.connect(lambda tid=task_id: self._on_task_pause(tid))
        task_card.resume_clicked.connect(lambda tid=task_id: self._on_task_resume(tid))
        task_card.cancel_clicked.connect(lambda tid=task_id: self._on_task_cancel(tid))

        # 添加到首页
        self.home_page.add_task_card(task_card)
        self._task_cards[task_id] = task_card

        # 保存任务元数据 (用于历史记录和后续下载)
        task_card.task_meta = {
            "platform": platform,
            "mode": mode,
            "url": parsed_url if parsed_url else original_url,
            "original_url": original_url,
            "config": config,
            "history_id": None,
            "nickname": nickname,
            "user_id": user_id,
        }

        # 设置状态为等待中
        task_card.set_status("pending")

        # 如果有错误，显示警告
        if error:
            print(f"⚠️ 解析警告 [{task_id}]: {error}")

        # 更新统计
        self._update_stats()

    def _cleanup_parse_worker(self, task_id: str):
        """清理解析工作器"""
        if task_id in self._parse_workers:
            del self._parse_workers[task_id]

    def _start_single_task(self, task_id: str):
        """开始单个任务下载"""
        if task_id not in self._task_cards:
            return

        card = self._task_cards[task_id]
        if card.status != "pending":
            return

        meta = getattr(card, "task_meta", {})
        platform = meta.get("platform", "douyin")
        mode = meta.get("mode", "one")
        url = meta.get("url", "")
        config = meta.get("config", {})

        # 开始下载
        self.download_controller.start_download(task_id, platform, mode, url, config)

        # 更新统计
        self._update_stats()

    def _create_download_task(self, platform: str, mode: str, url: str):
        """创建下载任务（立即开始下载 - 兼容旧接口）"""
        task_id = str(uuid.uuid4())[:8]

        # 获取完整的配置（包含所有设置项）
        config = self._get_full_config()

        # 获取平台和模式的显示名称
        platform_name = PLATFORM_CONFIG.get(platform, {}).get("name", platform.upper())
        mode_name = MODE_NAMES.get(mode, mode)

        # 创建任务卡片 - 使用新的参数
        task_card = DownloadTaskCard(
            task_id=task_id,
            title=f"{platform_name} - {mode_name}",
            platform=platform,
            mode=mode,
            url=url,
        )
        task_card.start_clicked.connect(
            lambda tid=task_id: self._start_single_task(tid)
        )
        task_card.pause_clicked.connect(lambda tid=task_id: self._on_task_pause(tid))
        task_card.resume_clicked.connect(lambda tid=task_id: self._on_task_resume(tid))
        task_card.cancel_clicked.connect(lambda tid=task_id: self._on_task_cancel(tid))

        # 添加到首页
        self.home_page.add_task_card(task_card)
        self._task_cards[task_id] = task_card

        # 保存任务元数据 (用于历史记录)
        task_card.task_meta = {
            "platform": platform,
            "mode": mode,
            "url": url,
            "config": config,
            "history_id": None,
        }

        # 开始下载
        self.download_controller.start_download(task_id, platform, mode, url, config)

        # 更新统计
        self._update_stats()

    def _on_task_pause(self, task_id: str):
        """暂停任务"""
        self.download_controller.pause_download(task_id)

    def _on_task_resume(self, task_id: str):
        """继续任务"""
        self.download_controller.resume_download(task_id)

    def _on_task_cancel(self, task_id: str):
        """取消任务"""
        self.download_controller.cancel_download(task_id)
        if task_id in self._task_cards:
            card = self._task_cards.pop(task_id)
            card.deleteLater()
        self._update_stats()

    def _on_task_progress(self, task_id: str, current: int, total: int):
        """任务进度更新"""
        if task_id in self._task_cards:
            progress = int((current / total) * 100) if total > 0 else 0
            card = self._task_cards[task_id]
            card.set_progress(progress)
            # 强制刷新 UI
            card.progress_bar.repaint()

    def _on_task_status_changed(self, task_id: str, status: str):
        """任务状态变化"""
        if task_id in self._task_cards:
            card = self._task_cards[task_id]
            card.set_status(status)

            # 任务完成或失败时，移动到已完成区域
            if status in ["completed", "failed", "error"]:
                self.home_page.move_to_completed(card)

        self._update_stats()

    def _on_task_message(self, task_id: str, message: str):
        """任务消息"""
        # 在控制台显示消息（带任务ID前缀便于区分）
        logger.info(f"[{task_id[:8]}] {message}")

    def _on_task_title_changed(self, task_id: str, title: str):
        """任务标题更新 - 显示用户名"""
        if task_id in self._task_cards:
            self._task_cards[task_id].set_title(title)

    def _on_task_user_info_changed(self, task_id: str, nickname: str, user_id: str):
        """用户信息更新 - 更新任务卡片的用户名和ID"""
        if task_id in self._task_cards:
            self._task_cards[task_id].set_user_info(nickname, user_id)

    def _on_task_url_parsed(self, task_id: str, parsed_url: str):
        """URL解析完成 - 更新任务卡片显示解析后的URL"""
        if task_id in self._task_cards:
            self._task_cards[task_id].set_url(parsed_url)

    def _on_task_completed(self, task_id: str, nickname: str):
        """任务完成 - 带用户名的完成通知"""
        display_name = nickname if nickname else task_id[:8]
        print(f"✅ 任务完成: {display_name}")

        # 保存到历史记录
        if task_id in self._task_cards:
            card = self._task_cards[task_id]
            meta = getattr(card, "task_meta", {})

            # 使用解析后的 URL，不是原始分享文本
            parsed_url = meta.get("url", "") or meta.get("original_url", "")

            history_manager.add_record(
                platform=meta.get("platform", "douyin"),
                url=parsed_url,
                download_type="视频",
                status="成功",
                file_count=0,
                mode=meta.get("mode", "one"),
                nickname=nickname or display_name,
                user_id=meta.get("user_id", ""),
            )

            # 刷新历史页面
            self.history_page.refresh()

    def _on_task_finished(self, task_id: str):
        """任务完成"""
        # 状态已经由 task_status_changed 处理
        self._update_stats()

    def _on_task_error(self, task_id: str, error: str):
        """任务出错"""
        # 尝试获取任务卡片的标题
        display_name = task_id[:8]
        nickname = ""
        if task_id in self._task_cards:
            card = self._task_cards[task_id]
            if hasattr(card, "get_title"):
                title = card.get_title()
            else:
                title = getattr(card, "_title", "")
            if title and not title.startswith(task_id[:8]):
                display_name = title
                nickname = title

            # 保存失败记录到历史
            meta = getattr(card, "task_meta", {})

            # 使用解析后的 URL
            parsed_url = meta.get("url", "") or meta.get("original_url", "")

            history_manager.add_record(
                platform=meta.get("platform", "douyin"),
                url=parsed_url,
                download_type="视频",
                status="失败",
                file_count=0,
                mode=meta.get("mode", "one"),
                nickname=nickname,
                user_id=meta.get("user_id", ""),
                error=error,
            )

            # 刷新历史页面
            self.history_page.refresh()

        print(f"❌ 任务出错: {display_name} - {error}")
        self._update_stats()

    def _on_add_from_history(self, platform: str, mode: str, url: str):
        """从历史记录添加到下载队列（不立即下载）"""
        self._add_task_to_queue(platform, mode, url)
        # 切换到首页
        self._switch_page(0)

    def _update_stats(self):
        """更新统计信息"""
        total = len(self._task_cards)
        pending = sum(
            1 for card in self._task_cards.values() if card.status == "pending"
        )
        downloading = sum(
            1 for card in self._task_cards.values() if card.status == "downloading"
        )
        completed = sum(
            1 for card in self._task_cards.values() if card.status == "completed"
        )
        failed = sum(1 for card in self._task_cards.values() if card.status == "failed")
        # 等待中的任务显示在下载中（合并显示）
        self.home_page.update_stats(total, downloading + pending, completed, failed)

    def _on_theme_changed(self, theme: str):
        """主题变化回调"""
        # 保存主题设置
        self.config_manager.set("theme", theme)
        self.config_manager.save()

    def _on_settings_changed(self, settings: dict):
        """设置变化回调 - 自动保存"""
        # 创建配置副本，避免修改原始数据
        settings_to_save = settings.copy()

        # 单独保存 cookies 到 secrets 文件
        if "cookies" in settings_to_save:
            cookies = settings_to_save.pop("cookies")
            self.config_manager.save_secrets(cookies)

        self.config_manager.update(settings_to_save)
        self.config_manager.save()

    def _load_config(self):
        """加载配置"""
        config = self.config_manager.get_all()

        # 窗口位置将在 showEvent 中恢复，这里只做基本设置
        window_config = config.get("window", {})
        if not window_config.get("maximized"):
            width = window_config.get("width", DEFAULT_WINDOW_WIDTH)
            height = window_config.get("height", DEFAULT_WINDOW_HEIGHT)
            self.resize(width, height)

        # 加载主题
        theme = config.get("theme", "light")
        tm = get_theme_manager()
        if theme == "dark":
            tm.set_theme("dark")
            app = QApplication.instance()
            if app:
                tm.apply_to_app(app)
            self.theme_btn.setText("☀️ 浅色模式")
        else:
            # 确保设置为 light 主题
            tm.set_theme("light")
            app = QApplication.instance()
            if app:
                tm.apply_to_app(app)
            self.theme_btn.setText("🌙 深色模式")

        # 加载设置页面配置
        self.settings_page.load_settings(config)

    def showEvent(self, event):
        """窗口显示事件 - 首次显示时恢复窗口位置"""
        super().showEvent(event)
        if self._first_show:
            self._first_show = False
            # 在窗口首次显示后重新应用位置
            self._restore_window_geometry()

    def _restore_window_geometry(self):
        """恢复窗口位置和大小"""
        window_config = self.config_manager.get("window") or {}

        if window_config.get("maximized"):
            self.showMaximized()
            return

        # 恢复窗口大小
        width = window_config.get("width", DEFAULT_WINDOW_WIDTH)
        height = window_config.get("height", DEFAULT_WINDOW_HEIGHT)
        self.resize(width, height)

        # 恢复窗口位置
        x = window_config.get("x")
        y = window_config.get("y")
        if x is not None and y is not None:
            # 获取所有屏幕的虚拟桌面范围（支持多显示器）
            screen = QApplication.primaryScreen()
            if screen:
                # 使用虚拟桌面几何，支持多显示器
                virtual_geo = screen.virtualGeometry()
                # 确保窗口位置在虚拟桌面范围内
                x = max(virtual_geo.x(), min(x, virtual_geo.right() - 100))
                y = max(virtual_geo.y(), min(y, virtual_geo.bottom() - 100))
            self.move(x, y)

    def closeEvent(self, event):
        """窗口关闭事件 - 保存配置"""
        # 保存窗口状态
        self.config_manager.set("window.width", self.width())
        self.config_manager.set("window.height", self.height())
        self.config_manager.set("window.maximized", self.isMaximized())

        # 保存窗口位置
        if not self.isMaximized():
            pos = self.pos()
            self.config_manager.set("window.x", pos.x())
            self.config_manager.set("window.y", pos.y())

        self.config_manager.save()

        event.accept()
