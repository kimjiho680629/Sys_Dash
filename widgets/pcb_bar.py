"""
화이트 & 다크 PCB AIDA64 센서 패널 스타일 플랫 프로그레스 바
클럭, 전압, 전력, VRAM, 스토리지 점유율 시각화 및 부드러운 쫀득 보간(Lerp) 애니메이션
"""

from PyQt6.QtWidgets import QWidget
from PyQt6.QtGui import QPainter, QPen, QColor, QBrush, QLinearGradient
from PyQt6.QtCore import Qt, QRectF, QTimer
from theme import WhitePCBColor, ThemeManager


class PCBProgressBar(QWidget):
    """
    레퍼런스 이미지 스타일 플랫 프로그레스 바 (부드러운 스프링 보간 애니메이션 내장)
    """
    def __init__(self, max_val=100.0, height=14, parent=None):
        super().__init__(parent)
        self.max_val = max_val
        self.curr_val = 0.0
        self.target_val = 0.0
        self.setFixedHeight(height)

        # 부드러운 수치 변화 보간 타이머 (약 40 FPS)
        self.anim_timer = QTimer(self)
        self.anim_timer.setInterval(25)
        self.anim_timer.timeout.connect(self._animate_step)

    def set_value(self, val):
        self.target_val = max(0.0, min(self.max_val, float(val)))
        if not self.anim_timer.isActive() and abs(self.target_val - self.curr_val) > 0.05:
            self.anim_timer.start()

    def _animate_step(self):
        diff = self.target_val - self.curr_val
        if abs(diff) < 0.1:
            self.curr_val = self.target_val
            self.anim_timer.stop()
        else:
            self.curr_val += diff * 0.25
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

        # 2. 채워진 바 (부드럽게 보간된 값)
        ratio = self.curr_val / self.max_val if self.max_val > 0 else 0
        fill_w = (w - 2) * ratio

        if fill_w > 0:
            fill_rect = QRectF(1, 1, fill_w, h - 2)
            if ThemeManager.is_dark():
                # 다크 모드: 세련된 네온 사이안 -> 딥 스카이블루 그라디언트
                grad = QLinearGradient(1, 1, fill_w, 1)
                grad.setColorAt(0.0, QColor(0, 160, 240))
                grad.setColorAt(1.0, WhitePCBColor.BAR_FILL)
                painter.setBrush(QBrush(grad))
            else:
                painter.setBrush(QBrush(WhitePCBColor.BAR_FILL))

            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawRect(fill_rect)
