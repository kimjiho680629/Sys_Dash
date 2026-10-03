"""
화이트 PCB AIDA64 센서 패널 스타일 플랫 프로그레스 바
클럭, 전압, 전력, VRAM, 스토리지 점유율 시각화
"""

from PyQt6.QtWidgets import QWidget
from PyQt6.QtGui import QPainter, QPen, QColor, QBrush
from PyQt6.QtCore import Qt, QRectF
from theme import WhitePCBColor


class PCBProgressBar(QWidget):
    """
    레퍼런스 이미지의 플랫 챠콜 그레이 프로그레스 바
    """
    def __init__(self, max_val=100.0, height=14, parent=None):
        super().__init__(parent)
        self.max_val = max_val
        self.curr_val = 0.0
        self.setFixedHeight(height)

    def set_value(self, val):
        self.curr_val = max(0.0, min(self.max_val, float(val)))
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        w = float(self.width())
        h = float(self.height())

        # 1. 외곽 사각 테두리 & 배경 슬롯
        painter.setBrush(QBrush(WhitePCBColor.BAR_BG))
        painter.setPen(QPen(WhitePCBColor.BORDER_MAIN, 1.2))
        painter.drawRect(QRectF(1, 1, w - 2, h - 2))

        # 2. 채워진 챠콜 바
        ratio = self.curr_val / self.max_val if self.max_val > 0 else 0
        fill_w = (w - 2) * ratio

        if fill_w > 0:
            painter.setBrush(QBrush(WhitePCBColor.BAR_FILL))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawRect(QRectF(1, 1, fill_w, h - 2))
