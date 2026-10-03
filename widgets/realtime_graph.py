"""
사이버펑크 네온 스트리밍 실시간 파형 그래프 위젯
부드러운 베지어 곡선, 수직 네온 그라디언트 채우기, 듀얼 트랙 지원
"""

from collections import deque
from PyQt6.QtWidgets import QWidget
from PyQt6.QtGui import QPainter, QPen, QColor, QBrush, QPainterPath, QLinearGradient
from PyQt6.QtCore import Qt, QRectF, QPointF
from theme import HUDColor, get_font_mono


class RealtimeGraph(QWidget):
    """
    실시간 스파크라인 / 파형 그래프 (단일 또는 듀얼 라인)
    """
    def __init__(self, title="ACTIVITY", max_points=60, max_val=100.0,
                 auto_scale=False,
                 color1=HUDColor.CYAN, label1="CPU",
                 color2=None, label2=None, parent=None):
        super().__init__(parent)
        self.title = title
        self.max_points = max_points
        self.max_val = max_val
        self.auto_scale = auto_scale

        self.color1 = color1
        self.label1 = label1
        self.color2 = color2
        self.label2 = label2

        self.data1 = deque([0.0] * max_points, maxlen=max_points)
        self.data2 = deque([0.0] * max_points, maxlen=max_points) if color2 else None

        self.curr_val1 = 0.0
        self.curr_val2 = 0.0

        self.setMinimumHeight(110)

    def add_point(self, val1, val2=None):
        self.curr_val1 = float(val1)
        self.data1.append(self.curr_val1)

        if self.data2 is not None and val2 is not None:
            self.curr_val2 = float(val2)
            self.data2.append(self.curr_val2)

        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        w = float(self.width())
        h = float(self.height())

        # 그래프 영역 마진
        m_top = 22.0
        m_bottom = 12.0
        m_left = 8.0
        m_right = 8.0

        plot_w = w - m_left - m_right
        plot_h = h - m_top - m_bottom

        # 1. 배경 프레임 및 수평 그리드선
        painter.setBrush(QBrush(HUDColor.BG_CARD))
        painter.setPen(QPen(HUDColor.BORDER_DIM, 0.5))
        painter.drawRect(QRectF(m_left, m_top, plot_w, plot_h))

        # 그리드선 (25%, 50%, 75%)
        painter.setPen(QPen(HUDColor.GRID_LINE, 1.0, Qt.PenStyle.DashLine))
        for ratio in [0.25, 0.5, 0.75]:
            gy = m_top + plot_h * (1.0 - ratio)
            painter.drawLine(QPointF(m_left, gy), QPointF(m_left + plot_w, gy))

        # 2. 오토스케일 계산
        peak_val = self.max_val
        if self.auto_scale:
            max_pt = max(self.data1)
            if self.data2:
                max_pt = max(max_pt, max(self.data2))
            peak_val = max(1.0, max_pt * 1.2)

        # 3. 라인 & 그라디언트 렌더링 헬퍼 함수
        def draw_series(data_queue, stroke_color, is_primary=True):
            if len(data_queue) < 2:
                return

            pts = []
            dx = plot_w / (self.max_points - 1)
            for i, val in enumerate(data_queue):
                x = m_left + i * dx
                ratio = min(1.0, max(0.0, val / peak_val))
                y = m_top + plot_h * (1.0 - ratio)
                pts.append(QPointF(x, y))

            # 베지어 곡선 패스 생성
            path = QPainterPath()
            path.moveTo(pts[0])
            for i in range(1, len(pts)):
                p_prev = pts[i - 1]
                p_curr = pts[i]
                cx = (p_prev.x() + p_curr.x()) / 2.0
                path.cubicTo(QPointF(cx, p_prev.y()), QPointF(cx, p_curr.y()), p_curr)

            # 아래 채우기 영역 (Fill Path)
            fill_path = QPainterPath(path)
            fill_path.lineTo(pts[-1].x(), m_top + plot_h)
            fill_path.lineTo(pts[0].x(), m_top + plot_h)
            fill_path.closeSubpath()

            grad = QLinearGradient(0, m_top, 0, m_top + plot_h)
            alpha_top = 40 if is_primary else 25
            grad.setColorAt(0.0, QColor(stroke_color.red(), stroke_color.green(), stroke_color.blue(), alpha_top))
            grad.setColorAt(1.0, QColor(stroke_color.red(), stroke_color.green(), stroke_color.blue(), 2))

            painter.setBrush(QBrush(grad))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawPath(fill_path)

            # 글로우 스트로크
            glow_pen = QPen(QColor(stroke_color.red(), stroke_color.green(), stroke_color.blue(), 70), 3.5)
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.setPen(glow_pen)
            painter.drawPath(path)

            # 본체 메인 라인
            main_pen = QPen(stroke_color, 1.8)
            painter.setPen(main_pen)
            painter.drawPath(path)

        # 4. 데이터 시리즈 그리기
        if self.data2:
            draw_series(self.data2, self.color2, is_primary=False)
        draw_series(self.data1, self.color1, is_primary=True)

        # 5. 헤더 라벨 및 현재 수치
        painter.setFont(get_font_mono(8, bold=True))
        # 타이틀
        painter.setPen(QPen(HUDColor.TEXT_MUTED))
        painter.drawText(QRectF(m_left + 4, 3, 220, 16), Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft, self.title)

        # 라벨1 및 수치
        rx = w - m_right
        v1_str = f"{self.label1}: {self.curr_val1:.1f}" if self.auto_scale else f"{self.label1}: {int(round(self.curr_val1))}%"
        painter.setPen(QPen(self.color1))
        painter.drawText(QRectF(rx - 110, 3, 110, 16), Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignRight, v1_str)

        # 라벨2 및 수치
        if self.data2 and self.label2:
            v2_str = f"{self.label2}: {self.curr_val2:.1f}" if self.auto_scale else f"{self.label2}: {int(round(self.curr_val2))}%"
            painter.setPen(QPen(self.color2))
            painter.drawText(QRectF(rx - 220, 3, 100, 16), Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignRight, v2_str)
