"""
下载控制器
~~~~~~~~~

管理下载任务的控制器，支持多平台下载。
采用 QThread + asyncio 模式处理异步下载任务。
"""

import asyncio
import sys
import traceback
from pathlib import Path
from typing import Any, Dict, List, Optional

from PyQt6.QtCore import QObject, QThread, pyqtSignal, pyqtSlot

import f2
from f2.log.logger import logger
from f2.utils.conf_manager import ConfigManager
from f2.utils.utils import merge_config


def get_platform_config(platform: str) -> Dict[str, Any]:
    """
    获取平台配置，合并 app.yaml 中的配置

    Args:
        platform: 平台名称 (douyin, tiktok, weibo, twitter)

    Returns:
        Dict: 合并后的配置
    """
    try:
        # 读取 F2 主配置文件
        main_manager = ConfigManager(f2.APP_CONFIG_FILE_PATH)
        main_conf = main_manager.get_config(platform)
        return main_conf if main_conf else {}
    except Exception as e:
        logger.warning(f"无法读取 {platform} 配置: {e}")
        return {}


class UrlParseWorker(QObject):
    """URL预解析工作器 - 在独立线程中解析URL和获取用户ID（不调用API）"""

    # 信号
    finished = pyqtSignal(str, str, str, str)  # parsed_url, nickname, user_id, error

    def __init__(self, platform: str, url: str, config: Dict[str, Any]):
        super().__init__()
        self.platform = platform
        self.url = url
        self.config = config
        self.loop = None

    @pyqtSlot()
    def parse(self):
        """开始解析"""
        try:
            self.loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self.loop)
            self.loop.run_until_complete(self._do_parse())
        except Exception as e:
            logger.error(f"URL解析失败: {e}")
            self.finished.emit(self.url, "", "", str(e))
        finally:
            if self.loop:
                self.loop.close()

    async def _do_parse(self):
        """执行解析 - 提取URL和用户ID，尝试从本地数据库获取昵称"""
        parsed_url = self.url
        nickname = ""
        user_id = ""

        try:
            if self.platform == "douyin":
                from f2.apps.douyin.db import AsyncUserDB
                from f2.apps.douyin.utils import SecUserIdFetcher
                from f2.utils.utils import extract_valid_urls

                # 提取有效URL
                valid_url = extract_valid_urls(self.url)
                if valid_url:
                    parsed_url = valid_url

                # 获取用户ID
                try:
                    sec_user_id = await SecUserIdFetcher.get_sec_user_id(parsed_url)
                    if sec_user_id:
                        user_id = sec_user_id

                        # 尝试从本地数据库获取用户昵称（不触发网络请求）
                        try:
                            async with AsyncUserDB("douyin_users.db") as db:
                                user_info = await db.get_user_info(sec_user_id)
                                if user_info:
                                    nickname = user_info.get("nickname", "")
                        except Exception:
                            pass  # 数据库查询失败不影响流程

                except Exception as e:
                    logger.warning(f"获取用户ID失败: {e}")

            elif self.platform == "tiktok":
                from f2.utils.utils import extract_valid_urls

                valid_url = extract_valid_urls(self.url)
                if valid_url:
                    parsed_url = valid_url

                # TikTok 暂不解析用户ID

            # 其他平台只提取URL
            else:
                from f2.utils.utils import extract_valid_urls

                valid_url = extract_valid_urls(self.url)
                if valid_url:
                    parsed_url = valid_url

            # 返回解析结果
            self.finished.emit(parsed_url, nickname, user_id, "")

        except Exception as e:
            logger.error(f"解析出错: {e}")
            # 即使解析失败，也返回原始URL
            self.finished.emit(parsed_url, nickname, user_id, str(e))


class DownloadWorker(QObject):
    """下载工作器 - 在独立线程中执行异步下载任务"""

    # 信号
    started = pyqtSignal()
    progress = pyqtSignal(str, int, int)  # task_id, current, total
    status_changed = pyqtSignal(str, str)  # task_id, status
    message = pyqtSignal(str, str)  # task_id, message
    title_changed = pyqtSignal(str, str)  # task_id, new_title (用于更新显示名称)
    user_info_changed = pyqtSignal(str, str, str)  # task_id, nickname, user_id
    url_parsed = pyqtSignal(str, str)  # task_id, parsed_url (解析后的URL)
    finished = pyqtSignal(str)  # task_id
    error = pyqtSignal(str, str)  # task_id, error_message

    def __init__(
        self,
        task_id: str,
        platform: str,
        mode: str,
        url: str,
        config: Dict[str, Any],
    ):
        super().__init__()
        self.task_id = task_id
        self.platform = platform
        self.mode = mode
        self.url = url
        self.config = config
        self.is_running = False
        self._is_paused = False
        self.loop = None
        self.nickname = ""  # 用户昵称
        self.user_id = ""  # 用户ID
        self.video_count = 0  # 总视频数
        self.downloaded_count = 0  # 已下载数

    @pyqtSlot()
    def download(self):
        """开始下载 - Qt槽函数"""
        try:
            self.started.emit()
            self.is_running = True
            self.status_changed.emit(self.task_id, "downloading")

            # 创建新的事件循环
            self.loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self.loop)

            # 运行下载任务
            self.loop.run_until_complete(self._run_download())

            if self.is_running:  # 正常完成
                self.status_changed.emit(self.task_id, "completed")
            self.finished.emit(self.task_id)

        except Exception as e:
            error_msg = f"下载出错: {str(e)}"
            logger.error(f"{error_msg}\n{traceback.format_exc()}")
            self.error.emit(self.task_id, str(e))
            self.status_changed.emit(self.task_id, "failed")
            self.finished.emit(self.task_id)
        finally:
            self.is_running = False
            if self.loop:
                self.loop.close()

    async def _run_download(self):
        """执行实际的下载任务"""
        self.message.emit(self.task_id, f"开始下载: {self.url}")

        # TikTok 特殊处理：在导入任何 TikTok 模块之前设置代理
        # 这是因为 DeviceIdManager._MSTOKEN 在模块加载时就会调用 TokenManager.gen_real_msToken()
        if self.platform == "tiktok":
            self._setup_tiktok_proxy_before_any_import()

        # 准备配置参数
        kwargs = self._prepare_config()

        try:
            # 根据平台选择对应的 Handler
            if self.platform == "douyin":
                await self._download_douyin(kwargs)
            elif self.platform == "tiktok":
                await self._download_tiktok(kwargs)
            elif self.platform == "weibo":
                await self._download_weibo(kwargs)
            elif self.platform == "twitter":
                await self._download_twitter(kwargs)
            else:
                raise ValueError(f"不支持的平台: {self.platform}")

        except Exception as e:
            self.message.emit(self.task_id, f"下载失败: {str(e)}")
            raise

    def _setup_tiktok_proxy_before_any_import(self):
        """在导入任何 TikTok 模块之前设置代理

        这个方法必须在 _prepare_config() 之前调用，因为 _prepare_config() 会导入 TikTok 模块。
        """
        # 获取 GUI 配置中的代理设置
        gui_conf = self.config.copy() if self.config else {}
        gui_proxy = gui_conf.get("proxy", {})

        if gui_proxy.get("enabled") and gui_proxy.get("address"):
            proxy_address = gui_proxy["address"]
            proxies = {
                "http://": proxy_address,
                "https://": proxy_address,
            }
            logger.info(f"TikTok 预设置代理: {proxy_address}")
            self._setup_tiktok_proxy_before_import(proxies)
        else:
            logger.debug("TikTok: 未配置代理，将使用配置文件中的代理设置")

    def _prepare_config(self) -> Dict[str, Any]:
        """准备下载配置 - 合并 F2 平台配置和 GUI 配置"""
        # 首先获取 F2 平台的默认配置（包含 cookie 等）
        platform_conf = get_platform_config(self.platform)

        # 合并 GUI 配置
        gui_conf = self.config.copy() if self.config else {}

        # 从 GUI 配置中提取特定设置
        gui_download = (
            gui_conf.get("download", {})
            if isinstance(gui_conf.get("download"), dict)
            else gui_conf
        )
        gui_cookies = gui_conf.get("cookies", {})
        gui_proxy = gui_conf.get("proxy", {})
        gui_time_filter = gui_conf.get("time_filter", {})

        # 平台配置优先，GUI 配置覆盖
        kwargs = merge_config(platform_conf, gui_download)

        # 设置必要的参数
        kwargs["mode"] = self.mode
        kwargs["url"] = self.url

        # 设置默认值
        # 注意：GUI 的 interval 是翻页等待时间（整数），而 F2 的 interval 是日期区间（字符串）
        # 必须强制设置为 "all"，后面时间筛选会根据需要覆盖
        kwargs["interval"] = "all"
        if "timeout" not in kwargs:
            kwargs["timeout"] = 30

        # 处理 GUI Cookie 覆盖（如果有设置）
        if self.platform in gui_cookies and gui_cookies[self.platform]:
            kwargs["cookie"] = gui_cookies[self.platform]
            logger.info(f"使用 GUI 配置的 {self.platform} Cookie")

        # 处理代理设置
        if gui_proxy.get("enabled") and gui_proxy.get("address"):
            proxy_address = gui_proxy["address"]
            kwargs["proxies"] = {
                "http://": proxy_address,
                "https://": proxy_address,
            }
            logger.info(f"使用 GUI 配置的代理: {proxy_address}")

        # 处理时间筛选
        if gui_time_filter.get("enabled"):
            start_date = gui_time_filter.get("start_date", "")
            end_date = gui_time_filter.get("end_date", "")

            if start_date and end_date:
                # F2 的 interval 格式只需要日期: 2022-01-01|2023-01-01
                # 不要包含时间，F2 会自动处理时间范围（开始日期00:00:00到结束日期23:59:59）
                interval = f"{start_date}|{end_date}"
                kwargs["interval"] = interval
                logger.info(f"启用时间筛选: {interval}")

        # 处理其他 GUI 配置
        if "naming_template" in gui_download:
            kwargs["naming"] = gui_download["naming_template"]
        if "path" in gui_download:
            kwargs["path"] = gui_download["path"]
        if "max_connections" in gui_download:
            kwargs["max_connections"] = gui_download["max_connections"]
        if "page_counts" in gui_download:
            kwargs["page_counts"] = gui_download["page_counts"]
        if "max_counts" in gui_download:
            kwargs["max_counts"] = gui_download["max_counts"]
        if "max_tasks" in gui_download:
            kwargs["max_tasks"] = gui_download["max_tasks"]
        if "max_retries" in gui_download:
            kwargs["max_retries"] = gui_download["max_retries"]
        if "timeout" in gui_download:
            kwargs["timeout"] = gui_download["timeout"]
        # GUI 中的 page_interval（翻页等待时间秒数）
        # 注意：F2 核心的 interval 是时间筛选日期区间，GUI 用 page_interval 避免冲突
        if "page_interval" in gui_download and isinstance(
            gui_download["page_interval"], (int, float)
        ):
            kwargs["timeout"] = gui_download["page_interval"]
            logger.info(f"翻页等待时间设置为: {gui_download['page_interval']} 秒")
        if "folderize" in gui_download:
            kwargs["folderize"] = gui_download["folderize"]
        if "lyric" in gui_download:
            kwargs["lyric"] = "yes" if gui_download["lyric"] else "no"

        # 设置 headers
        kwargs.setdefault("headers", {})

        # 根据平台设置特定的 headers
        if self.platform == "douyin":
            from f2.apps.douyin.utils import ClientConfManager

            kwargs["headers"]["User-Agent"] = ClientConfManager.user_agent()
            kwargs["headers"]["Referer"] = ClientConfManager.referer()
            # 如果没有设置代理，使用默认代理
            if "proxies" not in kwargs:
                kwargs["proxies"] = ClientConfManager.proxies()
        elif self.platform == "tiktok":
            # TikTok 代理已在 _setup_tiktok_proxy_before_any_import 中设置
            # 这里只需要导入 ClientConfManager 获取其他配置
            from f2.apps.tiktok.utils import ClientConfManager

            kwargs["headers"]["User-Agent"] = ClientConfManager.user_agent()
            kwargs["headers"]["Referer"] = ClientConfManager.referer()
            if "proxies" not in kwargs:
                kwargs["proxies"] = ClientConfManager.proxies()

        return kwargs

    def _setup_tiktok_proxy_before_import(self, proxies: dict):
        """在导入 TikTok 模块前设置代理配置

        通过 monkey patch ConfigManager 来确保 TikTok 模块加载时使用正确的代理。

        问题背景：
        - TikTok 的 DeviceIdManager 类在定义时（模块加载时）就会执行
          `_MSTOKEN = TokenManager.gen_real_msToken()`
        - TokenManager.gen_real_msToken() 会发起网络请求，需要使用代理
        - 但 TokenManager.proxies 来自 ClientConfManager.proxies()
        - ClientConfManager 在模块加载时从配置文件读取代理，此时 GUI 的代理设置还未生效

        解决方案：
        - 在导入 TikTok 模块前，先 monkey patch ConfigManager.load_config
        - 让它在加载配置后注入 GUI 的代理设置
        """
        try:
            # 检查 TikTok 模块是否已经被导入
            if "f2.apps.tiktok.utils" in sys.modules:
                # 模块已导入，直接修改类属性
                self._update_tiktok_proxy_after_import(proxies)
                return

            # 模块尚未导入，需要 patch ConfigManager
            from f2.utils.conf_manager import ConfigManager

            # 保存原始方法
            if not hasattr(ConfigManager, "_original_load_config"):
                ConfigManager._original_load_config = ConfigManager.load_config

            # 创建 patched 方法
            def patched_load_config(self):
                config = ConfigManager._original_load_config(self)
                # 注入 TikTok 代理
                if config and "f2" in config and "tiktok" in config["f2"]:
                    config["f2"]["tiktok"]["proxies"] = proxies
                    logger.debug(f"ConfigManager: 已注入 TikTok 代理 {proxies}")
                return config

            # 应用 patch
            ConfigManager.load_config = patched_load_config
            logger.info(f"已 patch ConfigManager 以注入 TikTok 代理: {proxies}")

        except Exception as e:
            logger.warning(f"设置 TikTok 代理失败: {e}")
            import traceback

            traceback.print_exc()

    def _update_tiktok_proxy_after_import(self, proxies: dict):
        """在 TikTok 模块已导入后更新代理配置

        直接修改已加载模块的类属性。
        """
        try:
            from f2.apps.tiktok.utils import ClientConfManager as TiktokClientConf
            from f2.apps.tiktok.utils import DeviceIdManager as TiktokDeviceIdManager
            from f2.apps.tiktok.utils import TokenManager as TiktokTokenManager

            # 更新 ClientConfManager 的 tiktok_conf
            TiktokClientConf.tiktok_conf["proxies"] = proxies
            # 更新 TokenManager 的 proxies 类属性
            TiktokTokenManager.proxies = proxies
            # 更新 DeviceIdManager 的 proxies 类属性
            TiktokDeviceIdManager.proxies = proxies

            # 尝试重新生成 msToken（可能会失败，但后续请求会使用正确的代理）
            try:
                new_mstoken = TiktokTokenManager.gen_real_msToken()
                TiktokDeviceIdManager._MSTOKEN = new_mstoken
                TiktokDeviceIdManager._DEVICE_ID_HEADERS["Cookie"] = (
                    f"msToken={new_mstoken}"
                )
                logger.info(f"已重新生成 TikTok msToken")
            except Exception as token_err:
                logger.warning(
                    f"重新生成 msToken 失败（将在后续请求中重试）: {token_err}"
                )

            logger.info(f"已更新已加载的 TikTok 模块代理配置: {proxies}")

        except Exception as e:
            logger.warning(f"更新 TikTok 模块代理配置失败: {e}")

    async def _detect_douyin_url_type(self, url: str) -> str:
        """检测抖音 URL 类型

        Returns:
            str: "video" | "user" | "mix" | "live" | "unknown"
        """
        import httpx

        from f2.apps.douyin.utils import ClientConfManager

        try:
            # 获取代理配置，兼容 httpx 新版本 (proxy 替代 proxies)
            proxy_config = ClientConfManager.proxies()
            proxy = None
            if proxy_config:
                # 提取单个代理URL
                proxy = (
                    proxy_config.get("http://")
                    or proxy_config.get("https://")
                    or proxy_config.get("all://")
                )
            headers = {"User-Agent": ClientConfManager.user_agent()}

            async with httpx.AsyncClient(proxy=proxy, headers=headers) as client:
                response = await client.get(url, follow_redirects=True, timeout=15)
                final_url = str(response.url)

                # 检测 URL 类型
                if "/video/" in final_url or "/note/" in final_url:
                    return "video"
                elif (
                    "/share/user/" in final_url
                    or "sec_uid=" in final_url
                    or "/user/" in final_url
                ):
                    return "user"
                elif "/collection/" in final_url:
                    return "mix"
                elif "/live/" in final_url:
                    return "live"
                else:
                    return "unknown"
        except Exception as e:
            logger.warning(f"URL 类型检测失败: {e}")
            return "unknown"

    async def _download_douyin(self, kwargs: Dict[str, Any]):
        """下载抖音内容"""
        from f2.apps.douyin.db import AsyncUserDB
        from f2.apps.douyin.dl import DouyinDownloader
        from f2.apps.douyin.handler import DouyinHandler
        from f2.apps.douyin.utils import SecUserIdFetcher
        from f2.utils.utils import extract_valid_urls

        self.message.emit(self.task_id, "正在解析抖音链接...")

        # 从分享文本中提取有效URL
        raw_url = kwargs.get("url", "")
        valid_url = extract_valid_urls(raw_url)
        if valid_url:
            kwargs["url"] = valid_url
            self.message.emit(self.task_id, f"提取到链接: {valid_url}")
        else:
            self.message.emit(self.task_id, f"使用原始链接: {raw_url}")
            valid_url = raw_url

        # 智能检测 URL 类型
        url_type = await self._detect_douyin_url_type(valid_url)
        self.message.emit(self.task_id, f"检测到链接类型: {url_type}")

        # 检查模式与 URL 类型是否匹配
        mode = self.mode
        if url_type == "user" and mode == "one":
            self.message.emit(
                self.task_id, "⚠️ 检测到用户主页链接，自动切换为下载用户作品"
            )
            mode = "post"
        elif url_type == "video" and mode == "post":
            self.message.emit(
                self.task_id, "⚠️ 检测到单个作品链接，自动切换为下载单个作品"
            )
            mode = "one"
        elif url_type == "mix" and mode not in ["mix"]:
            self.message.emit(self.task_id, "⚠️ 检测到合集链接，自动切换为下载合集")
            mode = "mix"
        elif url_type == "live" and mode != "live":
            self.message.emit(self.task_id, "⚠️ 检测到直播链接，自动切换为下载直播")
            mode = "live"

        if mode == "one":
            # 单个作品下载 - 直接使用 handler
            handler = DouyinHandler(kwargs)
            await handler.handle_one_video()
            self.message.emit(self.task_id, "单个作品下载完成")
            self.progress.emit(self.task_id, 100, 100)

        elif mode == "post":
            # 用户主页作品 - 实现详细进度
            await self._download_douyin_user_posts(kwargs)

        elif mode == "like":
            handler = DouyinHandler(kwargs)
            await handler.handle_user_like()
            self.progress.emit(self.task_id, 100, 100)

        elif mode == "collection":
            handler = DouyinHandler(kwargs)
            await handler.handle_user_collection()
            self.progress.emit(self.task_id, 100, 100)

        elif mode == "mix":
            handler = DouyinHandler(kwargs)
            await handler.handle_user_mix()
            self.progress.emit(self.task_id, 100, 100)

        elif mode == "music":
            handler = DouyinHandler(kwargs)
            await handler.handle_user_music_collection()
            self.progress.emit(self.task_id, 100, 100)

        elif mode == "live":
            handler = DouyinHandler(kwargs)
            await handler.handle_user_live()
            self.progress.emit(self.task_id, 100, 100)

        else:
            raise ValueError(f"抖音不支持的模式: {mode}")

    async def _download_douyin_user_posts(self, kwargs: Dict[str, Any]):
        """下载抖音用户主页作品 - 带详细进度"""
        from f2.apps.douyin.db import AsyncUserDB
        from f2.apps.douyin.dl import DouyinDownloader
        from f2.apps.douyin.handler import DouyinHandler
        from f2.apps.douyin.utils import SecUserIdFetcher
        from f2.utils.utils import extract_valid_urls

        # 从分享文本中提取有效URL
        raw_url = kwargs.get("url", "")
        valid_url = extract_valid_urls(raw_url)
        if valid_url:
            kwargs["url"] = valid_url
            self.url_parsed.emit(self.task_id, valid_url)  # 发送解析后的URL
            self.message.emit(self.task_id, f"提取到链接: {valid_url}")

        # 获取用户ID
        sec_user_id = await SecUserIdFetcher.get_sec_user_id(kwargs.get("url"))
        if not sec_user_id:
            raise ValueError("无法获取用户ID")

        self.user_id = sec_user_id  # 保存用户ID
        self.message.emit(self.task_id, f"获取到用户ID: {sec_user_id}")

        # 创建处理器和下载器
        handler = DouyinHandler(kwargs)
        downloader = DouyinDownloader(kwargs)

        # 获取用户信息
        async with AsyncUserDB("douyin_users.db") as db:
            user_path = await handler.get_or_add_user_data(kwargs, sec_user_id, db)
            user_info = await db.get_user_info(sec_user_id)

            if user_info:
                self.nickname = user_info.get("nickname", "未知用户")
            else:
                # 尝试从 API 获取用户信息
                try:
                    profile = await handler.fetch_user_profile(sec_user_id)
                    self.nickname = profile.nickname if profile else sec_user_id[:8]
                except:
                    self.nickname = sec_user_id[:8]

        # 发送用户信息更新 (新信号，包含 nickname 和 user_id)
        self.user_info_changed.emit(self.task_id, self.nickname, self.user_id)
        self.title_changed.emit(self.task_id, f"[抖音] {self.nickname}")
        self.message.emit(self.task_id, f"用户: {self.nickname}，正在获取作品列表...")

        # 获取作品列表参数
        min_cursor = 0
        max_cursor = kwargs.get("max_cursor", 0)
        interval = kwargs.get("interval", "all")
        page_counts = kwargs.get("page_counts", 20)
        max_counts = kwargs.get("max_counts", 0)

        # 处理时间区间
        if interval and interval != "all":
            from f2.utils.utils import interval_2_timestamp

            min_cursor = interval_2_timestamp(interval, date_type="start")
            max_cursor = interval_2_timestamp(interval, date_type="end")
            self.message.emit(
                self.task_id, f"[{self.nickname}] 设置日期区间过滤: {interval}"
            )

        video_count = 0
        updated_count = 0

        # 遍历获取作品
        async for aweme_list in handler.fetch_user_post_videos(
            sec_user_id=sec_user_id,
            min_cursor=min_cursor,
            max_cursor=max_cursor,
            page_counts=page_counts,
            max_counts=max_counts,
        ):
            if not self.is_running:
                break

            if not aweme_list:
                self.message.emit(self.task_id, f"[{self.nickname}] 无法获取作品信息")
                continue

            video_list = aweme_list._to_list()
            batch_count = len(video_list)
            video_count += batch_count

            self.message.emit(
                self.task_id,
                f"[{self.nickname}] 获取到 {batch_count} 个作品，总计: {video_count}",
            )

            # 创建下载任务
            batch_updated = await downloader.create_download_tasks(
                kwargs, video_list, user_path
            )

            if batch_updated and isinstance(batch_updated, int):
                updated_count += batch_updated
                if batch_updated > 0:
                    self.message.emit(
                        self.task_id,
                        f"[{self.nickname}] 本批次更新 {batch_updated} 个作品，总更新: {updated_count}",
                    )

            # 更新进度（基于 max_counts 或已处理数量）
            if max_counts and max_counts > 0:
                progress = min(100, int((video_count / max_counts) * 100))
            else:
                progress = min(95, video_count)  # 没有上限时，最多显示95%

            self.progress.emit(self.task_id, progress, 100)

        # 完成
        self.progress.emit(self.task_id, 100, 100)
        self.message.emit(
            self.task_id,
            f"[{self.nickname}] 下载完成！总获取 {video_count} 个作品，实际更新 {updated_count} 个",
        )

    async def _download_tiktok(self, kwargs: Dict[str, Any]):
        """下载 TikTok 内容"""
        from f2.apps.tiktok.handler import TiktokHandler

        self.message.emit(self.task_id, "正在解析 TikTok 链接...")

        # 刷新 device_id、msToken 和浏览器版本以确保 API 请求有效
        new_user_agent = await self._refresh_tiktok_tokens()

        # 更新 kwargs 中的 User-Agent（因为 _prepare_config 中已设置了旧版本）
        if new_user_agent:
            kwargs["headers"]["User-Agent"] = new_user_agent

        handler = TiktokHandler(kwargs)

        if self.mode == "one":
            await handler.handle_one_video()
            self.progress.emit(self.task_id, 100, 100)
        elif self.mode == "post":
            await handler.handle_user_post()
            self.progress.emit(self.task_id, 100, 100)
        elif self.mode == "like":
            await handler.handle_user_like()
            self.progress.emit(self.task_id, 100, 100)
        elif self.mode == "collect":
            await handler.handle_user_collect()
            self.progress.emit(self.task_id, 100, 100)
        elif self.mode == "mix":
            await handler.handle_user_mix()
            self.progress.emit(self.task_id, 100, 100)
        elif self.mode == "live":
            await handler.handle_user_live()
            self.progress.emit(self.task_id, 100, 100)
        else:
            raise ValueError(f"TikTok 不支持的模式: {self.mode}")

    async def _refresh_tiktok_tokens(self):
        """刷新 TikTok 的 device_id、msToken 和浏览器指纹信息

        TikTok API 有时会因为 device_id、msToken 或浏览器指纹不匹配导致返回空响应。
        此方法尝试生成新的认证信息并更新到配置和模型中。
        """
        try:
            from urllib.parse import quote

            from f2.apps.tiktok import model as tiktok_model
            from f2.apps.tiktok.utils import (
                ClientConfManager,
                DeviceIdManager,
                TokenManager,
            )

            self.message.emit(self.task_id, "正在刷新 TikTok 认证信息...")

            # 0. 更新浏览器版本信息（使用最新的 Chrome 版本）
            # 这是因为 TikTok 会检测浏览器版本是否过旧
            new_chrome_version = "142.0.0.0"
            new_user_agent = f"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{new_chrome_version} Safari/537.36"
            new_browser_version = f"5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{new_chrome_version} Safari/537.36"

            # 更新 ClientConfManager 中的浏览器配置
            if "browser" in ClientConfManager.tiktok_conf.get("BaseRequestModel", {}):
                ClientConfManager.tiktok_conf["BaseRequestModel"]["browser"][
                    "version"
                ] = new_browser_version
            if "headers" in ClientConfManager.tiktok_conf:
                ClientConfManager.tiktok_conf["headers"]["User-Agent"] = new_user_agent

            # 更新模型中的 browser_version 默认值
            models_to_update = [
                tiktok_model.BaseRequestModel,
                tiktok_model.UserProfile,
                tiktok_model.UserPost,
                tiktok_model.UserLike,
                tiktok_model.UserCollect,
                tiktok_model.UserPlayList,
                tiktok_model.UserMix,
                tiktok_model.PostDetail,
                tiktok_model.PostComment,
                tiktok_model.PostSearch,
                tiktok_model.UserLive,
                tiktok_model.CheckLiveAlive,
            ]

            # URL 编码的浏览器版本
            encoded_browser_version = quote(new_browser_version, safe="")

            for model_class in models_to_update:
                try:
                    if "browser_version" in model_class.model_fields:
                        model_class.model_fields["browser_version"].default = (
                            encoded_browser_version
                        )
                except Exception as e:
                    logger.debug(
                        f"更新 {model_class.__name__}.browser_version 失败: {e}"
                    )

            logger.info(f"已更新浏览器版本为 Chrome {new_chrome_version}")

            # 1. 生成新的 device_id
            device_info = await DeviceIdManager.gen_device_id(full_cookie=False)
            new_device_id = device_info.get("deviceId")

            if new_device_id:
                # 更新 ClientConfManager 中的 device_id
                ClientConfManager.tiktok_conf["BaseRequestModel"]["device"][
                    "id"
                ] = new_device_id

                # 获取旧的 device_id
                old_default = tiktok_model.BaseRequestModel.model_fields[
                    "device_id"
                ].default

                # 更新 BaseRequestModel 及其所有子类的 device_id 默认值
                for model_class in models_to_update:
                    try:
                        if "device_id" in model_class.model_fields:
                            model_class.model_fields["device_id"].default = (
                                new_device_id
                            )
                    except Exception as e:
                        logger.debug(f"更新 {model_class.__name__}.device_id 失败: {e}")

                logger.info(
                    f"已刷新 TikTok device_id: {old_default} -> {new_device_id}"
                )
                self.message.emit(
                    self.task_id, f"已刷新 device_id: {new_device_id[:10]}..."
                )

            # 2. 生成新的 msToken 并更新模型默认值
            try:
                new_msToken = TokenManager.gen_real_msToken()
                if new_msToken and len(new_msToken) == 148:
                    # 更新所有使用 msToken 的模型
                    for model_class in models_to_update:
                        try:
                            if "msToken" in model_class.model_fields:
                                model_class.model_fields["msToken"].default = (
                                    new_msToken
                                )
                        except Exception as e:
                            logger.debug(
                                f"更新 {model_class.__name__}.msToken 失败: {e}"
                            )

                    logger.info(f"已刷新 TikTok msToken: {new_msToken[:20]}...")
                    self.message.emit(
                        self.task_id, f"已刷新 msToken: {new_msToken[:15]}..."
                    )
            except Exception as e:
                logger.warning(f"刷新 msToken 失败: {e}，将使用默认值")

            # 3. 重建所有模型使更改生效
            for model_class in models_to_update:
                try:
                    model_class.model_rebuild(force=True)
                except Exception as e:
                    logger.debug(f"重建 {model_class.__name__} 失败: {e}")

            return new_user_agent

        except Exception as e:
            logger.warning(f"刷新 TikTok 认证信息失败: {e}")
            import traceback

            traceback.print_exc()
            # 不抛出异常，继续使用默认值
            return None

    async def _download_weibo(self, kwargs: Dict[str, Any]):
        """下载微博内容"""
        from f2.apps.weibo.handler import WeiboHandler

        self.message.emit(self.task_id, "正在解析微博链接...")

        handler = WeiboHandler(kwargs)

        if self.mode == "one":
            await handler.handle_one_video()
            self.progress.emit(self.task_id, 100, 100)
        elif self.mode == "post":
            await handler.handle_user_weibo()
            self.progress.emit(self.task_id, 100, 100)
        else:
            raise ValueError(f"微博不支持的模式: {self.mode}")

    async def _download_twitter(self, kwargs: Dict[str, Any]):
        """下载 Twitter/X 内容"""
        from f2.apps.twitter.handler import TwitterHandler

        self.message.emit(self.task_id, "正在解析 Twitter 链接...")

        handler = TwitterHandler(kwargs)

        if self.mode == "one":
            await handler.handle_one_tweet()
            self.progress.emit(self.task_id, 100, 100)
        elif self.mode == "post":
            await handler.handle_user_tweet()
            self.progress.emit(self.task_id, 100, 100)
        elif self.mode == "like":
            await handler.handle_user_like()
            self.progress.emit(self.task_id, 100, 100)
        elif self.mode == "bookmark":
            await handler.handle_user_bookmark()
            self.progress.emit(self.task_id, 100, 100)
        else:
            raise ValueError(f"Twitter 不支持的模式: {self.mode}")

    def pause(self):
        """暂停下载"""
        self._is_paused = True
        self.status_changed.emit(self.task_id, "paused")

    def resume(self):
        """继续下载"""
        self._is_paused = False
        self.status_changed.emit(self.task_id, "downloading")

    def stop(self):
        """停止下载"""
        self.is_running = False
        self._is_paused = False


class DownloadTask:
    """下载任务封装"""

    def __init__(self, task_id: str):
        self.task_id = task_id
        self.thread: Optional[QThread] = None
        self.worker: Optional[DownloadWorker] = None


class DownloadController(QObject):
    """下载控制器 - 管理所有下载任务"""

    # 信号
    task_added = pyqtSignal(str)  # task_id
    task_removed = pyqtSignal(str)  # task_id
    task_progress = pyqtSignal(str, int, int)  # task_id, current, total
    task_status_changed = pyqtSignal(str, str)  # task_id, status
    task_message = pyqtSignal(str, str)  # task_id, message
    task_title_changed = pyqtSignal(str, str)  # task_id, new_title
    task_user_info_changed = pyqtSignal(str, str, str)  # task_id, nickname, user_id
    task_url_parsed = pyqtSignal(str, str)  # task_id, parsed_url
    task_finished = pyqtSignal(str)  # task_id
    task_completed = pyqtSignal(str, str)  # task_id, nickname (带用户名的完成信号)
    task_error = pyqtSignal(str, str)  # task_id, error_message

    def __init__(self):
        super().__init__()
        self._tasks: Dict[str, DownloadTask] = {}

    def start_download(
        self,
        task_id: str,
        platform: str,
        mode: str,
        url: str,
        config: Dict[str, Any],
    ) -> bool:
        """
        开始下载任务

        Args:
            task_id: 任务ID
            platform: 平台名称 (douyin, tiktok, weibo, twitter)
            mode: 下载模式 (one, post, like, etc.)
            url: 下载链接
            config: 配置参数

        Returns:
            bool: 是否成功启动
        """
        if task_id in self._tasks:
            logger.warning(f"任务 {task_id} 已存在")
            return False

        # 创建任务
        task = DownloadTask(task_id)

        # 创建线程和工作器
        task.thread = QThread()
        task.worker = DownloadWorker(task_id, platform, mode, url, config)

        # 移动工作器到线程
        task.worker.moveToThread(task.thread)

        # 连接信号
        task.thread.started.connect(task.worker.download)
        task.worker.progress.connect(self._on_progress)
        task.worker.status_changed.connect(self._on_status_changed)
        task.worker.message.connect(self._on_message)
        task.worker.title_changed.connect(self._on_title_changed)
        task.worker.user_info_changed.connect(self._on_user_info_changed)
        task.worker.url_parsed.connect(self._on_url_parsed)
        task.worker.finished.connect(lambda tid: self._on_finished(tid))
        task.worker.error.connect(self._on_error)

        # 线程完成时清理
        task.worker.finished.connect(task.thread.quit)
        task.thread.finished.connect(lambda: self._cleanup_task(task_id))

        # 保存并启动
        self._tasks[task_id] = task
        task.thread.start()

        self.task_added.emit(task_id)
        logger.info(f"任务 {task_id} 已启动: {platform}/{mode} - {url}")
        return True

    def pause_download(self, task_id: str):
        """暂停下载"""
        if task_id in self._tasks and self._tasks[task_id].worker:
            self._tasks[task_id].worker.pause()
            logger.info(f"任务 {task_id} 已暂停")

    def resume_download(self, task_id: str):
        """继续下载"""
        if task_id in self._tasks and self._tasks[task_id].worker:
            self._tasks[task_id].worker.resume()
            logger.info(f"任务 {task_id} 已继续")

    def cancel_download(self, task_id: str):
        """取消下载"""
        if task_id in self._tasks:
            task = self._tasks[task_id]
            if task.worker:
                task.worker.stop()
            if task.thread and task.thread.isRunning():
                task.thread.quit()
                task.thread.wait(3000)
            self._cleanup_task(task_id)
            self.task_removed.emit(task_id)
            logger.info(f"任务 {task_id} 已取消")

    def _on_progress(self, task_id: str, current: int, total: int):
        """进度更新"""
        self.task_progress.emit(task_id, current, total)

    def _on_status_changed(self, task_id: str, status: str):
        """状态变化"""
        self.task_status_changed.emit(task_id, status)

    def _on_message(self, task_id: str, message: str):
        """消息通知"""
        self.task_message.emit(task_id, message)
        # 不再重复打印日志，由 main_window 统一处理显示

    def _on_title_changed(self, task_id: str, new_title: str):
        """标题变化"""
        self.task_title_changed.emit(task_id, new_title)

    def _on_user_info_changed(self, task_id: str, nickname: str, user_id: str):
        """用户信息变化"""
        self.task_user_info_changed.emit(task_id, nickname, user_id)

    def _on_url_parsed(self, task_id: str, parsed_url: str):
        """URL解析完成"""
        self.task_url_parsed.emit(task_id, parsed_url)

    def _on_finished(self, task_id: str):
        """任务完成"""
        # 获取用户名用于日志
        nickname = ""
        if task_id in self._tasks and self._tasks[task_id].worker:
            nickname = self._tasks[task_id].worker.nickname

        if nickname:
            logger.info(f"✅ 下载完成: {nickname}")
        else:
            logger.info(f"✅ 任务 {task_id} 完成")

        self.task_finished.emit(task_id)
        self.task_completed.emit(task_id, nickname)

    def _on_error(self, task_id: str, error: str):
        """任务出错"""
        logger.error(f"任务 {task_id} 出错: {error}")
        self.task_error.emit(task_id, error)

    def _cleanup_task(self, task_id: str):
        """清理任务"""
        if task_id in self._tasks:
            task = self._tasks.pop(task_id)
            if task.worker:
                task.worker.deleteLater()
            if task.thread:
                task.thread.deleteLater()

    def get_active_tasks(self) -> List[str]:
        """获取活动任务列表"""
        return list(self._tasks.keys())

    def cleanup(self):
        """清理所有任务"""
        for task_id in list(self._tasks.keys()):
            self.cancel_download(task_id)
