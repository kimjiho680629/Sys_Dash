"""
상단 사이버펑크 HUD 헤더 바 위젯
디지털 시계, 시스템 업타임, 하드웨어 스펙 배지, 깜빡이는 상태 LED
"""

import time
from PyQt6.QtWidgets import QWidget
from PyQt6.QtGui import QPainter, QPen, QColor, QBrush, QPolygonF
from PyQt6.QtCore import Qt, QRectF, QPointF, QTimer
from theme import HUDColor, get_font_mono, get_font_display


class HUDHeaderBar(QWidget):
    """
    사이버펑크 최상단 시스템 텔레메트리 헤더
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(50)
        self.uptime_str = "00h 00m 00s"
        self.clock_str = time.strftime("%H:%M:%S")
        self.date_str = time.strftime("%Y.%m.%d")
        self.led_blink = True

        # 시계 및 블링크 타이머 (1초 주기)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._tick)
        self.timer.start(1000)

    def _tick(self):
        self.clock_str = time.strftime("%H:%M:%S")
        self.date_str = time.strftime("%Y.%m.%d")
        self.led_blink = not self.led_blink
        self.update()

    def set_uptime(self, uptime_str):
        self.uptime_str = uptime_str
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        w = float(self.width())
        h = float(self.height())

        # 1. 헤더 배경 (하단 사각 모서리 챔퍼 컷)
        cut = 15.0
        poly = QPolygonF([
            QPointF(0, 0),
            QPointF(w, 0),
            QPointF(w, h - cut),
            QPointF(w - cut, h),
            QPointF(cut, h),
            QPointF(0, h - cut)
        ])
        painter.setBrush(QBrush(HUDColor.BG_PANEL))
        painter.setPen(QPen(HUDColor.BORDER_HUD, 1.2))
        painter.drawPolygon(poly)

        # 하단 네온 라인
        painter.setPen(QPen(HUDColor.CYAN, 1.5))
        painter.drawLine(QPointF(cut, h), QPointF(w - cut, h))

        # 2. 좌측: 시스템 로고 & 타이틀
        painter.setFont(get_font_display(14, bold=True))
        painter.setPen(QPen(HUDColor.CYAN))
        painter.drawText(QRectF(20, 10, 140, 30), Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft, "SYSTEM HUD //")

        painter.setFont(get_font_mono(10, bold=True))
        painter.setPen(QPen(HUDColor.TEXT_TITLE))
        painter.drawText(QRectF(168, 10, 280, 30), Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft, "TELEMETRY TERMINAL")

        # 3. 중앙: 하드웨어 스펙 배지
        painter.setFont(get_font_mono(9, bold=True))
        badge_w = 460
        badge_x = (w - badge_w) / 2.0
        painter.setBrush(QBrush(HUDColor.BG_CARD))
        painter.setPen(QPen(HUDColor.BORDER_DIM, 1.0))
        painter.drawRoundedRect(QRectF(badge_x, 10, badge_w, 28), 4, 4)

        # 칩셋 텍스트
        painter.setPen(QPen(HUDColor.TEXT_SECONDARY))
        painter.drawText(QRectF(badge_x + 10, 10, badge_w - 20, 28), Qt.AlignmentFlag.AlignCenter,
                         "RYZEN 7 9800X3D (8C/16T)  |  RTX 5070 Ti 16GB")

        # 4. 우측: 상태 LED, 업타임 및 디지털 시계
        right_x = w - 380

        # 상태 LED
        led_color = HUDColor.GREEN if self.led_blink else HUDColor.CYAN
        painter.setBrush(QBrush(led_color))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(QPointF(right_x, 24), 4, 4)

        painter.setFont(get_font_mono(8, bold=True))
        painter.setPen(QPen(HUDColor.GREEN))
        painter.drawText(QRectF(right_x + 12, 10, 90, 28), Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft, "SYSTEM ONLINE")

        # 업타임
        painter.setPen(QPen(HUDColor.TEXT_MUTED))
        painter.drawText(QRectF(right_x + 105, 10, 130, 28), Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft,
                         f"UPTIME: {self.uptime_str}")

        # 디지털 시계
        painter.setFont(get_font_display(13, bold=True))
        painter.setPen(QPen(HUDColor.CYAN))
        painter.drawText(QRectF(w - 110, 10, 95, 28), Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignRight, self.clock_str)
