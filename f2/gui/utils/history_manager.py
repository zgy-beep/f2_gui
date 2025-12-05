# -*- coding:utf-8 -*-
"""
历史记录管理器
~~~~~~~~~~~~~~

管理下载历史记录的存储和查询。
支持按模式分类、自动检查和修复。
"""

import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from f2.log.logger import logger


class HistoryManager:
    """历史记录管理器

    功能：
    - 按平台和模式分类存储历史记录
    - 自动检查和修复数据完整性
    - 去重：同一用户同一模式只保留一条记录
    """

    # 必需字段及其默认值
    REQUIRED_FIELDS = {
        "id": lambda: str(uuid.uuid4())[:8],
        "time": lambda: datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "platform": lambda: "unknown",
        "url": lambda: "",
        "type": lambda: "视频",
        "status": lambda: "未知",
        "file_count": lambda: 0,
        "mode": lambda: "one",
        "nickname": lambda: "",
        "user_id": lambda: "",
        "download_count": lambda: 1,
    }

    # 有效的平台和模式
    VALID_PLATFORMS = ["douyin", "tiktok", "weibo", "twitter"]
    VALID_MODES = [
        "one",
        "post",
        "like",
        "collection",
        "mix",
        "music",
        "live",
        "bookmark",
    ]
    VALID_STATUSES = ["成功", "失败", "进行中", "未知"]

    def __init__(self):
        self._history_file = self._get_history_file_path()
        self._records: List[Dict] = []
        self._load()
        # 加载后自动检查和修复
        self._auto_repair()

    def _get_history_file_path(self) -> Path:
        """获取历史记录文件路径"""
        gui_dir = Path(__file__).parent.parent
        return gui_dir / "download_history.json"

    def _load(self):
        """加载历史记录"""
        try:
            if self._history_file.exists():
                with open(self._history_file, "r", encoding="utf-8-sig") as f:
                    data = json.load(f)
                    self._records = data.get("records", [])
                    logger.debug(f"加载了 {len(self._records)} 条历史记录")
        except (json.JSONDecodeError, IOError) as e:
            logger.error(f"加载历史记录失败: {e}")
            self._records = []

    def _save(self):
        """保存历史记录"""
        try:
            # 添加元数据
            data = {
                "version": "2.0",
                "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "total_count": len(self._records),
                "records": self._records,
            }
            with open(self._history_file, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except IOError as e:
            logger.error(f"保存历史记录失败: {e}")

    def _auto_repair(self):
        """自动检查和修复数据"""
        if not self._records:
            return

        repaired_count = 0
        removed_count = 0
        records_to_keep = []

        for record in self._records:
            # 修复缺失字段
            was_repaired = False
            for field, default_factory in self.REQUIRED_FIELDS.items():
                if field not in record or record[field] is None:
                    record[field] = default_factory()
                    was_repaired = True

            # 修复无效的平台
            if record.get("platform") not in self.VALID_PLATFORMS:
                # 尝试从 URL 推断平台
                url = record.get("url", "").lower()
                if "douyin" in url:
                    record["platform"] = "douyin"
                elif "tiktok" in url:
                    record["platform"] = "tiktok"
                elif "weibo" in url:
                    record["platform"] = "weibo"
                elif "twitter" in url or "x.com" in url:
                    record["platform"] = "twitter"
                else:
                    record["platform"] = "douyin"  # 默认抖音
                was_repaired = True

            # 修复无效的模式
            if record.get("mode") not in self.VALID_MODES:
                record["mode"] = "one"
                was_repaired = True

            # 修复无效的状态
            if record.get("status") not in self.VALID_STATUSES:
                record["status"] = "未知"
                was_repaired = True

            # 修复时间格式
            try:
                datetime.strptime(record.get("time", ""), "%Y-%m-%d %H:%M:%S")
            except ValueError:
                record["time"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                was_repaired = True

            # 确保 download_count 是整数
            if not isinstance(record.get("download_count"), int):
                try:
                    record["download_count"] = int(record.get("download_count", 1))
                except (ValueError, TypeError):
                    record["download_count"] = 1
                was_repaired = True

            if was_repaired:
                repaired_count += 1

            records_to_keep.append(record)

        # 去重：同一用户 + 同一模式只保留最新的一条
        seen = set()
        deduplicated = []
        for record in records_to_keep:
            # 使用 (platform, user_id, mode) 作为唯一键
            user_id = record.get("user_id", "")
            if user_id:
                key = (record["platform"], user_id, record["mode"])
            else:
                # 没有 user_id 的使用 URL
                key = (record["platform"], record["url"], record["mode"])

            if key not in seen:
                seen.add(key)
                deduplicated.append(record)
            else:
                removed_count += 1

        self._records = deduplicated

        if repaired_count > 0 or removed_count > 0:
            logger.info(
                f"历史记录修复完成: 修复 {repaired_count} 条，去重 {removed_count} 条"
            )
            self._save()

    def check_and_repair(self) -> Dict[str, int]:
        """手动检查和修复数据，返回修复统计

        Returns:
            dict: {"repaired": 修复数量, "removed": 去重数量}
        """
        original_count = len(self._records)
        self._auto_repair()
        return {
            "repaired": 0,  # 详细统计在 _auto_repair 中
            "removed": original_count - len(self._records),
            "total": len(self._records),
        }

    def _find_duplicate(
        self, platform: str, user_id: str, url: str, mode: str
    ) -> Optional[Dict]:
        """查找重复记录（基于 user_id + mode 或 URL + mode）"""
        for record in self._records:
            if record.get("platform") != platform:
                continue
            if record.get("mode") != mode:
                continue
            # 优先按 user_id 匹配
            if user_id and record.get("user_id") == user_id:
                return record
            # 如果没有 user_id，则按 URL 匹配
            if not user_id and record.get("url") == url:
                return record
        return None

    def add_record(
        self,
        platform: str,
        url: str,
        download_type: str = "视频",
        status: str = "进行中",
        file_count: int = 0,
        mode: str = "one",
        nickname: str = "",
        **kwargs,
    ) -> str:
        """添加历史记录（自动去重，相同用户+模式只保留一条）"""
        user_id = kwargs.get("user_id", "")

        # 查找重复记录（同一用户同一模式）
        existing = self._find_duplicate(platform, user_id, url, mode)

        if existing:
            # 更新现有记录
            existing["time"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            existing["status"] = status
            existing["file_count"] = file_count
            existing["nickname"] = nickname or existing.get("nickname", "")
            existing["url"] = url
            if status == "成功":
                existing["download_count"] = existing.get("download_count", 1) + 1
            for key, value in kwargs.items():
                existing[key] = value

            # 移到最前面
            self._records.remove(existing)
            self._records.insert(0, existing)
            self._save()
            return existing["id"]

        # 创建新记录
        record_id = str(uuid.uuid4())[:8]
        record = {
            "id": record_id,
            "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "platform": platform,
            "url": url,
            "type": download_type,
            "status": status,
            "file_count": file_count,
            "mode": mode,
            "nickname": nickname,
            "download_count": 1,
            **kwargs,
        }
        self._records.insert(0, record)

        # 保留最近1000条记录
        if len(self._records) > 1000:
            self._records = self._records[:1000]

        self._save()
        return record_id

    def update_record(self, record_id: str, **kwargs):
        """更新历史记录"""
        for record in self._records:
            if record.get("id") == record_id:
                record.update(kwargs)
                self._save()
                break

    def get_record(self, record_id: str) -> Optional[Dict]:
        """获取单条记录"""
        for record in self._records:
            if record.get("id") == record_id:
                return record
        return None

    def get_all_records(self) -> List[Dict]:
        """获取所有记录"""
        return self._records.copy()

    def get_records_by_platform(self, platform: str) -> List[Dict]:
        """按平台获取记录"""
        return [r for r in self._records if r.get("platform") == platform]

    def get_records_by_mode(self, mode: str) -> List[Dict]:
        """按模式获取记录"""
        return [r for r in self._records if r.get("mode") == mode]

    def get_records_by_platform_and_mode(self, platform: str, mode: str) -> List[Dict]:
        """按平台和模式获取记录"""
        return [
            r
            for r in self._records
            if r.get("platform") == platform and r.get("mode") == mode
        ]

    def get_records_by_status(self, status: str) -> List[Dict]:
        """按状态获取记录"""
        return [r for r in self._records if r.get("status") == status]

    def get_records_filtered(
        self,
        platform: Optional[str] = None,
        mode: Optional[str] = None,
        status: Optional[str] = None,
        search: Optional[str] = None,
    ) -> List[Dict]:
        """多条件过滤获取记录"""
        results = self._records

        if platform and platform != "all":
            results = [r for r in results if r.get("platform") == platform]

        if mode and mode != "all":
            results = [r for r in results if r.get("mode") == mode]

        if status and status != "all":
            results = [r for r in results if r.get("status") == status]

        if search:
            search_lower = search.lower()
            results = [
                r
                for r in results
                if search_lower in r.get("nickname", "").lower()
                or search_lower in r.get("url", "").lower()
                or search_lower in r.get("user_id", "").lower()
            ]

        return results

    def delete_record(self, record_id: str):
        """删除记录"""
        self._records = [r for r in self._records if r.get("id") != record_id]
        self._save()

    def delete_records_by_mode(self, mode: str) -> int:
        """删除指定模式的所有记录"""
        original_count = len(self._records)
        self._records = [r for r in self._records if r.get("mode") != mode]
        deleted = original_count - len(self._records)
        if deleted > 0:
            self._save()
        return deleted

    def clear_all(self):
        """清空所有记录"""
        self._records = []
        self._save()

    def get_statistics(self) -> Dict[str, Any]:
        """获取统计信息"""
        total = len(self._records)
        success = len([r for r in self._records if r.get("status") == "成功"])
        failed = len([r for r in self._records if r.get("status") == "失败"])
        in_progress = len([r for r in self._records if r.get("status") == "进行中"])

        # 按平台统计
        platform_stats = {}
        for record in self._records:
            platform = record.get("platform", "unknown")
            platform_stats[platform] = platform_stats.get(platform, 0) + 1

        # 按模式统计
        mode_stats = {}
        for record in self._records:
            mode = record.get("mode", "unknown")
            mode_stats[mode] = mode_stats.get(mode, 0) + 1

        return {
            "total": total,
            "success": success,
            "failed": failed,
            "in_progress": in_progress,
            "by_platform": platform_stats,
            "by_mode": mode_stats,
        }

    def get_mode_statistics(self) -> Dict[str, int]:
        """获取按模式的统计"""
        stats = {}
        for record in self._records:
            mode = record.get("mode", "unknown")
            stats[mode] = stats.get(mode, 0) + 1
        return stats


# 全局实例
history_manager = HistoryManager()
