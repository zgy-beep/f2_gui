"""
GUI日志管理器
~~~~~~~~~~~~

管理GUI应用的日志记录和显示。
"""

from datetime import datetime
from typing import Optional, Callable
from enum import Enum


class LogLevel(Enum):
    """日志级别"""

    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    SUCCESS = "SUCCESS"


class LogMessage:
    """日志消息"""

    def __init__(self, level: LogLevel, message: str):
        self.level = level
        self.message = message
        self.timestamp = datetime.now()

    def format(self) -> str:
        """格式化日志消息"""
        time_str = self.timestamp.strftime("%H:%M:%S")
        return f"[{time_str}] [{self.level.value}] {self.message}"


class GUILogger:
    """GUI日志管理器"""

    def __init__(self, max_messages: int = 1000):
        self.max_messages = max_messages
        self._messages = []
        self._callbacks = []

    def add_callback(self, callback: Callable[[LogMessage], None]):
        """添加日志回调"""
        self._callbacks.append(callback)

    def remove_callback(self, callback: Callable[[LogMessage], None]):
        """移除日志回调"""
        if callback in self._callbacks:
            self._callbacks.remove(callback)

    def _log(self, level: LogLevel, message: str):
        """记录日志"""
        log_msg = LogMessage(level, message)
        self._messages.append(log_msg)

        # 限制日志数量
        if len(self._messages) > self.max_messages:
            self._messages = self._messages[-self.max_messages :]

        # 通知所有回调
        for callback in self._callbacks:
            try:
                callback(log_msg)
            except Exception as e:
                print(f"日志回调出错: {e}")

    def debug(self, message: str):
        """调试日志"""
        self._log(LogLevel.DEBUG, message)

    def info(self, message: str):
        """信息日志"""
        self._log(LogLevel.INFO, message)

    def warning(self, message: str):
        """警告日志"""
        self._log(LogLevel.WARNING, message)

    def error(self, message: str):
        """错误日志"""
        self._log(LogLevel.ERROR, message)

    def success(self, message: str):
        """成功日志"""
        self._log(LogLevel.SUCCESS, message)

    def get_messages(self, level: Optional[LogLevel] = None) -> list:
        """获取日志消息"""
        if level is None:
            return self._messages.copy()
        return [msg for msg in self._messages if msg.level == level]

    def clear(self):
        """清空日志"""
        self._messages.clear()

    def export_to_file(self, file_path: str) -> bool:
        """导出日志到文件"""
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                for msg in self._messages:
                    f.write(msg.format() + "\n")
            return True
        except Exception as e:
            self.error(f"导出日志失败: {e}")
            return False


# 全局日志实例
gui_logger = GUILogger()
