"""
配置管理器
~~~~~~~~~

管理GUI配置的保存和加载。
使用单例模式确保全局只有一个配置实例。
"""

import json
from pathlib import Path
from typing import Any, Dict, Optional

from f2.gui.config import CONFIG_FILE, DEFAULT_DOWNLOAD_CONFIG, SECRETS_FILE


class ConfigManager:
    """配置管理器 - 单例模式"""

    _instance = None
    _initialized = False

    def __new__(cls, config_file: Optional[Path] = None):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, config_file: Optional[Path] = None):
        # 避免重复初始化
        if ConfigManager._initialized:
            return
        ConfigManager._initialized = True

        self.config_file = config_file or CONFIG_FILE
        self._config: Dict[str, Any] = {}
        self.load()

    def load(self) -> Dict[str, Any]:
        """加载配置"""
        if self.config_file.exists():
            try:
                with open(self.config_file, "r", encoding="utf-8") as f:
                    self._config = json.load(f)
                # 合并默认配置，确保新增字段存在
                self._merge_defaults()
            except Exception as e:
                print(f"加载配置失败: {e}")
                self._config = self._get_default_config()
        else:
            self._config = self._get_default_config()

        return self._config

    def reload(self) -> Dict[str, Any]:
        """重新加载配置（从文件刷新）"""
        return self.load()

    def _merge_defaults(self):
        """将默认配置合并到现有配置，确保新增字段存在"""
        defaults = self._get_default_config()
        self._deep_merge_defaults(self._config, defaults)

    def _deep_merge_defaults(self, target: dict, defaults: dict):
        """深度合并默认值（只添加缺失的键，不覆盖现有值）"""
        for key, default_value in defaults.items():
            if key not in target:
                # 键不存在，添加默认值
                target[key] = default_value
            elif isinstance(default_value, dict) and isinstance(target.get(key), dict):
                # 递归合并嵌套字典
                self._deep_merge_defaults(target[key], default_value)

    def save(self) -> bool:
        """保存配置"""
        try:
            # 确保目录存在
            self.config_file.parent.mkdir(parents=True, exist_ok=True)

            with open(self.config_file, "w", encoding="utf-8") as f:
                json.dump(self._config, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"保存配置失败: {e}")
            return False

    def get(self, key: str, default: Any = None) -> Any:
        """获取配置值"""
        keys = key.split(".")
        value = self._config
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
                if value is None:
                    return default
            else:
                return default
        return value

    def set(self, key: str, value: Any):
        """设置配置值"""
        keys = key.split(".")
        config = self._config

        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]

        config[keys[-1]] = value

    def update(self, config: Dict[str, Any]):
        """更新配置"""
        self._deep_update(self._config, config)

    def _deep_update(self, target: dict, source: dict):
        """深度更新字典"""
        for key, value in source.items():
            if isinstance(value, dict) and key in target:
                self._deep_update(target[key], value)
            else:
                target[key] = value

    def _get_default_config(self) -> Dict[str, Any]:
        """获取默认配置"""
        return {
            "theme": "light",
            "window": {
                "width": 1400,
                "height": 900,
                "maximized": False,
            },
            "download": DEFAULT_DOWNLOAD_CONFIG.copy(),
            "card_states": {},  # 存储卡片折叠状态
            "time_filter": {
                "enabled": False,
                "start_date": "",
                "start_time": "00:00:00",
                "end_date": "",
                "end_time": "23:59:59",
            },
            "proxy": {
                "enabled": False,
                "address": "",
            },
            "advanced": {
                "log_level": "INFO",
            },
        }

    def get_all(self) -> Dict[str, Any]:
        """获取所有配置（包含默认值填充）"""
        # 确保配置包含所有默认字段
        self._merge_defaults()
        config = self._config.copy()
        # 加载 cookies 从 secrets 文件
        config["cookies"] = self.load_secrets()
        return config

    def get_download_config(self) -> Dict[str, Any]:
        """获取下载配置（确保包含所有默认值）"""
        download = self._config.get("download", {}).copy()
        # 合并默认值
        for key, value in DEFAULT_DOWNLOAD_CONFIG.items():
            if key not in download:
                download[key] = value
        return download

    def reset(self):
        """重置为默认配置"""
        self._config = self._get_default_config()
        self.save()

    def reset_section(self, section: str):
        """重置指定配置段落为默认值

        Args:
            section: 配置段落名，如 'download', 'proxy', 'time_filter' 等
        """
        defaults = self._get_default_config()
        if section in defaults:
            self._config[section] = (
                defaults[section].copy()
                if isinstance(defaults[section], dict)
                else defaults[section]
            )
            self.save()

    # ==================== Secrets 文件管理 ====================

    def load_secrets(self) -> Dict[str, str]:
        """从 secrets 文件加载 Cookie"""
        if SECRETS_FILE.exists():
            try:
                with open(SECRETS_FILE, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                print(f"加载 secrets 文件失败: {e}")
                return {}
        return {}

    def save_secrets(self, cookies: Dict[str, str]) -> bool:
        """保存 Cookie 到 secrets 文件

        只保存非空的 Cookie，自动清理空值。
        """
        try:
            # 确保目录存在
            SECRETS_FILE.parent.mkdir(parents=True, exist_ok=True)

            # 过滤掉空值
            cookies_to_save = {k: v for k, v in cookies.items() if v and v.strip()}

            with open(SECRETS_FILE, "w", encoding="utf-8") as f:
                json.dump(cookies_to_save, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"保存 secrets 文件失败: {e}")
            return False

    def get_cookie(self, platform: str) -> str:
        """获取指定平台的 Cookie"""
        cookies = self.load_secrets()
        return cookies.get(platform, "")

    def set_cookie(self, platform: str, cookie: str):
        """设置指定平台的 Cookie"""
        cookies = self.load_secrets()
        if cookie and cookie.strip():
            cookies[platform] = cookie.strip()
        elif platform in cookies:
            del cookies[platform]
        self.save_secrets(cookies)

    def clear_cookies(self):
        """清除所有 Cookie"""
        self.save_secrets({})

    def has_cookie(self, platform: str) -> bool:
        """检查指定平台是否有 Cookie"""
        return bool(self.get_cookie(platform))

    # ==================== 卡片状态管理 ====================

    def get_card_state(self, card_id: str) -> Optional[bool]:
        """获取卡片的展开状态

        Args:
            card_id: 卡片唯一标识

        Returns:
            bool: True=展开, False=折叠, None=未设置
        """
        card_states = self._config.get("card_states", {})
        return card_states.get(card_id)

    def set_card_state(self, card_id: str, expanded: bool):
        """设置卡片的展开状态

        Args:
            card_id: 卡片唯一标识
            expanded: True=展开, False=折叠
        """
        if "card_states" not in self._config:
            self._config["card_states"] = {}
        self._config["card_states"][card_id] = expanded

    def clear_card_states(self):
        """清除所有卡片状态"""
        self._config["card_states"] = {}
        self.save()
