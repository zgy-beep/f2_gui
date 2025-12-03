"""
任务管理器
~~~~~~~~~

管理下载任务的状态和队列。
"""

from typing import Dict, List, Optional
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


class TaskStatus(Enum):
    """任务状态枚举"""

    PENDING = "pending"  # 等待中
    DOWNLOADING = "downloading"  # 下载中
    PAUSED = "paused"  # 已暂停
    COMPLETED = "completed"  # 已完成
    ERROR = "error"  # 出错
    CANCELLED = "cancelled"  # 已取消


@dataclass
class DownloadTask:
    """下载任务数据类"""

    task_id: str
    platform: str
    mode: str
    url: str
    title: str = ""
    status: TaskStatus = TaskStatus.PENDING
    current: int = 0
    total: int = 0
    created_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    finished_at: Optional[datetime] = None
    error_message: str = ""

    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            "task_id": self.task_id,
            "platform": self.platform,
            "mode": self.mode,
            "url": self.url,
            "title": self.title,
            "status": self.status.value,
            "current": self.current,
            "total": self.total,
            "created_at": self.created_at.isoformat(),
            "started_at": self.started_at.isoformat()
            if self.started_at
            else None,
            "finished_at": self.finished_at.isoformat()
            if self.finished_at
            else None,
            "error_message": self.error_message,
        }


class TaskManager:
    """任务管理器"""

    def __init__(self):
        self._tasks: Dict[str, DownloadTask] = {}

    def add_task(
        self,
        task_id: str,
        platform: str,
        mode: str,
        url: str,
        title: str = "",
    ) -> DownloadTask:
        """添加任务"""
        task = DownloadTask(
            task_id=task_id,
            platform=platform,
            mode=mode,
            url=url,
            title=title,
        )
        self._tasks[task_id] = task
        return task

    def get_task(self, task_id: str) -> Optional[DownloadTask]:
        """获取任务"""
        return self._tasks.get(task_id)

    def update_task_status(self, task_id: str, status: TaskStatus):
        """更新任务状态"""
        if task_id in self._tasks:
            task = self._tasks[task_id]
            task.status = status

            if status == TaskStatus.DOWNLOADING and task.started_at is None:
                task.started_at = datetime.now()
            elif status in [TaskStatus.COMPLETED, TaskStatus.ERROR, TaskStatus.CANCELLED]:
                task.finished_at = datetime.now()

    def update_task_progress(self, task_id: str, current: int, total: int):
        """更新任务进度"""
        if task_id in self._tasks:
            task = self._tasks[task_id]
            task.current = current
            task.total = total

    def set_task_error(self, task_id: str, error_message: str):
        """设置任务错误"""
        if task_id in self._tasks:
            task = self._tasks[task_id]
            task.status = TaskStatus.ERROR
            task.error_message = error_message
            task.finished_at = datetime.now()

    def remove_task(self, task_id: str):
        """移除任务"""
        if task_id in self._tasks:
            del self._tasks[task_id]

    def get_all_tasks(self) -> List[DownloadTask]:
        """获取所有任务"""
        return list(self._tasks.values())

    def get_tasks_by_status(self, status: TaskStatus) -> List[DownloadTask]:
        """根据状态获取任务"""
        return [task for task in self._tasks.values() if task.status == status]

    def get_statistics(self) -> dict:
        """获取统计信息"""
        total = len(self._tasks)
        downloading = len(self.get_tasks_by_status(TaskStatus.DOWNLOADING))
        completed = len(self.get_tasks_by_status(TaskStatus.COMPLETED))
        error = len(self.get_tasks_by_status(TaskStatus.ERROR))

        return {
            "total": total,
            "downloading": downloading,
            "completed": completed,
            "error": error,
            "pending": len(self.get_tasks_by_status(TaskStatus.PENDING)),
            "paused": len(self.get_tasks_by_status(TaskStatus.PAUSED)),
        }

    def clear_completed(self):
        """清除已完成的任务"""
        completed_ids = [
            task.task_id
            for task in self._tasks.values()
            if task.status == TaskStatus.COMPLETED
        ]
        for task_id in completed_ids:
            del self._tasks[task_id]

    def clear_all(self):
        """清除所有任务"""
        self._tasks.clear()
