"""
화이트 & 다크 PCB AIDA64 스타일 미니 오실로스코프 그리드 그래프
0~100 눈금, 회색/다크 격자선, 실시간 파형 및 다크 모드 네온 사이안 글로우
"""

from collections import deque
from PyQt6.QtWidgets import QWidget
from PyQt6.QtGui import QPainter, QPen, QColor, QBrush, QPainterPath, QLinearGradient
from PyQt6.QtCore import Qt, QRectF, QPointF
from theme import WhitePCBColor, ThemeManager, get_font_regular, get_font_bold


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

        m_top = 13.0 if self.show_labels else 4.0
        m_bottom = 13.0 if self.show_labels else 4.0
        m_left = 2.0
        m_right = 2.0

        plot_w = w - m_left - m_right
        plot_h = h - m_top - m_bottom

        # 1. 외곽 사각 프레임 및 배경
        painter.setBrush(QBrush(WhitePCBColor.GRAPH_BG))
        painter.setPen(QPen(WhitePCBColor.BORDER_MAIN, 1.2))
        painter.drawRect(QRectF(m_left, m_top, plot_w, plot_h))

        # 2. 격자선 (가로 3등분, 세로 2등분)
        painter.setPen(QPen(WhitePCBColor.GRID_LINE, 0.8))
        # 수평선
        painter.drawLine(QPointF(m_left, m_top + plot_h * 0.5), QPointF(m_left + plot_w, m_top + plot_h * 0.5))
        # 수직선
        painter.drawLine(QPointF(m_left + plot_w * 0.33, m_top), QPointF(m_left + plot_w * 0.33, m_top + plot_h))
        painter.drawLine(QPointF(m_left + plot_w * 0.66, m_top), QPointF(m_left + plot_w * 0.66, m_top + plot_h))

        # 3. 0과 100 눈금 숫자
        if self.show_labels:
            painter.setFont(get_font_regular(8))
            painter.setPen(QPen(WhitePCBColor.TEXT_MUTED))
            painter.drawText(QRectF(m_left + 1, 0, 24, 12), Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter, "100")
            painter.drawText(QRectF(m_left + 1, h - 12, 24, 12), Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter, "0")

        # 4. 실시간 파형 라인 및 반투명 영역 채움
        if len(self.data) >= 2:
            path = QPainterPath()
            fill_path = QPainterPath()
            dx = plot_w / (self.max_points - 1)
            pts = []
            for i, val in enumerate(self.data):
                x = m_left + i * dx
                ratio = val / 100.0
                y = m_top + plot_h * (1.0 - ratio)
                pts.append(QPointF(x, y))

            path.moveTo(pts[0])
            fill_path.moveTo(pts[0].x(), m_top + plot_h)
            fill_path.lineTo(pts[0])
            for i in range(1, len(pts)):
                path.lineTo(pts[i])
                fill_path.lineTo(pts[i])
            fill_path.lineTo(pts[-1].x(), m_top + plot_h)
            fill_path.closeSubpath()

            # 다크 모드에서는 오실로스코프 파형 아래 은은한 네온 사이안 그라디언트 채우기
            if ThemeManager.is_dark():
                grad = QLinearGradient(0, m_top, 0, m_top + plot_h)
                grad.setColorAt(0.0, QColor(0, 230, 255, 60))
                grad.setColorAt(1.0, QColor(0, 230, 255, 5))
                painter.setBrush(QBrush(grad))
                painter.setPen(Qt.PenStyle.NoPen)
                painter.drawPath(fill_path)
                
                wave_color = QColor(0, 220, 255)
                painter.setPen(QPen(wave_color, 1.5))
            else:
                wave_color = WhitePCBColor.TEXT_MAIN
                painter.setPen(QPen(wave_color, 1.4))

            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.drawPath(path)
