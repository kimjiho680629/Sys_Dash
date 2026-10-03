"""
화이트 PCB 패널 프레임 및 중앙 시계/로고 엠블럼 바
"""

import time
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QFrame
from PyQt6.QtGui import QPainter, QPen, QColor, QBrush, QPolygonF, QPainterPath
from PyQt6.QtCore import Qt, QRectF, QPointF, QTimer
from theme import WhitePCBColor, get_font_bold, get_font_regular


class PCBPanelFrame(QFrame):
    """
    레퍼런스 이미지의 화이트 패널 프레임
    """
    def __init__(self, chamfer_tl=False, chamfer_br=False, parent=None):
        super().__init__(parent)
        self.chamfer_tl = chamfer_tl
        self.chamfer_br = chamfer_br
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

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
    레퍼런스 이미지 중앙의 사선 챔퍼 디지털 시계 & 엠블럼 로고 바
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(54)
        self.clock_str = time.strftime("%I:%M %p")
        self.date_str = time.strftime("%Y-%m-%d")

        self.timer = QTimer(self)
        self.timer.timeout.connect(self._tick)
        self.timer.start(1000)

    def _tick(self):
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

        # 좌측 디지털 시계 (레퍼런스 스타일: 굵은 볼드 폰트)
        painter.setFont(get_font_bold(20))
        painter.setPen(QPen(WhitePCBColor.TEXT_MAIN))
        painter.drawText(QRectF(16, 0, w * 0.55, h), Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft, self.clock_str)

        # 우측 게이밍 로고 엠블럼 (날렵한 기하학적 독수리/게이밍 팔콘 엠블럼)
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
        painter.setBrush(QBrush(WhitePCBColor.TEXT_MAIN))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawPolygon(logo_poly)

        # 최우측 날짜 텍스트 (2026-10-04)
        painter.setFont(get_font_bold(10))
        painter.setPen(QPen(WhitePCBColor.TEXT_SUB))
        painter.drawText(QRectF(w * 0.78, 0, w * 0.20, h), Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignRight, self.date_str)
