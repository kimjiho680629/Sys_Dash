"""
화이트 PCB AIDA64 스타일 미니 오실로스코프 그리드 그래프
0~100 눈금, 회색 격자선, 짙은 챠콜 실시간 파형
"""

from collections import deque
from PyQt6.QtWidgets import QWidget
from PyQt6.QtGui import QPainter, QPen, QColor, QBrush, QPainterPath
from PyQt6.QtCore import Qt, QRectF, QPointF
from theme import WhitePCBColor, get_font_regular, get_font_bold


class MiniScopeGraph(QWidget):
    """
    레퍼런스 이미지의 코어별/GPU별 0~100 눈금 미니 오실로스코프 그래프
    """
    def __init__(self, max_points=24, show_labels=True, parent=None):
        super().__init__(parent)
        self.max_points = max_points
        self.show_labels = show_labels
        self.data = deque([0.0] * max_points, maxlen=max_points)
        self.curr_val = 0.0
        self.setMinimumSize(42, 86)

    def add_point(self, val):
        self.curr_val = float(max(0.0, min(100.0, val)))
        self.data.append(self.curr_val)
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        w = float(self.width())
        h = float(self.height())

        m_top = 12.0 if self.show_labels else 4.0
        m_bottom = 12.0 if self.show_labels else 4.0
        m_left = 2.0
        m_right = 2.0

        plot_w = w - m_left - m_right
        plot_h = h - m_top - m_bottom

        # 1. 외곽 사각 프레임
        painter.setBrush(QBrush(Qt.GlobalColor.white))
        painter.setPen(QPen(WhitePCBColor.BORDER_MAIN, 1.2))
        painter.drawRect(QRectF(m_left, m_top, plot_w, plot_h))

        # 2. 회색 격자선 (가로 3등분, 세로 2등분)
        painter.setPen(QPen(WhitePCBColor.GRID_LINE, 0.8))
        # 수평선
        painter.drawLine(QPointF(m_left, m_top + plot_h * 0.5), QPointF(m_left + plot_w, m_top + plot_h * 0.5))
        # 수직선
        painter.drawLine(QPointF(m_left + plot_w * 0.33, m_top), QPointF(m_left + plot_w * 0.33, m_top + plot_h))
        painter.drawLine(QPointF(m_left + plot_w * 0.66, m_top), QPointF(m_left + plot_w * 0.66, m_top + plot_h))

        # 3. 0과 100 눈금 숫자 (레퍼런스 이미지처럼 좌상단 100, 좌하단 0)
        if self.show_labels:
            painter.setFont(get_font_regular(7))
            painter.setPen(QPen(WhitePCBColor.TEXT_MUTED))
            painter.drawText(QRectF(m_left + 1, 0, 22, 11), Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter, "100")
            painter.drawText(QRectF(m_left + 1, h - 11, 22, 11), Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter, "0")

        # 4. 실시간 챠콜 파형 라인
        if len(self.data) >= 2:
            path = QPainterPath()
            dx = plot_w / (self.max_points - 1)
            pts = []
            for i, val in enumerate(self.data):
                x = m_left + i * dx
                ratio = val / 100.0
                y = m_top + plot_h * (1.0 - ratio)
                pts.append(QPointF(x, y))

            path.moveTo(pts[0])
            for i in range(1, len(pts)):
                path.lineTo(pts[i])

            painter.setPen(QPen(WhitePCBColor.TEXT_MAIN, 1.4))
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.drawPath(path)
