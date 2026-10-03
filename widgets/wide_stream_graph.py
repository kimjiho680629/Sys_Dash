"""
와이드 60초 실시간 오실로스코프 듀얼 스트림 그래프 및 프로세스 센티넬 위젯
화면의 절반을 시원하게 채우는 고정밀 베지어 곡선 및 하단 TOP 5 프로세스 테이블
"""

from collections import deque
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout
from PyQt6.QtGui import QPainter, QPen, QColor, QBrush, QPainterPath, QLinearGradient
from PyQt6.QtCore import Qt, QRectF, QPointF
from theme import HUDColor, get_font_mono, get_font_display
from widgets.process_table import TopProcessTable


class WideOscilloscopeGraph(QWidget):
    """
    초광폭 60초 CPU vs GPU 듀얼 파형 그래프
    """
    def __init__(self, max_points=75, parent=None):
        super().__init__(parent)
        self.max_points = max_points
        self.cpu_data = deque([0.0] * max_points, maxlen=max_points)
        self.gpu_data = deque([0.0] * max_points, maxlen=max_points)
        self.curr_cpu = 0.0
        self.curr_gpu = 0.0
        self.setMinimumHeight(150)

    def add_points(self, cpu_p, gpu_p):
        self.curr_cpu = float(cpu_p)
        self.curr_gpu = float(gpu_p)
        self.cpu_data.append(self.curr_cpu)
        self.gpu_data.append(self.curr_gpu)
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        w = float(self.width())
        h = float(self.height())

        m_top = 22.0
        m_bottom = 14.0
        m_left = 10.0
        m_right = 10.0

        plot_w = w - m_left - m_right
        plot_h = h - m_top - m_bottom

        # 1. 배경 프레임 및 수평/수직 하이테크 그리드
        painter.setBrush(QBrush(HUDColor.BG_CARD))
        painter.setPen(QPen(HUDColor.BORDER_DIM, 0.8))
        painter.drawRect(QRectF(m_left, m_top, plot_w, plot_h))

        # 수평 그리드선 (25%, 50%, 75%)
        painter.setPen(QPen(HUDColor.GRID_LINE, 1.0, Qt.PenStyle.DashLine))
        for ratio in [0.25, 0.5, 0.75]:
            gy = m_top + plot_h * (1.0 - ratio)
            painter.drawLine(QPointF(m_left, gy), QPointF(m_left + plot_w, gy))

        # 수직 시간 마커선 (15초 단위)
        for i in range(1, 4):
            gx = m_left + (plot_w / 4.0) * i
            painter.drawLine(QPointF(gx, m_top), QPointF(gx, m_top + plot_h))

        # 2. 곡선 드로잉 헬퍼
        def draw_wave(data_q, stroke_c, alpha_fill):
            if len(data_q) < 2:
                return

            pts = []
            dx = plot_w / (self.max_points - 1)
            for i, val in enumerate(data_q):
                x = m_left + i * dx
                ratio = min(1.0, max(0.0, val / 100.0))
                y = m_top + plot_h * (1.0 - ratio)
                pts.append(QPointF(x, y))

            path = QPainterPath()
            path.moveTo(pts[0])
            for i in range(1, len(pts)):
                p0 = pts[i - 1]
                p1 = pts[i]
                cx = (p0.x() + p1.x()) / 2.0
                path.cubicTo(QPointF(cx, p0.y()), QPointF(cx, p1.y()), p1)

            # 아래 채우기 (Fill)
            fill_path = QPainterPath(path)
            fill_path.lineTo(pts[-1].x(), m_top + plot_h)
            fill_path.lineTo(pts[0].x(), m_top + plot_h)
            fill_path.closeSubpath()

            grad = QLinearGradient(0, m_top, 0, m_top + plot_h)
            grad.setColorAt(0.0, QColor(stroke_c.red(), stroke_c.green(), stroke_c.blue(), alpha_fill))
            grad.setColorAt(1.0, QColor(stroke_c.red(), stroke_c.green(), stroke_c.blue(), 2))
            painter.setBrush(QBrush(grad))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawPath(fill_path)

            # 네온 외곽 글로우
            glow_pen = QPen(QColor(stroke_c.red(), stroke_c.green(), stroke_c.blue(), 80), 4.0)
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.setPen(glow_pen)
            painter.drawPath(path)

            # 메인 스트로크
            main_pen = QPen(stroke_c, 2.0)
            painter.setPen(main_pen)
            painter.drawPath(path)

        # GPU 파형 (마젠타)
        draw_wave(self.gpu_data, HUDColor.MAGENTA, 45)
        # CPU 파형 (시안)
        draw_wave(self.cpu_data, HUDColor.CYAN, 60)

        # 3. 헤더 인디케이터
        painter.setFont(get_font_mono(8, bold=True))
        painter.setPen(QPen(HUDColor.TEXT_MUTED))
        painter.drawText(QRectF(m_left + 4, 3, 240, 16), Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft,
                         "LIVE LOAD OSCILLOSCOPE (60s BUFFER)")

        # 수치 배지
        rx = w - m_right
        painter.setPen(QPen(HUDColor.CYAN))
        painter.drawText(QRectF(rx - 190, 3, 90, 16), Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignRight,
                         f"CPU: {int(round(self.curr_cpu))}%")

        painter.setPen(QPen(HUDColor.MAGENTA))
        painter.drawText(QRectF(rx - 90, 3, 90, 16), Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignRight,
                         f"GPU: {int(round(self.curr_gpu))}%")


class WideGraphAndProcessWidget(QWidget):
    """
    상단 와이드 그래프 + 하단 프로세스 센티넬 통합 복합 위젯
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        self.osc_graph = WideOscilloscopeGraph(max_points=80, parent=self)
        self.proc_table = TopProcessTable(parent=self)

        layout.addWidget(self.osc_graph, stretch=1)
        layout.addWidget(self.proc_table, stretch=0)

    def update_telemetry(self, cpu_p, gpu_p, procs):
        self.osc_graph.add_points(cpu_p, gpu_p)
        self.proc_table.set_processes(procs)
