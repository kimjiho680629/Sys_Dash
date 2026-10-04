"""
화이트 & 다크 PCB 패널 프레임 및 중앙 시계/로고 엠블럼 바
"""

import time
import math
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QFrame
from PyQt6.QtGui import QPainter, QPen, QColor, QBrush, QPolygonF, QPainterPath
from PyQt6.QtCore import Qt, QRectF, QPointF, QTimer
from theme import WhitePCBColor, ThemeManager, get_font_bold, get_font_regular


class PCBPanelFrame(QFrame):
    """
    화이트 & 다크 패널 프레임 (사선 챔퍼 지원)
    """
    def __init__(self, chamfer_tl=False, chamfer_br=False, parent=None):
        super().__init__(parent)
        self.chamfer_tl = chamfer_tl
        self.chamfer_br = chamfer_br
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        ThemeManager.register_listener(self.update)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        w = float(self.width())
        h = float(self.height())
        cut = 12.0

        pts = []
        if self.chamfer_tl:
            pts.extend([QPointF(cut, 0), QPointF(w, 0)])
        else:
            pts.extend([QPointF(0, 0), QPointF(w, 0)])

        if self.chamfer_br:
            pts.extend([QPointF(w, h - cut), QPointF(w - cut, h), QPointF(0, h)])
        else:
            pts.extend([QPointF(w, h), QPointF(0, h)])

        if self.chamfer_tl:
            pts.append(QPointF(0, cut))

        poly = QPolygonF(pts)
        painter.setBrush(QBrush(WhitePCBColor.BG_PANEL))
        painter.setPen(QPen(WhitePCBColor.BORDER_MAIN, 2.5))
        painter.drawPolygon(poly)


class ClockLogoBar(QWidget):
    """
    중앙 사선 챔퍼 디지털 시계 & 엠블럼 로고 바 (부드러운 하트비트 펄스 내장)
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(54)
        self.clock_str = time.strftime("%I:%M %p")
        self.date_str = time.strftime("%Y-%m-%d")
        self.glow_phase = 0.0

        self.timer = QTimer(self)
        self.timer.timeout.connect(self._tick)
        self.timer.start(50)  # 50ms마다 부드러운 글로우 애니메이션

        ThemeManager.register_listener(self.update)

    def _tick(self):
        self.glow_phase = (self.glow_phase + 0.06) % (math.pi * 2)
        h = int(time.strftime("%I"))
        m = time.strftime("%M")
        ampm = "AM" if time.strftime("%p") in ("AM", "오전") else "PM"
        self.clock_str = f"{h}:{m} {ampm}"
        self.date_str = time.strftime("%Y-%m-%d")
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        w = float(self.width())
        h = float(self.height())
        cut = 16.0
        is_dark = ThemeManager.is_dark()

        # 사선 챔퍼 프레임
        poly = QPolygonF([
            QPointF(0, 0),
            QPointF(w - cut, 0),
            QPointF(w, cut),
            QPointF(w, h),
            QPointF(cut, h),
            QPointF(0, h - cut)
        ])
        painter.setBrush(QBrush(WhitePCBColor.BG_PANEL))
        painter.setPen(QPen(WhitePCBColor.BORDER_MAIN, 2.5))
        painter.drawPolygon(poly)

        # 좌측 디지털 시계 (굵은 볼드 폰트)
        painter.setFont(get_font_bold(20))
        painter.setPen(QPen(WhitePCBColor.TEXT_MAIN))
        painter.drawText(QRectF(16, 0, w * 0.55, h), Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft, self.clock_str)

        # 우측 게이밍 로고 엠블럼 (사이버틱한 게이밍 팔콘 엠블럼 + 미세 글로우)
        cx = w * 0.72
        cy = h / 2.0
        logo_poly = QPolygonF([
            QPointF(cx - 14, cy + 8),
            QPointF(cx - 4, cy - 10),
            QPointF(cx + 8, cy - 8),
            QPointF(cx + 2, cy - 2),
            QPointF(cx + 14, cy + 4),
            QPointF(cx, cy + 10)
        ])
        
        if is_dark:
            # 다크 모드에서는 로고에 은은한 사이안/바이올렛 글로우 효과
            pulse = (math.sin(self.glow_phase) + 1.0) / 2.0
            logo_color = QColor(0, int(180 + pulse * 50), 255)
        else:
            logo_color = WhitePCBColor.TEXT_MAIN

        painter.setBrush(QBrush(logo_color))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawPolygon(logo_poly)

        # 최우측 날짜 텍스트
        painter.setFont(get_font_bold(11))
        painter.setPen(QPen(WhitePCBColor.TEXT_SUB))
        painter.drawText(QRectF(w * 0.78, 0, w * 0.20, h), Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignRight, self.date_str)
