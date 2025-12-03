"""
基础卡片组件
~~~~~~~~~~~

可复用的基础卡片组件,扁平化现代设计。
"""

from PyQt6.QtWidgets import QFrame, QVBoxLayout, QGraphicsDropShadowEffect
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor

from f2.gui.config import CARD_BORDER_RADIUS


class BaseCard(QFrame):
    """基础卡片组件 - 扁平设计"""

    def __init__(self, parent=None, elevated: bool = False):
        super().__init__(parent)
        self._elevated = elevated
        self._setup_ui()

    def _setup_ui(self):
        """设置UI"""
        self.setObjectName("Card")

        # 设置布局 - 紧凑内边距
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(10, 8, 10, 8)
        self.layout.setSpacing(6)

        self.setFrameShape(QFrame.Shape.NoFrame)

        # 仅在需要时添加轻微阴影
        if self._elevated:
            self._add_shadow_effect()

    def _add_shadow_effect(self):
        """添加轻微阴影效果"""
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(8)
        shadow.setXOffset(0)
        shadow.setYOffset(1)
        shadow.setColor(QColor(0, 0, 0, 20))
        self.setGraphicsEffect(shadow)

    def set_elevated(self, elevated: bool):
        """设置是否显示阴影"""
        self._elevated = elevated
        if elevated:
            self._add_shadow_effect()
        else:
            self.setGraphicsEffect(None)
