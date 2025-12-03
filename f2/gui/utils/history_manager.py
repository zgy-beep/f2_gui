"""
历史记录管理器
~~~~~~~~~~~~~~

管理下载历史记录的存储和查询。
"""

import json
import os
import uuid
from datetime import datetime
from typing import List, Dict, Optional
from pathlib import Path


class HistoryManager:
    """历史记录管理器"""

    def __init__(self):
        self._history_file = self._get_history_file_path()
        self._records: List[Dict] = []
        self._load()

    def _get_history_file_path(self) -> Path:
        """获取历史记录文件路径"""
        # 使用 gui_v02 目录下的 download_history.json
        gui_dir = Path(__file__).parent.parent
        return gui_dir / "download_history.json"

    def _load(self):
        """加载历史记录"""
        try:
            if self._history_file.exists():
                # 使用 utf-8-sig 以支持带 BOM 的文件
                with open(self._history_file, "r", encoding="utf-8-sig") as f:
                    data = json.load(f)
                    self._records = data.get("records", [])
        except (json.JSONDecodeError, IOError) as e:
            print(f"加载历史记录失败: {e}")
            self._records = []

    def _save(self):
        """保存历史记录"""
        try:
            with open(self._history_file, "w", encoding="utf-8") as f:
                json.dump({"records": self._records}, f, ensure_ascii=False, indent=2)
        except IOError as e:
            print(f"保存历史记录失败: {e}")

    def _find_duplicate(self, platform: str, user_id: str, url: str) -> Optional[Dict]:
        """
        查找重复记录（基于 user_id 或 URL）
        
        Args:
            platform: 平台名称
            user_id: 用户ID
            url: 下载链接
            
        Returns:
            找到的重复记录，如果没有则返回 None
        """
        for record in self._records:
            if record.get("platform") != platform:
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
        download_type: str,
        status: str = "进行中",
        file_count: int = 0,
        mode: str = "one",
        nickname: str = "",
        **kwargs
    ) -> str:
        """
        添加历史记录（自动去重，相同用户只保留一条记录）

        Args:
            platform: 平台名称 (douyin, tiktok, weibo, twitter)
            url: 下载链接或用户标识
            download_type: 下载类型 (视频, 图片, 直播等)
            status: 状态 (进行中, 成功, 失败)
            file_count: 下载文件数量
            mode: 下载模式 (one, post, like, etc.)
            nickname: 用户昵称
            **kwargs: 其他自定义字段

        Returns:
            记录ID
        """
        user_id = kwargs.get("user_id", "")
        
        # 查找重复记录
        existing = self._find_duplicate(platform, user_id, url)
        
        if existing:
            # 更新现有记录而不是创建新记录
            existing["time"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            existing["status"] = status
            existing["file_count"] = file_count
            existing["nickname"] = nickname
            existing["url"] = url  # 更新 URL（可能从短链变成了长链）
            existing["download_count"] = existing.get("download_count", 1) + 1
            # 更新其他字段
            for key, value in kwargs.items():
                existing[key] = value
            
            # 将更新后的记录移到最前面
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
            **kwargs
        }
        self._records.insert(0, record)  # 新记录在前面

        # 保留最近1000条记录
        if len(self._records) > 1000:
            self._records = self._records[:1000]

        self._save()
        return record_id

    def update_record(self, record_id: str, **kwargs):
        """
        更新历史记录

        Args:
            record_id: 记录ID
            **kwargs: 要更新的字段
        """
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

    def get_records_by_status(self, status: str) -> List[Dict]:
        """按状态获取记录"""
        return [r for r in self._records if r.get("status") == status]

    def delete_record(self, record_id: str):
        """删除记录"""
        self._records = [r for r in self._records if r.get("id") != record_id]
        self._save()

    def clear_all(self):
        """清空所有记录"""
        self._records = []
        self._save()

    def get_statistics(self) -> Dict:
        """获取统计信息"""
        total = len(self._records)
        success = len([r for r in self._records if r.get("status") == "成功"])
        failed = len([r for r in self._records if r.get("status") == "失败"])
        in_progress = len([r for r in self._records if r.get("status") == "进行中"])

        platform_stats = {}
        for record in self._records:
            platform = record.get("platform", "unknown")
            platform_stats[platform] = platform_stats.get(platform, 0) + 1

        return {
            "total": total,
            "success": success,
            "failed": failed,
            "in_progress": in_progress,
            "by_platform": platform_stats
        }


# 全局实例
history_manager = HistoryManager()
